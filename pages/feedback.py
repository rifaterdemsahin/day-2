"""All feedback page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    ids = json.dumps(FB_IDS, ensure_ascii=False)
    body = f"""<h1>💬 All feedback</h1><p class="intro">Everything you wrote on any page, in pipeline order. 📋 Copy all and paste it to Claude.</p>
<div id="progress" class="card"></div>
<div class="bar"><button id="copy-all" class="primary">📋 Copy all feedback</button><button id="clear-all">🗑️ Clear all</button><span id="count"></span></div>
<div class="card hero" id="picker-doc"><b>🎯 Object picker: point at the thing you mean</b>
<ol class="why"><li><b>1️⃣ Open the 📝 notes panel</b> on any page (button bottom right, key <kbd>N</kbd>) and press <b>🎯 Pick element</b>. The panel hides and a pink frame follows your mouse; the top bar shows the element's address.</li>
<li><b>2️⃣ Click the element</b> (a button, a table row, a sentence, a diagram). <kbd>Esc</kbd> or ✖️ cancels. Menus and the notes panel itself cannot be picked.</li>
<li><b>3️⃣ The reference is copied and added to your note</b>, followed by <code>→ </code> so you can type what to change:<br><code>🎯 [s2-x.html › #xgo] &lt;button&gt; "▶️ Compute" · section: 🪞 S2-X Sandbox</code></li>
<li><b>4️⃣ Press 🚀 Run</b> (or 📋 copy the note to Claude). The prompt preview shows your references in the task.</li></ol>
<p><b>What the reference contains</b></p>
<ul><li><code>s2-x.html</code>: the page file. In the repo it is the module <code>pages/s2_x.py</code> (hyphen becomes underscore; <code>index.html</code> is <code>pages/index.py</code>).</li>
<li><code>#xgo</code>: the element's <b>id</b> when it has one; else a data attribute (<code>[data-fb="S2-X"]</code>, <code>[data-check="…"]</code>); else a short path such as <code>#xtab &gt; tr:nth-of-type(2) &gt; td:nth-of-type(2)</code>.</li>
<li><code>&lt;button&gt; "▶️ Compute"</code>: the tag and the first 60 characters of its text. The agent searches the page module for that text, so it still finds the spot if the selector changed.</li>
<li><code>section: …</code>: the nearest heading above it.</li></ul>
<p><b>Good to know</b></p>
<ul><li>📍 Prefer clicking an element with an id or text. Paths with <code>nth-of-type</code> break when rows are added; the text part is the safety net.</li>
<li>🧱 Pages are generated, so the agent edits the module or <code>assets/*.json</code>, never the built HTML.</li>
<li>🔒 Nothing leaves your browser: the reference is plain text in your note and the clipboard.</li></ul></div>
<div class="card hero" id="sprite-card"><b>🛰️ Execute on the Sprite</b>
<p>Send everything below to the agent on your Sprite. It edits the repo, the runner pushes and redeploys Fly.</p>
<div class="bar"><select id="fagent" title="Which CLI runs the task on the Sprite"><option value="auto">🧭 auto (by size)</option><option value="kilo">🧠 kilo (free)</option><option value="claude:haiku">🤖 claude haiku (cheap)</option><option value="claude">🤖 claude (primary)</option><option value="antigravity">🪐 antigravity</option></select>
<button id="fsp" class="primary">🚀 Execute all feedback on the sprite</button><button id="fspc">📋 Execute command</button></div>
<div class="bar"><a id="fprev" class="btn" href="#" target="d2-sprite" rel="noopener">👀 Preview the running sprite</a><button id="fprc">📋 Restart preview command</button><a id="fdash" class="btn" href="#" target="d2-sprite-dash" rel="noopener">🖥️ Sprite in Fly dashboard (status, no terminal)</a><button id="fterm">📋 Terminal command</button><button id="flog">📋 Tail preview log</button><a class="btn" href="s2-sp.html">🛰️ Setup</a></div>
<small id="fspmsg">Start the runner once: <code>python3 scripts/notes_runner.py</code>. The preview link needs you signed in to Fly Sprites (members only); it serves the latest <code>main</code> from the sprite.</small><pre id="fspout" hidden></pre></div>
<pre id="all"></pre>
<script>window.FB_IDS={ids};</script>"""
    page("feedback.html", "All feedback", body)
