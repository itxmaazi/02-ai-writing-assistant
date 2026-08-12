# config_paths.py
# ============================================================
# FILE PATHS (separated so utils.py and app.py can both import
# without circular dependency issues)
# ============================================================

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
os.makedirs(DATA_DIR, exist_ok=True)