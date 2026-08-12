# test_all.py

from tools import TOOLS
from templates_data import TEMPLATES
from utils import text_stats

print("Tools:")
for key, t in TOOLS.items():
    print(f"  {t['icon']} {t['name']}")

print(f"\nTemplates:")
for key, t in TEMPLATES.items():
    print(f"  {t['icon']} {t['name']}")

print(f"\nStats: {text_stats('Hello world this is a test sentence.')}")
print("\nAll imports working!")