"""Shared helpers for every page module: data, layout (page, nav), feedback box, copy button.

Page modules do `from pages._lib import *`. Facts live in assets/short.json (D), never in code.
"""
import hashlib, html, json, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_V = {n: hashlib.md5((ROOT / n).read_bytes()).hexdigest()[:8] for n in ("style.css", "app.js")}  # cache-busting: browsers reload changed files
D = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"  # generated and git-ignored: built here and again inside the Docker image
SITE.mkdir(exist_ok=True)
WRITTEN = []
FLY = D["deploy"]["url"]
E = html.escape


_TP = ROOT / "assets/scene_timing.json"


_TM = {r["clip"]: r for r in json.loads(_TP.read_text())["scenes"]} if _TP.exists() else {}


def clip_label(i, s):
    r = _TM.get(s["clips"][0], s)  # the voice drives the cuts (scene_timing.json) when it exists
    return f"🎬 Clip {s['clips'][0]} · {round(r['start'], 1):g}–{round(r['end'], 1):g} s"


CLIPS = [(s["clips"][0], s) for s in D["scenes"]]


SCENE_NAMES = {s["clips"][0]: s["readme"] for s in D["scenes"]}


FULL_VO = " ".join(s["vo"] for s in D["scenes"])


NAV = [("index.html", "🏠 Hub")] + [(f"{st['slug']}.html", f"{st['emoji']} {st['code']} {st['name']}") for st in D["steps"]] + [
    ("iterations.html", "🔁 Iterations"), ("feedback.html", "💬 All feedback"), ("spec.html", "📖 Master spec"), ("readme.html", "📄 Script (README)")]
PHASE = {"index.html": "preprod", "s2-w.html": "preprod",
         "s2-00.html": "preprod", "s2-01.html": "preprod", "s2-02.html": "preprod",
         "s2-03.html": "preprod", "s2-03b.html": "preprod", "s2-04.html": "preprod",
         "s2-05.html": "prod", "s2-06.html": "prod",
         "s2-07.html": "postprod", "s2-08.html": "postprod"}
PHASE_LABEL = {"preprod": "🟣 Preprod", "prod": "🟢 Prod", "postprod": "🔵 Postprod"}
PHASE_ORDER = ["preprod", "prod", "postprod"]


def nav(active):
    groups = {}
    for h, t in NAV:
        groups.setdefault(PHASE.get(h, "site"), []).append((h, t))
    items = ""
    for sec in PHASE_ORDER:
        items += f'<h3 class="navsec">{PHASE_LABEL[sec]}</h3>'
        for h, t in groups.get(sec, []):
            items += f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>'
    items += '<h3 class="navsec">📖 Site</h3>'
    for h, t in groups.get("site", []):
        items += f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>'
    return (f'<header><div class="hbar"><button id="menu-btn" aria-expanded="true">▾ Menu</button>'
            f'<b class="brand">📱 {E(D["code"])} · {E(D["title"])}</b>'
            f'<button id="hidden-btn" type="button" aria-pressed="false" title="Show the pages hidden from the menu (approved pages)">🙈 Hidden: 0</button></div>'
            f'<nav id="nav">{items}</nav></header>')


FAVICONS = {
    "index.html": ("🏠", "hub"),
    "s2-w.html": ("🧰", "s2-w"),
    "s2-r.html": ("🔬", "s2-r"),
    "development.html": ("💻", "development"),
    "analytics.html": ("📊", "analytics"),
    "s2-00.html": ("🧭", "s2-00"),
    "s2-01.html": ("📝", "s2-01"),
    "s2-02.html": ("🗺️", "s2-02"),
    "s2-03.html": ("🪄", "s2-03"),
    "s2-03b.html": ("🆚", "s2-03b"),
    "s2-04.html": ("🎞️", "s2-04"),
    "s2-05.html": ("🎙️", "s2-05"),
    "s2-06.html": ("✂️", "s2-06"),
    "s2-07.html": ("💬", "s2-07"),
    "s2-08.html": ("📈", "s2-08"),
    "iterations.html": ("🔁", "iterations"),
    "feedback.html": ("💬", "feedback"),
    "spec.html": ("📖", "spec"),
    "readme.html": ("📄", "readme"),
}


def page(fname, title, body, extra_head=""):
    pages = json.dumps(NAV, ensure_ascii=False)
    emoji, fav_slug = FAVICONS.get(fname, ("📱", fname.replace(".html", "")))
    fav_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
    fav_dir = ROOT / "assets/favicons"
    fav_dir.mkdir(parents=True, exist_ok=True)
    (fav_dir / f"{fav_slug}.svg").write_text(fav_svg, encoding="utf-8")
    fav_head = (f'<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>{emoji}</text></svg>">\n'
                f'<link rel="alternate icon" href="assets/favicons/{fav_slug}.svg">')
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
{fav_head}
<link rel="stylesheet" href="style.css?v={ASSET_V["style.css"]}">{extra_head}
</head><body>
{nav(fname)}
<main>{body}</main>
<footer>🔁 Update → deploy → feedback. Copy your feedback with 📋 and paste it back to Claude.<br><span id="deployed">🕒 Last deployed: checking…</span></footer>
<script>window.PAGES={pages};window.SPRITE={json.dumps(D.get("sprite", {}))};window.PROD={json.dumps(D.get("production", {}))};</script>
<script src="app.js?v={ASSET_V["app.js"]}"></script>
</body></html>"""
    (SITE / fname).write_text(out, encoding="utf-8")
    WRITTEN.append(fname)


def copybtn(text, label="📋 Copy"):
    return f'<button class="copy" data-copy="{E(text, quote=True)}">{label}</button>'


FB_IDS = []


def fb(fid, label):
    FB_IDS.append((fid, label))
    return f'<div class="fb" data-fb="{E(fid)}" data-label="{E(label, quote=True)}"></div>'


def step_head(st):
    return f'<h1>{st["emoji"]} <span class="code">{st["code"]}</span> {E(st["name"])}</h1><p class="intro">{E(st["intro"])}</p>'


def step_by_code(c):
    return next(s for s in D["steps"] if s["code"] == c)


def thumb_svg():
    th = D["thumbnail"]
    seed = [7]
    def rnd():
        seed[0] = (seed[0] * 1103515245 + 12345) & 0x7fffffff
        return seed[0] / 0x7fffffff
    dots = "".join(f'<circle cx="{int(rnd()*1080)}" cy="{int(rnd()*1920)}" r="{1+rnd()*3:.1f}" fill="#fff" opacity="{0.2+rnd()*0.6:.2f}"/>' for _ in range(90))
    def cluster(cx, cy, col, n):
        return "".join(f'<circle cx="{cx+(rnd()-.5)*280:.0f}" cy="{cy+(rnd()-.5)*280:.0f}" r="{8+rnd()*10:.0f}" fill="{col}" opacity=".9"/>' for _ in range(n))
    return f'''<svg class="thumb" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Thumbnail: {E(th["line1"])} {E(th["line2"])}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050816"/><stop offset=".6" stop-color="#1a1250"/><stop offset="1" stop-color="#2b0f4a"/></linearGradient>
<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="14"/></filter></defs>
<rect width="1080" height="1920" fill="url(#bg)"/>{dots}
<g>{cluster(300, 1450, "#ff8a3d", 14)}</g><g>{cluster(780, 1060, "#ffcf5a", 14)}</g>
<path d="M330 1420 C 480 1180, 620 1180, 760 1070" stroke="#4dd8ff" stroke-width="10" fill="none" stroke-linecap="round"/>
<circle cx="780" cy="1060" r="46" fill="#ffcf5a" filter="url(#gl)"/><circle cx="780" cy="1060" r="30" fill="#fff6c8"/>
<circle cx="780" cy="1060" r="5" fill="#4dd8ff"/>
<g font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-weight="900" text-anchor="middle">
<text x="540" y="470" font-size="140" fill="#4dd8ff" filter="url(#gl)" opacity=".7">{E(th["line1"])}</text>
<text x="540" y="470" font-size="140" fill="#fff">{E(th["line1"])}</text>
<text x="540" y="680" font-size="140" fill="#ffcf5a">{E(th["line2"])}</text>
<rect x="60" y="80" rx="26" width="260" height="92" fill="#4dd8ff"/><text x="190" y="146" font-size="62" fill="#001">{E(th["badge"])}</text>
<text x="540" y="1790" font-size="84" fill="#fff">{E(th["sub"])}</text></g></svg>'''


def title_thumb_block(compact=False):
    th = D["thumbnail"]
    titles = "".join(f'<li class="ttl"><b>{"⭐ " if i == 0 else ""}{E(t)}</b><br>{copybtn(t, "📋 Copy title")}{fb("S2-00.title" + str(i + 1), "🏷️ Title option " + str(i + 1))}</li>' for i, t in enumerate(D["titles"]))
    return (f'<div class="card hero tt"><div class="tt-img">{thumb_svg()}'
            f'<p class="intro">🖼️ Thumbnail draft</p>{copybtn(th["prompt"], "📋 Copy thumbnail prompt")}</div>'
            f'<div class="tt-txt"><h2 style="margin-top:0">🏷️ Title options</h2><ol class="why">{titles}</ol>'
            f'<p class="intro">{E(th["note"])}</p>{fb("S2-00.thumb", "🖼️ Thumbnail")}</div></div>')


def _svg(w, h, inner, label):
    return (f'<svg class="dia" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(label)}">'
            '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#4dd8ff"/></marker>'
            '<marker id="ag" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#ffcf5a"/></marker></defs>'
            f'<rect width="{w}" height="{h}" rx="14" fill="#070b1c" stroke="#26305a"/>{inner}</svg>')


def _t(x, y, s, c="#e8ecff", size=15, anchor="middle", weight=400):
    return f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" font-family="system-ui,sans-serif">{E(s)}</text>'


def md_page(fname, title, src, emoji):
    text = (ROOT / src).read_text(encoding="utf-8")
    data = json.dumps(text).replace("</", "<\\/")
    body = f'<h1>{emoji} {E(title)}</h1><article id="md"></article><script>window.MD={data};</script><script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script><script>document.getElementById("md").innerHTML=window.marked?marked.parse(window.MD):"<pre>"+window.MD.replace(/</g,"&lt;")+"</pre>";</script>'
    page(fname, title, body)


__all__ = ['hashlib', 'html', 'json', 'pathlib', 'shutil', 'ROOT', 'ASSET_V', 'D', 'SITE', 'WRITTEN', 'FLY', 'E', '_TP', '_TM', 'clip_label', 'CLIPS', 'SCENE_NAMES', 'FULL_VO', 'NAV', 'nav', 'FAVICONS', 'page', 'copybtn', 'FB_IDS', 'fb', 'step_head', 'step_by_code', 'thumb_svg', 'title_thumb_block', '_svg', '_t', 'md_page']
