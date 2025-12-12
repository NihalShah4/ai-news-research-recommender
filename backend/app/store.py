import numpy as np
from typing import List, Dict, Set
from app.models import Article


class VectorStore:
    def __init__(self):
        self.articles: List[Article] = []
        self.embeddings: List[List[float]] = []
        self._seen_urls: Set[str] = set()

    def add(self, article: Article):
        # simple dedupe by URL
        if article.url in self._seen_urls:
            return

        self._seen_urls.add(article.url)
        self.articles.append(article)
        self.embeddings.append(article.embedding)

    def search(self, query_embedding, top_k=5):
        if not self.embeddings:
            return []

        emb_matrix = np.array(self.embeddings)
        query = np.array(query_embedding)

        # Cosine similarity (embeddings are normalized)
        scores = emb_matrix @ query

        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            art = self.articles[idx]
            results.append(
                {
                    "title": art.title,
                    "url": art.url,
                    "summary": art.summary,
                    "score": float(scores[idx]),
                }
            )

        return results
