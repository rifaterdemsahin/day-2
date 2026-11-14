"""index.html Hub page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
