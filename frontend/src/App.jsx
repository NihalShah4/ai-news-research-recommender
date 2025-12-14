import { useEffect, useState } from "react";
import "./App.css";

const BACKEND_BASE = (import.meta.env.VITE_BACKEND_BASE || "http://127.0.0.1:8000").replace(
  /\/+$/,
  ""
);

async function getJson(path) {
  const res = await fetch(`${BACKEND_BASE}${path}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Request failed");
  return data;
}

async function postJson(path, body) {
  const res = await fetch(`${BACKEND_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Request failed");
  return data;
}

export default function App() {
  const [topics, setTopics] = useState([]);
  const [topicKey, setTopicKey] = useState("");
  const [perFeedLimit, setPerFeedLimit] = useState(10);

  const [indexed, setIndexed] = useState(0);
  const [query, setQuery] = useState("AI");
  const [results, setResults] = useState([]);

  const [loadingFetch, setLoadingFetch] = useState(false);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await getJson("/topics");
        setTopics(data.topics);
        if (data.topics.length > 0) {
          setTopicKey(data.topics[0].key);
        }
      } catch (e) {
        setError("Failed to load topics");
      }
    })();
  }, []);

  const handleFetch = async () => {
    try {
      setError("");
      setLoadingFetch(true);
      setResults([]);

      const data = await postJson("/ingest", {
        topic_key: topicKey,
        per_feed_limit: perFeedLimit,
      });

      setIndexed(data.total_indexed || 0);
    } catch (e) {
      setError(`Fetch failed: ${e.message}`);
    } finally {
      setLoadingFetch(false);
    }
  };

  const handleSearch = async () => {
    try {
      setError("");
      setLoadingSearch(true);

      const data = await postJson("/search", { query });
      setResults(data.results || []);
    } catch (e) {
      setError(`Search failed: ${e.message}`);
    } finally {
      setLoadingSearch(false);
    }
  };

  return (
    <div className="appShell">
      <header className="header">
        <h1>AI News & Research Recommender</h1>
        <p className="subtitle">
          A simple tool that finds relevant AI / ML papers and tech articles for ingest-and-search.
          No coding needed.
        </p>
      </header>

      <main className="grid">
        {/* LEFT PANEL */}
        <section className="card">
          <div className="pill">Step 1 · Choose a topic & fetch</div>
          <h2>Choose a topic & fetch articles</h2>

          <label className="label">Topic</label>
          <select
            className="select"
            value={topicKey}
            onChange={(e) => setTopicKey(e.target.value)}
          >
            {topics.map((t) => (
              <option key={t.key} value={t.key}>
                {t.label}
              </option>
            ))}
          </select>

          <label className="label">Articles per feed</label>
          <input
            className="input"
            type="number"
            min="1"
            max="50"
            value={perFeedLimit}
            onChange={(e) => setPerFeedLimit(Number(e.target.value))}
          />

          <button className="btn primary" onClick={handleFetch} disabled={loadingFetch}>
            {loadingFetch ? "Fetching..." : "Fetch latest articles"}
          </button>

          <div className="pill" style={{ marginTop: 20 }}>
            Step 2 · Ask a question
          </div>

          <label className="label">Query</label>
          <div className="row">
            <input
              className="input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              className="btn"
              onClick={handleSearch}
              disabled={indexed === 0 || loadingSearch}
            >
              {loadingSearch ? "Searching..." : "Search"}
            </button>
          </div>

          <div className="muted">Indexed: {indexed}</div>

          {error && <div className="error">{error}</div>}
        </section>

        {/* RIGHT PANEL */}
        <section className="card">
          <h2>Results</h2>
          <p className="muted">
            Relevant papers and articles with short summaries and source links.
          </p>

          {results.length === 0 ? (
            <div className="empty">
              No results yet. Fetch articles and run a search.
            </div>
          ) : (
            <div className="results">
              {results.map((r) => (
                <article key={r.url} className="resultCard">
                  <h3>{r.title}</h3>
                  <p>{r.summary || "No summary available."}</p>
                  <a href={r.url} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        Runs locally using public RSS feeds. No data is sent to any third-party AI API.
      </footer>
    </div>
  );
}
