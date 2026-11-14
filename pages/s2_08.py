"""S2-08 Publish and analytics page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-08")
    body = step_head(st) + """<ul><li>📈 Average percentage viewed (target: <b>200%+</b>)</li><li>🔁 Loops per view</li>
<li>⏱️ Swipe-away in the first 3 s</li><li>💬 Comments mentioning the hidden number 9246</li><li>🧪 BROWSERTEST-1 notes-button check</li></ul>
<p>📝 Paste the numbers below and into the next short's S3-00 brief.</p>""" + fb('S2-08', '📈 Numbers after 24 h / 7 days')
    page("s2-08.html", "S2-08 Analytics", body)
