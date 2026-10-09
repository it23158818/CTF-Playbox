import os
import sys

# Ensure parent directory is in path so local modules (db, crypto_vault) import properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Vercel Serverless WSGI Handler
app = app
