#!/usr/bin/env python3
"""SYNAPSE — minimal Flask resume site (EN default, FA with full RTL)."""
import json
import os
import functools
from pathlib import Path

from flask import Flask, render_template, jsonify, request, abort

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
SSH_PORT = os.environ.get("SYNAPSE_PORT", "22")

# ── API KEY ────────────────────────────────────────────────────────────────
ADMIN_API_KEY = os.environ.get("SYNAPSE_ADMIN_KEY", "change-me-please")

def require_api_key(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key") or request.args.get("api_key")
        if key != ADMIN_API_KEY:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ── HELPERS ────────────────────────────────────────────────────────────────
def ssh_hint(host):
    if SSH_PORT == "22":
        return "ssh %s" % host
    return "ssh %s -p %s" % (host, SSH_PORT)


PROJECTS_FILE = BASE / "projects.json"

def load_projects():
    try:
        with open(PROJECTS_FILE, encoding="utf-8") as f:
            return json.load(f).get("projects", [])
    except Exception:
        return []

def resume_projects():
    """Add presentation categories without modifying the stored project records."""
    hardware_tags = {"IOT", "EMBEDDED", "HARDWARE", "PCB DESIGN", "ESP32", "MICROPYTHON"}
    result = []
    for project in load_projects():
        tags = {str(tag).upper() for tag in project.get("tags", [])}
        category = "hardware" if tags & hardware_tags else "software"
        result.append({**project, "category": category})
    return sorted(result, key=lambda project: project["category"] != "software")


def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"projects": projects}, f, ensure_ascii=False, indent=2)

CONTENT_FILE = BASE / "content.json"

def load_content():
    """Load editable content from content.json, fallback to I18N defaults."""
    try:
        with open(CONTENT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_content(data):
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── I18N (static defaults — overridden by content.json at runtime) ─────────
I18N_DEFAULTS = {
    "en": {
        "lang_other": "FA", "theme_dark": "DARK", "theme_light": "LIGHT",
        "site": "SYNAPSE", "name": "MOHAMMAD REZA EBADOLLAH",
        "role": "COMPUTER ENGINEER · IOT / EMBEDDED / SIGNAL + IMAGE",
        "ssh_line": "TERMINAL TWIN · {hint} · NO LOGIN NEEDED",
        "sec_about": "ABOUT", "sec_skills": "SKILLS", "sec_boards": "BOARDS",
        "sec_exp": "EXPERIENCE", "sec_projects": "PROJECTS", "sec_links": "CONTACT",
        "bio": """Computer Engineering student interested in both hardware and software — from web scraping, bots, and automation to electronics, building devices, and the Internet of Things.

My main board is currently the ESP32, but I've also worked with Arduino, Raspberry Pi Pico, the ESP8266 family, Pi Zero, and Pi 5.

Data, audio, signal, and image processing are some of the areas I've always found interesting and enjoy exploring.

If you have a project you think I could help with, I'd be happy to work together!
""",
        "skills_note": "self-assessed",
        "skill_items": [
            {"k": "PYTHON", "pct": 80},
            {"k": "C / C++ / ARDUINO / EMBEDDED C", "pct": 60},
            {"k": "PHP", "pct": 40},
        ],
        "tools": "FLASK · FASTAPI · uv · SQL · GIT · DOCKER (A BIT)",
        "boards_items": ["ESP32 — MAIN BOARD", "ARDUINO", "RASPBERRY PI PICO",
                         "ESP8266 FAMILY", "RASPBERRY PI ZERO", "RASPBERRY PI 5"],
        "exp_items": [
            {"role": "R&D · University of Qom", "dur": "2026-present", "note": "making a DataLogger and other IoT Projects"},
            {"role": "FREELANCE DEVELOPER · PARSCODERS", "dur": "2020-2024 · 4 years", "note": "python webscrapping expert and bot automation [https://parscoders.com/resume/150715/mohammad_e]"},
        ],
        "proj_loading": "LOADING PROJECTS\u2026",
        "links_note": "SAME USERNAME EVERYWHERE",
        "more_link": "MORE \u2192", "more_title": "MORE / SETUP",
        "sec_system": "SYSTEM / OS", "os_line": "WINDOWS — DAILY DRIVER · UBUNTU GNOME — SECOND HOME",
        "sec_term": "TERMINAL", "term_line": "GHOSTTY — EVERYWHERE",
        "sec_tools": "TOOLS", "tools_line": "GIT · DOCKER (A BIT) · uv · SQL · LEARNING POSTGRESQL",
        "sec_devops": "DEVOPS", "devops_line": "INTERESTED — CI/CD, CONTAINERS, LINUX BOXES",
        "sec_making": "MAKING", "making_line": "DATALOGGERS · SMART SENSORS · HOME AUTOMATION · ROBOTICS · 3D PRINTING",
        "sec_site": "THIS SITE", "site_line": "FLASK + ONE CSS FILE — NO JS LIBRARIES, NO CDN",
        "foot": "\u00a9 2026 MOHAMMAD REZA EBADOLLAH — SYNAPSE",
    },
    "fa": {
        "lang_other": "EN",
        "theme_dark": "تیره",
        "theme_light": "روشن",
        "site": "سینپس",
        "name": "محمدرضا عبادالله",
        "role": "مهندس کامپیوتر · اینترنت اشیا / سیستم‌های نهفته / سیگنال و تصویر",
        "ssh_line": "نسخهٔ ترمینالی · {hint} · بدون لاگین",
        "sec_about": "دربارهٔ من",
        "sec_skills": "مهارت‌ها",
        "sec_boards": "بردها",
        "sec_exp": "تجربه",
        "sec_projects": "پروژه‌ها",
        "sec_links": "ارتباط",
        "bio": """در حال تحصیل در رشته مهندسی کامپیوتر هستم و به حوزه‌های سخت‌افزار و نرم‌افزار علاقه دارم؛ از وب‌اسکرپینگ، بات و اتومیشن گرفته تا الکترونیک، ساخت دستگاه‌ها و اینترنت اشیا (IoT).

در حال حاضر بیشتر با ESP32 کار می‌کنم، اما تجربه کار با آردوینو، Raspberry Pi Pico، خانواده ESP8266، Raspberry Pi Zero و Raspberry Pi 5 رو هم دارم.

پردازش داده، صوت، سیگنال و تصویر از حوزه‌هایی هستن که همیشه برام جذاب بودن و دوست دارم بیشتر توی این زمینه‌ها تجربه کسب کنم.

اگه پروژه‌ای دارید که فکر می‌کنید می‌تونم توش کمکی کنم، خوشحال می‌شم با هم همکاری کنیم!
""",
        "skills_note": "برآورد شخصی",
        "skill_items": [
            {"k": "پایتون", "pct": 80},
            {"k": "C / C++ / آردوینو / EMBEDDED C", "pct": 60},
            {"k": "PHP", "pct": 40}
        ],
        "tools": "فلسک · فست‌ای‌پی‌آی · uv · اسکیول · گیت · داکر (کمی)",
        "boards_items": [
            "ESP32 — برد اصلی",
            "آردوینو",
            "رزبری‌پای پیکو",
            "خانوادهٔ ESP8266",
            "رزبری‌پای زیرو",
            "رزبری‌پای 5"
        ],
        "exp_items": [
            {"role": "دانشگاه قم R&D", "dur": "2026-present", "note": "پروژه IoT و دیتالاگر"},
            {"role": "توسعه‌دهندهٔ فریلنسر · پارس‌کدرز", "dur": "2020-2024 · 4 years", "note": "python webscrapping expert and bot automation [https://parscoders.com/resume/150715/mohammad_e]"},
        ],
        "proj_loading": "در حال بارگذاری پروژه‌ها…",
        "links_note": "در همه‌جا همین نام کاربری",
        "more_link": "بیشتر ←",
        "more_title": "بیشتر / سیستم",
        "sec_system": "سیستم / عامل",
        "os_line": "ویندوز — سیستم اصلی · اوبونتو گنوم — خانهٔ دوم",
        "sec_term": "ترمینال",
        "term_line": "ghostty — همه‌جا",
        "sec_tools": "ابزارها",
        "tools_line": "گیت · داکر (کمی) · uv · اسکیول · در حال یادگیری پستگرس",
        "sec_devops": "دواپس",
        "devops_line": "علاقه‌مند — CI/CD، کانتینرها، باکس‌های لینوکس",
        "sec_making": "ساخت",
        "making_line": "دیتالاگر · سنسور هوشمند · هوشمندسازی خانه · رباتیک · پرینتر سه‌بعدی",
        "sec_site": "این سایت",
        "site_line": "فلسک + یک فایل css — بدون کتابخانهٔ جاوااسکریپت و بدون CDN",
        "foot": "© ۲۰۲۶ محمدرضا عبادالله — سینپس"
    }
}

def get_i18n():
    """Merge defaults with any saved overrides from content.json."""
    overrides = load_content()
    result = {}
    for lang in ("en", "fa"):
        merged = dict(I18N_DEFAULTS[lang])
        if lang in overrides:
            merged.update(overrides[lang])
        result[lang] = merged
    return result


# ── PUBLIC ROUTES ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    return page("en")


@app.route("/<lang>")
def page(lang):
    I18N = get_i18n()
    if lang not in I18N:
        abort(404)
    host = request.host.split(":")[0]
    return render_template(
        "index.html", lang=lang, t=I18N[lang], rtl=(lang == "fa"),
        ssh_hint=ssh_hint(host),
        has_profile=(BASE / "static" / "profile.jpg").exists(),
        projects=resume_projects(),
    )


@app.route("/more")
def more_en():
    return _more("en")


@app.route("/fa/more")
def more_fa():
    return _more("fa")


def _more(lang):
    I18N = get_i18n()
    host = request.host.split(":")[0]
    return render_template("more.html", lang=lang, t=I18N[lang], rtl=(lang == "fa"),
                           ssh_hint=ssh_hint(host))


@app.route("/api/projects")
def api_projects():
    return jsonify({"projects": load_projects()})


@app.route("/teapot")
def teapot():
    lang = request.args.get("lang", "en")
    return render_template("teapot.html", lang=lang if lang in I18N_DEFAULTS else "en"), 418


# ── ADMIN API ──────────────────────────────────────────────────────────────

# --- Projects ---

@app.route("/admin/projects", methods=["GET"])
@require_api_key
def admin_get_projects():
    """GET all projects."""
    return jsonify({"projects": load_projects()})


@app.route("/admin/projects", methods=["POST"])
@require_api_key
def admin_add_project():
    """
    POST — add a new project.
    Body (JSON):
      id        string  unique slug (e.g. "my-project")
      title     {en, fa}
      desc      {en, fa}
      tags      [string, ...]
      link      string | null
      image     string | null
    """
    data = request.get_json(force=True)
    if not data or not data.get("id"):
        return jsonify({"error": "id is required"}), 400

    projects = load_projects()
    if any(p["id"] == data["id"] for p in projects):
        return jsonify({"error": f"project with id '{data['id']}' already exists"}), 409

    project = {
        "id":    data["id"],
        "title": data.get("title", {"en": data["id"], "fa": data["id"]}),
        "desc":  data.get("desc",  {"en": "", "fa": ""}),
        "tags":  data.get("tags",  []),
        "link":  data.get("link",  None),
        "image": data.get("image", None),
    }
    projects.append(project)
    save_projects(projects)
    return jsonify({"ok": True, "project": project}), 201


@app.route("/admin/projects/<project_id>", methods=["GET"])
@require_api_key
def admin_get_project(project_id):
    """GET a single project by id."""
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return jsonify({"error": "not found"}), 404
    return jsonify(project)


@app.route("/admin/projects/<project_id>", methods=["PUT"])
@require_api_key
def admin_update_project(project_id):
    """
    PUT — update an existing project (partial update supported).
    Body (JSON): any subset of {title, desc, tags, link, image, id}
    """
    data = request.get_json(force=True)
    projects = load_projects()
    idx = next((i for i, p in enumerate(projects) if p["id"] == project_id), None)
    if idx is None:
        return jsonify({"error": "not found"}), 404

    project = projects[idx]
    for key in ("id", "title", "desc", "tags", "link", "image"):
        if key in data:
            project[key] = data[key]
    projects[idx] = project
    save_projects(projects)
    return jsonify({"ok": True, "project": project})


@app.route("/admin/projects/<project_id>", methods=["DELETE"])
@require_api_key
def admin_delete_project(project_id):
    """DELETE a project by id."""
    projects = load_projects()
    new_projects = [p for p in projects if p["id"] != project_id]
    if len(new_projects) == len(projects):
        return jsonify({"error": "not found"}), 404
    save_projects(new_projects)
    return jsonify({"ok": True, "deleted": project_id})


@app.route("/admin/projects/reorder", methods=["POST"])
@require_api_key
def admin_reorder_projects():
    """
    POST — reorder projects.
    Body (JSON): {"order": ["id1", "id2", "id3"]}
    """
    data = request.get_json(force=True)
    order = data.get("order", [])
    projects = load_projects()
    proj_map = {p["id"]: p for p in projects}
    reordered = [proj_map[pid] for pid in order if pid in proj_map]
    # append any projects not in the order list at the end
    for p in projects:
        if p["id"] not in order:
            reordered.append(p)
    save_projects(reordered)
    return jsonify({"ok": True, "order": [p["id"] for p in reordered]})


# --- Content (bio, skills, experience, etc.) ---

@app.route("/admin/content", methods=["GET"])
@require_api_key
def admin_get_content():
    """GET all editable content (current overrides merged with defaults)."""
    return jsonify(get_i18n())


@app.route("/admin/content/<lang>", methods=["PUT"])
@require_api_key
def admin_update_content(lang):
    """
    PUT — update content for a language (partial update).
    lang: 'en' or 'fa'
    Body (JSON): any subset of the I18N fields, e.g.:
      {"bio": "new bio text", "role": "new role"}

    Editable fields:
      bio, role, name, tools, skills_note
      skill_items   → [{k, pct}, ...]
      boards_items  → [string, ...]
      exp_items     → [{role, dur, note}, ...]
      foot, os_line, term_line, tools_line, devops_line, making_line, site_line
    """
    if lang not in ("en", "fa"):
        return jsonify({"error": "lang must be 'en' or 'fa'"}), 400

    data = request.get_json(force=True)
    overrides = load_content()
    if lang not in overrides:
        overrides[lang] = {}
    overrides[lang].update(data)
    save_content(overrides)
    return jsonify({"ok": True, "updated": lang, "fields": list(data.keys())})


@app.route("/admin/content/<lang>/skills", methods=["PUT"])
@require_api_key
def admin_update_skills(lang):
    """
    PUT — replace skill_items for a language.
    Body (JSON): {"skills": [{"k": "PYTHON", "pct": 85}, ...]}
    """
    if lang not in ("en", "fa"):
        return jsonify({"error": "lang must be 'en' or 'fa'"}), 400
    data = request.get_json(force=True)
    skills = data.get("skills")
    if not isinstance(skills, list):
        return jsonify({"error": "'skills' must be a list"}), 400
    overrides = load_content()
    overrides.setdefault(lang, {})["skill_items"] = skills
    save_content(overrides)
    return jsonify({"ok": True, "skill_items": skills})


@app.route("/admin/content/<lang>/experience", methods=["PUT"])
@require_api_key
def admin_update_experience(lang):
    """
    PUT — replace exp_items for a language.
    Body (JSON): {"experience": [{"role": "...", "dur": "...", "note": "..."}, ...]}
    """
    if lang not in ("en", "fa"):
        return jsonify({"error": "lang must be 'en' or 'fa'"}), 400
    data = request.get_json(force=True)
    exp = data.get("experience")
    if not isinstance(exp, list):
        return jsonify({"error": "'experience' must be a list"}), 400
    overrides = load_content()
    overrides.setdefault(lang, {})["exp_items"] = exp
    save_content(overrides)
    return jsonify({"ok": True, "exp_items": exp})


@app.route("/admin/content/<lang>/boards", methods=["PUT"])
@require_api_key
def admin_update_boards(lang):
    """
    PUT — replace boards_items for a language.
    Body (JSON): {"boards": ["ESP32", "Arduino", ...]}
    """
    if lang not in ("en", "fa"):
        return jsonify({"error": "lang must be 'en' or 'fa'"}), 400
    data = request.get_json(force=True)
    boards = data.get("boards")
    if not isinstance(boards, list):
        return jsonify({"error": "'boards' must be a list"}), 400
    overrides = load_content()
    overrides.setdefault(lang, {})["boards_items"] = boards
    save_content(overrides)
    return jsonify({"ok": True, "boards_items": boards})


@app.route("/admin/content/reset", methods=["POST"])
@require_api_key
def admin_reset_content():
    """POST — reset all content overrides back to hardcoded defaults."""
    save_content({})
    return jsonify({"ok": True, "message": "content reset to defaults"})


# --- Status ---

@app.route("/admin/status", methods=["GET"])
@require_api_key
def admin_status():
    """GET — quick health check + stats."""
    overrides = load_content()
    return jsonify({
        "ok": True,
        "projects_count": len(load_projects()),
        "content_overrides": {lang: list(fields.keys()) for lang, fields in overrides.items()},
    })


# ── ADMIN WEB PANEL ────────────────────────────────────────────────────────
@app.route("/admin")
def admin_panel():
    """Serve the admin web panel (authentication handled client-side with API key)."""
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)