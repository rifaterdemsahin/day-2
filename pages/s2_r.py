"""S2-R Research page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


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


def build():
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
