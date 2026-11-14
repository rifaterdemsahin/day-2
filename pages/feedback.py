"""All feedback page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    ids = json.dumps(FB_IDS, ensure_ascii=False)
    body = f"""<h1>💬 All feedback</h1><p class="intro">Everything you wrote on any page, in pipeline order. 📋 Copy all and paste it to Claude.</p>
<div id="progress" class="card"></div>
<div class="bar"><button id="copy-all" class="primary">📋 Copy all feedback</button><button id="clear-all">🗑️ Clear all</button><span id="count"></span></div>
<div class="card hero" id="sprite-card"><b>🛰️ Execute on the Sprite</b>
<p>Send everything below to the agent on your Sprite. It edits the repo, the runner pushes and redeploys Fly.</p>
<div class="bar"><select id="fagent" title="Which CLI runs the task on the Sprite"><option value="kilo">🧠 kilo</option><option value="claude">🤖 claude</option><option value="antigravity">🪐 antigravity</option></select>
<button id="fsp" class="primary">🚀 Execute all feedback on the sprite</button><button id="fspc">📋 Execute command</button></div>
<div class="bar"><a id="fprev" class="btn" href="#" target="d2-sprite" rel="noopener">👀 Preview the running sprite</a><button id="fprc">📋 Restart preview command</button><a id="fdash" class="btn" href="#" target="d2-sprite-dash" rel="noopener">🖥️ Sprite in Fly dashboard (status, no terminal)</a><button id="fterm">📋 Terminal command</button><button id="flog">📋 Tail preview log</button><a class="btn" href="s2-sp.html">🛰️ Setup</a></div>
<small id="fspmsg">Start the runner once: <code>python3 scripts/notes_runner.py</code>. The preview link needs you signed in to Fly Sprites (members only); it serves the latest <code>main</code> from the sprite.</small><pre id="fspout" hidden></pre></div>
<pre id="all"></pre>
<script>window.FB_IDS={ids};</script>"""
    page("feedback.html", "All feedback", body)
