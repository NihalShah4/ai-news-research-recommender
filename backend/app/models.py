from pydantic import BaseModel
from typing import List, Optional


class Article(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    content: Optional[str] = None
    embedding: Optional[List[float]] = None


class IngestRequest(BaseModel):
    topic: str
    urls: List[str]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    title: str
    url: str
    score: float
