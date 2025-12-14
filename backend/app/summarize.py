import re
from html import unescape


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_html(text: str) -> str:
    text = unescape(text or "")
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


def summarize(text: str, max_chars: int = 320) -> str:
    """
    Simple extractive-ish summary without external models:
    - clean html
    - take first ~max_chars, cut at sentence boundary when possible
    """
    t = clean_html(text)
    if not t:
        return ""

    if len(t) <= max_chars:
        return t

    cut = t[:max_chars]
    # try to end at a nice boundary
    last_period = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if last_period > 120:
        return cut[: last_period + 1].strip()

    return cut.strip() + "..."
