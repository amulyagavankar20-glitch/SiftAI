import io
from pathlib import Path
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from pypdf import PdfReader

from schemas.evidence import PDFParseInput, PageFetchInput

PAGE_CACHE: Dict[str, str] = {}
USER_AGENT = "ResearchAgent/1.0"


@tool("fetch_page", args_schema=PageFetchInput)
def fetch_page(url: str) -> Dict[str, Any]:
    """Fetch and clean readable text from an HTTP(S) page."""
    if url in PAGE_CACHE:
        return {"url": url, "text": PAGE_CACHE[url], "cached": True}

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"url": url, "text": "", "error": f"Page fetch failed: {exc}"}

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
    text = " ".join(soup.stripped_strings)[:6000]
    PAGE_CACHE[url] = text
    return {"url": url, "text": text, "status": "success"}


@tool("parse_pdf", args_schema=PDFParseInput)
def parse_pdf(url_or_path: str) -> Dict[str, Any]:
    """Download or open a PDF and extract text from its first ten pages."""
    try:
        if url_or_path.startswith(("http://", "https://")):
            response = requests.get(
                url_or_path,
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
            response.raise_for_status()
            reader = PdfReader(io.BytesIO(response.content))
        else:
            reader = PdfReader(Path(url_or_path))
    except (OSError, requests.RequestException, ValueError) as exc:
        return {"source": url_or_path, "text": "", "error": f"PDF access failed: {exc}"}

    pages = []
    for index, page in enumerate(reader.pages[:6]):
        page_text = page.extract_text()
        if page_text:
            pages.append(f"--- Page {index + 1} ---\n{page_text}")
    return {
        "source": url_or_path,
        "pages_parsed": min(len(reader.pages), 6),
        "text": "\n".join(pages)[:8000],
    }
