import os
import sys

# Ensure root directory is in python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    # Strip Vercel function routing prefixes if present
    if path.startswith("/api/index.py"):
        environ["PATH_INFO"] = path[len("/api/index.py") :] or "/"
    elif path.startswith("/api/"):
        environ["PATH_INFO"] = path[len("/api") :] or "/"
    elif path == "/api":
        environ["PATH_INFO"] = "/"

    return flask_app(environ, start_response)
