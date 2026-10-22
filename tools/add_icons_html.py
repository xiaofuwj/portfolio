#!/usr/bin/env python3
# Add Mage Icons to every page: nav logo mark, footer social row, and case-progress rail.
import os, re, glob

ROOT_PAGES = ["index.html", "about.html", "work.html", "contact.html"]

def sprite_for(path):
    return "../assets/icons/mage-sprite.svg" if path.startswith("work/") else "assets/icons/mage-sprite.svg"

def ico(sprite, name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="{sprite}#mage-{name}"/></svg>'

def process(path):
    sp = sprite_for(path)
    html = open(path, encoding="utf-8").read()
    orig = html

    # 1) nav logo mark (idempotent)
    if "mage-compass" not in html:
        html = html.replace(
            'class="nav__logo">XIAOFU</a>',
            f'class="nav__logo">{ico(sp, "compass", "ico ico--brand")}XIAOFU</a>',
            1,
        )

    # 2) footer social row (idempotent)
    if "footer__social" not in html:
        social = (
            '  <div class="footer__social">\n'
            f'    <a href="https://github.com/xiaofuwj" target="_blank" rel="noopener" aria-label="GitHub">{ico(sp, "github", "ico ico--fill")}</a>\n'
            f'    <a href="https://www.linkedin.com/in/xiaofu" target="_blank" rel="noopener" aria-label="LinkedIn">{ico(sp, "linkedin", "ico ico--fill")}</a>\n'
            f'    <a href="https://x.com/xiaofuwj" target="_blank" rel="noopener" aria-label="X">{ico(sp, "x", "ico ico--fill")}</a>\n'
            f'    <a href="mailto:156944098@qq.com" aria-label="Email">{ico(sp, "email")}</a>\n'
            '  </div>\n'
        )
        html = html.replace("</footer>", social + "</footer>", 1)

    # 3) case-progress rail icons (only case pages)
    if path.startswith("work/") and "case-progress" in html:
        mapping = {"bg": "compass", "role": "user", "flow": "settings", "solution": "pen", "result": "trophy"}
        for key, icon in mapping.items():
            # match: <a href="#bg" class="active" data-tip="背景"></a> or <a href="#role" data-tip="角色"></a>
            pat = re.compile(r'(<a href="#%s"[^>]*?data-tip="[^"]*"[^>]*>)(</a>)' % re.escape(key))
            if pat.search(html):
                html = pat.sub(lambda m: m.group(1) + ico(sp, icon, "ico ico--sm") + m.group(2), html, count=1)

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        print("updated:", path)
    else:
        print("no change:", path)

# root pages
for p in ROOT_PAGES:
    if os.path.exists(p):
        process(p)
# case pages
for p in sorted(glob.glob("work/*.html")):
    process(p)
