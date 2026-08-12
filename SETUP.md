# Beacon Writer — Setup Guide

## Requirements

- Python 3.10 or newer
- VS Code with the Python + Pylance extensions (optional)
- An API key for Gemini and/or Groq

## Installation

```bash
cd D:\Python\02-ai-writing-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure keys

Copy `.env.example` to `.env` and fill in at least one key:

```
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

Gemini is tried first; Groq is the fallback. If a key is missing the sidebar
marks that provider red and the app says so instead of failing silently.

## Run

```bash
streamlit run app.py
```

The app opens at http://localhost:8501.

## Verify the setup

```bash
python engine.py     # prints provider status and streams a test response
python tools.py      # lists the tools and runs the grammar fixer
ruff check .         # lint
flake8 .             # lint
pylint *.py          # lint
```

## Project structure

```
02-ai-writing-assistant/
├── app.py                  UI and page flow
├── engine.py               Gemini + Groq calls
├── tools.py                Tool definitions and prompt builders
├── templates_data.py       Templates
├── utils.py                Stats, export, storage
├── config_paths.py         Shared paths
├── assets/style.css        All styling
├── .streamlit/config.toml  Theme and server settings
├── requirements.txt
├── .env.example
└── data/documents.json     Saved documents (git-ignored)
```
