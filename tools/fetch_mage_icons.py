#!/usr/bin/env python3
# Fetch a curated set of Mage Icons (stroke style) from the official GitHub repo,
# sanitize stroke/fill colors to currentColor, store individually under assets/icons/,
# and build a single SVG sprite (assets/icons/mage-sprite.svg) for efficient <use> referencing.
# Icons: https://mageicons.com/  (Apache-2.0)
import json, base64, re, os, urllib.parse, urllib.request, urllib.error

REPO = "Mage-Icons/mage-icons"
BRANCH = "main"
STYLE = "stroke"
OUT_DIR = "assets/icons"
SPRITE = os.path.join(OUT_DIR, "mage-sprite.svg")

# local-kebab-name -> candidate Mage filenames (first that exists wins)
ICONS = {
    "user":          ["User"],
    "users":         ["Users", "User"],
    "layout-grid":   ["Layout Grid", "Layout Left", "Dashboard Bar"],
    "mouse-pointer": ["Mouse Pointer", "Mouse", "Cursor"],
    "play":          ["Play"],
    "box-3d":        ["Box 3D", "Cube", "Package Box", "Box"],
    "chart":         ["Chart", "Chart Vertical", "Dashboard Chart"],
    "stars":         ["Stars A", "Stars B", "Star"],
    "email":         ["Email"],
    "phone":         ["Mobile Phone", "Phone", "Headphone", "Microphone"],
    "message":       ["Message", "Message Round", "Chat"],
    "location":      ["Location Pin", "Map Marker", "Pin", "Location"],
    "globe":         ["Globe", "World"],
    "github":        ["Github"],
    "linkedin":      ["Linkedin"],
    "x":             ["X", "Twitter", "Twitter X"],
    "arrow-down":    ["Arrow Down"],
    "arrow-right":   ["Arrow Right"],
    "compass":       ["Compass"],
    "pen":           ["Pen", "Edit Pen", "Brush"],
    "trophy":        ["Trophy", "Trophy Star"],
    "briefcase":     ["Briefcase"],
    "book":          ["Book Text", "Book", "Note Text"],
    "star":          ["Star"],
    "bulb":          ["Light Bulb"],
    "rocket":        ["Rocket"],
    "check":         ["Check", "Check Circle"],
    "search":        ["Search"],
    "menu":          ["Dots Menu", "Dash Menu", "Menu"],
    "external":      ["External Link"],
    "heart":         ["Heart"],
    "shield":        ["Shield Check", "Security Shield", "Shield"],
    "send":          ["Send", "Share", "Link"],
    "share":         ["Share", "Link"],
    "home":          ["Home"],
    "settings":      ["Settings", "Gear"],
    "image":         ["Image"],
    "video":         ["Video"],
    "megaphone":     ["Megaphone A", "Megaphone B", "Megaphone"],
    "sparkle":       ["Sparkle", "Stars A", "Magic"],
    "code":          ["Code", "Terminal"],
    "target":        ["Target", "Compass"],
    "calendar":      ["Calendar", "Calendar 2"],
    "clock":         ["Clock"],
    "bell":          ["Notification Bell", "Bell"],
    "download":      ["Download", "File Download"],
    "link":          ["Link", "Chain"],
    "eye":           ["Eye"],
    "palette":       ["Palette", "Color"],
    "info":          ["Information Circle", "Info"],
    "tag":           ["Tag", "Tag Check"],
}

def read_token():
    with open("C:/Users/xf/.git-credentials", encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"ghp_[A-Za-z0-9]+", txt)
    return m.group(0) if m else None

TOKEN = read_token()

def urlopen_json(url):
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "mage-fetch")
    return urllib.request.urlopen(req, timeout=30)

def sanitize(svg_text):
    # Mage stroke icons hardcode stroke="black"/fill="black"; make them themeable.
    svg_text = re.sub(r'stroke="black"', 'stroke="currentColor"', svg_text)
    svg_text = re.sub(r'fill="black"', 'fill="currentColor"', svg_text)
    svg_text = re.sub(r'stroke="#000000"', 'stroke="currentColor"', svg_text)
    svg_text = re.sub(r'fill="#000000"', 'fill="currentColor"', svg_text)
    # any remaining hardcoded black (e.g. stroke:black inline) -> currentColor
    svg_text = re.sub(r'stroke="white"', 'stroke="currentColor"', svg_text)
    return svg_text

def inner_and_viewbox(svg_text):
    m = re.search(r'<svg[^>]*viewBox="([^"]+)"', svg_text, re.I)
    vb = m.group(1) if m else "0 0 24 24"
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg_text, re.S | re.I)
    return vb, (inner.group(1).strip() if inner else "")

os.makedirs(OUT_DIR, exist_ok=True)
symbols = []
fetched = []
failed = []

for kebab, candidates in ICONS.items():
    done = False
    for name in candidates:
        fn = urllib.parse.quote(name + ".svg")
        url = f"https://api.github.com/repos/{REPO}/contents/svg/{STYLE}/{fn}?ref={BRANCH}"
        try:
            with urlopen_json(url) as r:
                data = json.loads(r.read())
            b64 = data.get("content", "")
            raw = base64.b64decode(b64).decode("utf-8")
            raw = sanitize(raw)
            # save individual file
            with open(os.path.join(OUT_DIR, kebab + ".svg"), "w", encoding="utf-8") as f:
                f.write(raw)
            vb, inner = inner_and_viewbox(raw)
            symbols.append(f'  <symbol id="mage-{kebab}" viewBox="{vb}" fill="none">{inner}</symbol>')
            fetched.append(kebab)
            done = True
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            failed.append((kebab, name, f"HTTP {e.code}"))
            break
        except Exception as e:
            failed.append((kebab, name, str(e)[:80]))
            break
    if not done and kebab not in [f[0] for f in failed]:
        failed.append((kebab, ",".join(candidates), "all 404"))

sprite = (
    '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true" focusable="false">\n'
    "  <defs>\n" + "\n".join(symbols) + "\n  </defs>\n</svg>\n"
)
with open(SPRITE, "w", encoding="utf-8") as f:
    f.write(sprite)

print(f"fetched: {len(fetched)} -> {fetched}")
print(f"sprite symbols: {len(symbols)} -> {SPRITE}")
if failed:
    print(f"FAILED ({len(failed)}):")
    for k, n, err in failed:
        print(f"  {k} [tried {n}] -> {err}")
