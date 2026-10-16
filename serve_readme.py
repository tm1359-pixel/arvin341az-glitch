"""
Minimal dev server: renders README.md to HTML and serves it on port 3000.
Re-reads the file on every request so edits appear immediately.
"""
import html
import http.server
import os
import re
import socketserver
import markdown

PORT = int(os.environ.get("PORT", "3000"))
ROOT = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Profile README Preview</title>
<style>
  :root {
    --bg: #0d1117;
    --fg: #e6edf3;
    --border: #30363d;
    --link: #58a6ff;
    --code-bg: #161b22;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
  }
  .container {
    max-width: 980px;
    margin: 0 auto;
    padding: 32px 24px 64px;
  }
  a { color: var(--link); text-decoration: none; }
  a:hover { text-decoration: underline; }
  img { max-width: 100%; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
  }
  th, td {
    border: 1px solid var(--border);
    padding: 8px 12px;
    text-align: left;
  }
  code {
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
  }
  pre {
    background: var(--code-bg);
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
  }
  pre code { background: none; padding: 0; }
  hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
  }
  blockquote {
    border-left: 4px solid var(--border);
    margin: 16px 0;
    padding: 0 16px;
    color: #8b949e;
  }
  h1, h2, h3 { border-bottom: 1px solid var(--border); padding-bottom: 8px; }
  /* GitHub README allows raw HTML alignment attrs */
  [align="center"] { text-align: center; }
  [align="right"] { float: right; margin-left: 16px; }
  [align="absmiddle"] { vertical-align: middle; }
</style>
</head>
<body>
<div class="container">
__BODY__
</div>
</body>
</html>"""


def render_readme() -> str:
    path = os.path.join(ROOT, "README.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "attr_list", "md_in_html", "sane_lists"],
    )
    return TEMPLATE.replace("__BODY__", body)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/index.html":
            html_content = render_readme()
            data = html_content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # serve files from assets/ and root
        safe_path = os.path.normpath(path.lstrip("/"))
        if safe_path.startswith(".."):
            self.send_error(403)
            return
        full = os.path.join(ROOT, safe_path)
        if os.path.isfile(full):
            self._serve_file(full)
        else:
            self.send_error(404)

    def _serve_file(self, full):
        ext = os.path.splitext(full)[1].lower()
        ct = {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".css": "text/css",
            ".js": "application/javascript",
        }.get(ext, "application/octet-stream")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass  # quiet


class ReuseTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with ReuseTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving README on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
