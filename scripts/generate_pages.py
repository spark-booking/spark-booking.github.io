"""
Generates static redirect pages that force the correct managed browser
to open on BYOD devices for internal Walmart room-booking links.

Why this exists: Zoom Rooms' QR generator requires a normal https://
URL, but plain https:// links can't force a specific app to open --
each platform needs its own trick, and BYOD devices don't all use the
same corporate-tunnel browser:

  - iOS:     Edge is the tunneled browser -> microsoft-edge-https://
  - Android: the tunneled browser is the "Web" app (Workspace ONE Web)
             -> Android intent:// URI targeting its package, which
             falls back to a plain https:// link if the app isn't
             installed (S.browser_fallback_url).

Browsers won't let a plain https:// link auto-hijack into a different
app, so we need a real, publicly-reachable https:// page (this one, on
GitHub Pages) that detects the platform client-side and hands off
accordingly.

KNOWN UNCONFIRMED VALUE: ANDROID_WEB_APP_PACKAGE below is a best guess
(VMware Workspace ONE Web, commonly just labeled "Web" in the app
drawer) -- not yet confirmed against the actual app on a real device.
Confirm via Settings > Apps > Web > App details > look for the
package/App ID, then update the constant below.

Also unconfirmed: whether Android's Work Profile / Personal Profile
split affects intent resolution when the QR is scanned from the
personal-profile camera app. If the "Web" app only lives in the Work
Profile, this intent link may not cross into it -- needs testing on a
real BYOD device before wide rollout.

To add a new room: add its slug to ROOM_SLUGS below, run this script,
commit, and push. GitHub Pages picks up the change automatically.
"""
from pathlib import Path
from urllib.parse import quote

APP_HOST = "ai-innovation-lab-app-ebbdbdbfaecdbeba.walmart.com"
ROOM_SLUGS = ["w2281", "w2282", "w2367"]

# BEST GUESS -- NOT YET CONFIRMED. See module docstring.
ANDROID_WEB_APP_PACKAGE = "com.vmware.browser"

OUTPUT_DIR = Path(__file__).parent.parent

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Opening Room {slug}...</title>
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
  <h1 id="heading">Opening Room {slug}&hellip;</h1>
  <p>If nothing happens, tap the button below.</p>
  <a class="btn" id="launch-btn" href="{https_url}">Open Room {slug}</a>
  <a class="fallback" href="{https_url}">Having trouble? Open normally instead</a>
  <script>
    // Force the corporate-tunnel browser based on platform, since
    // BYOD devices route Walmart apps through different apps per OS:
    //   iOS     -> Microsoft Edge     (microsoft-edge-https:// scheme)
    //   Android -> "Web" app          (intent:// URI, package-targeted)
    // Anything else (desktop, etc.) just uses the plain https:// link
    // already set as the default href above.
    (function () {{
      var ua = navigator.userAgent || "";
      var isIOS = /iPhone|iPad|iPod/.test(ua);
      var isAndroid = /Android/.test(ua);
      var heading = document.getElementById("heading");
      var btn = document.getElementById("launch-btn");
      var targetUrl = null;

      if (isIOS) {{
        targetUrl = "{edge_url}";
        heading.textContent = "Opening Room {slug} in Microsoft Edge\\u2026";
        btn.textContent = "Open in Microsoft Edge";
      }} else if (isAndroid) {{
        targetUrl = "{android_intent_url}";
        heading.textContent = "Opening Room {slug} in Web\\u2026";
        btn.textContent = "Open in Web";
      }}

      if (targetUrl) {{
        btn.href = targetUrl;
        // Some mobile browsers block scheme/intent navigation without
        // a user gesture -- this covers the ones that allow it
        // automatically; the button covers the ones that don't.
        window.location.href = targetUrl;
      }}
    }})();
  </script>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Room Booking -- Managed Browser Redirects</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 480px;
          margin: 40px auto; padding: 0 20px; color: #1a1a1a; }}
  a {{ display: block; padding: 14px; margin-bottom: 10px;
       background: #f0f0f0; border-radius: 10px; color: #0071ce;
       text-decoration: none; font-weight: 600; }}
</style>
</head>
<body>
  <h1>Room Booking -- Managed Browser Redirects</h1>
  <p>Internal use: these links force the corporate-tunnel browser on
  BYOD devices (Edge on iOS, Web on Android).</p>
  {links}
</body>
</html>
"""


def _android_intent_url(https_url: str) -> str:
    """Build an Android intent:// URI that targets the Web app package,
    falling back to the plain https:// URL if it isn't installed."""
    without_scheme = https_url.split("://", 1)[1]
    fallback = quote(https_url, safe="")
    return (
        f"intent://{without_scheme}#Intent;"
        f"scheme=https;"
        f"package={ANDROID_WEB_APP_PACKAGE};"
        f"S.browser_fallback_url={fallback};"
        f"end;"
    )


def build():
    links_html = []
    for slug in ROOM_SLUGS:
        https_url = f"https://{APP_HOST}/room/{slug}"
        edge_url = f"microsoft-edge-https://{APP_HOST}/room/{slug}"
        android_intent_url = _android_intent_url(https_url)

        page = PAGE_TEMPLATE.format(
            slug=slug,
            https_url=https_url,
            edge_url=edge_url,
            android_intent_url=android_intent_url,
        )
        (OUTPUT_DIR / f"{slug}.html").write_text(page)
        links_html.append(f'  <a href="{slug}.html">Room {slug}</a>')

    index = INDEX_TEMPLATE.format(links="\n".join(links_html))
    (OUTPUT_DIR / "index.html").write_text(index)

    print(f"Generated {len(ROOM_SLUGS)} room pages + index.html in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
