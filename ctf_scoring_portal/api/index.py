import os
import sys

# Ensure parent directory is in path so local modules (db, crypto_vault) import properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app as flask_app

class VercelPathMiddleware:
    """
    Normalizes PATH_INFO when Vercel rewrite forwards /api/index.py or /api/index
    to the WSGI application, ensuring Flask matches root and child routes correctly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        # If Vercel rewrote / to /api/index.py or /api/index, strip that prefix
        if path in ("/api/index.py", "/api/index"):
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/index.py/"):
            environ["PATH_INFO"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            environ["PATH_INFO"] = path[len("/api/index"):]
        return self.wsgi_app(environ, start_response)

# Vercel Serverless WSGI Handler
app = VercelPathMiddleware(flask_app)
