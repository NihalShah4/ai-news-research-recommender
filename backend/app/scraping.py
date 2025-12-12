import feedparser
from typing import List, Dict


# You can expand this mapping later
RSS_SOURCES: Dict[str, List[str]] = {
    "ai": [
        "https://export.arxiv.org/rss/cs.AI",
        "https://export.arxiv.org/rss/cs.LG",
    ],
    "ml": [
        "https://export.arxiv.org/rss/cs.LG",
        "https://export.arxiv.org/rss/stat.ML",
    ],
    "general-tech": [
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://feeds.arstechnica.com/arstechnica/science",
    ],
}


def fetch_rss_articles(topic: str, limit: int = 30) -> List[Dict]:
    """
    Fetch basic article metadata from RSS feeds.
    Returns list of dicts: {title, url, summary}
    """
    topic = topic.lower()
    feeds = RSS_SOURCES.get(topic, [])

    # If unknown topic, just use AI feeds as default
    if not feeds:
        feeds = RSS_SOURCES["ai"]

    articles: List[Dict] = []

    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)

        for entry in parsed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = getattr(entry, "summary", "").strip() or getattr(entry, "description", "").strip()

            if not title or not link:
                continue

            articles.append(
                {
                    "title": title,
                    "url": link,
                    "summary": summary,
                }
            )

            if len(articles) >= limit:
                return articles

    return articles
