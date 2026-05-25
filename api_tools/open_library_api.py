"""
api_tools/open_library_api.py
------------------------------
External API #2 — Open Library API (Internet Archive)

Searches for books, authors, and subjects.
100% free, no API key required.
Docs: https://openlibrary.org/dev/docs/api
"""

import requests


class OpenLibraryClient:
    """
    Wrapper around the Open Library Search API.
    Endpoint: https://openlibrary.org/search.json
    """

    SEARCH_URL = "https://openlibrary.org/search.json"
    SUBJECT_URL = "https://openlibrary.org/subjects/{subject}.json"

    def search_books(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search for books matching the query.

        Args:
            query: Free text search (title, author, subject)
            max_results: Number of results to return

        Returns:
            List of book dicts with: title, author, year, subjects, description
        """
        params = {
            "q": query,
            "limit": max_results,
            "fields": "title,author_name,first_publish_year,subject,isbn",
        }

        try:
            response = requests.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            books = []
            for doc in data.get("docs", []):
                books.append({
                    "title": doc.get("title", "Unknown Title"),
                    "authors": doc.get("author_name", ["Unknown Author"]),
                    "year": doc.get("first_publish_year", "N/A"),
                    "subjects": doc.get("subject", [])[:5],  # first 5 subjects
                    "isbn": (doc.get("isbn") or ["N/A"])[0],
                })

            print(f"[OpenLibrary] Query: '{query}' → {len(books)} book(s)")
            return books

        except requests.exceptions.RequestException as e:
            print(f"[OpenLibrary] Request failed: {e}")
            return self._mock_books(query)

    def format_for_agent(self, books: list[dict]) -> str:
        """Format book results into a readable string for agent prompts."""
        if not books:
            return "No books found in Open Library."

        lines = ["📚 Relevant Books from Open Library:\n"]
        for i, b in enumerate(books, 1):
            authors_str = ", ".join(b["authors"][:2]) if b["authors"] else "Unknown"
            subjects_str = ", ".join(b["subjects"][:3]) if b["subjects"] else "N/A"
            lines.append(
                f"{i}. \"{b['title']}\" by {authors_str} ({b['year']})\n"
                f"   Subjects: {subjects_str}\n"
                f"   ISBN: {b['isbn']}\n"
            )
        return "\n".join(lines)

    def _mock_books(self, query: str) -> list[dict]:
        """Mock results for offline testing."""
        return [
            {
                "title": f"Introduction to {query}",
                "authors": ["Mock Author"],
                "year": 2023,
                "subjects": [query, "Research", "Science"],
                "isbn": "0000000000",
            }
        ]
