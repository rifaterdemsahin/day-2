"""S2-02 Storyboard page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-02")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)}</div><p>👀 {E(s["visual"])}</p>'
        f'<p>🔤 On-screen text: <code>{E(s["text"])}</code></p>{copybtn(s["visual"] + " | text: " + s["text"])}'
        f'{fb("S2-02." + c, "🗺️ " + c + " storyboard")}</div>' for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + cards + fb('S2-02', '🗺️ Storyboard overall')
    page("s2-02.html", "S2-02 Storyboard", body)
