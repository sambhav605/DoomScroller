"""
rss_fetcher.py

Fetches all articles published in the last 24 hours from configured
Nepali news RSS feeds. Returns a normalized list of article dicts.
"""

import feedparser
from datetime import datetime, timedelta, timezone
from time import mktime

RSS_FEEDS = {
    "RONB Post": "https://www.ronbpost.com/feed", 
    # "Online Khabar": "https://www.onlinekhabar.com/feed",      
}

HOURS_WINDOW = 24


def _entry_published_dt(entry):
    """Extract a timezone-aware published datetime from a feed entry, or None."""
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not time_struct:
        return None
    return datetime.fromtimestamp(mktime(time_struct), tz=timezone.utc)


def fetch_recent_articles(hours=HOURS_WINDOW):
    """
    Fetch and return all articles published within the last `hours` hours
    across all configured RSS feeds.

    Returns:
        List[dict]: each dict has keys:
            title, link, summary, source, published_at (UTC datetime)
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            parsed_feed = feedparser.parse(feed_url)

            if parsed_feed.bozo and not parsed_feed.entries:
                print(f"[warn] Could not parse feed for {source_name}: {feed_url}")
                continue

            for entry in parsed_feed.entries:
                published_at = _entry_published_dt(entry)

                # Skip entries with no date, or older than the cutoff window
                if published_at is None or published_at < cutoff:
                    continue

                articles.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "summary": entry.get("summary", "").strip(),
                    "source": source_name,
                    "published_at": published_at,
                })

        except Exception as e:
            print(f"[error] Failed fetching {source_name}: {e}")
            continue

    return articles


if __name__ == "__main__":
    # Quick manual test: run `python rss_fetcher.py`
    results = fetch_recent_articles()
    print(f"Fetched {len(results)} articles from the last {HOURS_WINDOW}h:\n")
    for a in results:
        print(f"- [{a['source']}] {a['title']} ({a['published_at']}) ({a['summary']})")