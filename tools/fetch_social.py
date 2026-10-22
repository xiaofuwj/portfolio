#!/usr/bin/env python3
# Fetch brand/social icons from Mage Icons social-bw folder and append to the sprite.
import json, base64, re, os, urllib.parse, urllib.request, urllib.error

REPO = "Mage-Icons/mage-icons"
BRANCH = "main"
STYLE = "social-bw"
OUT_DIR = "assets/icons"
SPRITE = os.path.join(OUT_DIR, "mage-sprite.svg")

# local-kebab -> Mage filename (in social-bw)
SOCIAL = {
    "github":   "Github",
    "linkedin": "Linkedin",
    "x":        "X",
    "we-chat":  "We Chat",
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
    svg_text = re.sub(r'fill="black"', 'fill="currentColor"', svg_text)
    svg_text = re.sub(r'stroke="black"', 'stroke="currentColor"', svg_text)
    svg_text = re.sub(r'fill="white"', 'fill="currentColor"', svg_text)
    svg_text = re.sub(r'stroke="white"', 'stroke="currentColor"', svg_text)
    return svg_text

def inner_and_viewbox(svg_text):
    m = re.search(r'<svg[^>]*viewBox="([^"]+)"', svg_text, re.I)
    vb = m.group(1) if m else "0 0 24 24"
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg_text, re.S | re.I)
    return vb, (inner.group(1).strip() if inner else "")

added = []
for kebab, name in SOCIAL.items():
    fn = urllib.parse.quote(name + ".svg")
    url = f"https://api.github.com/repos/{REPO}/contents/svg/{STYLE}/{fn}?ref={BRANCH}"
    try:
        with urlopen_json(url) as r:
            data = json.loads(r.read())
        raw = base64.b64decode(data["content"]).decode("utf-8")
        raw = sanitize(raw)
        with open(os.path.join(OUT_DIR, kebab + ".svg"), "w", encoding="utf-8") as f:
            f.write(raw)
        vb, inner = inner_and_viewbox(raw)
        sym = f'  <symbol id="mage-{kebab}" viewBox="{vb}" fill="currentColor">{inner}</symbol>'
        added.append((kebab, sym))
        print(f"OK {kebab} <- {name}")
    except Exception as e:
        print(f"FAIL {kebab}: {e}")

if added:
    with open(SPRITE, "r", encoding="utf-8") as f:
        sprite = f.read()
    syms = "\n".join(s for _, s in added)
    # insert before </defs>
    sprite = sprite.replace("  </defs>", syms + "\n  </defs>", 1)
    with open(SPRITE, "w", encoding="utf-8") as f:
        f.write(sprite)
    print(f"appended {len(added)} symbols to sprite")
