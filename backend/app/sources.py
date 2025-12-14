from app.models import Topic, FeedSource

# Notes:
# - arXiv RSS: use export.arxiv.org (reliable RSS)
# - HN RSS search: hnrss.org provides RSS feeds for keyword searches (community signal)
# - We keep your existing topics and add more feeds to make the dataset richer.

TOPICS = [
    Topic(
        key="ai_general",
        label="AI (feeds: 12)",
        description="Recent AI/ML papers and articles from multiple public feeds.",
        feeds=[
            # --- arXiv (papers) ---
            FeedSource(name="arXiv cs.AI", url="https://export.arxiv.org/rss/cs.AI"),
            FeedSource(name="arXiv cs.LG", url="https://export.arxiv.org/rss/cs.LG"),
            FeedSource(name="arXiv cs.CL", url="https://export.arxiv.org/rss/cs.CL"),
            FeedSource(name="arXiv stat.ML", url="https://export.arxiv.org/rss/stat.ML"),

            # --- Your existing blog feed ---
            FeedSource(name="Hugging Face Blog", url="https://huggingface.co/blog/feed.xml"),

            # --- Major research blogs ---
            FeedSource(name="Microsoft Research Blog", url="https://www.microsoft.com/en-us/research/feed/"),
            FeedSource(name="DeepMind Blog", url="https://deepmind.google/blog/rss.xml"),
            FeedSource(name="OpenAI Blog", url="https://openai.com/blog/rss.xml"),

            # --- Practitioner / community-friendly sources ---
            FeedSource(name="The Batch (DeepLearning.AI)", url="https://www.deeplearning.ai/the-batch/feed/"),
            FeedSource(name="Sebastian Ruder", url="https://ruder.io/rss/"),

            # --- Community (Hacker News keyword RSS) ---
            FeedSource(name="Hacker News (AI)", url="https://hnrss.org/newest?q=ai"),
            FeedSource(name="Hacker News (Machine Learning)", url="https://hnrss.org/newest?q=machine%20learning"),
        ],
    ),

    Topic(
        key="llms_agents",
        label="LLMs & Agents (feeds: 12)",
        description="Agents, tool use, RAG, evaluation, safety.",
        feeds=[
            # --- Your existing feeds ---
            FeedSource(name="arXiv cs.CL", url="https://export.arxiv.org/rss/cs.CL"),
            FeedSource(name="LangChain Blog", url="https://blog.langchain.dev/rss/"),
            FeedSource(name="Microsoft Research Blog", url="https://www.microsoft.com/en-us/research/feed/"),

            # --- arXiv expansions ---
            FeedSource(name="arXiv cs.AI", url="https://export.arxiv.org/rss/cs.AI"),
            FeedSource(name="arXiv cs.LG", url="https://export.arxiv.org/rss/cs.LG"),
            FeedSource(name="arXiv stat.ML", url="https://export.arxiv.org/rss/stat.ML"),

            # --- Core LLM ecosystem blogs ---
            FeedSource(name="Hugging Face Blog", url="https://huggingface.co/blog/feed.xml"),
            FeedSource(name="OpenAI Blog", url="https://openai.com/blog/rss.xml"),
            FeedSource(name="Anthropic News", url="https://www.anthropic.com/news/rss.xml"),

            # --- More depth: RAG/agents/tooling discussion sources ---
            FeedSource(name="Simon Willison", url="https://simonwillison.net/atom/everything/"),
            FeedSource(name="Lil'Log", url="https://lilianweng.github.io/lil-log/feed.xml"),

            # --- Community (HN) ---
            FeedSource(name="Hacker News (LLM)", url="https://hnrss.org/newest?q=llm"),
            FeedSource(name="Hacker News (Agents)", url="https://hnrss.org/newest?q=agents"),
            FeedSource(name="Hacker News (RAG)", url="https://hnrss.org/newest?q=rag"),
        ],
    ),

    Topic(
        key="engineering",
        label="AI Engineering (feeds: 12)",
        description="Infra, deployment, performance, systems, MLOps.",
        feeds=[
            # --- Your existing feeds ---
            FeedSource(name="NVIDIA Developer Blog", url="https://developer.nvidia.com/blog/feed/"),
            FeedSource(name="Google AI Blog", url="https://ai.googleblog.com/feeds/posts/default?alt=rss"),
            FeedSource(name="AWS ML Blog", url="https://aws.amazon.com/blogs/machine-learning/feed/"),

            # --- Add strong engineering sources ---
            FeedSource(name="Google Cloud Blog (AI/ML)", url="https://cloud.google.com/blog/topics/ai-machine-learning/rss"),
            FeedSource(name="Microsoft Azure Blog", url="https://azure.microsoft.com/en-us/blog/feed/"),
            FeedSource(name="Netflix TechBlog", url="https://netflixtechblog.com/feed"),
            FeedSource(name="Uber Engineering", url="https://www.uber.com/blog/engineering/rss/"),
            FeedSource(name="Cloudflare Blog", url="https://blog.cloudflare.com/rss/"),
            FeedSource(name="Databricks Blog", url="https://www.databricks.com/blog/rss.xml"),

            # --- MLOps adjacent ---
            FeedSource(name="Weights & Biases Blog", url="https://wandb.ai/fully-connected/rss.xml"),

            # --- Community (HN) ---
            FeedSource(name="Hacker News (MLOps)", url="https://hnrss.org/newest?q=mlops"),
            FeedSource(name="Hacker News (Kubernetes)", url="https://hnrss.org/newest?q=kubernetes"),
        ],
    ),

    # Optional: keep dataset growing with a dedicated "research" heavy topic
    Topic(
        key="research_safety_eval",
        label="Safety & Eval (feeds: 10)",
        description="Alignment, safety research, evals, robustness, governance.",
        feeds=[
            FeedSource(name="arXiv cs.CL", url="https://export.arxiv.org/rss/cs.CL"),
            FeedSource(name="arXiv cs.AI", url="https://export.arxiv.org/rss/cs.AI"),
            FeedSource(name="arXiv stat.ML", url="https://export.arxiv.org/rss/stat.ML"),
            FeedSource(name="OpenAI Blog", url="https://openai.com/blog/rss.xml"),
            FeedSource(name="Anthropic News", url="https://www.anthropic.com/news/rss.xml"),
            FeedSource(name="DeepMind Blog", url="https://deepmind.google/blog/rss.xml"),
            FeedSource(name="Microsoft Research Blog", url="https://www.microsoft.com/en-us/research/feed/"),
            FeedSource(name="Hacker News (AI Safety)", url="https://hnrss.org/newest?q=ai%20safety"),
            FeedSource(name="Hacker News (Alignment)", url="https://hnrss.org/newest?q=alignment"),
            FeedSource(name="Hacker News (Evaluation)", url="https://hnrss.org/newest?q=llm%20evaluation"),
        ],
    ),
]


def get_topics():
    return TOPICS


def get_topic_by_key(key: str):
    for t in TOPICS:
        if t.key == key:
            return t
    return None
