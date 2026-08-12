"""Writing tools.

Each tool pairs a system prompt (the role the model plays) with a
temperature and a prompt builder that shapes the user's input.
"""

from __future__ import annotations

from collections.abc import Iterator

from engine import generate, stream

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: dict[str, dict] = {
    "write": {
        "name": "Write",
        "icon": "✍️",
        "description": "Generate content from a topic or idea",
        "temperature": 0.7,
        "system_prompt": (
            "You are a professional writer. You create clear, engaging, "
            "well-structured content with a natural, human voice. Use "
            "headings, paragraphs and bullet points where they help. "
            "Never open with 'Sure!' or 'Here is' — write the content "
            "directly."
        ),
    },
    "improve": {
        "name": "Improve",
        "icon": "⬆️",
        "description": "Sharpen word choice, flow and clarity",
        "temperature": 0.3,
        "system_prompt": (
            "You are an expert editor. Improve the given text by replacing "
            "weak words with stronger ones, smoothing sentence flow and "
            "transitions, and clarifying meaning — while keeping the "
            "original voice and intent. Return ONLY the improved text."
        ),
    },
    "rewrite": {
        "name": "Rewrite",
        "icon": "🔄",
        "description": "Same meaning, completely different words",
        "temperature": 0.5,
        "system_prompt": (
            "You are a rewriting specialist. Rewrite the given text "
            "completely while preserving its exact meaning and "
            "information. Use different sentence structures and "
            "vocabulary. Return ONLY the rewritten text."
        ),
    },
    "tone": {
        "name": "Change Tone",
        "icon": "🎭",
        "description": "Recast text in a different tone or style",
        "temperature": 0.4,
        "system_prompt": (
            "You are a tone adaptation expert. Rewrite the given text to "
            "match the requested tone while keeping the same information "
            "and meaning. Adapt vocabulary, sentence structure and style. "
            "Return ONLY the rewritten text."
        ),
    },
    "grammar": {
        "name": "Grammar Fix",
        "icon": "✅",
        "description": "Correct grammar, spelling and punctuation",
        "temperature": 0.1,
        "system_prompt": (
            "You are a proofreading expert. Fix grammar, spelling, "
            "punctuation and awkward phrasing. Keep the original style "
            "and voice, and make minimal changes — only fix what is "
            "actually wrong. Return ONLY the corrected text."
        ),
    },
    "expand": {
        "name": "Expand",
        "icon": "📐",
        "description": "Turn short notes into detailed content",
        "temperature": 0.6,
        "system_prompt": (
            "You are a content expansion specialist. Expand short text or "
            "bullet points into full, detailed content with supporting "
            "details, examples, explanations and context. Maintain the "
            "original voice. Return ONLY the expanded text."
        ),
    },
    "shorten": {
        "name": "Shorten",
        "icon": "✂️",
        "description": "Condense text while keeping every key point",
        "temperature": 0.3,
        "system_prompt": (
            "You are a conciseness expert. Condense the given text while "
            "keeping all key information. Remove redundancy, tighten "
            "sentences and cut fluff. Return ONLY the shortened text."
        ),
    },
    "translate": {
        "name": "Translate",
        "icon": "🌐",
        "description": "Translate text into another language",
        "temperature": 0.2,
        "system_prompt": (
            "You are a professional translator. Translate the given text "
            "accurately and naturally, preserving tone, style and "
            "meaning. Use natural phrasing in the target language rather "
            "than word-for-word translation. Return ONLY the translation."
        ),
    },
    "summarize": {
        "name": "Summarize",
        "icon": "📝",
        "description": "Pull the key points into a summary",
        "temperature": 0.2,
        "system_prompt": (
            "You are a summarization expert. Extract the key points of "
            "the given text into a clear, concise summary that captures "
            "the main ideas, important facts and conclusions. "
            "Return ONLY the summary."
        ),
    },
}

# ---------------------------------------------------------------------------
# Option lists
# ---------------------------------------------------------------------------

TONES: list[str] = [
    "Professional",
    "Casual",
    "Academic",
    "Creative",
    "Persuasive",
    "Friendly",
    "Formal",
    "Humorous",
    "Empathetic",
    "Confident",
    "Simple / Plain English",
]

LANGUAGES: list[str] = [
    "English", "Spanish", "French", "German", "Italian",
    "Portuguese", "Chinese", "Japanese", "Korean", "Arabic",
    "Hindi", "Russian", "Turkish", "Dutch", "Swedish", "Urdu",
]

LENGTHS: list[str] = [
    "Short (300-500 words)",
    "Medium (800-1200 words)",
    "Long (1500-2500 words)",
]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def _prompt_write(text: str, params: dict) -> str:
    return (
        f"Write about the following topic:\n\n{text}\n\n"
        f"Tone: {params.get('tone', 'Professional')}\n"
        f"Length: {params.get('length', LENGTHS[1])}\n"
        f"Target audience: {params.get('audience') or 'General'}\n"
    )


def _prompt_improve(text: str, _params: dict) -> str:
    return f"Improve the following text:\n\n{text}"


def _prompt_rewrite(text: str, params: dict) -> str:
    tone = params.get("tone", "")
    if tone and tone != "Keep original tone":
        return (
            f"Rewrite the following text, adapting it to a {tone} "
            f"tone:\n\n{text}"
        )
    return f"Rewrite the following text:\n\n{text}"


def _prompt_tone(text: str, params: dict) -> str:
    tone = params.get("tone", "Professional")
    return f"Change the tone of the following text to {tone}:\n\n{text}"


def _prompt_grammar(text: str, _params: dict) -> str:
    return f"Fix all grammar and spelling errors:\n\n{text}"


def _prompt_expand(text: str, params: dict) -> str:
    factor = params.get("factor", "2x")
    return (
        f"Expand the following text to about {factor} its current length. "
        f"Add details, examples and explanations:\n\n{text}"
    )


def _prompt_shorten(text: str, params: dict) -> str:
    target = params.get("target", "50%")
    return (
        f"Shorten the following text to about {target} of its current "
        f"length, keeping all key points:\n\n{text}"
    )


def _prompt_translate(text: str, params: dict) -> str:
    language = params.get("language", "Spanish")
    return f"Translate the following text to {language}:\n\n{text}"


def _prompt_summarize(text: str, params: dict) -> str:
    style = params.get("format", "Paragraph")
    return f"Summarize the following text as {style}:\n\n{text}"


PROMPT_BUILDERS = {
    "write": _prompt_write,
    "improve": _prompt_improve,
    "rewrite": _prompt_rewrite,
    "tone": _prompt_tone,
    "grammar": _prompt_grammar,
    "expand": _prompt_expand,
    "shorten": _prompt_shorten,
    "translate": _prompt_translate,
    "summarize": _prompt_summarize,
}


def build_prompt(tool_id: str, input_text: str,
                 extra_params: dict | None = None) -> str:
    """Shape the user's input into the prompt for ``tool_id``.

    When ``extra_params['raw']`` is true the text is passed through
    untouched.  Templates rely on this: they already produce a fully
    formed instruction, and wrapping it in the tool's own scaffolding
    would nest one prompt inside another.
    """
    params = extra_params or {}

    if params.get("raw"):
        return input_text

    builder = PROMPT_BUILDERS.get(tool_id)
    if builder is None:
        return input_text
    return builder(input_text, params)


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------


def run_tool(tool_id: str, input_text: str,
             extra_params: dict | None = None) -> str:
    """Run a tool and return the complete result."""
    tool = TOOLS[tool_id]
    return generate(
        system_prompt=tool["system_prompt"],
        user_prompt=build_prompt(tool_id, input_text, extra_params),
        temperature=tool["temperature"],
    )


def run_tool_stream(tool_id: str, input_text: str,
                    extra_params: dict | None = None) -> Iterator[str]:
    """Run a tool and yield result chunks as they arrive."""
    tool = TOOLS[tool_id]
    yield from stream(
        system_prompt=tool["system_prompt"],
        user_prompt=build_prompt(tool_id, input_text, extra_params),
        temperature=tool["temperature"],
    )


# ---------------------------------------------------------------------------
# Manual smoke test:  python tools.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Available tools:\n")
    for entry in TOOLS.values():
        print(
            f"  {entry['icon']} {entry['name']:14s} "
            f"temp={entry['temperature']}  {entry['description']}"
        )

    print("\nTesting the grammar tool...\n")
    print(run_tool(
        "grammar",
        "Their going to the store to buy they're groceries and its "
        "going to be a long day for theyre family.",
    ))
