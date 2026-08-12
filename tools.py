# tools.py
# ============================================================
# WRITING TOOLS
# ============================================================
# Each tool has:
#   - A name and description (shown in UI)
#   - A system prompt (tells the AI what role to play)
#   - A temperature (how creative to be)
#   - A function that builds the user prompt and calls the engine
# ============================================================

from engine import generate, stream


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = {
    "write": {
        "name": "Write",
        "icon": "✍️",
        "description": "Generate content from a topic or idea",
        "temperature": 0.7,
        "system_prompt": (
            "You are a professional writer. You create clear, engaging, "
            "well-structured content. You write with a natural, human voice. "
            "Use proper formatting with headings, paragraphs, and bullet points "
            "where appropriate. Never start with 'Sure!' or 'Here is' — "
            "just write the content directly."
        ),
    },
    "improve": {
        "name": "Improve",
        "icon": "⬆️",
        "description": "Enhance existing text — better word choice, flow, clarity",
        "temperature": 0.3,
        "system_prompt": (
            "You are an expert editor. Given text to improve, you enhance it by: "
            "1) Replacing weak words with stronger ones, "
            "2) Improving sentence flow and transitions, "
            "3) Making the meaning clearer, "
            "4) Keeping the original voice and intent. "
            "Return ONLY the improved text. Do not explain what you changed."
        ),
    },
    "rewrite": {
        "name": "Rewrite",
        "icon": "🔄",
        "description": "Same meaning, completely different words",
        "temperature": 0.5,
        "system_prompt": (
            "You are a rewriting specialist. Given text, you rewrite it completely "
            "while preserving the exact same meaning and information. Use different "
            "sentence structures, different vocabulary, and a fresh perspective. "
            "Return ONLY the rewritten text. Do not explain what you changed."
        ),
    },
    "tone": {
        "name": "Change Tone",
        "icon": "🎭",
        "description": "Rewrite text in a different tone or style",
        "temperature": 0.4,
        "system_prompt": (
            "You are a tone adaptation expert. Given text and a target tone, "
            "you rewrite the text to match that tone while keeping the same "
            "information and meaning. Adapt vocabulary, sentence structure, "
            "and style to match the requested tone. "
            "Return ONLY the rewritten text."
        ),
    },
    "grammar": {
        "name": "Grammar Fix",
        "icon": "✅",
        "description": "Fix grammar, spelling, and punctuation errors",
        "temperature": 0.1,
        "system_prompt": (
            "You are a grammar and proofreading expert. Fix all grammar errors, "
            "spelling mistakes, punctuation issues, and awkward phrasing. "
            "Keep the original style and voice. Make minimal changes — "
            "only fix what is actually wrong. "
            "Return ONLY the corrected text. Do not list the errors."
        ),
    },
    "expand": {
        "name": "Expand",
        "icon": "📐",
        "description": "Turn short text into longer, detailed content",
        "temperature": 0.6,
        "system_prompt": (
            "You are a content expansion specialist. Given short text or "
            "bullet points, you expand it into full, detailed content. "
            "Add supporting details, examples, explanations, and context. "
            "Maintain the original voice and intent. "
            "Return ONLY the expanded text."
        ),
    },
    "shorten": {
        "name": "Shorten",
        "icon": "✂️",
        "description": "Condense long text while keeping key points",
        "temperature": 0.3,
        "system_prompt": (
            "You are a conciseness expert. Given long text, you condense it "
            "while keeping all key information and main points. Remove "
            "redundancy, tighten sentences, and eliminate fluff. "
            "The result should be clear and to the point. "
            "Return ONLY the shortened text."
        ),
    },
    "translate": {
        "name": "Translate",
        "icon": "🌐",
        "description": "Translate text to another language",
        "temperature": 0.2,
        "system_prompt": (
            "You are a professional translator. Translate the given text "
            "to the target language accurately and naturally. Preserve "
            "the tone, style, and meaning. Use natural phrasing in the "
            "target language — not word-for-word translation. "
            "Return ONLY the translated text."
        ),
    },
    "summarize": {
        "name": "Summarize",
        "icon": "📝",
        "description": "Extract key points into a summary",
        "temperature": 0.2,
        "system_prompt": (
            "You are a summarization expert. Given long text, you extract "
            "the key points and create a clear, concise summary. "
            "Capture the main ideas, important facts, and conclusions. "
            "Return ONLY the summary."
        ),
    },
}

# ============================================================
# AVAILABLE TONES
# ============================================================

TONES = [
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

# ============================================================
# AVAILABLE LANGUAGES
# ============================================================

LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian",
    "Portuguese", "Chinese", "Japanese", "Korean", "Arabic",
    "Hindi", "Russian", "Turkish", "Dutch", "Swedish",
    "Urdu",
]

# ============================================================
# TOOL FUNCTIONS
# ============================================================

def run_tool(tool_id, input_text, extra_params=None):
    """
    Runs a writing tool and returns the complete result.

    Args:
        tool_id: key from TOOLS dict (e.g., "write", "improve")
        input_text: the user's input text
        extra_params: optional dict with tone, language, length, etc.

    Returns:
        str: the AI's response
    """
    tool = TOOLS[tool_id]
    user_prompt = _build_prompt(tool_id, input_text, extra_params)

    return generate(
        system_prompt=tool["system_prompt"],
        user_prompt=user_prompt,
        temperature=tool["temperature"],
    )


def run_tool_stream(tool_id, input_text, extra_params=None):
    """
    Runs a writing tool with streaming output.

    Args:
        tool_id: key from TOOLS dict
        input_text: the user's input text
        extra_params: optional dict with tone, language, length, etc.

    Yields:
        str: text chunks as they arrive
    """
    tool = TOOLS[tool_id]
    user_prompt = _build_prompt(tool_id, input_text, extra_params)

    for chunk in stream(
        system_prompt=tool["system_prompt"],
        user_prompt=user_prompt,
        temperature=tool["temperature"],
    ):
        yield chunk


def _build_prompt(tool_id, input_text, extra_params=None):
    """
    Builds the user prompt based on the tool type.
    Each tool needs slightly different input formatting.
    """
    if extra_params is None:
        extra_params = {}

    if tool_id == "write":
        topic = input_text
        tone = extra_params.get("tone", "Professional")
        length = extra_params.get("length", "Medium")
        audience = extra_params.get("audience", "General")

        prompt = (
            f"Write about the following topic:\n\n{topic}\n\n"
            f"Tone: {tone}\n"
            f"Length: {length}\n"
            f"Target audience: {audience}\n"
        )
        return prompt

    elif tool_id == "improve":
        return f"Improve the following text:\n\n{input_text}"

    elif tool_id == "rewrite":
        tone = extra_params.get("tone", "")
        if tone:
            return (
                f"Rewrite the following text. "
                f"Optionally adapt to a {tone} tone:\n\n{input_text}"
            )
        return f"Rewrite the following text:\n\n{input_text}"

    elif tool_id == "tone":
        target_tone = extra_params.get("tone", "Professional")
        return (
            f"Change the tone of the following text to {target_tone}:\n\n"
            f"{input_text}"
        )

    elif tool_id == "grammar":
        return f"Fix all grammar and spelling errors:\n\n{input_text}"

    elif tool_id == "expand":
        factor = extra_params.get("factor", "2x")
        return (
            f"Expand the following text to about {factor} its current length. "
            f"Add details, examples, and explanations:\n\n{input_text}"
        )

    elif tool_id == "shorten":
        target = extra_params.get("target", "50%")
        return (
            f"Shorten the following text to about {target} of its current length. "
            f"Keep all key points:\n\n{input_text}"
        )

    elif tool_id == "translate":
        language = extra_params.get("language", "Spanish")
        return (
            f"Translate the following text to {language}:\n\n{input_text}"
        )

    elif tool_id == "summarize":
        format_type = extra_params.get("format", "Paragraph")
        return (
            f"Summarize the following text as {format_type}:\n\n{input_text}"
        )

    else:
        return input_text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("Available tools:\n")
    for key, tool in TOOLS.items():
        print(f"  {tool['icon']} {tool['name']:15s} | temp={tool['temperature']} | {tool['description']}")

    print(f"\nTesting 'grammar' tool...\n")
    result = run_tool(
        "grammar",
        "Their going to the store to buy they're groceries and its going to be a long day for theyre family.",
    )
    print(f"Result: {result}")