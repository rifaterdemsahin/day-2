"""S2-01 Script page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-01")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)} · {E(s["readme"])}</div>'
        f'<p class="vo">“{E(s["vo"])}”</p>{copybtn(s["vo"])}{fb("S2-01." + c, "📝 " + c + " VO")}</div>'
        for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + f"""<p>⚠️ Draft by Claude from the README beats. Edit freely.</p>
<div class="card"><b>🗣️ Full voice-over (loop-ready)</b><p>{E(FULL_VO)}</p>{copybtn(FULL_VO, "📋 Copy full VO")}</div>
{cards}{fb('S2-01', '📝 Script overall')}"""
    page("s2-01.html", "S2-01 Script", body)
