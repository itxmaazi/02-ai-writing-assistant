"""Filesystem paths used across the app.

Kept in its own module so ``app.py`` and ``utils.py`` can both import the
paths without creating a circular dependency.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
STYLESHEET = os.path.join(ASSETS_DIR, "style.css")

os.makedirs(DATA_DIR, exist_ok=True)
