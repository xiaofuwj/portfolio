#!/usr/bin/env python3
# Deploy the static site to the gh-pages branch via GitHub API (git protocol is blocked here).
import os, re, base64, json, urllib.request, urllib.error

REPO = "xiaofuwj/portfolio"
TOKEN = re.search(r"ghp_[A-Za-z0-9]+", open("C:/Users/xf/.git-credentials", encoding="utf-8").read()).group(0)
API = "https://api.github.com/repos/%s" % REPO
HEADERS = {"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json", "User-Agent": "deploy"}

# Files to publish (relative to repo root). Excludes docs/, content/, tools/, .workbuddy/, .git/
INCLUDE = [
    "index.html", "about.html", "work.html", "contact.html",
    ".nojekyll",
    "assets/css/style.css", "assets/js/main.js",
]
for f in sorted(os.listdir("work")):
    if f.endswith(".html"):
        INCLUDE.append("work/" + f)
for f in sorted(os.listdir("assets/icons")):
    INCLUDE.append("assets/icons/" + f)

def api(method, url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

# 1) get gh-pages HEAD
st, head = api("GET", f"{API}/git/refs/heads/gh-pages")
if st != 200:
    print("gh-pages ref error:", st, head); raise SystemExit(1)
base_sha = head["object"]["sha"]
st, base_commit = api("GET", f"{API}/git/commits/{base_sha}")
base_tree = base_commit["tree"]["sha"]

# 2) create blobs
blobs = {}
for path in INCLUDE:
    if not os.path.exists(path):
        print("skip missing:", path); continue
    raw = open(path, "rb").read()
    st, b = api("POST", f"{API}/git/blobs", {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
    if st != 201:
        print("blob fail", path, st, b); raise SystemExit(1)
    blobs[path] = b["sha"]

# 3) build tree (full replace of these paths)
tree = [{"path": p, "mode": "100644", "type": "blob", "sha": sha} for p, sha in blobs.items()]
st, new_tree = api("POST", f"{API}/git/trees", {"base_tree": base_tree, "tree": tree})
if st != 201:
    print("tree fail", st, new_tree); raise SystemExit(1)

# 4) commit
msg = "site: add Mage Icons (sprite + iconography) across all pages"
st, commit = api("POST", f"{API}/git/commits", {"message": msg, "tree": new_tree["sha"], "parents": [base_sha]})
if st != 201:
    print("commit fail", st, commit); raise SystemExit(1)

# 5) update ref
st, ref = api("PATCH", f"{API}/git/refs/heads/gh-pages", {"sha": commit["sha"]})
print("deploy status:", st, "| commit:", commit["sha"][:8])
print("published files:", len(blobs))
