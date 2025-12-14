# AI News & Research Recommender

## Overview

AI News & Research Recommender is a lightweight local web application that ingests recent AI / ML research papers and tech articles from multiple public RSS feeds and allows users to search across them.

The goal of the project is to provide a simple, no-code way to:
- Collect AI-related content from trusted sources
- Index it locally
- Search and explore relevant articles using natural language queries

No external AI APIs are used. All data is fetched from public RSS feeds and processed locally.

---

## Key Features

- Topic-based article ingestion from curated RSS feeds
- Support for multiple AI-focused categories (AI, LLMs & Agents, Engineering, Safety & Evaluation)
- Local indexing of articles
- Keyword-based search across indexed content
- Clean, minimal UI focused on usability
- Fully local execution

---

## Tech Stack

### Backend
- Python
- FastAPI
- RSS feed ingestion
- In-memory / lightweight local storage

### Frontend
- React (Vite)
- Plain CSS (no heavy UI frameworks)
- Fetch-based API communication

---

## Project Structure
ai-news-research-recommender/
│
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI entry point
│ │ ├── sources.py # Topic and RSS feed definitions
│ │ ├── ingest.py # RSS ingestion logic
│ │ ├── search.py # Search logic
│ │ └── models.py # Data models
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React application
│ │ ├── App.css # Styling
│ │ └── main.jsx # React entry point
│ └── package.json
│
└── README.md


---

## Topics and Data Sources

Articles are grouped into predefined topics. Each topic consists of multiple public RSS feeds.

Example sources include:
- arXiv (cs.AI, cs.LG, cs.CL, stat.ML)
- OpenAI Blog
- DeepMind Blog
- Hugging Face Blog
- Microsoft Research Blog
- Anthropic News
- Hacker News (AI-related queries)

All feeds are defined in `backend/app/sources.py`.

---

## How It Works

1. **Choose a Topic**
   - Select a predefined topic such as AI, LLMs & Agents, or AI Engineering.

2. **Fetch Articles**
   - The backend pulls recent entries from all RSS feeds associated with the topic.
   - Articles are stored and indexed locally.

3. **Search**
   - Enter a query to search across titles and summaries of indexed articles.
   - Results are ranked by relevance and displayed with summaries and source links.

---

## Running the Project Locally

### Prerequisites
- Python 3.9+
- Node.js 18+

---

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Backend

The backend runs locally at:
http://127.0.0.1:8000

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

The frontend runs locally at:
http://localhost:5173

---

### API Endpoints (Backend)

- GET /topics
Returns available topics and their metadata.

- POST /ingest
Fetches and indexes articles for a given topic.

- POST /search
Searches indexed articles using a text query.

---

### Design Decisions

- No external AI APIs are used to keep the project lightweight and privacy-friendly.
- Features that did not add clear value (trend dashboards, visual maps) were intentionally removed.
- The focus is on stability, clarity, and practical usability rather than feature count.

---

### Limitations

- Search is keyword-based, not embedding-based.
- Data is not persisted across restarts unless extended.
- RSS feeds depend on third-party availability and update frequency.

---

### Possible Future Improvements

- Persistent storage using SQLite or PostgreSQL
- Embedding-based semantic search
- User profiles and saved searches
- Scheduled background ingestion
- Deployment support using Docker or cloud hosting