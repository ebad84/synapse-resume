#!/usr/bin/env python3
# SYNAPSE SSH TUI — the resume site as a minimal interactive terminal.
#
#   run:      python ssh_server.py            (binds 0.0.0.0:22 by default)
#   login:    NONE — terminal.shop style:  ssh <host>  and the content
#             is just there (auth "none" is accepted for everyone).
#
#   layout:   [ Synapse ASCII logo + name + icon/link strip ]  <- fixed header
#             [ content pane of the section ]
#             [ nav bar ]                                      <- fixed footer
#
#   keys:     1-5  switch section (ABOUT / INTERESTS / PROJECTS / EXPERIENCE / LINKS)
#             N    in PROJECTS: open project N
#             B    back to the project list
#             ?    help
#             418  i'm a teapot
#             Q    quit / disconnect
#
import json
import os
import socket
import sys
import threading
from pathlib import Path

import paramiko

BASE = Path(__file__).resolve().parent
HOST_KEY_PATH = BASE / "data" / "host.key"
PASSWORD = os.environ.get("SYNAPSE_PASS", "synapse")
PORT = int(os.environ.get("SYNAPSE_PORT", "22"))
HOST = os.environ.get("SYNAPSE_HOST", "0.0.0.0")
WEB_URL = os.environ.get("SYNAPSE_WEB", "http://localhost:5000")

CLEAR = "\x1b[2J\x1b[H"
NAV_BAR = "  [1] ABOUT   [2] INTERESTS   [3] PROJECTS   [4] EXPERIENCE   [5] LINKS     (Q)UIT"

# fallback logo (hand-made) — used only if data/ascii_logo.txt is missing
FALLBACK_LOGO = """        \u2588  \u2588 \u2588\u2588      \u2588
         \u2588\u2588\u2588\u2588         \u2588\u2588
            \u2588       \u2588
    \u2588        \u2588      \u2588\u2588\u2588\u2588
   \u2588\u2588        \u2588\u2588    \u2588
 \u2588\u2588\u2588 \u2588\u2588     \u2588\u2588\u2588\u2588\u2588\u2588\u2588
       \u2588\u2588\u2588\u2588\u2588 \u2588 \u2588 \u2588 \u2588
          \u2588\u2588 \u2588   \u2588 \u2588\u2588           \u2588\u2588\u2588     \u2588
          \u2588\u2588 \u2588   \u2588 \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588  \u2588\u2588   \u2588   \u2588  \u2588\u2588
        \u2588\u2588\u2588\u2588 \u2588 \u2588 \u2588 \u2588\u2588       \u2588\u2588      \u2588\u2588\u2588
  \u2588   \u2588\u2588   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588
  \u2588\u2588\u2588\u2588       \u2588\u2588   \u2588\u2588
    \u2588        \u2588      \u2588\u2588\u2588\u2588
    \u2588       \u2588       \u2588\u2588   \u2588
         \u2588\u2588 \u2588\u2588     \u2588  \u2588\u2588
           \u2588\u2588 \u2588"""


def load_projects():
    try:
        data = json.loads((BASE / "projects.json").read_text(encoding="utf-8"))
        return data.get("projects", [])
    except Exception:
        return []


def ascii_logo():
    p = BASE / "data" / "ascii_logo.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").rstrip("\n")
    return FALLBACK_LOGO


def banner_links():
    p = BASE / "data" / "banner_links.txt"
    if p.exists():
        lines = [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]
        lines = [ln for ln in lines if ln.strip()]
        if lines:
            return lines
    return ["  t.me/ebad84 · github.com/ebad84 · linkedin.com/in/ebad84"]


ABOUT = """\
  MOHAMMAD REZA EBADOLLAH
  COMPUTER ENGINEER · IOT / EMBEDDED / SIGNAL + IMAGE

  I like to build things: electronics, devices, and the internet
  of things. My main board is the ESP32; I also work with Arduino,
  Raspberry Pi Pico, the ESP8266 family, Pi Zero and Pi 5.

  SOFTWARE
    PYTHON 80% · C/C++/ARDUINO/EMBEDDED C 60% · PHP 40%
    FLASK · FASTAPI · uv · SQL · GIT · DOCKER (a bit)
    learning POSTGRESQL · interested in DEVOPS

  SYSTEM
    WINDOWS (daily driver) · UBUNTU GNOME · GHOSTTY

  THIS SITE
    web: {web}   ssh: you are here — no login, just like that
    press ? for help · type 418 for a surprise"""

INTERESTS = """\
  ELECTRONICS COMPONENTS     DATALOGGERS
  IOT                       SMART SENSORS
  DATA PROCESSING           HOME AUTOMATION
  SIGNAL + IMAGE ANALYSIS   ROBOTICS
                            3D PRINTING"""

EXPERIENCE = """\
  FREELANCE DEVELOPER — PARSCODERS
  6 YEARS

  client software projects, IoT prototypes and data tooling."""

LINKS = """\
  GITHUB     https://github.com/ebad84
  LINKEDIN   https://linkedin.com/in/ebad84
  TELEGRAM   https://t.me/ebad84

  WEB        {web}"""

HELP = """\
  KEYS
    1-5       switch section (about / interests / projects / experience / links)
    NUMBER    in PROJECTS: open that project
    B         in a project: back to the list
    ?         this help
    418       i'm a teapot
    Q         quit / disconnect"""

TEAPOT = r"""        .---.
       /_____\
      (  o o  )    418 — I'M A TEAPOT
       '-\_-/'
         ( )
    RFC 2324 · SHORT AND STOUT
   (any key to continue)"""


def projects_list_block(projects):
    lines = [f"  {i:>2}. {p['title']['en']}" for i, p in enumerate(projects, 1)]
    lines += ["", "  press a number to open a project · B to go back"]
    return "\n".join(lines)


def project_detail(p):
    title = p["title"]["en"]
    return "\n".join([
        f"  {title}",
        "  " + "-" * min(56, max(4, len(title))),
        "",
        "  " + p["desc"]["en"].replace("\n", "\n  "),
        "",
        "  TAGS  " + " · ".join(p.get("tags", [])),
        "  LINK  " + (p.get("link") or "none"),
        "  IMAGE " + ("static/projects/" + p["image"] if p.get("image") else "none"),
        "",
        "  B — back to project list",
    ])


class Tui:
    SECTIONS = ["about", "interests", "projects", "experience", "links"]

    def __init__(self, chan, projects, width=80, height=24):
        self.chan = chan
        self.projects = projects
        self.width, self.height = width, height
        self.section = "about"
        self.project = None
        self.overlay = None
        self.buf = []
        self.logo = ascii_logo().split("\n")
        self.links = banner_links()
        self.body = {
            "about": ABOUT.format(web=WEB_URL),
            "interests": INTERESTS,
            "projects": projects_list_block(projects),
            "experience": EXPERIENCE,
            "links": LINKS.format(web=WEB_URL),
        }

    def send(self, s):
        try:
            self.chan.send(s)
        except Exception:
            pass

    def render(self):
        w, h = self.width, self.height
        logo_h = len(self.logo)
        links_h = len(self.links)
        full_header_h = logo_h + links_h + 2   # logo + name + link strip + rule
        footer_h = 3
        if h < full_header_h + footer_h + 10:
            header_h = 3   # small terminal: name + links + rule
        else:
            header_h = full_header_h
        avail = max(4, h - header_h - footer_h - 1)

        if self.overlay is not None:
            body = self.overlay
        elif self.project is not None:
            body = project_detail(self.projects[self.project])
        else:
            body = self.body[self.section]
        lines = body.split("\n")
        shown = lines[:avail]
        if len(lines) > avail:
            shown.append("  ... (terminal too short for this section)")

        out = [CLEAR]
        if header_h == 3:
            out.append("  SYNAPSE — MOHAMMAD REZA EBADOLLAH".ljust(w))
            out.append("  t.me/ebad84 · github.com/ebad84 · linkedin.com/in/ebad84".ljust(w))
            out.append("=" * w)
        else:
            out += [("  " + ln).ljust(w) for ln in self.logo]
            out.append("  MOHAMMAD REZA EBADOLLAH — SYNAPSE TUI".ljust(w))
            out += [("  " + ln).ljust(w) for ln in self.links]
            out.append("=" * w)
        out += [ln.ljust(w) for ln in shown]
        out += [""] * (avail - len(shown))
        out.append("=" * w)
        out.append(NAV_BAR.ljust(w))
        out.append(("> " + "".join(self.buf)).ljust(w))
        self.send("\r\n".join(out) + "\r\n")

    def handle(self, c):
        if c.lower() == "q":
            self.send("\r\nBYE — SYNAPSE OUT. (web: " + WEB_URL + ")\r\n")
            return False
        if self.overlay is not None:
            self.overlay = None
            self.buf = []
            return True
        self.buf.append(c)
        self.buf = self.buf[-3:]
        if "".join(self.buf) == "418":
            self.overlay = TEAPOT
            return True
        if c == "?":
            self.overlay = HELP
            return True
        if self.project is not None:
            if c.lower() == "b":
                self.project = None
            elif c.isdigit() and 1 <= int(c) <= len(self.projects):
                self.project = int(c) - 1
            return True
        if c.isdigit():
            n = int(c)
            if self.section == "projects" and 1 <= n <= len(self.projects):
                self.project = n - 1
            elif 1 <= n <= 5:
                self.section = self.SECTIONS[n - 1]
        return True

    def run(self):
        self.chan.settimeout(0.4)
        self.render()
        threading.Timer(0.8, self.render).start()  # re-render once pty size arrives
        while True:
            try:
                data = self.chan.recv(1)
            except socket.timeout:
                continue
            except Exception:
                break
            if not data:
                break
            ch = data.decode("utf-8", "ignore")
            if not ch or not ch.isprintable():
                continue
            if not self.handle(ch):
                break
            self.render()
        try:
            self.chan.close()
        except Exception:
            pass


class SynapseServer(paramiko.ServerInterface):
    def __init__(self):
        self.width, self.height = 80, 24

    # terminal.shop style: NO LOGIN — anyone connects, zero prompts
    def get_allowed_auths(self, username):
        return "none,password"

    def check_auth_none(self, username):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL if password == PASSWORD else paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pw, ph, modes):
        self.width, self.height = width, height
        return True

    def check_channel_shell_request(self, channel):
        return True

    def check_window_change_request(self, channel, width, height, pw, ph):
        self.width, self.height = width, height
        return True


def get_host_key():
    if HOST_KEY_PATH.exists():
        return paramiko.RSAKey(filename=str(HOST_KEY_PATH))
    HOST_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(str(HOST_KEY_PATH))
    return key


def handle_connection(conn, addr):
    transport = paramiko.Transport(conn)
    transport.add_server_key(get_host_key())
    server = SynapseServer()
    try:
        transport.start_server(server=server)
        chan = transport.accept(15)
        if chan is None:
            return
        tui = Tui(chan, load_projects())
        # wait briefly for the client's pty request so the first frame
        # is rendered with the real terminal size (~1.5s max)
        for _ in range(30):
            if (server.width, server.height) != (80, 24):
                break
            threading.Event().wait(0.05)
        tui.width, tui.height = server.width, server.height
        tui.run()
    except Exception as exc:
        sys.stderr.write("[synapse] %s: %s\n" % (addr, exc))
    finally:
        transport.close()


def run_server(host=HOST, port=PORT, stop_event=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
    except OSError as exc:
        print("[synapse] could not bind %s:%s — %s" % (host, port, exc))
        print("[synapse] port 22 needs admin rights; try:  SYNAPSE_PORT=2222 python ssh_server.py")
        raise
    sock.listen(8)
    sock.settimeout(1.0)
    hint = "ssh %s" % host if port == 22 else "ssh %s -p %s" % (host, port)
    print("[synapse] terminal twin ready — %s  (no login needed)" % hint)
    try:
        while True:
            if stop_event is not None and stop_event.is_set():
                break
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()
    finally:
        sock.close()


if __name__ == "__main__":
    run_server()
