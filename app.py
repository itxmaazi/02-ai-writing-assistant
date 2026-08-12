"""Beacon Writer — an AI writing assistant built on Streamlit.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import html
import os
import time
from datetime import datetime

import streamlit as st

from config_paths import STYLESHEET
from engine import EngineError, provider_status
from templates_data import TEMPLATES
from tools import LANGUAGES, LENGTHS, TONES, TOOLS, run_tool_stream
from utils import (
    delete_document,
    export_markdown,
    export_text,
    load_documents,
    safe_filename,
    save_document,
    text_stats,
)

st.set_page_config(
    page_title="Beacon Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _read_stylesheet(path: str, mtime: float) -> str:
    """Read the stylesheet, re-reading whenever its mtime changes."""
    del mtime  # only present so the cache invalidates on edit
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def load_css() -> None:
    """Inject assets/style.css into the page."""
    try:
        css = _read_stylesheet(STYLESHEET, os.path.getmtime(STYLESHEET))
    except OSError:
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

DEFAULT_STATE = {
    "view": "tool",
    "tool_id": "write",
    "template_id": "blog_post",
    "output": "",
    "output_title": "",
    "output_meta": "",
    "show_source": False,
    "clear_inputs": False,
}

INPUT_PREFIXES = ("in_", "tf_")


def init_state() -> None:
    """Seed session state and honour a pending clear request."""
    for key, value in DEFAULT_STATE.items():
        st.session_state.setdefault(key, value)

    # Widget values must be removed *before* the widgets are created;
    # once a keyed widget exists, Streamlit ignores its `value=` argument.
    if st.session_state.clear_inputs:
        for key in list(st.session_state.keys()):
            if key.startswith(INPUT_PREFIXES):
                del st.session_state[key]
        st.session_state.clear_inputs = False


def reset_output() -> None:
    """Drop the current result."""
    st.session_state.output = ""
    st.session_state.output_title = ""
    st.session_state.output_meta = ""
    st.session_state.show_source = False


def select_tool(tool_id: str) -> None:
    """Switch the workspace to a tool."""
    st.session_state.view = "tool"
    st.session_state.tool_id = tool_id
    reset_output()


def select_template(template_id: str) -> None:
    """Switch the workspace to a template."""
    st.session_state.view = "template"
    st.session_state.template_id = template_id
    reset_output()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_brand() -> None:
    """Render the sidebar wordmark."""
    st.markdown(
        '<div class="bw-brand">'
        '<div class="bw-brand__mark">✍️</div>'
        '<div><div class="bw-brand__name">Beacon Writer</div>'
        '<div class="bw-brand__tag">AI writing assistant</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    """Render a small uppercase section heading."""
    st.markdown(
        f'<div class="bw-section-label">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_provider_status() -> None:
    """Show which AI providers are configured."""
    pills = []
    for provider in provider_status():
        state = "on" if provider["ready"] else "off"
        pills.append(
            f'<span class="bw-pill bw-pill--{state}">'
            f'<span class="bw-pill__dot"></span>'
            f'{html.escape(provider["name"])}</span>'
        )
    st.markdown(
        f'<div class="bw-status">{"".join(pills)}</div>',
        unsafe_allow_html=True,
    )


def render_library() -> None:
    """List saved documents with load and delete controls."""
    docs = load_documents()
    if not docs:
        st.caption("Nothing saved yet.")
        return

    for doc in reversed(docs[-10:]):
        col_open, col_delete = st.columns([5, 1], gap="small")
        with col_open:
            if st.button(
                f"📄  {doc.get('title', 'Untitled')[:24]}",
                key=f"open_{doc['id']}",
                use_container_width=True,
            ):
                st.session_state.output = doc.get("content", "")
                st.session_state.output_title = doc.get("title", "Document")
                st.session_state.output_meta = (
                    f"Saved {doc.get('created', '')}"
                )
                st.session_state.show_source = False
                st.rerun()
        with col_delete:
            if st.button("✕", key=f"del_{doc['id']}",
                         help="Delete this document"):
                delete_document(doc["id"])
                st.rerun()


def render_sidebar() -> None:
    """Render the whole sidebar."""
    with st.sidebar:
        render_brand()

        section_label("Tools")
        for tool_id, tool in TOOLS.items():
            active = (st.session_state.view == "tool"
                      and st.session_state.tool_id == tool_id)
            st.button(
                f"{tool['icon']}  {tool['name']}",
                key=f"nav_tool_{tool_id}",
                use_container_width=True,
                type="primary" if active else "secondary",
                on_click=select_tool,
                args=(tool_id,),
            )

        section_label("Templates")
        for template_id, template in TEMPLATES.items():
            active = (st.session_state.view == "template"
                      and st.session_state.template_id == template_id)
            st.button(
                f"{template['icon']}  {template['name']}",
                key=f"nav_tmpl_{template_id}",
                use_container_width=True,
                type="primary" if active else "secondary",
                on_click=select_template,
                args=(template_id,),
            )

        section_label("Library")
        render_library()

        st.divider()
        section_label("Providers")
        render_provider_status()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------


def current_subject() -> dict:
    """Return the tool or template currently selected."""
    if st.session_state.view == "template":
        return TEMPLATES.get(st.session_state.template_id, {})
    return TOOLS.get(st.session_state.tool_id, {})


def render_header() -> None:
    """Render the page title block."""
    subject = current_subject()
    st.markdown(
        '<div class="bw-header">'
        f'<div class="bw-header__icon">{subject.get("icon", "✍️")}</div>'
        "<div>"
        f'<h1 class="bw-header__title">'
        f'{html.escape(subject.get("name", "Writer"))}</h1>'
        f'<p class="bw-header__desc">'
        f'{html.escape(subject.get("description", ""))}</p>'
        "</div></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Input area
# ---------------------------------------------------------------------------


def render_template_inputs(template: dict) -> dict:
    """Render a template's fields and return the entered values."""
    values = {}
    columns = st.columns(2, gap="medium")
    template_id = st.session_state.template_id

    for index, field in enumerate(template.get("fields", [])):
        key = f"tf_{template_id}_{field['name']}"
        with columns[index % 2]:
            if field["type"] == "textarea":
                values[field["name"]] = st.text_area(
                    field["label"],
                    placeholder=field.get("placeholder", ""),
                    height=90,
                    key=key,
                )
            elif field["type"] == "select":
                options = field.get("options", [])
                default = field.get("default")
                index_of = options.index(default) if default in options else 0
                values[field["name"]] = st.selectbox(
                    field["label"],
                    options=options,
                    index=index_of,
                    key=key,
                )
            else:
                values[field["name"]] = st.text_input(
                    field["label"],
                    placeholder=field.get("placeholder", ""),
                    key=key,
                )
    return values


def render_tool_inputs(tool_id: str) -> tuple:
    """Render a tool's inputs and return ``(text, extra_params)``."""
    params: dict = {}

    prompts = {
        "write": ("What do you want to write about?",
                  "Describe your topic or idea…", 130),
        "tone": ("Your text", "Paste the text to re-tone…", 170),
        "translate": ("Your text", "Paste the text to translate…", 170),
        "expand": ("Your text", "Paste short text or bullet points…", 170),
        "shorten": ("Your text", "Paste the long text to condense…", 170),
        "summarize": ("Your text", "Paste the text to summarise…", 170),
        "rewrite": ("Your text", "Paste the text to rewrite…", 170),
    }
    label, placeholder, height = prompts.get(
        tool_id, ("Your text", "Paste the text to work on…", 170)
    )

    text = st.text_area(
        label,
        placeholder=placeholder,
        height=height,
        key=f"in_{tool_id}",
    )

    if tool_id == "write":
        col_a, col_b, col_c = st.columns(3, gap="medium")
        params["tone"] = col_a.selectbox("Tone", TONES, index=0)
        params["length"] = col_b.selectbox("Length", LENGTHS, index=1)
        params["audience"] = col_c.text_input("Audience",
                                              placeholder="General")
    elif tool_id == "tone":
        params["tone"] = st.selectbox("Target tone", TONES, index=0)
    elif tool_id == "translate":
        params["language"] = st.selectbox("Translate to", LANGUAGES, index=1)
    elif tool_id == "expand":
        params["factor"] = st.selectbox("Expand by", ["2x", "3x", "5x"],
                                        index=0)
    elif tool_id == "shorten":
        params["target"] = st.selectbox("Target length",
                                        ["25%", "50%", "75%"], index=1)
    elif tool_id == "summarize":
        params["format"] = st.selectbox(
            "Format",
            ["Paragraph", "Bullet points", "TL;DR (1-2 sentences)"],
            index=0,
        )
    elif tool_id == "rewrite":
        params["tone"] = st.selectbox(
            "Tone", ["Keep original tone", *TONES], index=0
        )

    return text, params


def build_request() -> tuple:
    """Render the input area and return ``(tool_id, prompt, params, title)``.

    ``prompt`` is empty when the user has not supplied enough input.
    """
    if st.session_state.view == "template":
        template = TEMPLATES.get(st.session_state.template_id, {})
        values = render_template_inputs(template)
        filled = [v for v in values.values() if str(v).strip()]
        builder = template.get("prompt_builder")

        if len(filled) < 2 or builder is None:
            return template.get("tool", "write"), "", {}, template.get(
                "name", "Document")

        # Templates emit a complete instruction; `raw` stops the tool from
        # wrapping it inside a second layer of prompt scaffolding.
        return (
            template.get("tool", "write"),
            builder(values),
            {"raw": True},
            template.get("name", "Document"),
        )

    tool_id = st.session_state.tool_id
    text, params = render_tool_inputs(tool_id)
    title = TOOLS.get(tool_id, {}).get("name", "Document")
    return tool_id, text.strip(), params, title


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def render_stats(text: str) -> None:
    """Render the word / character / sentence / reading-time row."""
    stats = text_stats(text)
    cells = [
        (stats["words"], "Words"),
        (stats["characters"], "Characters"),
        (stats["sentences"], "Sentences"),
        (stats["reading_time"], "Read time"),
    ]
    body = "".join(
        f'<div class="bw-stat"><div class="bw-stat__value">{value}</div>'
        f'<div class="bw-stat__label">{label}</div></div>'
        for value, label in cells
    )
    st.markdown(f'<div class="bw-stats">{body}</div>',
                unsafe_allow_html=True)


def output_label(text: str) -> None:
    """Render the small uppercase label above the output panel."""
    st.markdown(
        f'<div class="bw-output-label">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def run_generation(tool_id: str, prompt: str, params: dict,
                   title: str) -> None:
    """Stream a result into the output panel and store it in state."""
    output_label("Output")
    started = time.perf_counter()

    with st.container(key="bw_output"):
        try:
            result = st.write_stream(
                run_tool_stream(tool_id, prompt, params)
            )
        except EngineError as error:
            st.error(str(error))
            return
        except Exception as error:  # noqa: BLE001 - surface, do not crash
            st.error(f"Generation failed: {error}")
            return

    text = result if isinstance(result, str) else "".join(result)
    if not text.strip():
        st.warning("The model returned an empty response. Try again.")
        return

    elapsed = time.perf_counter() - started
    st.session_state.output = text
    st.session_state.output_title = (
        f"{title} — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    st.session_state.output_meta = f"Generated in {elapsed:.1f}s"
    st.session_state.show_source = False


def render_saved_output() -> None:
    """Re-render a result that was produced on an earlier run."""
    output_label("Output")
    with st.container(key="bw_output"):
        st.markdown(st.session_state.output)


def render_output_actions() -> None:
    """Render the stats row and the export / save controls."""
    text = st.session_state.output
    title = st.session_state.output_title or "Document"

    if st.session_state.output_meta:
        st.markdown(
            f'<div class="bw-meta">{html.escape(st.session_state.output_meta)}'
            "</div>",
            unsafe_allow_html=True,
        )

    render_stats(text)

    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        if st.button("📋  Copy text", use_container_width=True):
            st.session_state.show_source = not st.session_state.show_source
            st.rerun()

    with col2:
        st.download_button(
            "⬇️  Markdown",
            data=export_markdown(title, text, {
                "Generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Words": text_stats(text)["words"],
            }),
            file_name=safe_filename(title, "md"),
            mime="text/markdown",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "⬇️  Plain text",
            data=export_text(title, text),
            file_name=safe_filename(title, "txt"),
            mime="text/plain",
            use_container_width=True,
        )

    with col4:
        if st.button("💾  Save", use_container_width=True):
            save_document(title, text, st.session_state.tool_id)
            st.toast("Saved to your library.")
            st.rerun()

    if st.session_state.show_source:
        st.caption("Select the block below, then copy.")
        st.code(text, language="markdown")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Compose the page."""
    load_css()
    init_state()
    render_sidebar()
    render_header()

    tool_id, prompt, params, title = build_request()

    st.write("")
    col_generate, col_clear, _ = st.columns([1.1, 1, 3.4], gap="small")
    generate_clicked = col_generate.button(
        "⚡  Generate", type="primary", use_container_width=True
    )
    clear_clicked = col_clear.button("Clear", use_container_width=True)

    if clear_clicked:
        st.session_state.clear_inputs = True
        reset_output()
        st.rerun()

    if generate_clicked:
        if not prompt:
            st.warning(
                "Add some input first — fill in the box above "
                "(or at least two template fields)."
            )
        else:
            reset_output()
            run_generation(tool_id, prompt, params, title)

    elif st.session_state.output:
        render_saved_output()

    if st.session_state.output:
        render_output_actions()
    elif not generate_clicked:
        output_label("Output")
        st.markdown(
            '<div class="bw-empty">Your generated text will appear here.'
            "</div>",
            unsafe_allow_html=True,
        )


main()
