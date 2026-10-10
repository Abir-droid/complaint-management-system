import sys
import os

# Ensure the project root is on sys.path so `from app import app` works
# regardless of the working directory (Vercel, local, etc.)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

# Entrypoint for Vercel Serverless Function