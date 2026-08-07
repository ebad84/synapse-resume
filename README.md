# SYNAPSE — resume site (Flask) + SSH terminal twin

Minimal monochrome engineering-style resume site for Mohammad Reza Ebadollah,
with a second face: an interactive SSH terminal version of the same content.

## quick start (web)

    uv venv
    uv pip install -r requirements.txt
    uv run python app.py          # → http://127.0.0.1:5000

or with plain python:

    python -m venv .venv
    .venv/bin/pip install -r requirements.txt   # windows: .venv\Scripts\pip
    .venv/bin/python app.py

## ssh terminal version

    uv run python ssh_server.py   # binds 0.0.0.0:2222

connect from another machine:

    ssh ebad84@<your-ip> -p 2222

    password: synapse   (change it:  export SYNAPSE_PASS=yourpass)

inside the tui:  1-5 switch sections · digits open a project · B back ·
? help · Q quit · typing 418 shows the teapot (easter egg).
The Synapse ASCII logo is generated from static/synapse.png.

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

    SYNAPSE_PORT / SYNAPSE_PASS / SYNAPSE_HOST   env vars for the ssh server
    PORT                                         env var for the web server
    static/profile.jpg                           replace the profile photo
    the ssh hint in the site header shows your own host automatically

## notes

- Windows: allow the app through the firewall when prompted (port 2222).
- The ssh host key is generated once at data/host.key — keep it so your
  clients don't get a changed-key warning.
- No external fonts/CDNs — the site works fully offline.
