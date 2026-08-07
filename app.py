#!/usr/bin/env python3
"""SYNAPSE — minimal Flask resume site (EN default, FA with full RTL)."""
import json
import os
from pathlib import Path

from flask import Flask, render_template, jsonify, request, abort

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
SSH_PORT = os.environ.get("SYNAPSE_PORT", "2222")


def load_projects():
    try:
        with open(BASE / "projects.json", encoding="utf-8") as f:
            return json.load(f).get("projects", [])
    except Exception:
        return []


I18N = {
    "en": {
        "lang_other": "FA", "theme_dark": "DARK", "theme_light": "LIGHT",
        "site": "SYNAPSE", "name": "MOHAMMAD REZA EBADOLLAH",
        "role": "COMPUTER ENGINEER · IOT / EMBEDDED / SIGNAL + IMAGE",
        "ssh_line": "SSH: ssh ebad84@{host} -p {port}  —  terminal twin of this site",
        "sec_about": "ABOUT", "sec_skills": "SKILLS", "sec_boards": "BOARDS",
        "sec_exp": "EXPERIENCE", "sec_projects": "PROJECTS", "sec_links": "CONTACT",
        "bio": "Computer engineer who likes to build things — electronics, devices and the "
               "internet of things. My main board is the ESP32; I also work with Arduino, "
               "Raspberry Pi Pico, the ESP8266 family, Pi Zero and Pi 5. Data processing, "
               "signals and images are the areas I dig into.",
        "skills_note": "self-assessed",
        "skill_items": [
            {"k": "PYTHON", "pct": 80},
            {"k": "C / C++ / ARDUINO / EMBEDDED C", "pct": 60},
            {"k": "PHP", "pct": 40},
        ],
        "tools": "FLASK · FASTAPI · uv · SQL · GIT · DOCKER (A BIT)",
        "boards_items": ["ESP32 — MAIN BOARD", "ARDUINO", "RASPBERRY PI PICO",
                         "ESP8266 FAMILY", "RASPBERRY PI ZERO", "RASPBERRY PI 5"],
        "exp_role": "FREELANCE DEVELOPER · PARSCODERS",
        "exp_dur": "6 YEARS",
        "exp_note": "client software projects, IoT prototypes and data tooling",
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
        "lang_other": "EN", "theme_dark": "\u062a\u06cc\u0631\u0647", "theme_light": "\u0631\u0648\u0634\u0646",
        "site": "\u0633\u06cc\u0646\u067e\u0633", "name": "\u0645\u062d\u0645\u062f\u0631\u0636\u0627 \u0639\u0628\u0627\u062f\u0627\u0644\u0647",
        "role": "\u0645\u0647\u0646\u062f\u0633 \u06a9\u0627\u0645\u067e\u06cc\u0648\u062a\u0631 \u00b7 \u0627\u06cc\u0646\u062a\u0631\u0646\u062a \u0627\u0634\u06cc\u0627 / \u0633\u06cc\u0633\u062a\u0645\u200c\u0647\u0627\u06cc \u0646\u0647\u0641\u062a\u0647 / \u0633\u06cc\u06af\u0646\u0627\u0644 \u0648 \u062a\u0635\u0648\u06cc\u0631",
        "ssh_line": "\u0646\u0633\u062e\u0647\u0654 \u062a\u0631\u0645\u06cc\u0646\u0627\u0644\u06cc \u0647\u0645\u06cc\u0646 \u0633\u0627\u06cc\u062a: ssh ebad84@{host} -p {port}",
        "sec_about": "\u062f\u0631\u0628\u0627\u0631\u0647\u0654 \u0645\u0646", "sec_skills": "\u0645\u0647\u0627\u0631\u062a\u200c\u0647\u0627", "sec_boards": "\u0628\u0631\u062f\u0647\u0627",
        "sec_exp": "\u062a\u062c\u0631\u0628\u0647", "sec_projects": "\u067e\u0631\u0648\u0698\u0647\u200c\u0647\u0627", "sec_links": "\u0627\u0631\u062a\u0628\u0627\u0637",
        "bio": "\u0645\u0647\u0646\u062f\u0633 \u06a9\u0627\u0645\u067e\u06cc\u0648\u062a\u0631\u0645 \u0648 \u0627\u0632 \u0633\u0627\u062e\u062a\u0646 \u0686\u06cc\u0632\u0647\u0627 \u0644\u0630\u062a \u0645\u06cc\u200c\u0628\u0631\u0645 \u2014 \u0642\u0637\u0639\u0627\u062a \u0627\u0644\u06a9\u062a\u0631\u0648\u0646\u06cc\u06a9\u06cc\u060c \u062f\u0633\u062a\u06af\u0627\u0647 \u0648 \u0627\u06cc\u0646\u062a\u0631\u0646\u062a \u0627\u0634\u06cc\u0627. \u0628\u0631\u062f \u0627\u0635\u0644\u06cc\u200c\u0627\u0645 ESP32 \u0627\u0633\u062a\u061b \u0628\u0627 \u0622\u0631\u062f\u0648\u06cc\u0646\u0648\u060c \u0631\u0632\u0628\u0631\u06cc\u200c\u067e\u0627\u06cc \u067e\u06cc\u06a9\u0648\u060c \u062e\u0627\u0646\u0648\u0627\u062f\u0647\u0654 ESP8266\u060c \u0631\u0632\u0628\u0631\u06cc\u200c\u067e\u0627\u06cc \u0632\u06cc\u0631\u0648 \u0648 \u0631\u0632\u0628\u0631\u06cc\u200c\u067e\u0627\u06cc 5 \u0647\u0645 \u06a9\u0627\u0631 \u06a9\u0631\u062f\u0647\u200c\u0627\u0645. \u067e\u0631\u062f\u0627\u0632\u0634 \u062f\u0627\u062f\u0647\u060c \u0633\u06cc\u06af\u0646\u0627\u0644 \u0648 \u062a\u0635\u0648\u06cc\u0631 \u0647\u0645 \u062d\u0648\u0632\u0647\u200c\u0647\u0627\u06cc\u06cc \u0647\u0633\u062a\u0646\u062f \u06a9\u0647 \u062f\u0631 \u0622\u0646\u200c\u0647\u0627 \u06a9\u0627\u0648\u0634 \u0645\u06cc\u200c\u06a9\u0646\u0645.",
        "skills_note": "\u0628\u0631\u0622\u0648\u0631\u062f \u0634\u062e\u0635\u06cc",
        "skill_items": [
            {"k": "\u067e\u0627\u06cc\u062a\u0648\u0646", "pct": 80},
            {"k": "C / C++ / \u0622\u0631\u062f\u0648\u06cc\u0646\u0648 / EMBEDDED C", "pct": 60},
            {"k": "PHP", "pct": 40},
        ],
        "tools": "\u0641\u0644\u0633\u06a9 \u00b7 \u0641\u0633\u062a\u200c\u0627\u06cc\u200c\u067e\u06cc\u200c\u0622\u06cc \u00b7 uv \u00b7 \u0627\u0633\u200c\u06a9\u06cc\u0648\u0644 \u00b7 \u06af\u06cc\u062a \u00b7 \u062f\u0627\u06a9\u0631 (\u06a9\u0645\u06cc)",
        "boards_items": ["ESP32 \u2014 \u0628\u0631\u062f \u0627\u0635\u0644\u06cc", "\u0622\u0631\u062f\u0648\u06cc\u0646\u0648", "\u0631\u0632\u0628\u0631\u06cc \u067e\u0627\u06cc \u067e\u06cc\u06a9\u0648",
                         "\u062e\u0627\u0646\u0648\u0627\u062f\u0647\u0654 ESP8266", "\u0631\u0632\u0628\u0631\u06cc \u067e\u0627\u06cc \u0632\u06cc\u0631\u0648", "\u0631\u0632\u0628\u0631\u06cc \u067e\u0627\u06cc 5"],
        "exp_role": "\u062a\u0648\u0633\u0639\u0647\u200c\u062f\u0647\u0646\u062f\u0647\u0654 \u0641\u0631\u06cc\u0644\u0646\u0633\u0631 \u00b7 \u067e\u0627\u0631\u0633\u200c\u06a9\u062f\u0631\u0632",
        "exp_dur": "\u06f6 \u0633\u0627\u0644",
        "exp_note": "\u067e\u0631\u0648\u0698\u0647\u200c\u0647\u0627\u06cc \u0646\u0631\u0645\u200c\u0627\u0641\u0632\u0627\u0631\u06cc \u0645\u0634\u062a\u0631\u06cc\u060c \u0646\u0645\u0648\u0646\u0647\u200c\u0633\u0627\u0632\u06cc IoT \u0648 \u0627\u0628\u0632\u0627\u0631\u0647\u0627\u06cc \u062f\u0627\u062f\u0647",
        "proj_loading": "\u062f\u0631 \u062d\u0627\u0644 \u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc \u067e\u0631\u0648\u0698\u0647\u200c\u0647\u0627\u2026",
        "links_note": "\u062f\u0631 \u0647\u0645\u0647\u200c\u062c\u0627 \u0647\u0645\u06cc\u0646 \u0646\u0627\u0645 \u06a9\u0627\u0631\u0628\u0631\u06cc",
        "more_link": "\u0628\u06cc\u0634\u062a\u0631 \u2190", "more_title": "\u0628\u06cc\u0634\u062a\u0631 / \u0633\u06cc\u0633\u062a\u0645",
        "sec_system": "\u0633\u06cc\u0633\u062a\u0645 / \u0639\u0627\u0645\u0644", "os_line": "\u0648\u06cc\u0646\u062f\u0648\u0632 \u2014 \u0633\u06cc\u0633\u062a\u0645 \u0627\u0635\u0644\u06cc \u00b7 \u0627\u0648\u0628\u0648\u0646\u062a\u0648 \u06af\u0646\u0648\u0645 \u2014 \u062e\u0627\u0646\u0647\u0654 \u062f\u0648\u0645",
        "sec_term": "\u062a\u0631\u0645\u06cc\u0646\u0627\u0644", "term_line": "ghostty \u2014 \u0647\u0645\u0647\u200c\u062c\u0627",
        "sec_tools": "\u0627\u0628\u0632\u0627\u0631\u0647\u0627", "tools_line": "\u06af\u06cc\u062a \u00b7 \u062f\u0627\u06a9\u0631 (\u06a9\u0645\u06cc) \u00b7 uv \u00b7 \u0627\u0633\u200c\u06a9\u06cc\u0648\u0644 \u00b7 \u062f\u0631 \u062d\u0627\u0644 \u06cc\u0627\u062f\u06af\u06cc\u0631\u06cc \u067e\u0633\u062a\u06af\u0631\u0633",
        "sec_devops": "\u062f\u0648\u0627\u067e\u0633", "devops_line": "\u0639\u0644\u0627\u0642\u0647\u200c\u0645\u0646\u062f \u2014 CI/CD\u060c \u06a9\u0627\u0646\u062a\u06cc\u0646\u0631\u0647\u0627\u060c \u0628\u0627\u06a9\u0633\u200c\u0647\u0627\u06cc \u0644\u06cc\u0646\u0648\u06a9\u0633",
        "sec_making": "\u0633\u0627\u062e\u062a", "making_line": "\u062f\u06cc\u062a\u0627\u0644\u0627\u06af\u0631 \u00b7 \u0633\u0646\u0633\u0648\u0631 \u0647\u0648\u0634\u0645\u0646\u062f \u00b7 \u0647\u0648\u0634\u0645\u0646\u062f\u0633\u0627\u0632\u06cc \u062e\u0627\u0646\u0647 \u00b7 \u0631\u0628\u0627\u062a\u06cc\u06a9 \u00b7 \u067e\u0631\u06cc\u0646\u062a\u0631 \u0633\u0647\u200c\u0628\u0639\u062f\u06cc",
        "sec_site": "\u0627\u06cc\u0646 \u0633\u0627\u06cc\u062a", "site_line": "\u0641\u0644\u0633\u06a9 + \u06cc\u06a9 \u0641\u0627\u06cc\u0644 css \u2014 \u0628\u062f\u0648\u0646 \u06a9\u062a\u0627\u0628\u062e\u0627\u0646\u0647\u0654 \u062c\u0627\u0648\u0627\u0627\u0633\u06a9\u0631\u06cc\u067e\u062a \u0648 \u0628\u062f\u0648\u0646 CDN",
        "foot": "\u00a9 \u06f2\u06f0\u06f2\u06f6 \u0645\u062d\u0645\u062f\u0631\u0636\u0627 \u0639\u0628\u0627\u062f\u0627\u0644\u0647 \u2014 \u0633\u06cc\u0646\u067e\u0633",
    },
}


@app.route("/")
def index():
    return page("en")


@app.route("/<lang>")
def page(lang):
    if lang not in I18N:
        abort(404)
    host = request.host.split(":")[0]
    return render_template(
        "index.html", lang=lang, t=I18N[lang], rtl=(lang == "fa"),
        host=host, ssh_port=SSH_PORT,
        has_profile=(BASE / "static" / "profile.jpg").exists(),
    )


@app.route("/more")
def more_en():
    return _more("en")


@app.route("/fa/more")
def more_fa():
    return _more("fa")


def _more(lang):
    host = request.host.split(":")[0]
    return render_template("more.html", lang=lang, t=I18N[lang], rtl=(lang == "fa"),
                           host=host, ssh_port=SSH_PORT)


@app.route("/api/projects")
def api_projects():
    return jsonify({"projects": load_projects()})


@app.route("/teapot")
def teapot():
    lang = request.args.get("lang", "en")
    return render_template("teapot.html", lang=lang if lang in I18N else "en"), 418


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
