import os
import sys
from urllib.parse import parse_qs

# Ensure root directory is in python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


def app(environ, start_response):
    # Check query string for explicit __path rewrite from vercel.json
    qs = environ.get("QUERY_STRING", "")
    params = parse_qs(qs)
    
    if "__path" in params and params["__path"]:
        target_path = params["__path"][0]
        if target_path and target_path not in ("/api/index.py", "/api/index", "/api"):
            environ["PATH_INFO"] = target_path
    else:
        # Fallback to headers
        for key in ("HTTP_X_MATCHED_PATH", "HTTP_X_VERCEL_MATCHED_PATH", "HTTP_X_FORWARDED_URI", "REQUEST_URI", "RAW_URI"):
            val = environ.get(key)
            if val:
                path_only = val.split("?")[0]
                if path_only and path_only not in ("/api/index.py", "/api/index", "/api"):
                    environ["PATH_INFO"] = path_only
                    break

    return flask_app(environ, start_response)
