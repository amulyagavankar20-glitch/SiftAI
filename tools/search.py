from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from schemas.evidence import SearchInput
from tools.providers import search_with_fallback


@tool("web_search", args_schema=SearchInput)
def web_search(
    query: str,
    max_results: int = 4,
    recency_days: Optional[int] = None,
    allowed_domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Search for research sources and return title, URL, snippet, and date metadata."""
    search_query = query
    if allowed_domains:
        domains = " OR ".join(f"site:{domain}" for domain in allowed_domains)
        search_query = f"{query} ({domains})"

    timelimit = None
    if recency_days is not None:
        timelimit = (
            "d" if recency_days <= 1
            else "w" if recency_days <= 7
            else "m" if recency_days <= 30
            else "y"
        )

    result = search_with_fallback(search_query, max_results)
    if not result["results"]:
        result["error"] = "No search results were returned by configured providers."
    if timelimit:
        result["requested_recency"] = timelimit
    return result
