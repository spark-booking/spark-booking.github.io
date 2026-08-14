"""
Generates static redirect pages that force Microsoft Edge to open on
BYOD devices for internal Walmart room-booking links.

Why this exists: Zoom Rooms' QR generator requires a normal https://
URL, but the only way to force a specific browser (Edge) regardless of
a phone's default browser is the microsoft-edge-https:// custom
scheme. Browsers won't let a plain https:// link auto-hijack into a
different app, so we need a real, publicly-reachable https:// page
(this one, on GitHub Pages) that hands off to Edge once loaded.

To add a new room: add its slug to ROOM_SLUGS below, run this script,
commit, and push. GitHub Pages picks up the change automatically.
"""
from pathlib import Path

APP_HOST = "ai-innovation-lab-app-ebbdbdbfaecdbeba.walmart.com"
ROOM_SLUGS = ["w2281", "w2282", "w2367"]

OUTPUT_DIR = Path(__file__).parent.parent

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Opening Room {slug}...</title>
<meta http-equiv="refresh" content="0; url={edge_url}">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 100vh; margin: 0;
    background: #f7f7f7; text-align: center; padding: 24px;
    box-sizing: border-box;
  }}
  h1 {{ font-size: 1.25rem; color: #1a1a1a; margin-bottom: 8px; }}
  p {{ color: #555; font-size: 0.95rem; margin: 4px 0 24px; }}
  a.btn {{
    display: inline-block; background: #0071ce; color: #fff;
    text-decoration: none; font-weight: 700; padding: 16px 32px;
    border-radius: 12px; font-size: 1rem; margin-bottom: 16px;
  }}
  a.fallback {{ color: #0071ce; font-size: 0.85rem; }}
</style>
</head>
<body>
  <h1>Opening Room {slug} in Microsoft Edge&hellip;</h1>
  <p>If nothing happens, tap the button below.</p>
  <a class="btn" href="{edge_url}">Open in Microsoft Edge</a>
  <a class="fallback" href="{https_url}">Don't have Edge? Open normally instead</a>
  <script>
    // Some mobile browsers block scheme navigation without a user
    // gesture -- the meta-refresh above covers the ones that allow
    // it; this covers the ones needing a JS-triggered nudge.
    window.location.href = "{edge_url}";
  </script>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Room Booking -- Edge Redirects</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 480px;
          margin: 40px auto; padding: 0 20px; color: #1a1a1a; }}
  a {{ display: block; padding: 14px; margin-bottom: 10px;
       background: #f0f0f0; border-radius: 10px; color: #0071ce;
       text-decoration: none; font-weight: 600; }}
</style>
</head>
<body>
  <h1>Room Booking -- Force Edge Redirects</h1>
  <p>Internal use: these links force Microsoft Edge on BYOD devices.</p>
  {links}
</body>
</html>
"""


def build():
    links_html = []
    for slug in ROOM_SLUGS:
        https_url = f"https://{APP_HOST}/room/{slug}"
        edge_url  = f"microsoft-edge-https://{APP_HOST}/room/{slug}"

        page = PAGE_TEMPLATE.format(slug=slug, edge_url=edge_url, https_url=https_url)
        (OUTPUT_DIR / f"{slug}.html").write_text(page)
        links_html.append(f'  <a href="{slug}.html">Room {slug}</a>')

    index = INDEX_TEMPLATE.format(links="\n".join(links_html))
    (OUTPUT_DIR / "index.html").write_text(index)

    print(f"Generated {len(ROOM_SLUGS)} room pages + index.html in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
