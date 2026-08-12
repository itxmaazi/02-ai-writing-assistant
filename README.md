# Beacon Writer

An AI writing assistant built with Streamlit. Nine writing tools, eight
templates, streaming output, a local document library and Markdown / plain
text export.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then add at least one API key
streamlit run app.py
```

## Project layout

| File / folder            | Purpose                                        |
| ------------------------ | ---------------------------------------------- |
| `app.py`                 | UI, layout and page flow                       |
| `engine.py`              | Provider calls (Gemini primary, Groq fallback) |
| `tools.py`               | Tool definitions and prompt builders           |
| `templates_data.py`      | Template definitions and their prompt builders |
| `utils.py`               | Text stats, export helpers, document storage   |
| `config_paths.py`        | Shared filesystem paths                        |
| `assets/style.css`       | All presentation rules                         |
| `.streamlit/config.toml` | Streamlit theme and server settings            |
| `data/documents.json`    | Saved documents (git-ignored)                  |

## Configuration

At least one provider key is required in `.env`:

```
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

The sidebar shows a green dot for every provider that is ready and a red dot
for one that is not, so a missing key is visible before you hit Generate.

## Styling

Presentation lives entirely in `assets/style.css`; `app.py` contains no
inline `<style>` blocks. The stylesheet is re-read whenever its modification
time changes, so edits show up on the next rerun.

Two rules there are load-bearing and should not be reverted:

- The Streamlit header is **not** hidden. The button that reopens a collapsed
  sidebar (`data-testid="stExpandSidebarButton"`) lives inside it, so
  `header { visibility: hidden }` leaves no way to bring the sidebar back.
- The body font is applied to containers, never blanket-applied to every
  `span` with `!important`. Streamlit renders icons as ligature glyphs inside
  spans; overriding that font erases every icon in the app.

## Development

```bash
ruff check .
flake8 .
pylint *.py
```

All three are configured in `pyproject.toml` / `.flake8` and pass clean.
