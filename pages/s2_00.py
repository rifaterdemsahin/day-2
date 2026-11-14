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
    sel = D["title_selected"]
    sel_card = (f'<div class="card hero"><h2 style="margin-top:0">✅ Selected title</h2><p><b>{E(sel)}</b></p>'
                f'{copybtn(sel, "📋 Copy title")}{fb("S2-00.selected", "✅ Selected title")}</div>')
    cg = D["curiosity_gap"]
    subs = "".join(f'<li><b>{x["emoji"]} {E(x["name"])}</b><br>{E(x["formula"])}</li>' for x in cg["subs"])
    ctxt = cg["title"] + "\n" + cg["intro"] + "\n" + cg["formula"] + "\n" + "\n".join(f'- {x["name"]}: {x["formula"]}' for x in cg["subs"])
    gap = (f'<div class="card hero"><h2 style="margin-top:0">🕳️ {E(cg["title"])}</h2><p class="intro">{E(cg["intro"])}</p>'
           f'<p><b>🧪 Curiosity Gap Formula:</b> {E(cg["formula"])}</p><ol class="why">{subs}</ol>'
           f'<p class="intro">{E(cg["why_rejected"])}</p>{copybtn(ctxt, "📋 Copy technique")}{fb("S2-00.gap", "🕳️ Curiosity gap")}</div>')
    body = step_head(st) + title_thumb_block() + sel_card + why + f"""
<div class="card"><b>🪝 Hook (first second)</b><p id="hook">{E(D['hook'])}</p>{copybtn(D['hook'])}</div>
<div class="card"><b>🔄 Loop plan</b><p>{E(D['loop']['plan'])}</p>{copybtn(D['loop']['plan'])}</div>
<div class="card"><b>🥚 Rewatch bait</b><p>{E(D['loop']['bait'])}</p>{copybtn(D['loop']['bait'])}</div>
<div class="card"><b>🎨 Style line (same on every Flow prompt)</b><p>{E(D['style'])}</p>{copybtn(D['style'])}</div>
<h2>🔁 Rewatch rules</h2><ol>
<li>⚡ Hook in the first second.</li><li>🔄 Seamless loop: last line leads into the first.</li>
<li>🥚 One detail you only see the second time.</li><li>🎞️ A visual change every 2–3 s.</li>
<li>🏁 Payoff in the last third, teaser last.</li><li>💬 Captions always on, in the safe area.</li></ol>
{fb('S2-00.hook', '🪝 Hook')}{fb('S2-00.loop', '🔄 Loop plan & bait')}""" + gap
    page("s2-00.html", "S2-00 Brief", body)
