"""Vercel entrypoint. Vercel serves this ASGI app for every route via vercel.json rewrites."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402,F401
