"""S2-04 Generate in Flow page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
