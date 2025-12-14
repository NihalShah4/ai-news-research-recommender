from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import TrendsRequest, TrendsResponse, MapRequest, MapResponse, MapPoint, DailyCount

from app.models import (
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StatsResponse,
)
from app.sources import get_topics, get_topic_by_key
from app.scraping import ingest_from_feeds
from app.store import VectorStore

app = FastAPI(
    title="AI News & Research Recommender",
    version="0.4.1",
)

# Adjust if needed
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VectorStore()

@app.post("/reset")
def reset():
    store.reset()
    return {"status": "ok", "total_indexed": store.total()}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/topics")
def topics():
    return {"topics": [t.model_dump() for t in get_topics()]}


@app.get("/stats", response_model=StatsResponse)
def stats():
    return StatsResponse(total_indexed=store.total())


@app.post("/trends", response_model=TrendsResponse)
def trends(req: TrendsRequest):
    data = store.trends(days=req.days, top_n=req.top_n, sources=req.sources)
    # Pydantic will validate/shape it via TrendsResponse
    return data


@app.post("/map", response_model=MapResponse)
def map_2d(req: MapRequest):
    data = store.map_2d(k=req.k, query=req.query, days=req.days, sources=req.sources)
    return {
        "total_indexed": store.total(),
        "points": [MapPoint(**p) for p in data["points"]],
        "query_point": data["query_point"],
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    topic = get_topic_by_key(req.topic_key)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Unknown topic_key: {req.topic_key}")

    articles = ingest_from_feeds(topic.feeds, per_feed_limit=req.per_feed_limit)
    added = store.add_many(articles)

    return IngestResponse(added=added, total_indexed=store.total())


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    results = store.search(req.query, k=req.k, days=req.days, sources=req.sources)
    return SearchResponse(
        total_indexed=store.total(),
        results=[SearchResult(**r) for r in results],
    )




from pathlib import Path
import os
from datetime import datetime

@app.get("/persist-info")
def persist_info():
    path = Path(os.getenv("VECTORSTORE_PATH", "./data/vectorstore.joblib"))
    exists = path.exists()
    mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat() if exists else None

    return {
        "path": str(path.resolve()),
        "exists": exists,
        "last_modified": mtime,
        "total_indexed": store.total(),
    }
