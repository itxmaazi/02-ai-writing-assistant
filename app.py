# app.py
# ============================================================
# BEACON WRITER — AI Writing Assistant
# ============================================================
# Run with: streamlit run app.py
#
# A full-featured AI writing assistant built with Streamlit.
# Uses Gemini (primary) + Groq (fallback) for AI generation.
# ============================================================

import streamlit as st
import time
from datetime import datetime

from tools import TOOLS, TONES, LANGUAGES, run_tool_stream
from templates_data import TEMPLATES
from utils import text_stats, save_document, load_documents, delete_document, export_markdown, export_text


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Beacon Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background-color: #0a0a0f;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #12121a;
        border-right: 1px solid #1e1e2e;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label {
        color: #a1a1aa;
    }

    /* Text areas */
    .stTextArea textarea {
        background-color: #12121a !important;
        border: 1px solid #1e1e2e !important;
        color: #e4e4e7 !important;
        border-radius: 10px !important;
        font-size: 15px !important;
    }

    .stTextArea textarea:focus {
        border-color: #6c63ff !important;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.15) !important;
    }

    /* Text input */
    .stTextInput input {
        background-color: #12121a !important;
        border: 1px solid #1e1e2e !important;
        color: #e4e4e7 !important;
        border-radius: 8px !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #12121a !important;
        border: 1px solid #1e1e2e !important;
        color: #e4e4e7 !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #6c63ff !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background-color: #5b54e6 !important;
        transform: translateY(-1px) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #1e1e2e !important;
        color: #a1a1aa !important;
        border: 1px solid #2e2e3e !important;
        border-radius: 8px !important;
    }

    .stDownloadButton > button:hover {
        border-color: #6c63ff !important;
        color: #e4e4e7 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #6c63ff !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    [data-testid="stMetricLabel"] {
        color: #71717a !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #12121a !important;
        border: 1px solid #1e1e2e !important;
        border-radius: 8px !important;
        color: #e4e4e7 !important;
    }

    /* Dividers */
    hr {
        border-color: #1e1e2e !important;
    }

    /* Success/Info boxes */
    .stAlert {
        background-color: #12121a !important;
        border-radius: 8px !important;
    }

    /* Radio buttons */
    .stRadio > div {
        gap: 4px;
    }

    .stRadio > div > label {
        background-color: #12121a;
        border: 1px solid #1e1e2e;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 2px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "current_tool" not in st.session_state:
    st.session_state.current_tool = "write"

if "output_text" not in st.session_state:
    st.session_state.output_text = ""

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# ✍️ Beacon Writer")
    st.markdown("*AI-Powered Writing Assistant*")
    st.divider()

    # ── Tools Section ──
    st.markdown("### 🛠️ Tools")

    for tool_id, tool in TOOLS.items():
        if st.button(
            f"{tool['icon']}  {tool['name']}",
            key=f"tool_{tool_id}",
            use_container_width=True,
            type="secondary" if st.session_state.current_tool != tool_id else "primary",
        ):
            st.session_state.current_tool = tool_id
            st.session_state.output_text = ""
            st.rerun()

    st.divider()

    # ── Templates Section ──
    st.markdown("### 📋 Templates")

    for tmpl_id, tmpl in TEMPLATES.items():
        if st.button(
            f"{tmpl['icon']}  {tmpl['name']}",
            key=f"tmpl_{tmpl_id}",
            use_container_width=True,
        ):
            st.session_state.current_tool = "template"
            st.session_state.current_template = tmpl_id
            st.session_state.output_text = ""
            st.rerun()

    st.divider()

    # ── Saved Documents ──
    st.markdown("### 📁 Saved Documents")

    docs = load_documents()
    if docs:
        for doc in reversed(docs[-10:]):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"📄 {doc['title'][:25]}",
                    key=f"doc_{doc['id']}",
                    use_container_width=True,
                ):
                    st.session_state.output_text = doc["content"]
                    st.session_state.input_text = ""
                    st.session_state.current_tool = "write"
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{doc['id']}"):
                    delete_document(doc["id"])
                    st.rerun()
    else:
        st.caption("No saved documents yet.")


# ============================================================
# MAIN WORKSPACE
# ============================================================

# ── Header ──
current = st.session_state.current_tool

if current == "template":
    tmpl = TEMPLATES[st.session_state.get("current_template", "blog_post")]
    st.markdown(f"## {tmpl['icon']} {tmpl['name']}")
    st.caption(tmpl["description"])
elif current in TOOLS:
    tool = TOOLS[current]
    st.markdown(f"## {tool['icon']} {tool['name']}")
    st.caption(tool["description"])
else:
    st.markdown("## ✍️ Beacon Writer")

# Stats bar for output
if st.session_state.output_text:
    stats = text_stats(st.session_state.output_text)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Words", stats["words"])
    col2.metric("Characters", stats["characters"])
    col3.metric("Sentences", stats["sentences"])
    col4.metric("Reading Time", stats["reading_time"])

st.divider()


# ============================================================
# TOOL-SPECIFIC INPUTS
# ============================================================

extra_params = {}

if current == "template":
    # ── Template Mode ──
    tmpl = TEMPLATES[st.session_state.get("current_template", "blog_post")]
    fields = tmpl["fields"]

    field_values = {}
    cols = st.columns(2)

    for i, field in enumerate(fields):
        with cols[i % 2]:
            if field["type"] == "text":
                field_values[field["name"]] = st.text_input(
                    field["label"],
                    placeholder=field.get("placeholder", ""),
                    key=f"tmpl_field_{field['name']}",
                )
            elif field["type"] == "textarea":
                field_values[field["name"]] = st.text_area(
                    field["label"],
                    placeholder=field.get("placeholder", ""),
                    height=80,
                    key=f"tmpl_field_{field['name']}",
                )
            elif field["type"] == "select":
                default_idx = 0
                if "default" in field:
                    default_idx = field["options"].index(field["default"]) if field["default"] in field["options"] else 0
                field_values[field["name"]] = st.selectbox(
                    field["label"],
                    options=field["options"],
                    index=default_idx,
                    key=f"tmpl_field_{field['name']}",
                )

    extra_params["template"] = tmpl
    extra_params["fields"] = field_values

    # No manual input needed — template builds the prompt
    st.session_state.input_text = ""

elif current == "write":
    # ── Write Tool ──
    st.session_state.input_text = st.text_area(
        "What do you want to write about?",
        value=st.session_state.input_text,
        placeholder="e.g., A blog post about the future of remote work...",
        height=120,
        key="write_input",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        extra_params["tone"] = st.selectbox("Tone", TONES, index=0)
    with col2:
        extra_params["length"] = st.selectbox("Length", [
            "Short (300-500 words)", "Medium (800-1200 words)", "Long (1500-2500 words)"
        ], index=1)
    with col3:
        extra_params["audience"] = st.text_input("Audience", placeholder="e.g., General, Developers, Managers")

elif current == "tone":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste the text you want to change the tone of...",
        height=150,
        key="tone_input",
    )
    extra_params["tone"] = st.selectbox("Target Tone", TONES, index=0)

elif current == "translate":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste the text you want to translate...",
        height=150,
        key="translate_input",
    )
    extra_params["language"] = st.selectbox("Translate to", LANGUAGES, index=1)

elif current == "expand":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste short text or bullet points to expand...",
        height=150,
        key="expand_input",
    )
    extra_params["factor"] = st.selectbox("How much to expand", ["2x", "3x", "5x"], index=0)

elif current == "shorten":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste long text to condense...",
        height=150,
        key="shorten_input",
    )
    extra_params["target"] = st.selectbox("Target length", [
        "25%", "50%", "75%"
    ], index=1)

elif current == "summarize":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste long text to summarize...",
        height=150,
        key="summarize_input",
    )
    extra_params["format"] = st.selectbox("Summary format", [
        "Paragraph", "Bullet Points", "TL;DR (1-2 sentences)"
    ], index=0)

elif current == "rewrite":
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste the text you want to rewrite...",
        height=150,
        key="rewrite_input",
    )
    extra_params["tone"] = st.selectbox("Optional: Keep or change tone", [
        "Keep original tone", *TONES
    ], index=0)

else:
    # ── Simple tools: Improve, Grammar ──
    st.session_state.input_text = st.text_area(
        "Paste your text here:",
        value=st.session_state.input_text,
        placeholder="Paste the text you want to improve or fix...",
        height=150,
        key="simple_input",
    )


# ============================================================
# GENERATE BUTTON
# ============================================================

st.divider()

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    generate_clicked = st.button(
        "⚡ Generate",
        use_container_width=True,
        type="primary",
    )

with col_btn2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.output_text = ""
        st.session_state.input_text = ""
        st.rerun()


# ============================================================
# GENERATE OUTPUT
# ============================================================

if generate_clicked:
    # Validate input
    has_input = False
    tool_id = current

    if current == "template":
        tmpl = TEMPLATES.get(st.session_state.get("current_template"))
        if tmpl:
            # Check if required fields have values
            field_values = extra_params.get("fields", {})
            filled = [v for v in field_values.values() if v and v.strip()]
            has_input = len(filled) > 0
            # Build prompt from template
            if has_input:
                user_prompt = tmpl["prompt_builder"](field_values)
                tool_id = tmpl["tool"]
    else:
        has_input = bool(st.session_state.input_text and st.session_state.input_text.strip())
        user_prompt = st.session_state.input_text

    if not has_input:
        st.warning("Please enter some text or fill in the template fields.")
    else:
        st.session_state.is_generating = True
        st.session_state.output_text = ""

        # Create output container
        output_container = st.empty()
        output_container.markdown("*Generating...*")

        full_text = ""
        start_time = time.time()

        try:
            for chunk in run_tool_stream(tool_id, user_prompt, extra_params):
                full_text += chunk
                output_container.markdown(full_text)

            elapsed = round(time.time() - start_time, 1)
            st.session_state.output_text = full_text
            st.session_state.is_generating = False

            # Show generation time
            st.caption(f"Generated in {elapsed}s")

            # Update stats
            stats = text_stats(full_text)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Words", stats["words"])
            col2.metric("Characters", stats["characters"])
            col3.metric("Sentences", stats["sentences"])
            col4.metric("Reading Time", stats["reading_time"])

        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
            st.session_state.is_generating = False


# ============================================================
# OUTPUT SECTION (if content exists)
# ============================================================

if st.session_state.output_text and not st.session_state.is_generating:
    st.divider()
    st.markdown("### Output")

    # Display the output
    st.markdown(st.session_state.output_text)

    st.divider()

    # ── Action Buttons ──
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📋 Copy", use_container_width=True):
            st.code(st.session_state.output_text, language=None)
            st.success("Select the text above and press Ctrl+C to copy!")

    with col2:
        # Determine title for export
        if current == "template":
            tmpl = TEMPLATES.get(st.session_state.get("current_template"), {})
            title = tmpl.get("name", "Document")
        else:
            title = TOOLS.get(current, {}).get("name", "Document")

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        export_title = f"{title} - {now}"

        md_content = export_markdown(
            export_title,
            st.session_state.output_text,
            metadata={
                "Tool": title,
                "Generated": now,
                "Words": str(text_stats(st.session_state.output_text)["words"]),
            },
        )

        st.download_button(
            label="📥 Markdown",
            data=md_content,
            file_name=f"{export_title.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col3:
        txt_content = export_text(export_title, st.session_state.output_text)
        st.download_button(
            label="📥 Text",
            data=txt_content,
            file_name=f"{export_title.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col4:
        if st.button("💾 Save", use_container_width=True):
            doc_id = save_document(
                title=export_title,
                content=st.session_state.output_text,
                tool=current,
                extra_info=extra_params,
            )
            st.success("Document saved!")
            time.sleep(0.5)
            st.rerun()

    with col5:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.rerun()

    # ── Show original input for reference ──
    if st.session_state.input_text:
        with st.expander("📝 Original Input"):
            st.text(st.session_state.input_text)