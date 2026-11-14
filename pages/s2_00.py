"""S2-00 Brief page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
