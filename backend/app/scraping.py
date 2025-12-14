import re
import time
from typing import List
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

from app.models import Article, FeedSource


UA = "ai-news-research-recommender/1.0 (+local)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}


def _clean_text(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    # Strip HTML if present (RSS summaries often contain tags)
    s = BeautifulSoup(s, "html.parser").get_text(" ")
    s = re.sub(r"\s+", " ", s).strip()
    return s




def _summarize(text: str, max_chars: int = 320) -> str:
    text = _clean_text(text)
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _extract_article_text(url: str, timeout: int = 12) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove junk
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Prefer paragraphs
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join([p for p in paras if p])
    return _clean_text(text)


def ingest_from_feeds(feeds: List[FeedSource], per_feed_limit: int = 10) -> List[Article]:
    articles: List[Article] = []

    for feed in feeds:
        parsed = feedparser.parse(feed.url)
        entries = parsed.entries[:per_feed_limit]

        for e in entries:
            title = _clean_text(getattr(e, "title", "") or "")
            url = getattr(e, "link", None) or getattr(e, "id", None) or ""
            url = _clean_text(url)

            if not title or not url:
                continue

            published = ""
            if getattr(e, "published", None):
                published = str(e.published)
            elif getattr(e, "updated", None):
                published = str(e.updated)
            else:
                published = datetime.utcnow().isoformat()

            # Many RSS feeds already include a good summary/abstract
            rss_summary = _clean_text(getattr(e, "summary", "") or "")

            text = ""
            # If summary is too short, try fetching the page
            if len(rss_summary) < 200:
                text = _extract_article_text(url)
            else:
                text = rss_summary

            summary = _summarize(text)

            articles.append(
                Article(
                    title=title,
                    url=url,
                    source=feed.name,
                    published=published,
                    text=text,
                    summary=summary if summary else "No summary available.",
                )
            )

            # be polite to websites
            time.sleep(0.2)

    return articles
