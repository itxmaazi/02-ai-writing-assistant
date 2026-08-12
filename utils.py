# utils.py
# ============================================================
# HELPER UTILITIES
# ============================================================

import json
import os
import re
from datetime import datetime
from config_paths import DATA_DIR, DOCUMENTS_FILE


# ============================================================
# TEXT ANALYSIS
# ============================================================

def word_count(text):
    """Counts words in text."""
    if not text:
        return 0
    return len(text.split())


def char_count(text):
    """Counts characters in text."""
    if not text:
        return 0
    return len(text)


def sentence_count(text):
    """Counts sentences in text."""
    if not text:
        return 0
    return len(re.split(r'[.!?]+', text.strip())) - 1


def reading_time(text):
    """Estimates reading time (average 200 words per minute)."""
    words = word_count(text)
    minutes = words / 200
    if minutes < 1:
        return "< 1 min"
    return f"{int(minutes)} min"


def text_stats(text):
    """Returns a complete stats dict for any text."""
    return {
        "words": word_count(text),
        "characters": char_count(text),
        "sentences": sentence_count(text),
        "reading_time": reading_time(text),
    }


# ============================================================
# EXPORT
# ============================================================

def export_markdown(title, content, metadata=None):
    """
    Exports content as a Markdown string with metadata.

    Args:
        title: document title
        content: the main text
        metadata: optional dict with tool, date, etc.

    Returns:
        str: formatted Markdown content
    """
    lines = []
    lines.append(f"# {title}\n")

    if metadata:
        lines.append("---")
        for key, value in metadata.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("---\n")

    lines.append(content)
    return "\n".join(lines)


def export_text(title, content):
    """Exports content as plain text."""
    return f"{title}\n{'=' * len(title)}\n\n{content}"


# ============================================================
# DOCUMENT STORAGE
# ============================================================

def load_documents():
    """Loads saved documents from disk."""
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    try:
        with open(DOCUMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_document(title, content, tool, extra_info=None):
    """
    Saves a document to disk.

    Returns:
        str: the document ID
    """
    docs = load_documents()

    doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    doc = {
        "id": doc_id,
        "title": title,
        "content": content,
        "tool": tool,
        "created": datetime.now().isoformat(),
        "stats": text_stats(content),
    }

    if extra_info:
        doc["extra"] = extra_info

    docs.append(doc)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    return doc_id


def delete_document(doc_id):
    """Deletes a document by ID."""
    docs = load_documents()
    docs = [d for d in docs if d["id"] != doc_id]
    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)