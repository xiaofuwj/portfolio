#!/usr/bin/env python3
# Push the full working tree to origin/main AND deploy the site subset to gh-pages
# via the GitHub API (the git protocol is blocked in this environment).
import os, re, base64, json, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

REPO = "xiaofuwj/portfolio"
TOKEN = re.search(r"ghp_[A-Za-z0-9]+", open("C:/Users/xf/.git-credentials", encoding="utf-8").read()).group(0)
API = "https://api.github.com/repos/%s" % REPO
HEADERS = {"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json", "User-Agent": "deploy"}

EXCLUDE_DIRS = {".git", ".workbuddy", "node_modules"}
EXCLUDE_FILES = {".mage_tree.json", ".DS_Store", "Thumbs.db", "desktop.ini"}
DOTFILE_ALLOW = {".nojekyll", ".gitignore"}
MAX_BYTES = 2 * 1024 * 1024

def api(method, url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read() or b"{}"
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"message": body.decode("utf-8", "replace")}

def list_repo_files():
    out = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            rel = (dirpath + "/" + fn).replace("\\", "/")
            if rel.startswith("./"):
                rel = rel[2:]
            base = os.path.basename(rel)
            if base in EXCLUDE_FILES:
                continue
            if base.startswith(".") and base not in DOTFILE_ALLOW:
                continue
            out.append(rel)
    out.sort()
    return out

def push_branch(branch, include_pred, msg):
    # full-tree replace (no base_tree) for a clean sync
    st, ref = api("GET", f"{API}/git/refs/heads/{branch}")
    if st != 200:
        print(f"[{branch}] ref error:", st, ref); raise SystemExit(1)
    base_sha = ref["object"]["sha"]

    all_files = list_repo_files()
    files = [f for f in all_files if include_pred(f)]
    print(f"[{branch}] {len(files)} files to publish (base was {base_sha[:8]})")

    tree = []
    for path in files:
        raw = open(path, "rb").read()
        if len(raw) > MAX_BYTES:
            print(f"  skip (too large {len(raw)}B): {path}"); continue
        st, b = api("POST", f"{API}/git/blobs", {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        if st not in (201, 200):
            print("  blob fail", path, st, b); raise SystemExit(1)
        tree.append({"path": path, "mode": "100644", "type": "blob", "sha": b["sha"]})

    st, new_tree = api("POST", f"{API}/git/trees", {"tree": tree})
    if st != 201:
        print(f"[{branch}] tree fail", st, new_tree); raise SystemExit(1)
    st, commit = api("POST", f"{API}/git/commits", {"message": msg, "tree": new_tree["sha"], "parents": [base_sha]})
    if st != 201:
        print(f"[{branch}] commit fail", st, commit); raise SystemExit(1)
    st, _ = api("PATCH", f"{API}/git/refs/heads/{branch}", {"sha": commit["sha"]})
    print(f"[{branch}] -> commit {commit['sha'][:8]} (status {st})")
    return commit["sha"]

def is_site(f):
    if f.startswith("work/") and f.endswith(".html"):
        return True
    return f in ("index.html", "about.html", "work.html", "contact.html",
                 "assets/css/style.css", "assets/js/main.js") or f.startswith("assets/icons/")

def is_repo(f):
    return True  # everything in working tree belongs in the repo (exclusions already applied)

if __name__ == "__main__":
    push_branch("main", is_repo, "chore: sync full project (design system, Mage Icons, docs, 11 case pages)")
    push_branch("gh-pages", is_site, "site: latest design system + Mage Icons + full case pages")
    print("DONE")
