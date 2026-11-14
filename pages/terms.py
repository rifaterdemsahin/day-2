"""S2-T Dictionary: terms.html (status board, new term, bulk update) and term.html (edit one term).

Both pages are static shells; vanilla JS in app.js reads and writes through the API (api/main.py).
Token and API address are typed in the browser and kept in localStorage, never in the repo.
"""
from pages._lib import *  # noqa: F401,F403

STATUS_EMOJI = {"idea": "💡", "script": "📝", "clips": "🎬", "voice": "🎙️", "rendered": "🎞️", "published": "🚀"}


def build():
    st = step_by_code("S2-T")
    cfg = D["dictionary"]
    head = f'<script>window.DICT={json.dumps({"statuses": STATUS_EMOJI, "local_api": cfg["local_api"], "example": cfg["bulk_example"]}, ensure_ascii=False)};</script>'
    conn = ('<div class="card hero" id="d2conn"><b>🔌 Connection</b>'
            '<p class="intro">The token is typed once and kept only in this browser (localStorage). It is never in the repo or the page.</p>'
            '<div class="frow"><label>API address <small>(empty = same site)</small><input id="d2api" placeholder="http://127.0.0.1:8960"></label>'
            '<label>Edit token<input id="d2tok" type="password" autocomplete="off" placeholder="Bearer token"></label></div>'
            '<button id="d2save" class="primary">💾 Save and test</button><button id="d2forget">🧹 Forget token</button>'
            '<p id="d2cmsg" class="intro">…</p></div>')
    body = (step_head(st) + conn + '<div id="d2terms"></div>'
            + fb("S2-T", "📚 Dictionary: index and status board"))
    page("terms.html", "S2-T Dictionary", body, head)
    body2 = ('<h1>✏️ <span class="code">S2-T</span> <span id="d2tname">Term</span></h1>'
             '<p><a href="terms.html">⬅️ Dictionary</a></p>' + conn + '<div id="d2term"></div>'
             + fb("S2-T.term", "✏️ Term editor"))
    page("term.html", "S2-T Term editor", body2, head)
