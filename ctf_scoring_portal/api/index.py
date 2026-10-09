import os
import sys

# Ensure parent directory is in path so local modules (db, crypto_vault) import properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app as flask_app

class VercelPathMiddleware:
    """
    Normalizes PATH_INFO and SCRIPT_NAME when Vercel serverless function receives requests.
    Uses HTTP_X_VERCEL_MATCHED_PATH (the exact path the client requested, e.g. /login, /register)
    and clears SCRIPT_NAME so url_for() generates clean root-relative links (e.g. / instead of /api/index.py).
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Clear SCRIPT_NAME so url_for generates clean paths without /api/index.py
        environ["SCRIPT_NAME"] = ""

        # Vercel passes the original requested path in HTTP_X_VERCEL_MATCHED_PATH
        matched_path = environ.get("HTTP_X_VERCEL_MATCHED_PATH")
        if matched_path:
            environ["PATH_INFO"] = matched_path
        else:
            path = environ.get("PATH_INFO", "")
            if path in ("/api/index.py", "/api/index"):
                environ["PATH_INFO"] = "/"
            elif path.startswith("/api/index.py/"):
                environ["PATH_INFO"] = path[len("/api/index.py"):]
            elif path.startswith("/api/index/"):
                environ["PATH_INFO"] = path[len("/api/index"):]

        return self.wsgi_app(environ, start_response)

# Vercel Serverless WSGI Handler
app = VercelPathMiddleware(flask_app)
