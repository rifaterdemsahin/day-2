#!/usr/bin/env python3
"""Build the short-form site from assets/short.json (facts live in data, not code).
Run: python3 -I scripts/build_short_site.py
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
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


def nav(active):
    items = "".join(
        f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>' for h, t in NAV)
    return (f'<header><button id="menu-btn" aria-expanded="true">▾ Menu</button>'
            f'<b class="brand">📱 {E(D["code"])} · {E(D["title"])}</b>'
            f'<nav id="nav">{items}</nav></header>')


FAVICONS = {
    "index.html": ("🏠", "hub"),
    "s2-r.html": ("🔬", "s2-r"),
    "development.html": ("💻", "development"),
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
<link rel="stylesheet" href="style.css">{extra_head}
</head><body>
{nav(fname)}
<main>{body}</main>
<footer>🔁 Update → deploy → feedback. Copy your feedback with 📋 and paste it back to Claude.</footer>
<script>window.PAGES={pages};</script>
<script src="app.js"></script>
</body></html>"""
    (ROOT / fname).write_text(out, encoding="utf-8")


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

# ---------- hub
def hub():
    rows = "".join(
        f'<a class="card step" href="{s["slug"]}.html"><span class="code">{s["code"]}</span>'
        f'<b>{s["emoji"]} {E(s["name"])}</b><small>{E(s["intro"])}</small></a>' for s in D["steps"])
    body = f"""<h1>📱 {E(D['title'])}</h1>
<p class="intro">🎯 {E(D['series'])} · ⏱️ {D['length_s']} s · 📐 {E(D['format'])} · 🛠️ Google Flow (by hand, no API)</p>
<div class="card hero"><b>🪝 Hook</b><p>{E(D['hook'])}</p>
<b>🔄 Why people will rewatch</b><p>{E(D['loop']['plan'])}</p><p>🥚 {E(D['loop']['bait'])}</p></div>
{title_thumb_block()}
<h2>✔️ Review progress</h2><div id="progress" class="card"></div>
<h2>🔢 Numbered production pipeline</h2><div class="grid">{rows}</div>
<h2>👉 How to give feedback</h2>
<ol><li>Open a step page (start with 📝 S2-01 Script).</li>
<li>Press 📝 (bottom right, or the key <b>N</b>) on any page to write a quick note, then tick ✔️ <b>I have reviewed this page</b>: a check mark appears in the menu.</li><li>On any card you can also tap ✅ approve, 🔧 change or ❌ cut and type what you want.</li>
<li>Tap 📋 Copy, or go to 💬 All feedback and tap 📋 Copy all, then paste it to Claude.</li></ol>
{fb('S2', '🏠 Overall')}"""
    page("index.html", f"{D['code']} Short Hub", body)


# ---------- steps
# ---------- research page: inline SVG diagrams (self-contained dark panels, readable in both themes)
def _svg(w, h, inner, label):
    return (f'<svg class="dia" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(label)}">'
            '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#4dd8ff"/></marker>'
            '<marker id="ag" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#ffcf5a"/></marker></defs>'
            f'<rect width="{w}" height="{h}" rx="14" fill="#070b1c" stroke="#26305a"/>{inner}</svg>')


def _t(x, y, s, c="#e8ecff", size=15, anchor="middle", weight=400):
    return f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" font-family="system-ui,sans-serif">{E(s)}</text>'


def dia_tokens():
    rows = "".join(f'<rect x="440" y="{50+i*26}" width="150" height="22" rx="4" fill="{"#ffcf5a" if i==3 else "#141b33"}" stroke="#26305a"/>'
                   + _t(455, 66 + i * 26, f"{9243+i}", "#001" if i == 3 else "#97a3d6", 12, "start")
                   + _t(575, 66 + i * 26, "[ 0.12, -0.80, … ]" if i == 3 else "[ … ]", "#001" if i == 3 else "#566", 11, "end") for i in range(6))
    return _svg(640, 230, _t(80, 28, "1. text", "#97a3d6", 13) + _t(250, 28, "2. token ID", "#97a3d6", 13) + _t(515, 38, "3. embedding table (one row per ID)", "#97a3d6", 13)
        + '<rect x="30" y="80" width="100" height="50" rx="10" fill="#141b33" stroke="#4dd8ff"/>' + _t(80, 112, "king", "#e8ecff", 22, "middle", 700)
        + '<path d="M135 105 H190" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>' + _t(162, 95, "tokenizer", "#97a3d6", 11)
        + '<rect x="195" y="80" width="110" height="50" rx="10" fill="#141b33" stroke="#ffcf5a"/>' + _t(250, 114, "9246", "#ffcf5a", 24, "middle", 700)
        + '<path d="M310 105 H435" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>' + _t(372, 95, "look up row", "#97a3d6", 11)
        + rows + _t(320, 215, "The ID is just a row number. It carries no meaning yet.", "#97a3d6", 13), "Token to ID to embedding table row")


def dia_unfold():
    seed = [11]
    def r():
        seed[0] = (seed[0] * 1103515245 + 12345) & 0x7fffffff
        return seed[0] / 0x7fffffff
    bars = ""
    for i in range(48):
        v = r() * 80 - 40
        y = 110 - v if v > 0 else 110
        bars += f'<rect x="{230+i*8}" y="{y:.0f}" width="5" height="{abs(v):.0f}" fill="{"#4dd8ff" if v > 0 else "#b48cff"}"/>'
    return _svg(640, 230, '<rect x="30" y="85" width="120" height="50" rx="10" fill="#141b33" stroke="#ffcf5a"/>' + _t(90, 120, "9246", "#ffcf5a", 26, "middle", 700)
        + '<path d="M155 110 H220" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>' + _t(188, 98, "unfold", "#97a3d6", 12)
        + '<line x1="226" y1="110" x2="616" y2="110" stroke="#26305a"/>' + bars
        + _t(420, 40, "1,536 numbers (only 48 drawn): cyan above zero, violet below", "#97a3d6", 13)
        + _t(420, 205, "one integer  →  a point in a 1,536-dimensional space", "#e8ecff", 14), "One ID unfolds into 1536 coordinates")


def dia_clusters():
    pts = [("apple", 140, 90, "#ff8a5c"), ("pear", 200, 130, "#ff8a5c"), ("grape", 120, 160, "#ff8a5c"),
           ("king", 460, 80, "#ffcf5a"), ("queen", 520, 130, "#ffcf5a"), ("crown", 440, 165, "#ffcf5a")]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{c}"/>' + _t(x, y - 15, n, "#e8ecff", 13) for n, x, y, c in pts)
    return _svg(640, 230, '<ellipse cx="160" cy="130" rx="90" ry="62" fill="#ff8a5c" opacity=".12" stroke="#ff8a5c" stroke-dasharray="4 4"/>'
        '<ellipse cx="480" cy="125" rx="90" ry="62" fill="#ffcf5a" opacity=".12" stroke="#ffcf5a" stroke-dasharray="4 4"/>'
        + '<path d="M140 90 L200 130" stroke="#4dd8ff" stroke-width="2"/>' + _t(180, 105, "close", "#4dd8ff", 11)
        + '<path d="M200 130 L440 165" stroke="#f87171" stroke-width="1.5" stroke-dasharray="6 5"/>' + _t(320, 160, "far apart", "#f87171", 12)
        + dots + _t(160, 215, "🍎 fruit", "#ff8a5c", 14) + _t(480, 215, "👑 royalty", "#ffcf5a", 14)
        + _t(320, 24, "2 of 1,536 dimensions, drawn flat", "#97a3d6", 12), "Fruit and royalty clusters; similar words close")


def dia_arith():
    return _svg(640, 250, '<path d="M110 205 L140 135" stroke="#b48cff" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#ar)"/>' + _t(70, 170, "+ female", "#b48cff", 12)
        + '<path d="M400 205 L430 135" stroke="#b48cff" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#ar)"/>' + _t(468, 175, "same step", "#b48cff", 12)
        + '<path d="M400 205 L125 205" stroke="#f87171" stroke-width="1.5" stroke-dasharray="2 5"/><path d="M430 135 L140 135" stroke="#f87171" stroke-width="1.5" stroke-dasharray="2 5"/>'
        + '<circle cx="110" cy="205" r="9" fill="#4dd8ff"/>' + _t(110, 232, "man", "#e8ecff", 14)
        + '<circle cx="140" cy="135" r="9" fill="#4dd8ff"/>' + _t(140, 120, "woman", "#e8ecff", 14)
        + '<circle cx="400" cy="205" r="11" fill="#ffcf5a"/>' + _t(400, 232, "king", "#ffcf5a", 15, "middle", 700)
        + '<circle cx="430" cy="135" r="11" fill="#ffcf5a" stroke="#fff" stroke-width="2"/>' + _t(430, 118, "queen", "#ffcf5a", 15, "middle", 700)
        + _t(320, 28, "king − man + woman ≈ queen", "#e8ecff", 18, "middle", 700)
        + _t(320, 52, "the step from man to woman is a direction; it moves king to queen too", "#97a3d6", 12), "Vector arithmetic: king minus man plus woman lands near queen")


def dia_learned():
    return _svg(640, 230, '<rect x="20" y="30" width="270" height="34" rx="8" fill="#141b33" stroke="#26305a"/>' + _t(155, 53, "“The king wore a crown.”", "#e8ecff", 14)
        + '<rect x="20" y="80" width="270" height="34" rx="8" fill="#141b33" stroke="#26305a"/>' + _t(155, 103, "“The queen wore a crown.”", "#e8ecff", 14)
        + '<rect x="20" y="130" width="270" height="34" rx="8" fill="#141b33" stroke="#26305a"/>' + _t(155, 153, "“Apples are ripe and sweet.”", "#e8ecff", 14)
        + '<path d="M295 47 C350 47 360 80 400 85" stroke="#4dd8ff" fill="none" marker-end="url(#ar)"/><path d="M295 97 C350 97 360 95 400 95" stroke="#4dd8ff" fill="none" marker-end="url(#ar)"/>'
        + '<path d="M295 147 C380 150 420 170 470 175" stroke="#ff8a5c" fill="none"/>'
        + '<circle cx="410" cy="82" r="9" fill="#ffcf5a"/>' + _t(410, 68, "king", "#ffcf5a", 12) + '<circle cx="440" cy="102" r="9" fill="#ffcf5a"/>' + _t(470, 108, "queen", "#ffcf5a", 12, "start")
        + '<circle cx="480" cy="178" r="9" fill="#ff8a5c"/>' + _t(480, 200, "apple", "#ff8a5c", 12)
        + _t(320, 220, "shared contexts pull words together; nobody wrote “queen = female king”", "#97a3d6", 12), "Shared contexts place king and queen close together")


def dia_attention():
    ws = ["The", "river", "bank", "was", "wet"]
    xs = [70 + i * 125 for i in range(5)]
    arcs = "".join(f'<path d="M{xs[2]} 100 Q{(xs[2]+xs[i])//2} {100-abs(i-2)*28-10} {xs[i]} 100" stroke="#4dd8ff" stroke-width="{w}" fill="none" opacity=".85"/>'
                   for i, w in [(0, 1), (1, 6), (3, 1.5), (4, 3)])
    nodes = "".join(f'<circle cx="{x}" cy="115" r="10" fill="{"#ffcf5a" if i==2 else "#141b33"}" stroke="#4dd8ff"/>' + _t(x, 150, w, "#e8ecff", 15) for i, (x, w) in enumerate(zip(xs, ws)))
    return _svg(640, 210, arcs + nodes + _t(320, 28, "attention: every word looks at the others", "#e8ecff", 15, "middle", 700)
        + _t(320, 185, "“bank” pulls most from “river”, so it means riverbank, not money (line thickness = attention)", "#97a3d6", 12), "Attention links between words in a sentence")


def dia_why():
    boxes = [("📝 text", 20), ("🔢 tokens", 125), ("🌌 embeddings", 240)]
    base = "".join(f'<rect x="{x}" y="88" width="{100 if i<2 else 120}" height="44" rx="10" fill="#141b33" stroke="#4dd8ff"/>' + _t(x + (50 if i < 2 else 60), 116, n, "#e8ecff", 14) for i, (n, x) in enumerate(boxes))
    base += '<path d="M122 110 H125 M227 110 H240" stroke="#4dd8ff" stroke-width="2"/><path d="M365 110 H400" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>'
    outs = [("🔎 search", 40), ("📚 RAG", 90), ("🎯 recommend", 140), ("🧱 LLMs", 190)]
    for n, y in outs:
        base += f'<path d="M400 110 L415 {y+14}" stroke="#4dd8ff" stroke-width="1.5"/><rect x="415" y="{y}" width="150" height="28" rx="8" fill="#141b33" stroke="#ffcf5a"/>' + _t(490, y + 19, n, "#ffcf5a", 14)
    return _svg(640, 230, base + _t(190, 190, "one idea feeds four everyday uses", "#97a3d6", 12), "Embeddings feed search, RAG, recommendations and LLMs")


DIAGRAMS = {"tokens": dia_tokens, "unfold": dia_unfold, "clusters": dia_clusters, "arithmetic": dia_arith, "learned": dia_learned, "attention": dia_attention}


def sR():
    st = step_by_code("S2-R")
    R = D["research"]
    cards = ""
    for sec in R["sections"]:
        s = next(x for c, x in CLIPS if c == sec["clip"])
        txt = f'{sec["title"]} ({sec["clip"]}): {sec["explain"]}'
        cards += (f'<div class="card research"><div class="meta">{clip_label(0, s)} · 🗣️ “{E(sec["say"])}”</div>'
                  f'<h2 style="margin-top:6px">{sec["emoji"]} {E(sec["title"])}</h2>{DIAGRAMS[sec["diagram"]]()}'
                  f'<p>{E(sec["explain"])}</p><p class="intro">⚖️ <b>Honest note:</b> {E(sec["nuance"])}</p>'
                  f'{copybtn(txt)}{fb("S2-R." + sec["clip"], "🔬 " + sec["clip"] + " research")}</div>')
    why = "".join(f'<li><b>{x["emoji"]} {E(x["point"])}</b><br>{E(x["detail"])}</li>' for x in R["why"])
    src = "".join(f'<li><a href="{E(x["url"])}" target="_blank" rel="noopener">{E(x["label"])}</a></li>' for x in R["sources"])
    body = step_head(st) + f"""<div class="card hero"><b>🧭 The idea in one paragraph</b><p>{E(R['bigpicture'])}</p>{copybtn(R['bigpicture'])}</div>
<h2>🗺️ The pipeline in one picture</h2>{dia_why()}
<h2>🎬 The script, beat by beat</h2><p class="intro">Each block shows the line spoken, a diagram of what is happening, the plain explanation, and where the short simplifies.</p>{cards}
<h2>🌍 Why this topic matters</h2><ol class="why">{why}</ol>
<div class="card"><b>🎯 The takeaway for the viewer</b><p>Meaning in AI is geometry: close points mean similar things, and directions mean relationships. Once you see that, search, chatbots and recommendations stop being magic.</p></div>
<h2>🔗 Sources</h2><ul>{src}</ul>{fb('S2-R', '🔬 Research overall: what to add, cut or fix?')}"""
    page("s2-r.html", "S2-R Research", body)


# ---------- workbench: an MVP guided checklist (two Chrome windows, progress kept in localStorage)
URLS = {"site": "https://rifaterdemsahin.github.io/day-2/s2-w.html", "flow": "https://labs.google/fx/tools/flow",
        "higgs": "https://higgsfield.ai", "studio": "http://localhost:3001"}


def openbtn(key, label, name):
    return f'<a class="btn" href="{URLS[key]}" target="{name}" rel="noopener">{label}</a>'


def layout_svg():
    inner = ('<rect x="20" y="20" width="270" height="190" rx="10" fill="#141b33" stroke="#4dd8ff"/>'
             + _t(155, 45, "🪟 WINDOW A (left)", "#4dd8ff", 14, "middle", 700) + _t(155, 70, "this Workbench page", "#e8ecff", 13)
             + _t(155, 95, "prompts, checklist, notes", "#97a3d6", 12) + _t(155, 130, "stays on the live site", "#97a3d6", 12) + _t(155, 150, "(your ticks are saved here)", "#97a3d6", 12)
             + '<rect x="310" y="20" width="310" height="190" rx="10" fill="#141b33" stroke="#ffcf5a"/>'
             + _t(465, 45, "🪟 WINDOW B (right)", "#ffcf5a", 14, "middle", 700)
             + '<rect x="325" y="58" width="85" height="26" rx="6" fill="#26305a"/>' + _t(367, 76, "🪄 Flow", "#e8ecff", 12)
             + '<rect x="418" y="58" width="95" height="26" rx="6" fill="#26305a"/>' + _t(465, 76, "🌈 Higgsfield", "#e8ecff", 12)
             + '<rect x="521" y="58" width="85" height="26" rx="6" fill="#26305a"/>' + _t(563, 76, "🎛️ Studio", "#e8ecff", 12)
             + _t(465, 120, "tools only: at most 3 tabs", "#97a3d6", 12) + _t(465, 140, "pin them, never open more", "#97a3d6", 12)
             + '<path d="M255 190 H345" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>' + _t(300, 182, "copy → paste", "#4dd8ff", 11))
    return _svg(640, 230, inner, "Two windows: workbench on the left, tools on the right")


def sW():
    st = step_by_code("S2-W")
    P = lambda s: s["prompt"] + " Style: " + D["style"]
    setup = [("W.s1", "🪟 <b>Window A:</b> open the live Workbench in a normal window and keep it. Use only this address so your ticks stay (they are saved per address).", openbtn("site", "🌐 Open live Workbench", "d2-site")),
             ("W.s2", "↔️ Snap Window A to the <b>left half</b> of the screen (hold the green button → Tile Window to Left, or drag it to the left edge).", ""),
             ("W.s3", "🪟 <b>Window B:</b> press <kbd>⌘ N</kbd> for a new window and snap it to the <b>right half</b>. This window is only for tools.", ""),
             ("W.s4", "🪄 In Window B open Google Flow and sign in. Right-click the tab → <b>Pin</b>.", openbtn("flow", "🪄 Open Flow", "d2-flow")),
             ("W.s5", "🎛️ In Window B open Remotion Studio (start it first: step below) and pin it.", openbtn("studio", "🎛️ Open Studio", "d2-studio") + copybtn("cd ~/projects/day-2/remotion && npm run studio", "📋 Copy: start Studio")),
             ("W.s6", "🌈 Optional: open Higgsfield as the third tab, only when you want a second take or a camera preset.", openbtn("higgs", "🌈 Open Higgsfield", "d2-higgs"))]
    def chk(key, text, extra=""):
        return f'<label class="card check"><input type="checkbox" data-check="{key}"> {text}{("<br>" + extra) if extra else ""}</label>'
    s_html = "".join(chk(k, t, e) for k, t, e in setup)
    clips = ""
    for i, (c, s) in enumerate(CLIPS):
        hf = f"{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}"
        clips += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 🗣️ “{E(s["vo"])}”</div>'
                  f'<p class="prompt">{E(s["prompt"])}</p>'
                  f'{copybtn(P(s), "📋 1. Copy prompt + style")}{openbtn("flow", "🪄 2. Go to Flow", "d2-flow")}'
                  f'<ol class="why"><li>In Flow (Window B): new clip, <b>9:16</b>, paste, generate. Pick the best take.</li>'
                  f'<li>Download it and rename to <code>S2-04-{c}.mp4</code> in <code>~/Downloads/day-2/</code>.</li></ol>'
                  f'<label class="check"><input type="checkbox" data-check="W.gen.{c}"> 🎞️ generated a take I like</label> '
                  f'<label class="check"><input type="checkbox" data-check="S2-04.{c}"> 💾 saved as <code>S2-04-{c}.mp4</code></label>'
                  f'<details><summary>🌈 Second opinion in Higgsfield ({E(s["hf_camera"])})</summary>{copybtn(hf, "📋 Copy Higgsfield prompt")}{openbtn("higgs", "🌈 Go to Higgsfield", "d2-higgs")}</details></div>')
    mv = "mkdir -p ~/projects/day-2/remotion/public/clips && cp ~/Downloads/day-2/S2-04-c*.mp4 ~/projects/day-2/remotion/public/clips/ && cd ~/projects/day-2/remotion && npm run sync"
    loop = "".join(chk(f"S2-06.{k}", t) for k, t in [("a", "🎞️ Last frame matches first frame"), ("b", "🗣️ Last word flows into first word"), ("c", "🥚 Tiny 9246 visible in the Queen on the 2nd watch"), ("d", "💬 Captions in safe area, large"), ("e", "⏱️ 45 s or less, 9:16")])
    body = step_head(st) + f"""<div class="card hero" id="next"><b>👉 Next up</b><p id="next-txt">…</p><div class="bar-track"><div class="bar-fill" id="wbar" style="width:0%"></div></div><small id="wcount"></small><br><button id="goto">⬇️ Jump to it</button> <button id="wreset">↩️ Reset workbench ticks</button></div>
<h2>🪟 The two-window rule</h2>{layout_svg()}
<ul><li>🚫 Never open a third kind of tab. Close extras with <kbd>⌘ W</kbd>.</li><li>🔁 The buttons reuse the same tab each time, so you never pile up Flow tabs.</li><li>⌨️ <kbd>⌘ 1…9</kbd> jumps to a pinned tab, <kbd>⌘ ⌥ →</kbd> cycles tabs.</li>
<li>💾 Progress is saved on this device for this address. Ticks here also tick S2-04 and S2-06.</li></ul>
<h2>1️⃣ Set up once (5 minutes)</h2>{s_html}
<h2>2️⃣ Make the clips (the long part)</h2><p class="intro">Do one clip at a time: copy here, paste in Flow, download, tick. When both boxes of a clip are ticked, move to the next.</p>{clips}
<h2>3️⃣ Bring the clips into the video</h2>
{chk("W.move", "📂 Move the downloads into the project and refresh the sync (one command, in Terminal).", copybtn(mv, "📋 Copy move + sync command"))}
{chk("W.studio", "🎛️ In the Studio tab press reload (<kbd>⌘ R</kbd>) and watch it once with sound.", openbtn("studio", "🎛️ Go to Studio", "d2-studio"))}
<h2>4️⃣ Loop and bait check</h2>{loop}
<h2>5️⃣ Export and publish</h2>
{chk("W.render", "🎬 Render the final video.", copybtn("cd ~/projects/day-2/remotion && npm run render", "📋 Copy render command"))}
{chk("W.publish", '📤 Add title, description and hashtags, upload, then paste the numbers on S2-08. <a href="s2-07.html">Open S2-07</a>')}
<p class="intro">🧭 MVP: ticks live in your browser (not in the repo). Next version could write them to a file so Claude can see them.</p>
{fb('S2-W', '🧰 Workbench: what was confusing or missing?')}
<script>document.addEventListener("DOMContentLoaded",function(){{
var boxes=[].slice.call(document.querySelectorAll("main input[data-check]"));
function upd(){{var n=boxes.filter(function(b){{return b.checked}}).length,nx=boxes.filter(function(b){{return !b.checked}})[0];
document.getElementById("wbar").style.width=Math.round(100*n/boxes.length)+"%";document.getElementById("wcount").textContent=n+" / "+boxes.length+" steps done";
var t=document.getElementById("next-txt");
if(!nx){{t.textContent="🎉 Everything is ticked. Time to publish and watch the numbers.";window.__nx=null;}}
else{{var l=nx.closest("label");var c=l.cloneNode(true);[].slice.call(c.querySelectorAll("a,button")).forEach(function(x){{x.remove()}});t.textContent=Array.from(c.textContent.replace(/\\s+/g," ").trim()).slice(0,150).join("");window.__nx=l;}}}}
document.addEventListener("change",upd);upd();
document.getElementById("goto").onclick=function(){{if(window.__nx)window.__nx.scrollIntoView({{block:"center",behavior:"smooth"}});}};
document.getElementById("wreset").onclick=function(){{if(confirm("Clear all workbench ticks on this device?")){{boxes.forEach(function(b){{b.checked=false;try{{var k="d2fb:chk:"+b.dataset.check;localStorage.setItem(k,JSON.stringify({{v:false}}))}}catch(e){{}}}});upd();}}}};
}});</script>"""
    page("s2-w.html", "S2-W Workbench", body)


def s00():
    st = step_by_code("S2-00")
    m = D["scenes"]
    w = D["why"]
    pts = "".join(f'<li><b>{x["emoji"]} {E(x["principle"])}</b><br>{E(x["meaning"])}</li>' for x in w["points"])
    wtxt = w["title"] + "\n" + "\n".join(f'- {x["principle"]} {x["meaning"]}' for x in w["points"])
    why = (f'<div class="card hero"><h2 style="margin-top:0">🧭 {E(w["title"])}</h2><p class="intro">{E(w["note"])}</p>'
           f'<ol class="why">{pts}</ol>{copybtn(wtxt, "📋 Copy why")}{fb("S2-00.why", "🧭 Why (first principles)")}</div>')
    body = step_head(st) + title_thumb_block() + why + f"""
<div class="card"><b>🪝 Hook (first second)</b><p id="hook">{E(D['hook'])}</p>{copybtn(D['hook'])}</div>
<div class="card"><b>🔄 Loop plan</b><p>{E(D['loop']['plan'])}</p>{copybtn(D['loop']['plan'])}</div>
<div class="card"><b>🥚 Rewatch bait</b><p>{E(D['loop']['bait'])}</p>{copybtn(D['loop']['bait'])}</div>
<div class="card"><b>🎨 Style line (same on every Flow prompt)</b><p>{E(D['style'])}</p>{copybtn(D['style'])}</div>
<h2>🔁 Rewatch rules</h2><ol>
<li>⚡ Hook in the first second.</li><li>🔄 Seamless loop: last line leads into the first.</li>
<li>🥚 One detail you only see the second time.</li><li>🎞️ A visual change every 2–3 s.</li>
<li>🏁 Payoff in the last third, teaser last.</li><li>💬 Captions always on, in the safe area.</li></ol>
{fb('S2-00.hook', '🪝 Hook')}{fb('S2-00.loop', '🔄 Loop plan & bait')}"""
    page("s2-00.html", "S2-00 Brief", body)


def s01():
    st = step_by_code("S2-01")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)} · {E(s["readme"])}</div>'
        f'<p class="vo">“{E(s["vo"])}”</p>{copybtn(s["vo"])}{fb("S2-01." + c, "📝 " + c + " VO")}</div>'
        for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + f"""<p>⚠️ Draft by Claude from the README beats. Edit freely.</p>
<div class="card"><b>🗣️ Full voice-over (loop-ready)</b><p>{E(FULL_VO)}</p>{copybtn(FULL_VO, "📋 Copy full VO")}</div>
{cards}{fb('S2-01', '📝 Script overall')}"""
    page("s2-01.html", "S2-01 Script", body)


def s02():
    st = step_by_code("S2-02")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)}</div><p>👀 {E(s["visual"])}</p>'
        f'<p>🔤 On-screen text: <code>{E(s["text"])}</code></p>{copybtn(s["visual"] + " | text: " + s["text"])}'
        f'{fb("S2-02." + c, "🗺️ " + c + " storyboard")}</div>' for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + cards + fb('S2-02', '🗺️ Storyboard overall')
    page("s2-02.html", "S2-02 Storyboard", body)


def s03():
    st = step_by_code("S2-03")
    cards = ""
    for i, (c, s) in enumerate(CLIPS):
        full = s["prompt"] + " Style: " + D["style"]
        cards += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 📄 file <code>S2-04-{c}.mp4</code></div>'
                  f'<p class="prompt">{E(s["prompt"])}</p>'
                  f'{copybtn(s["prompt"], "📋 Copy prompt")}{copybtn(full, "📋 Copy prompt + style")}'
                  f'{fb("S2-03." + c, "🪄 " + c + " prompt")}</div>')
    cards += (f'<div class="card"><div class="meta">🖼️ Thumbnail (still image) · 📄 file <code>S2-04-thumb.png</code></div>'
              f'<p class="prompt">{E(D["thumbnail"]["prompt"])}</p>{copybtn(D["thumbnail"]["prompt"], "📋 Copy prompt")}{fb("S2-03.thumb", "🖼️ thumbnail prompt")}</div>')
    allp = "\n\n".join(f"CLIP {c} ({s['start']}-{s['end']} s)\n{s['prompt']} Style: {D['style']}" for c, s in CLIPS)
    body = step_head(st) + f"""<div class="card hero"><b>📦 All {len(CLIPS)} clip prompts in one go</b><p>Each already has the style line added. Paste one clip at a time into Flow.</p>{copybtn(allp, "📋 Copy ALL prompts (+ style)")}<p>🆚 Not sure which tool? See <a href="s2-03b.html">S2-03b Flow vs Higgsfield</a>.</p></div>
<div class="card"><b>🎨 Style line</b><p>{E(D['style'])}</p>{copybtn(D['style'], "📋 Copy style")}</div>
<p>🙋 Flow has no API: paste into Flow with your own Google account. Choose vertical 9:16, about 8 s.</p>{cards}{fb('S2-03', '🪄 Prompts overall')}"""
    page("s2-03.html", "S2-03 Flow prompts", body)


def s03b():
    st = step_by_code("S2-03b")
    rows = [
        ("🧩 What it is", "Google's AI film studio around the Veo models (Scene Builder, Ingredients to Video, Frames to Video, clip extension).", "Multi-model video platform: Kling, Seedance, Wan, and premium models such as Sora 2 and Veo 3.1 under one login, plus its own camera model (DoP)."),
        ("🎥 Camera control", "Plain-language camera words in the prompt, plus Flow's camera controls.", "Named camera presets (sources say 70 to 100+) from the DoP model: dolly, orbit, crane, push-in. Pick, don't describe."),
        ("⏱️ Clip length", "4, 6 or 8 s (Quality tier: 8 s only). Matches our ~8 s beats.", "Varies by model, typically 5 s or more. Check the model you pick against our 8.8 s and 9.3 s scenes."),
        ("🔊 Audio", "Veo 3.x makes native sound. We do not need it: the voice is ElevenLabs (S2-05), so mute or drop the clip audio.", "Not needed either. Voice and captions come from S2-05 and Remotion."),
        ("🧬 Consistency", "Ingredients to Video keeps a character or object the same across clips.", "Character locking, plus image-to-video from our own stills."),
        ("🪄 Extras", "Scene Builder to chain clips. Natural-language edits.", "Upscaling (up to 8K), frame interpolation (up to 120 fps), lip sync, video editing. Mostly beyond what a 9:16 abstract short needs."),
        ("🤖 Automation", "No usable API (standing assumption B1). Pasted by hand.", "Public API launched Sept 2026, pay per generation. Could automate step S2-04 and remove the manual paste."),
        ("💰 Cost", "Free tier: 50 daily credits, no rollover. Plus ~200, Pro ~1,000, Ultra 10,000+ credits a month. Veo 3.1 Lite ≈ 10 credits, Fast ≈ 20, Quality ≈ 100 per clip.", "Plans roughly $15–19 up to $84+ a month (sources disagree). API per second: Kling 3.0 from $0.084, Seedance 2.0 from $0.141, Seedance 2.5 from $0.206. Rejected-but-usable takes are still charged."),
        ("🎯 Fits this short", "✅ Default. 8 s beats, strong dark cinematic look, free credits for 6 clips. Hand paste is acceptable for 6 clips.", "✅ Worth a trial for camera presets (orbit in c3, push-in in c5) and to test other models on the same prompt. ⚠️ Verify plan, credits and API terms live before paying."),
    ]
    tbl = "".join(f"<tr><th>{a}</th><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in rows)
    cards = ""
    for i, (c, s) in enumerate(CLIPS):
        hf = f"{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}"
        cards += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 🎥 preset idea: <b>{E(s["hf_camera"])}</b></div>'
                  f'<p class="prompt">{E(hf)}</p>{copybtn(hf, "📋 Copy Higgsfield prompt")}{fb("S2-03b." + c, "🆚 " + c + " Higgsfield prompt")}</div>')
    allhf = "\n\n".join(f"CLIP {c}\n{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}" for c, s in CLIPS)
    body = step_head(st) + f"""<div class="card hero"><b>📌 Short answer</b>
<p>Keep <b>Google Flow</b> as the default for S2-04 (free credits, 8 s clips, great dark look). Use <b>Higgsfield</b> as a second opinion: same prompt, a camera preset, a different model, and compare the takes. If you like it, its API is the one way to stop pasting by hand.</p></div>
<h2>🆚 Side by side</h2>
<div class="tablewrap"><table class="cmp"><tr><th>🔎</th><th>🪄 Google Flow</th><th>🌈 Higgsfield</th></tr>{tbl}</table></div>
<p class="intro">🕒 Researched 2026-11-14 from public pages and reviews; prices and plan names changed several times in 2026 and sources disagree, so confirm on the live pricing pages before paying.</p>
<h2>🧪 What you can do with Higgsfield for this short</h2><ol class="why">
<li><b>🎥 Camera presets:</b> choose dolly-in for c1, orbit for c3, push-in for c5 instead of describing them.</li>
<li><b>🔀 Model shootout:</b> run the same c3 prompt on Kling, Seedance and Veo 3.1 and keep the best (the take that matches the style line).</li>
<li><b>🖼️ Image to video:</b> turn the thumbnail still (S2-03 thumb prompt) into the opening shot so frame 1 matches the loop end.</li>
<li><b>🔁 Loop frame:</b> use the c1 first frame as the last frame target of c6 to make the seam invisible.</li>
<li><b>🤖 API:</b> script S2-04 later (pay per generation, no subscription). Today's standing rule B1 still says by hand.</li></ol>
<h2>🪄 Higgsfield prompts (same story, camera preset added)</h2>
<div class="card"><b>📦 All prompts</b><br>{copybtn(allhf, "📋 Copy ALL Higgsfield prompts")}</div>{cards}
<h2>🔗 Sources</h2><ul>
<li><a href="https://higgsfield.ai/blog/ai-video-api-pricing-vs-subscriptions">Higgsfield: API pricing vs subscriptions</a></li>
<li><a href="https://apiframe.ai/guides/higgsfield-api-guide">Higgsfield API guide (third party)</a></li>
<li><a href="https://www.saasodds.com/blog/higgsfield-ai-video-generator">Higgsfield features and fit</a></li>
<li><a href="https://www.mindstudio.ai/blog/google-flow-pricing-credits-tiers-explained">Google Flow credits and tiers</a></li>
<li><a href="https://dev.to/neuraitool/google-flow-explained-googles-ai-video-studio-credits-and-who-its-for-42ad">Google Flow explained</a></li></ul>
{fb('S2-03b', '🆚 Which tool do we use, and why?')}"""
    page("s2-03b.html", "S2-03b Flow vs Higgsfield", body)


def s04():
    st = step_by_code("S2-04")
    rows = "".join(
        f'<label class="card check"><input type="checkbox" data-check="S2-04.{c}"> <b>{clip_label(i, s)}</b> '
        f'→ save as <code>S2-04-{c}.mp4</code> <small>(prompt on S2-03)</small></label>' for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + f"""<h2>✅ Checklist</h2>{rows}
<ol><li>Open Google Flow, new project, set 9:16.</li><li>Paste a prompt from 🪄 S2-03, generate, pick the best take.</li>
<li>Download as <code>S2-04-cN.mp4</code> into <code>~/Downloads/day-2/</code> (never into git).</li>
<li>If a clip drifts from the style, regenerate with “prompt + style”.</li></ol>
{fb('S2-04', '🎞️ Which clips need another take, and why?')}"""
    page("s2-04.html", "S2-04 Generate", body)


def s05():
    st = step_by_code("S2-05")
    subs = "".join(
        f'<label class="card check"><input type="checkbox" data-check="{x["code"]}"> <span class="code">{x["code"]}</span> <b>{x["emoji"]} {E(x["text"])}</b>'
        + (f'<br><code>{E(x["cmd"])}</code><br>{copybtn(x["cmd"], "📋 Copy command")}' if x.get("cmd") else "") + '</label>'
        for x in st.get("substeps", []))
    body = step_head(st) + f"""<h2>🔢 Steps to follow (tick each one)</h2>{subs}
<div class="card"><b>🗣️ Voice-over text</b><p>{E(FULL_VO)}</p>{copybtn(FULL_VO, "📋 Copy full VO")}</div>
<div class="card hero"><b>🤖 Generate with ElevenLabs on fal.ai</b>
<p>Voice <b>{E(D['voice']['voice'])}</b> · model <code>{E(D['voice']['endpoint'])}</code> · {len(FULL_VO)} characters (a few cents of fal credit). Change the voice in <code>assets/short.json › voice</code>.</p>
<p>🔑 Use a <b>7-day key</b> (steps below). The key is read from the macOS Keychain (service <code>fal-key</code>) or the <code>FAL_KEY</code> environment variable, and is never printed or saved in the repo.</p>
<p>➡️ Writes <code>remotion/public/S2-05-vo.wav</code> and <code>assets/words.json</code> (word timings), so the animated captions in Remotion follow the real speech.</p></div>
<ul><li>🎤 Calm, curious, slightly fast. Target 44 s.</li><li>🔇 No silence at the end: the last word must flow into the first word on replay.</li>
<li>📄 Save as <code>S2-05-vo.wav</code>.</li></ul>{fb('S2-05', '🎙️ Voice: own voice or AI voice? Tone notes?')}"""
    page("s2-05.html", "S2-05 Voice", body)


def s06():
    st = step_by_code("S2-06")
    tp = ROOT / "assets/scene_timing.json"
    tm = {r["clip"]: r for r in json.loads(tp.read_text())["scenes"]} if tp.exists() else {}
    trows = "".join(f"<tr><td>{c}</td><td>{tm.get(c, s)['start']}–{tm.get(c, s)['end']} s{' 🎙️' if c in tm else ''}</td><td>{E(s['text'])}</td></tr>" for c, s in CLIPS)
    body = step_head(st) + f"""<table><tr><th>🎬 Clip</th><th>⏱️ Time</th><th>🔤 Caption</th></tr>{trows}</table>
<h2>🔄 Loop and bait checklist</h2>
<label class="card check"><input type="checkbox" data-check="S2-06.a"> 🎞️ Last frame matches first frame</label>
<label class="card check"><input type="checkbox" data-check="S2-06.b"> 🗣️ Last word flows into first word</label>
<label class="card check"><input type="checkbox" data-check="S2-06.c"> 🥚 Tiny 9246 visible in the Queen on the 2nd watch</label>
<label class="card check"><input type="checkbox" data-check="S2-06.d"> 💬 Captions in safe area, large</label>
<label class="card check"><input type="checkbox" data-check="S2-06.e"> ⏱️ 45 s or less, 9:16</label>
<div class="card hero"><b>🎛️ Remotion Studio (assembly in code)</b>
<p>Opens a 9:16, 45 s timeline from <code>assets/short.json</code>: clips that exist are used, missing ones show a placeholder card, captions sit in the safe area, voice is added when <code>S2-05-vo.wav</code> exists.</p>
<p>▶️ <a href="http://localhost:3001" target="_blank">http://localhost:3001</a> (only works while Studio runs on your Mac)</p>
{copybtn("cd ~/projects/day-2/remotion && npm run studio", "📋 Copy: start Studio")}{copybtn("cd ~/projects/day-2/remotion && npm run render", "📋 Copy: render S2-06-final.mp4")}
<p>📁 Put clips in <code>remotion/public/clips/S2-04-cN.mp4</code> and the voice in <code>remotion/public/S2-05-vo.wav</code> (never committed).</p></div>
<p>💬 <b>Animated captions:</b> each word pops in, the spoken word glows gold. Style comes from <code>assets/short.json › captions</code>; timing is estimated until <code>assets/words.json</code> (Whisper words) exists.</p>
<p>🛠️ Or assemble in CapCut or ffmpeg: hard cuts, no transitions, captions from the table, voice from S2-05. Export <code>S2-06-final.mp4</code>.</p>
{fb('S2-06', '✂️ Edit notes (pace, cuts, loop feel)')}"""
    page("s2-06.html", "S2-06 Assemble", body)


def s07():
    st = step_by_code("S2-07")
    m = D["metadata"]
    cards = "".join(f'<div class="card"><b>{lab}</b><p>{E(m[k])}</p>{copybtn(m[k])}{fb("S2-07." + k, lab)}</div>'
                    for k, lab in [("title", "🏷️ Title"), ("description", "📄 Description"), ("tags", "#️⃣ Hashtags"), ("pinned", "📌 Pinned comment")])
    body = step_head(st) + cards
    page("s2-07.html", "S2-07 Metadata", body)


def s08():
    st = step_by_code("S2-08")
    body = step_head(st) + """<ul><li>📈 Average percentage viewed (target: <b>200%+</b>)</li><li>🔁 Loops per view</li>
<li>⏱️ Swipe-away in the first 3 s</li><li>💬 Comments mentioning the hidden number 9246</li></ul>
<p>📝 Paste the numbers below and into the next short's S3-00 brief.</p>""" + fb('S2-08', '📈 Numbers after 24 h / 7 days')
    page("s2-08.html", "S2-08 Analytics", body)


# ---------- feedback gather
def feedback():
    ids = json.dumps(FB_IDS, ensure_ascii=False)
    body = f"""<h1>💬 All feedback</h1><p class="intro">Everything you wrote on any page, in pipeline order. 📋 Copy all and paste it to Claude.</p>
<div id="progress" class="card"></div>
<div class="bar"><button id="copy-all" class="primary">📋 Copy all feedback</button><button id="clear-all">🗑️ Clear all</button><span id="count"></span></div>
<pre id="all"></pre>
<script>window.FB_IDS={ids};</script>"""
    page("feedback.html", "All feedback", body)


# ---------- iterations (one page documents every round)
def iterations():
    its = json.loads((ROOT / "assets/iterations.json").read_text(encoding="utf-8"))
    rows = ""
    for it in its:
        codes = " ".join(f'<span class="code">{c}</span>' for c in it["codes"])
        txt = f'{it["v"]} ({it["date"]}) {it["change"]} Why: {it["why"]}'
        rows += (f'<div class="card"><div class="meta">{it["emoji"]} <b>{E(it["v"])}</b> · 📅 {E(it["date"])} · {E(it["status"])}</div>'
                 f'<p>🔧 {E(it["change"])}</p><p>🎯 <i>{E(it["why"])}</i></p><p>{codes}</p>{copybtn(txt)}</div>')
    body = f"""<h1>🔁 Iterations</h1><p class="intro">We always iterate. Every round (your feedback → my change → deploy) is logged here, newest first. 📋 Copy any entry to reference it.</p>
<div class="card hero"><b>🔄 The loop</b><p>1️⃣ Claude deploys and opens the site in Chrome → 2️⃣ you review and copy feedback with 📋 → 3️⃣ you paste it to Claude → 4️⃣ Claude changes the spec and site, adds a row here, redeploys → back to 1️⃣</p></div>
{rows}{fb('S2-iter', '🔁 Iteration process')}"""
    page("iterations.html", "Iterations", body)


# ---------- spec + readme pages (markdown rendered in browser)
def md_page(fname, title, src, emoji):
    text = (ROOT / src).read_text(encoding="utf-8")
    data = json.dumps(text).replace("</", "<\\/")
    body = f'<h1>{emoji} {E(title)}</h1><article id="md"></article><script>window.MD={data};</script><script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script><script>document.getElementById("md").innerHTML=window.marked?marked.parse(window.MD):"<pre>"+window.MD.replace(/</g,"&lt;")+"</pre>";</script>'
    page(fname, title, body)


hub(); sW(); sR(); s00(); s01(); s02(); s03(); s03b(); s04(); s05(); s06(); s07(); s08(); iterations(); feedback()
md_page("spec.html", "Master spec", "MASTER_SPEC.md", "📖")
md_page("readme.html", "Script draft (README)", "README.md", "📄")
(ROOT / ".nojekyll").write_text("")
print("built", 5 + len(D["steps"]), "pages;", len(FB_IDS), "feedback boxes")
