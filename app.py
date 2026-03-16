"""
DOS Data Entry — Transit
Flask app for Railway deployment.
Each visitor gets an isolated session — upload and work independently.
"""
import os
import re
import tempfile
import uuid
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, session
from extract_dos_data import extract_dos_data

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
# SESSION_COOKIE_SECURE: set in production via env; Railway serves HTTPS

# Per-session DOS data: { session_id: { employees, date } }
_dos_data: dict[str, dict] = {}


def _uid():
    """Get or create a unique session id for this visitor."""
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    return session["uid"]


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/data")
def api_data():
    """Return extracted DOS data or 404 if none loaded."""
    uid = _uid()
    data = _dos_data.get(uid)
    if data is None:
        return jsonify({"error": "No data loaded. Upload an Excel file first."}), 404
    return jsonify(data)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Accept Excel file, extract data, store per-session."""
    uid = _uid()
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"error": "File must be Excel (.xlsx or .xls)"}), 400
    format_hint = request.form.get("format") or None  # "standard" | "raw" | None (auto)
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            file.save(tmp.name)
            data = extract_dos_data(tmp.name, format=format_hint)
        os.unlink(tmp.name)
        # Prefer first date from filename (schedule date; ignore generated_at date)
        m = re.search(r"\d{4}-\d{2}-\d{2}", file.filename or "")
        if m:
            data["date"] = m.group(0)
        _dos_data[uid] = data
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(data)


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear this session's DOS data (resets to upload screen on reload)."""
    uid = _uid()
    if uid in _dos_data:
        del _dos_data[uid]
    return jsonify({"ok": True})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# CTE list: employee IDs who prefer 3002 over 1013 for OT
_cte_session: dict[str, list[str]] = {}  # uid -> list of employee_ids
CONFIG_CTE_PATH = Path(__file__).resolve().parent / "config_cte.json"

# Supervisors list: employee IDs excluded from Op view and export
_supervisors_session: dict[str, list[str]] = {}
CONFIG_SUPERVISORS_PATH = Path(__file__).resolve().parent / "config_supervisors.json"


@app.route("/api/cte", methods=["GET"])
def api_cte_get():
    """Return CTE list (from config file + session upload)."""
    uid = _uid()
    ids = set()
    if CONFIG_CTE_PATH.exists():
        try:
            import json
            with open(CONFIG_CTE_PATH, encoding="utf-8") as f:
                data = json.load(f)
            ids.update(str(x) for x in (data if isinstance(data, list) else data.get("ids", data.get("employee_ids", []))))
        except Exception:
            pass
    ids.update(_cte_session.get(uid, []))
    return jsonify({"ids": list(ids)})


@app.route("/api/cte", methods=["POST"])
def api_cte_post():
    """Upload CTE list (employee IDs), merge with session."""
    uid = _uid()
    try:
        data = request.get_json(force=True, silent=True) or {}
        ids = data.get("ids", data.get("employee_ids", data if isinstance(data, list) else []))
        ids = [str(x).strip() for x in ids if x]
        _cte_session[uid] = list(set(ids))
        return jsonify({"ok": True, "count": len(_cte_session[uid])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/supervisors", methods=["GET"])
def api_supervisors_get():
    """Return supervisors list (from config file + session)."""
    uid = _uid()
    ids = set()
    if CONFIG_SUPERVISORS_PATH.exists():
        try:
            import json
            with open(CONFIG_SUPERVISORS_PATH, encoding="utf-8") as f:
                data = json.load(f)
            ids.update(str(x) for x in (data if isinstance(data, list) else data.get("ids", data.get("employee_ids", []))))
        except Exception:
            pass
    ids.update(_supervisors_session.get(uid, []))
    return jsonify({"ids": list(ids)})


@app.route("/api/supervisors", methods=["POST"])
def api_supervisors_post():
    """Upload supervisors list (employee IDs), merge with session."""
    uid = _uid()
    try:
        data = request.get_json(force=True, silent=True) or {}
        ids = data.get("ids", data.get("employee_ids", data if isinstance(data, list) else []))
        ids = [str(x).strip() for x in ids if x]
        _supervisors_session[uid] = list(set(ids))
        return jsonify({"ok": True, "count": len(_supervisors_session[uid])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
