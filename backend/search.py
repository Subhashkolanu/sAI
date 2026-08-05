"""
=========================================================
sAI V1 - Search Engine
=========================================================
Features
- DuckDuckGo Web Search
- Fetch page content
- HTML text extraction
=========================================================
"""

from __future__ import annotations

from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from config import SEARCH_RESULTS


class SearchEngine:
    def __init__(self):
        self.timeout = 10

    # --------------------------------------------------

    def web_search(self, query: str, limit: int = SEARCH_RESULTS) -> List[Dict]:
        results = []

        with DDGS() as ddgs:
            search = ddgs.text(query, max_results=limit)

            for item in search:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "body": item.get("body", ""),
                    }
                )

        return results

    # --------------------------------------------------

    def fetch_page(self, url: str) -> str:
        headers = {
            "User-Agent": "sAI/1.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    # --------------------------------------------------

    def summarize_page(self, url: str, max_chars: int = 2000) -> str:
        text = self.fetch_page(url)

        if len(text) <= max_chars:
            return text

        return text[:max_chars] + "\n..."

    # --------------------------------------------------

    def search_and_fetch(self, query: str):
        results = self.web_search(query)

        if not results:
            return None

        first = results[0]

        try:
            content = self.summarize_page(first["url"])
        except Exception:
            content = ""

        return {
            "query": query,
            "result": first,
            "content": content,
        }


if __name__ == "__main__":

    search = SearchEngine()

    data = search.search_and_fetch("Artificial Intelligence")

    if data:
        print("\nTitle:\n")
        print(data["result"]["title"])

        print("\nURL:\n")
        print(data["result"]["url"])

        print("\nContent Preview:\n")
        print(data["content"])