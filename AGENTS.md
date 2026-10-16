# Base44 Dev Environment

## What this repo is

A GitHub profile README repository (`README.md` + `assets/` SVG/PNG files). There is no application server, frontend framework, or backend — the README is designed to render on a GitHub profile page.

## How it runs in Base44

`serve_readme.py` is a minimal Python dev server that renders `README.md` to HTML on each request and serves it on port 3000, alongside static files from `assets/`. It re-reads the file every request, so edits to `README.md` or assets appear immediately without a restart.

- **Compose:** `docker compose -f docker-compose.base44.yml up -d`
- **Preview:** http://localhost:3000
- **No secrets required** — all content is local or references external image URLs.
- **No build step** — `pip install markdown` runs at container startup.
