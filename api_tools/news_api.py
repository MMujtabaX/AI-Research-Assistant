"""
api_tools/news_api.py
----------------------
External API #1 — NewsAPI

Fetches recent news articles relevant to the research query.
Free tier: https://newsapi.org (register for a free key)
"""

import requests
from config.settings import NEWS_API_KEY


class NewsAPIClient:
    """
    Wrapper around the NewsAPI /v2/everything endpoint.
    Docs: https://newsapi.org/docs/endpoints/everything
    """

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self):
        self.api_key = NEWS_API_KEY
        if not self.api_key:
            print("[NewsAPI] ⚠️  NEWS_API_KEY not set — news search will return empty results.")

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search recent news articles by keyword.

        Args:
            query: The search term (e.g. 'quantum computing research')
            max_results: How many articles to return (max 100 on free tier)

        Returns:
            List of article dicts with keys: title, description, url, publishedAt, source
        """
        if not self.api_key:
            return self._mock_results(query)

        params = {
            "q": query,
            "apiKey": self.api_key,
            "pageSize": max_results,
            "sortBy": "relevancy",
            "language": "en",
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = data.get("articles", [])
            results = []
            for article in articles:
                results.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "url": article.get("url", ""),
                    "published": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                })

            print(f"[NewsAPI] Query: '{query}' → {len(results)} article(s)")
            return results

        except requests.exceptions.RequestException as e:
            print(f"[NewsAPI] Request failed: {e}")
            return self._mock_results(query)

    def format_for_agent(self, articles: list[dict]) -> str:
        """Format articles into a readable string for agent prompts."""
        if not articles:
            return "No recent news articles found."

        lines = ["📰 Recent News Articles:\n"]
        for i, a in enumerate(articles, 1):
            lines.append(
                f"{i}. [{a['source']}] {a['title']}\n"
                f"   {a['description']}\n"
                f"   Published: {a['published'][:10] if a['published'] else 'N/A'}\n"
                f"   URL: {a['url']}\n"
            )
        return "\n".join(lines)

    def _mock_results(self, query: str) -> list[dict]:
        """Return mock results when API key is missing (for testing)."""
        return [
            {
                "title": f"[MOCK] Latest developments in {query}",
                "description": f"Researchers have made significant advances in {query}.",
                "url": "https://example.com/mock-article",
                "published": "2025-01-01",
                "source": "Mock News Source",
            }
        ]
