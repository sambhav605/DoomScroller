"""
parser.py

Fetches the full article page for a given link and extracts clean
body text using BeautifulSoup4. Used when an RSS summary is truncated
and we want the full story before summarizing.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


TAGS_TO_STRIP = ["script", "style", "nav", "header", "footer", "aside", "form", "iframe"]


BODY_SELECTORS = [
    {"name": "article"},
    {"name": "div", "attrs": {"class": "post-content"}},
    {"name": "div", "attrs": {"class": "entry-content"}},
    {"name": "div", "attrs": {"class": "content-body"}},
    {"name": "div", "attrs": {"class": "article-content"}},
]

MIN_PARAGRAPH_LENGTH = 40 


def fetch_full_article(url, timeout=10):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[error] Failed to fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(TAGS_TO_STRIP):
        tag.decompose()

    container = None
    for selector in BODY_SELECTORS:
        container = soup.find(selector["name"], attrs=selector.get("attrs", {}))
        if container:
            break

    # Fallback: no known container matched, use the whole page body
    if container is None:
        container = soup.body or soup

    paragraphs = container.find_all("p")
    text_chunks = [
        p.get_text(strip=True)
        for p in paragraphs
        if len(p.get_text(strip=True)) >= MIN_PARAGRAPH_LENGTH
    ]

    return "\n\n".join(text_chunks)


if __name__ == "__main__":
    test_url = "https://www.onlinekhabar.com/"  # replace with a real article link
    text = fetch_full_article(test_url)
    print(text[:1000] if text else "[no text extracted]")