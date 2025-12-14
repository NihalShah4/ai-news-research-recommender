from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Article(BaseModel):
    title: str
    url: str
    source: str
    published: Optional[str] = None
    text: str = ""
    summary: str = ""


class FeedSource(BaseModel):
    name: str
    url: str


class Topic(BaseModel):
    key: str
    label: str
    description: str
    feeds: List[FeedSource]


class IngestRequest(BaseModel):
    topic_key: str = Field(..., description="Topic key from /topics")
    per_feed_limit: int = Field(10, ge=1, le=50, description="How many items to pull per feed")


class IngestResponse(BaseModel):
    added: int
    total_indexed: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(8, ge=1, le=25)
    # Optional filters (safe defaults)
    days: Optional[int] = Field(None, ge=1, le=365, description="Only include items published in last N days")
    sources: Optional[List[str]] = Field(None, description="Only include these source names")


class SearchResult(BaseModel):
    title: str
    url: str
    source: str
    summary: str
    score: float
    # Phase 1.2 “Why it matches”
    why: Optional[List[str]] = None


class SearchResponse(BaseModel):
    total_indexed: int
    results: List[SearchResult]


class StatsResponse(BaseModel):
    total_indexed: int


# ----------------------------
# Phase 2: Trending dashboard
# ----------------------------
class TrendsRequest(BaseModel):
    days: int = Field(7, ge=1, le=365)
    top_n: int = Field(12, ge=3, le=50)
    sources: Optional[List[str]] = None  # optional source filter


class DailyCount(BaseModel):
    day: str  # YYYY-MM-DD
    count: int


class TrendsResponse(BaseModel):
    days: int
    total_items: int
    by_day: List[DailyCount]
    top_sources: List[Dict[str, int]]  # [{"source": "...", "count": 12}, ...]
    top_keywords: List[Dict[str, int]]  # [{"term": "...", "count": 18}, ...]


# ----------------------------
# Phase 2: Research map
# ----------------------------
class MapRequest(BaseModel):
    # If query is provided, we return the k closest points to query in 2D space
    query: Optional[str] = None
    k: int = Field(150, ge=20, le=1000)
    sources: Optional[List[str]] = None
    days: Optional[int] = Field(None, ge=1, le=365)


class MapPoint(BaseModel):
    x: float
    y: float
    title: str
    url: str
    source: str
    published: Optional[str] = None


class MapResponse(BaseModel):
    total_indexed: int
    points: List[MapPoint]
    query_point: Optional[Dict[str, float]] = None  # {"x":..., "y":...}
