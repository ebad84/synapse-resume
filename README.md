# SYNAPSE — resume site (Flask) + SSH terminal twin

Minimal monochrome engineering-style resume site for Mohammad Reza Ebadollah,
with a second face: an interactive SSH terminal version of the same content —
login-free, terminal.shop style.

## quick start (web)

    uv venv
    uv pip install -r requirements.txt
    uv run python app.py          # → http://127.0.0.1:5000

or with plain python:

    python -m venv .venv
    .venv/bin/pip install -r requirements.txt   # windows: .venv\Scripts\pip
    .venv/bin/python app.py

## ssh terminal version — NO LOGIN (terminal.shop style)

    uv run python ssh_server.py   # listens on port 22 by default

visitors just type:

    ssh <your-domain-or-ip>

no username, no password — the resume TUI appears immediately:
Synapse ASCII logo (rendered from static/synapse.png), telegram/github/
linkedin icons + links, sections 1-5, project drill-down, and the
418 teapot easter egg.

notes:
- port 22 needs admin rights on linux — run with sudo, or:
      export SYNAPSE_PORT=2222
  and visitors use:  ssh <host> -p 2222
- windows: allow the app through the firewall when prompted.
- the ssh host key is generated once at data/host.key — keep it so your
  clients don't get a changed-key warning.
- ascii logo: rendered from static/synapse.png into data/ascii_logo.txt;
  if that file is missing, a built-in hand-made fallback art is shown.
- the website shows a matching hint in its header ("ssh <host> · no login").

## edit your projects (no code needed)

Edit `projects.json`. Each entry:

    {
      "id": "my-project",
      "title": {"en": "...", "fa": "..."},
      "desc":  {"en": "...", "fa": "..."},
      "tags": ["ESP32", "MQTT"],
      "link": "https://github.com/ebad84/...",   <- optional, any url
      "image": "photo.jpg"                       <- optional: drop the file in
    }                                               static/projects/ and set the name

Projects without a github link are fine — description + optional photo carry
the story (photo shows in the web grid; SSH shows its filename).

## customize

    SYNAPSE_PORT / SYNAPSE_HOST   env vars for the ssh server
    PORT                          env var for the web server
    static/profile.jpg            replace the profile photo
    the circuit-board background lives in static/style.css (inline SVG)

## notes

- No external fonts/CDNs — the site works fully offline.
- The web contact icons are static/icon-tg.svg / icon-gh.svg / icon-in.svg.
