import json
import os
import re
import time
from pathlib import Path
from flask import Flask, abort, jsonify, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "site_content.json"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg", "gif"}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024


def is_local_request() -> bool:
    """
    Allow /edit and write/upload APIs ONLY when running locally on loopback.
    On Render (or behind any proxy), strictly return False -> 404.
    """
    if os.environ.get("RENDER") or os.environ.get("ENV") == "production":
        return False

    host = request.host.split(":")[0].lower()
    remote_ip = request.remote_addr or ""
    forwarded_for = request.headers.get("X-Forwarded-For")

    return (
        host in ("127.0.0.1", "localhost")
        and remote_ip in ("127.0.0.1", "::1")
        and not forwarded_for
    )


def load_content() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_content(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = DATA_FILE.with_suffix(".json.tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_file.replace(DATA_FILE)

    projects_file = BASE_DIR / "projects.json"
    tmp_proj = projects_file.with_suffix(".json.tmp")
    with tmp_proj.open("w", encoding="utf-8") as f:
        json.dump({"projects": data.get("projects", [])}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_proj.replace(projects_file)


def list_uploads() -> list[str]:
    if not UPLOAD_DIR.exists():
        return []
    return [
        f"/static/uploads/{p.name}"
        for p in sorted(UPLOAD_DIR.iterdir(), reverse=True)
        if p.is_file() and p.suffix.lstrip(".").lower() in ALLOWED_EXTENSIONS
    ]


@app.route("/")
@app.route("/fa")
@app.route("/en")
def index():
    lang = "fa" if request.path == "/fa" or request.args.get("lang") == "fa" else "en"
    content = load_content()
    return render_template(
        "index.html",
        content=content,
        lang=lang,
        is_local=is_local_request(),
    )


@app.route("/teapot")
def teapot():
    lang = request.args.get("lang", "en")
    return render_template("teapot.html", lang=lang if lang in ("en", "fa") else "en"), 418


@app.route("/api/content")
def api_content():
    return jsonify(load_content())


@app.route("/api/projects")
def api_projects():
    return jsonify({"projects": load_content().get("projects", [])})


@app.route("/edit")
def edit_page():
    if not is_local_request():
        abort(404)
    return render_template(
        "edit.html",
        content=load_content(),
        uploads=list_uploads(),
    )


@app.route("/api/save", methods=["POST"])
def api_save():
    if not is_local_request():
        abort(404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "profile" not in payload or "projects" not in payload:
        return jsonify({"error": "Invalid JSON payload"}), 400
    save_content(payload)
    return jsonify({"ok": True})


@app.route("/api/uploads", methods=["GET"])
def api_uploads():
    if not is_local_request():
        abort(404)
    return jsonify({"files": list_uploads()})


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if not is_local_request():
        abort(404)

    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "No file provided"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type"}), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stem = secure_filename(Path(file.filename).stem) or "img"
    stem = re.sub(r"[^a-zA-Z0-9_-]", "-", stem)[:40]
    filename = f"{stem}-{int(time.time())}.{ext}"
    file.save(UPLOAD_DIR / filename)

    return jsonify({"ok": True, "url": f"/static/uploads/{filename}", "files": list_uploads()})


@app.route("/api/upload/<filename>", methods=["DELETE"])
def api_delete_upload(filename: str):
    if not is_local_request():
        abort(404)
    safe_name = secure_filename(filename)
    target = UPLOAD_DIR / safe_name
    if target.exists() and target.is_file():
        target.unlink()
    return jsonify({"ok": True, "files": list_uploads()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
