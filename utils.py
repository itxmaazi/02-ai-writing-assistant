"""Text statistics, export helpers and document storage."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime

from config_paths import DATA_DIR, DOCUMENTS_FILE

WORDS_PER_MINUTE = 200

_SENTENCE_SPLIT = re.compile(r"[.!?\n]+")

# ---------------------------------------------------------------------------
# Text analysis
# ---------------------------------------------------------------------------


def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split()) if text else 0


def char_count(text: str) -> int:
    """Count characters."""
    return len(text) if text else 0


def sentence_count(text: str) -> int:
    """Count sentences.

    Counts non-empty fragments rather than subtracting one from the split
    result, so a single unpunctuated sentence still counts as one.
    """
    if not text or not text.strip():
        return 0
    parts = [p for p in _SENTENCE_SPLIT.split(text) if p.strip()]
    return len(parts)


def reading_time(text: str) -> str:
    """Estimate reading time at ~200 words per minute."""
    minutes = word_count(text) / WORDS_PER_MINUTE
    if minutes < 1:
        return "< 1 min"
    return f"{round(minutes)} min"


def text_stats(text: str) -> dict:
    """Return words, characters, sentences and reading time for ``text``."""
    return {
        "words": word_count(text),
        "characters": char_count(text),
        "sentences": sentence_count(text),
        "reading_time": reading_time(text),
    }


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_markdown(title: str, content: str,
                    metadata: dict | None = None) -> str:
    """Render ``content`` as a Markdown document with optional front matter."""
    lines = [f"# {title}", ""]

    if metadata:
        lines.append("---")
        lines.extend(f"- **{key}:** {value}" for key, value in metadata.items())
        lines.extend(["---", ""])

    lines.append(content)
    return "\n".join(lines)


def export_text(title: str, content: str) -> str:
    """Render ``content`` as plain text with an underlined title."""
    return f"{title}\n{'=' * len(title)}\n\n{content}"


def safe_filename(name: str, extension: str) -> str:
    """Turn a document title into a filesystem-safe file name."""
    cleaned = re.sub(r"[^\w\s-]", "", name).strip()
    cleaned = re.sub(r"[\s_-]+", "_", cleaned) or "document"
    return f"{cleaned[:80]}.{extension.lstrip('.')}"


# ---------------------------------------------------------------------------
# Document storage
# ---------------------------------------------------------------------------


def _write_documents(docs: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as handle:
        json.dump(docs, handle, indent=2, ensure_ascii=False)


def load_documents() -> list[dict]:
    """Load saved documents, returning an empty list if none exist."""
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    try:
        with open(DOCUMENTS_FILE, encoding="utf-8") as handle:
            docs = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return []
    return docs if isinstance(docs, list) else []


def save_document(title: str, content: str, tool: str,
                  extra_info: dict | None = None) -> str:
    """Persist a document and return its generated id."""
    docs = load_documents()
    stamp = datetime.now()

    doc = {
        "id": f"doc_{stamp.strftime('%Y%m%d_%H%M%S_%f')}",
        "title": title,
        "content": content,
        "tool": tool,
        "created": stamp.isoformat(timespec="seconds"),
        "stats": text_stats(content),
    }
    if extra_info:
        doc["extra"] = extra_info

    docs.append(doc)
    _write_documents(docs)
    return doc["id"]


def delete_document(doc_id: str) -> None:
    """Delete a document by id."""
    docs = [doc for doc in load_documents() if doc.get("id") != doc_id]
    _write_documents(docs)
