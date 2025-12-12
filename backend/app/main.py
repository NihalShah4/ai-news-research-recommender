from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.embedder import Embedder
from app.store import VectorStore
from app.models import IngestRequest, SearchRequest, Article
from app.scraping import fetch_rss_articles


app = FastAPI(
    title="AI News & Research Recommendation Engine",
    version="0.3.0"
)

# --- CORS so the React app (localhost:5173) can call the API ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core engine setup ---
embedder = Embedder()
store = VectorStore()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_articles(request: IngestRequest):
    embeddings = embedder.embed(request.urls)

    for url, emb in zip(request.urls, embeddings):
        article = Article(title=url, url=url, embedding=emb)
        store.add(article)

    return {"message": "Articles ingested", "count": len(request.urls)}


@app.post("/ingest_topic")
def ingest_topic(topic: str, limit: int = 30):
    """
    Ingest live articles for a given topic from RSS feeds.
    Topics supported: 'ai', 'ml', 'general-tech' (more can be added).
    """
    raw_articles = fetch_rss_articles(topic=topic, limit=limit)

    if not raw_articles:
        return {"message": "No articles found for topic", "topic": topic, "count": 0}

    texts_to_embed = [
        f"{a['title']} {a.get('summary', '')}" for a in raw_articles
    ]
    embeddings = embedder.embed(texts_to_embed)

    for raw, emb in zip(raw_articles, embeddings):
        article = Article(
            title=raw["title"],
            url=raw["url"],
            summary=raw.get("summary", None),
            embedding=emb,
        )
        store.add(article)

    return {"message": "Topic ingested", "topic": topic, "count": len(raw_articles)}


@app.post("/search")
def search_articles(request: SearchRequest):
    query_emb = embedder.embed(request.query)[0]
    results = store.search(query_emb, top_k=request.top_k)
    return {"results": results}
