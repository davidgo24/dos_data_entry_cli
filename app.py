"""
DOS Data Entry — Transit
Flask app for Railway deployment.
"""
import os
import tempfile
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from extract_dos_data import extract_dos_data

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# In-memory store for extracted data (single-tenant for transit dept)
_dos_data = None


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/data")
def api_data():
    """Return extracted DOS data or 404 if none loaded."""
    global _dos_data
    if _dos_data is None:
        return jsonify({"error": "No data loaded. Upload an Excel file first."}), 404
    return jsonify(_dos_data)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Accept Excel file, extract data, store in memory."""
    global _dos_data
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"error": "File must be Excel (.xlsx or .xls)"}), 400
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            file.save(tmp.name)
            _dos_data = extract_dos_data(tmp.name)
        os.unlink(tmp.name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True, "employees": len(_dos_data["employees"])})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
