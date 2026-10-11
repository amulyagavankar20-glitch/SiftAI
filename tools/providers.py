import os
import time
from typing import Any, Dict, List, Protocol

import requests
from ddgs import DDGS
from ddgs.exceptions import DDGSException


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        ...


class TavilySearchProvider:
    endpoint = "https://api.tavily.com/search"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        response = requests.post(
            self.endpoint,
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:400],
                "published": item.get("published_date", "Unknown"),
            }
            for item in payload.get("results", [])
        ]


class DDGSSearchProvider:
    def search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        with DDGS() as client:
            raw_results = client.text(query=query, max_results=max_results)
            return [
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")[:400],
                    "published": item.get("date", "Unknown"),
                }
                for item in raw_results
            ]


def configured_search_providers() -> List[SearchProvider]:
    providers: List[SearchProvider] = []
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        providers.append(TavilySearchProvider(tavily_key))
    providers.append(DDGSSearchProvider())
    return providers


def search_with_fallback(
    query: str,
    max_results: int,
    retries_per_provider: int = 2,
) -> Dict[str, Any]:
    errors: List[str] = []
    for provider in configured_search_providers():
        for attempt in range(retries_per_provider):
            try:
                results = provider.search(query, max_results)
                if results:
                    return {
                        "query": query,
                        "count": len(results),
                        "results": results,
                        "provider": type(provider).__name__,
                    }
                errors.append(f"{type(provider).__name__}: no results")
            except (
                DDGSException,
                requests.RequestException,
                ConnectionError,
                TimeoutError,
                OSError,
            ) as exc:
                errors.append(f"{type(provider).__name__}: {exc}")
            if attempt + 1 < retries_per_provider:
                time.sleep(0.5)
    return {"query": query, "count": 0, "results": [], "errors": errors}
