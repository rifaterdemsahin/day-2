"""Iterations page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
