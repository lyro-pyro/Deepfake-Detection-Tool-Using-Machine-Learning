import os
import sys

# Ensure root directory is in python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


def app(environ, start_response):
    # Retrieve the original matched path from Vercel header if available
    real_path = environ.get("HTTP_X_MATCHED_PATH") or environ.get("HTTP_X_VERCEL_MATCHED_PATH")

    if real_path:
        environ["PATH_INFO"] = real_path
    else:
        path = environ.get("PATH_INFO", "")
        if path.startswith("/api/index.py"):
            environ["PATH_INFO"] = path[len("/api/index.py") :] or "/"
        elif path.startswith("/api/"):
            environ["PATH_INFO"] = path[len("/api") :] or "/"
        elif path in ("/api", "/api/index"):
            environ["PATH_INFO"] = "/"

    return flask_app(environ, start_response)
