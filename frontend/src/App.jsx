import React, { useState } from "react";

const TOPICS = [
  {
    value: "ai_arxiv",
    label: "AI research (arXiv cs.AI / cs.LG)",
    description: "Recent AI / ML papers from arXiv cs.AI, cs.LG, etc.",
  },
  {
    value: "ml_engineering",
    label: "ML engineering & MLOps",
    description: "Production ML, monitoring, MLOps tooling and patterns.",
  },
  {
    value: "llm_apps",
    label: "LLM applications & agents",
    description: "Agent frameworks, prompt engineering, evals, safety.",
  },
];

function App() {
  const [topic, setTopic] = useState(TOPICS[0].value);
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState("");
  const [results, setResults] = useState([]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const handleIngest = async () => {
    setIsIngesting(true);
    setStatus("Fetching latest articles and indexing them locally…");

    try {
      const resp = await fetch("http://127.0.0.1:8000/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });

      if (!resp.ok) {
        throw new Error(`Server responded with ${resp.status}`);
      }

      const data = await resp.json();
      setStatus(
        `Indexed ${data.count ?? data.num_articles ?? "the latest"} articles for "${data.topic_label ?? topic}". You can now ask a question.`
      );
    } catch (err) {
      console.error(err);
      setStatus("Something went wrong while ingesting articles.");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleSearch = async () => {
    if (!question.trim()) {
      setStatus("Please type a question or keyword first.");
      return;
    }

    setIsSearching(true);
    setStatus("Searching through your local index…");

    try {
      const resp = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, query: question }),
      });

      if (!resp.ok) {
        throw new Error(`Server responded with ${resp.status}`);
      }

      const data = await resp.json();
      setResults(data.results || []);
      setStatus(
        `Found ${data.results?.length ?? 0} relevant articles for your query.`
      );
    } catch (err) {
      console.error(err);
      setStatus("Something went wrong while searching. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-shell">
        <header className="app-header">
          <h1 className="app-title">AI News &amp; Research Recommender</h1>
          <p className="app-subtitle">
            A simple tool that finds relevant AI / ML papers and tech articles
            for your questions. No coding needed.
          </p>
        </header>

        <main className="app-main">
          {/* LEFT: controls */}
          <section className="panel panel--sidebar">
            <div className="panel-header">
              <div className="badge-pill">Step 1 · Choose a topic &amp; fetch</div>
              <h2 className="panel-title">Choose a topic &amp; fetch articles</h2>
              <p className="panel-caption">
                Start by choosing a broad topic. The app will pull the latest
                articles and research from public RSS feeds and index them
                locally on your machine.
              </p>
            </div>

            <div className="field-group">
              <label className="field-label" htmlFor="topic-select">
                Topic
              </label>
              <select
                id="topic-select"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              >
                {TOPICS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
              <p className="status-text">
                {
                  TOPICS.find((t) => t.value === topic)?.description ??
                  "Choose the feed you want to work with."
                }
              </p>
            </div>

            <div className="field-group">
              <button
                className="btn-primary"
                onClick={handleIngest}
                disabled={isIngesting}
              >
                {isIngesting ? "Fetching & indexing…" : "Fetch latest articles"}
              </button>
            </div>

            <div className="panel-header" style={{ marginTop: 18 }}>
              <div className="badge-pill">Step 2 · Ask a question</div>
              <h2 className="panel-title">Ask a question</h2>
              <p className="panel-caption">
                Type a question or keyword and the engine will look for the most
                relevant papers / articles in what you just ingested.
              </p>
            </div>

            <div className="field-group">
              <label className="field-label" htmlFor="question-input">
                Query
              </label>
              <input
                id="question-input"
                type="text"
                placeholder='Examples: "LLMs for financial fraud", "Graph neural nets for recommender systems"'
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </div>

            <div className="button-row">
              <button
                className="btn-secondary"
                onClick={handleSearch}
                disabled={isSearching}
              >
                {isSearching ? "Searching…" : "Search"}
              </button>
            </div>

            {status && <p className="status-text">{status}</p>}
          </section>

          {/* RIGHT: results */}
          <section className="panel panel--results">
            <div className="panel-header">
              <h2 className="panel-title">Results</h2>
              <p className="panel-caption">
                You&apos;ll see the most relevant papers and articles here, with
                short summaries and links.
              </p>
            </div>

            <div className="results-wrapper">
              <div className="results-list">
                {results.length === 0 ? (
                  <p className="status-text">
                    No results yet. Fetch some articles and then ask a question.
                  </p>
                ) : (
                  results.map((item, idx) => (
                    <article key={idx} className="result-item">
                      <h3 className="result-title">{item.title}</h3>
                      <div className="result-meta">
                        {item.source && <span>{item.source}</span>}
                        {item.published && (
                          <span> · {new Date(item.published).toLocaleString()}</span>
                        )}
                      </div>
                      {item.summary && (
                        <p className="result-snippet">{item.summary}</p>
                      )}
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            fontSize: "0.8rem",
                            color: "#008f83",
                            textDecoration: "none",
                            marginTop: "4px",
                            display: "inline-block",
                          }}
                        >
                          Open article →
                        </a>
                      )}
                    </article>
                  ))
                )}
              </div>
            </div>
          </section>
        </main>

        <footer className="app-footer">
          Runs locally using free public RSS feeds and open-source models. No
          data is sent to any third-party API.
        </footer>
      </div>
    </div>
  );
}

export default App;
