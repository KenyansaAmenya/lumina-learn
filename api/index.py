import os
import sys

api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

print(f"[VERCEL] API directory: {api_dir}")
print(f"[VERCEL] Python path: {sys.path[:2]}")

from main import app

app = app
