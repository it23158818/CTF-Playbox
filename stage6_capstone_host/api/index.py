import os
import sys
import urllib.parse

# Ensure stage6_capstone_host root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from capstone_server import app as flask_app

class VercelPathMiddleware:
    """
    Normalizes PATH_INFO and SCRIPT_NAME when Vercel serverless function receives requests.
    Inspects the 'path' query parameter passed by vercel.json rewrite (e.g. /, /api/exec, /health, /reset)
    and resets SCRIPT_NAME so routing works properly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ["SCRIPT_NAME"] = ""

        # Check query string for path passed by vercel.json rewrite
        query_string = environ.get("QUERY_STRING", "")
        parsed_params = urllib.parse.parse_qs(query_string, keep_blank_values=True)

        target_path = None
        if "path" in parsed_params and parsed_params["path"]:
            val = parsed_params["path"][0]
            if val:
                target_path = val if val.startswith("/") else "/" + val

        # Fallback to HTTP_X_VERCEL_MATCHED_PATH or PATH_INFO
        if not target_path:
            raw_path = environ.get("HTTP_X_VERCEL_MATCHED_PATH") or environ.get("PATH_INFO", "")
            if raw_path in ("/api/index", "/api/index.py", ""):
                target_path = "/"
            elif raw_path.startswith("/api/index/"):
                target_path = raw_path[len("/api/index"):]
            elif raw_path.startswith("/api/index.py/"):
                target_path = raw_path[len("/api/index.py"):]
            else:
                target_path = raw_path

        if target_path in ("/api/index", "/api/index.py", ""):
            target_path = "/"

        environ["PATH_INFO"] = target_path

        return self.wsgi_app(environ, start_response)

# Vercel Serverless WSGI Handler
app = VercelPathMiddleware(flask_app)
