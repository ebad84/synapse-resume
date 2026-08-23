#!/usr/bin/env python3
"""SYNAPSE — minimal Flask resume site (EN default, FA with full RTL)."""
import json
import os
from pathlib import Path

from flask import Flask, render_template, jsonify, request, abort

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
SSH_PORT = os.environ.get("SYNAPSE_PORT", "22")


def ssh_hint(host):
    if SSH_PORT == "22":
        return "ssh %s" % host
    return "ssh %s -p %s" % (host, SSH_PORT)


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
        "ssh_line": "TERMINAL TWIN · {hint} · NO LOGIN NEEDED",
        "sec_about": "ABOUT", "sec_skills": "SKILLS", "sec_boards": "BOARDS",
        "sec_exp": "EXPERIENCE", "sec_projects": "PROJECTS", "sec_links": "CONTACT",
        "bio": "Computer engineer who likes to build things — electronics, devices and the "
               "internet of things. My main board is the ESP32; I have also worked with Arduino, "
               "Raspberry Pi Pico, the ESP8266 family, Pi Zero and Pi 5. Data logging/processing, "
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
        "exp_items": [
            {"role": "FREELANCE DEVELOPER · PARSCODERS", "dur": "6 YEARS", "note": "client software projects, IoT prototypes and data tooling"},
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
            {"role": "توسعه‌دهندهٔ فریلنسر · پارس‌کدرز", "dur": "۶ سال", "note": "پروژه‌های نرم‌افزاری مشتری، نمونه‌سازی IoT و ابزارهای داده"},
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
        ssh_hint=ssh_hint(host),
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
                           ssh_hint=ssh_hint(host))


@app.route("/api/projects")
def api_projects():
    return jsonify({"projects": load_projects()})


@app.route("/teapot")
def teapot():
    lang = request.args.get("lang", "en")
    return render_template("teapot.html", lang=lang if lang in I18N else "en"), 418


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)