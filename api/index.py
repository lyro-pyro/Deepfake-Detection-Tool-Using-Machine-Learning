import os
import sys

# Ensure root directory is in python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


def app(environ, start_response):
    debug_keys = {k: v for k, v in environ.items() if isinstance(v, str) and not k.startswith("npm_")}
    print(f"VERCEL_ENVIRON_DEBUG: {debug_keys}")
    return flask_app(environ, start_response)
