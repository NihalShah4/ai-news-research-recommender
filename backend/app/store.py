from __future__ import annotations

from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timezone
import math
import re
import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

from app.models import Article


class VectorStore:
    def __init__(self):
        self.articles: List[Article] = []
        self._seen_urls: Set[str] = set()

        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=50000,
            ngram_range=(1, 2),
        )
        self._matrix = None  # TF-IDF matrix

        # Phase 2: cached 2D map
        self._svd: Optional[TruncatedSVD] = None
        self._map_xy: Optional[np.ndarray] = None

    def total(self) -> int:
        return len(self.articles)

    def add_many(self, new_articles: List[Article]) -> int:
        added = 0
        for a in new_articles:
            if not a.url:
                continue
            if a.url in self._seen_urls:
                continue
            self._seen_urls.add(a.url)
            self.articles.append(a)
            added += 1

        if added > 0:
            self._rebuild_index()

        return added

    # -------------------------
    # Indexing
    # -------------------------
    def _doc_text(self, a: Article) -> str:
        text = (a.text or "").strip()
        return f"{a.title}\n{text}"

    def _rebuild_index(self):
        docs = [self._doc_text(a) for a in self.articles]
        if not docs:
            self._matrix = None
            self._svd = None
            self._map_xy = None
            return

        self._matrix = self._vectorizer.fit_transform(docs)

        # Build 2D map cache (Phase 2)
        try:
            if self._matrix.shape[0] >= 3:
                self._svd = TruncatedSVD(n_components=2, random_state=42)
                xy = self._svd.fit_transform(self._matrix)
                self._map_xy = xy.astype(float)
            else:
                self._svd = None
                self._map_xy = None
        except Exception:
            self._svd = None
            self._map_xy = None

    # -------------------------
    # Utilities
    # -------------------------
    def _parse_published_dt(self, published: str) -> Optional[datetime]:
        s = (published or "").strip()
        if not s:
            return None
        # Try ISO first
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
        # Try RFC-ish / common feed strings (best effort)
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(s, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                continue
        return None

    def _age_days(self, a: Article) -> Optional[float]:
        dt = self._parse_published_dt(a.published or "")
        if dt is None:
            return None
        now = datetime.now(timezone.utc)
        return max(0.0, (now - dt).total_seconds() / 86400.0)

    def _split_sentences(self, text: str) -> list[str]:
        text = (text or "").strip()
        if not text:
            return []
        parts = re.split(r"(?<=[.!?])\s+", text)
        sents = [p.strip() for p in parts if len((p or "").strip()) >= 40]
        return sents[:60]

    def _extractive_summary(self, query: str, a: Article, max_sentences: int = 2, max_chars: int = 320) -> str:
        text = (a.text or "").strip()
        if not text:
            return (a.summary or "").strip() or "No summary available."

        sents = self._split_sentences(text)
        if not sents:
            return (a.summary or "").strip() or "No summary available."

        try:
            q_vec = self._vectorizer.transform([query])
            sent_vecs = self._vectorizer.transform(sents)
            sent_sims = cosine_similarity(q_vec, sent_vecs).flatten()

            ranked = sorted(range(len(sents)), key=lambda i: float(sent_sims[i]), reverse=True)

            picked = []
            total = 0
            for idx in ranked:
                s = sents[idx].strip()
                if s in picked:
                    continue
                if total + len(s) > max_chars and picked:
                    break
                picked.append(s)
                total += len(s)
                if len(picked) >= max_sentences:
                    break

            out = " ".join(picked).strip()
            return out if out else ((a.summary or "").strip() or "No summary available.")
        except Exception:
            return (a.summary or "").strip() or "No summary available."

    def _why_terms(self, query: str, a: Article, max_terms: int = 6) -> list[str]:
        analyzer = self._vectorizer.build_analyzer()
        q_tokens = [t for t in analyzer((query or "").strip()) if len(t) >= 3]
        if not q_tokens:
            return []

        doc_text = f"{a.title} {(a.text or '')}".strip()
        d_tokens = set(analyzer(doc_text))

        seen = set()
        out = []
        for t in q_tokens:
            if t in d_tokens and t not in seen:
                out.append(t)
                seen.add(t)
            if len(out) >= max_terms:
                break
        return out

    def _filter_articles(self, days: Optional[int] = None, sources: Optional[List[str]] = None) -> List[int]:
        idxs = []
        for i, a in enumerate(self.articles):
            if sources and a.source not in sources:
                continue
            if days is not None:
                ad = self._age_days(a)
                if ad is None or ad > days:
                    continue
            idxs.append(i)
        return idxs

    # -------------------------
    # Search (Phase 1 complete)
    # -------------------------
    def search(self, query: str, k: int = 8, days: Optional[int] = None, sources: Optional[List[str]] = None) -> List[Dict]:
        query = (query or "").strip()
        if not query or self._matrix is None or self.total() == 0:
            return []

        now = datetime.now(timezone.utc)
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()

        # Tunables
        half_life_days = float(os.getenv("RECENCY_HALF_LIFE_DAYS", "14"))
        recency_boost_strength = float(os.getenv("RECENCY_BOOST_STRENGTH", "0.25"))
        title_boost_strength = float(os.getenv("TITLE_BOOST_STRENGTH", "0.35"))

        recency_base = 1.0 - recency_boost_strength
        title_base = 1.0 - title_boost_strength

        scored: list[Tuple[float, int]] = []

        for i, sim in enumerate(sims):
            a = self.articles[i]

            if sources and a.source not in sources:
                continue

            dt = self._parse_published_dt(a.published or "")
            age_days = None if dt is None else max(0.0, (now - dt).total_seconds() / 86400.0)

            if days is not None:
                if age_days is None or age_days > days:
                    continue

            if age_days is None:
                recency_factor = 0.5
            else:
                recency_factor = math.exp(-math.log(2) * (age_days / max(half_life_days, 1e-6)))

            recency_multiplier = recency_base + recency_boost_strength * recency_factor

            # quick title similarity using TF-IDF overlap
            title_sim = float(cosine_similarity(q_vec, self._vectorizer.transform([a.title])).flatten()[0])
            title_multiplier = title_base + title_boost_strength * title_sim

            score = float(sim) * recency_multiplier * title_multiplier
            scored.append((score, i))

        if not scored:
            return []

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:k]

        results = []
        for score, i in top:
            a = self.articles[i]
            results.append(
                {
                    "title": a.title,
                    "url": a.url,
                    "source": a.source,
                    "summary": self._extractive_summary(query, a),
                    "score": float(score),
                    "why": self._why_terms(query, a),
                }
            )
        return results

    # -------------------------
    # Phase 2.1: Trends
    # -------------------------
    def trends(self, days: int = 7, top_n: int = 12, sources: Optional[List[str]] = None) -> Dict:
        idxs = self._filter_articles(days=days, sources=sources)

        # by_day
        day_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {}

        # keyword counts
        kw_counts: Dict[str, int] = {}

        analyzer = self._vectorizer.build_analyzer()

        for i in idxs:
            a = self.articles[i]

            # Source counts
            source_counts[a.source] = source_counts.get(a.source, 0) + 1

            # Day counts
            dt = self._parse_published_dt(a.published or "")
            if dt is None:
                day = "unknown"
            else:
                day = dt.date().isoformat()
            day_counts[day] = day_counts.get(day, 0) + 1

            # Keywords (title weighted)
            title_tokens = analyzer(a.title or "")
            body_tokens = analyzer((a.text or "")[:2500])  # cap for speed

            # Remove very common stop words + tiny tokens
            def keep(t: str) -> bool:
                return len(t) >= 3 and t not in ENGLISH_STOP_WORDS

            for t in title_tokens:
                if keep(t):
                    kw_counts[t] = kw_counts.get(t, 0) + 2  # title weight
            for t in body_tokens:
                if keep(t):
                    kw_counts[t] = kw_counts.get(t, 0) + 1

        # Sort outputs
        by_day_sorted = sorted(
            [{"day": d, "count": c} for d, c in day_counts.items()],
            key=lambda x: x["day"],
        )

        top_sources = sorted(
            [{"source": s, "count": c} for s, c in source_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:top_n]

        top_keywords = sorted(
            [{"term": t, "count": c} for t, c in kw_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:top_n]

        return {
            "days": days,
            "total_items": len(idxs),
            "by_day": by_day_sorted,
            "top_sources": top_sources,
            "top_keywords": top_keywords,
        }

    # -------------------------
    # Phase 2.2: Research map
    # -------------------------
    def map_2d(self, k: int = 150, query: Optional[str] = None, days: Optional[int] = None, sources: Optional[List[str]] = None) -> Dict:
        if self._map_xy is None or self._svd is None or self._matrix is None:
            return {"points": [], "query_point": None}

        idxs = self._filter_articles(days=days, sources=sources)
        if not idxs:
            return {"points": [], "query_point": None}

        xy = self._map_xy[idxs, :]

        query_point = None
        if query and query.strip():
            try:
                q_vec = self._vectorizer.transform([query.strip()])
                q_xy = self._svd.transform(q_vec)[0]
                query_point = {"x": float(q_xy[0]), "y": float(q_xy[1])}

                # pick closest in 2D space
                dists = np.sqrt(((xy - q_xy) ** 2).sum(axis=1))
                order = np.argsort(dists)[: min(k, len(idxs))]
                pick = [idxs[int(j)] for j in order]
            except Exception:
                pick = idxs[: min(k, len(idxs))]
        else:
            pick = idxs[: min(k, len(idxs))]

        points = []
        for i in pick:
            a = self.articles[i]
            x, y = self._map_xy[i]
            points.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "title": a.title,
                    "url": a.url,
                    "source": a.source,
                    "published": a.published,
                }
            )

        return {"points": points, "query_point": query_point}
