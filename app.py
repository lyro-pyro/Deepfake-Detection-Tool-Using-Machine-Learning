"""
Flask app for Deepfake Detection.
Routes:
  GET  /          → landing page (homepage)
  GET  /detect    → upload & analyze page
  POST /analyze   → JSON API — returns detection results
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from detector import analyze_image

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Explicit static file serving
# ---------------------------------------------------------------------------
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
@app.route("/")
@app.route("/api")
@app.route("/api/index")
@app.route("/api/index.py")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Detect page (upload UI)
# ---------------------------------------------------------------------------
@app.route("/detect")
@app.route("/api/detect")
def detect_page():
    return render_template("detect.html")


# ---------------------------------------------------------------------------
# Analyze API endpoint
# ---------------------------------------------------------------------------
@app.route("/analyze", methods=["POST"])
@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Please upload an image."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file type. Please upload: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    try:
        file_bytes = file.read()
        result = analyze_image(file_bytes)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.exception("Unexpected error during analysis")
        return jsonify({"error": "An internal error occurred during analysis."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
