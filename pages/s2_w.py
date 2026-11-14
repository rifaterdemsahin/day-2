"""S2-W Workbench page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


URLS = {"site": D["deploy"]["url"] + "s2-w.html", "flow": "https://labs.google/fx/tools/flow",
        "higgs": "https://higgsfield.ai", "studio": "http://localhost:3001"}


def openbtn(key, label, name):
    return f'<a class="btn" href="{URLS[key]}" target="{name}" rel="noopener">{label}</a>'


def layout_svg():
    inner = ('<rect x="20" y="20" width="270" height="190" rx="10" fill="#141b33" stroke="#4dd8ff"/>'
             + _t(155, 45, "🪟 WINDOW A (left)", "#4dd8ff", 14, "middle", 700) + _t(155, 70, "this Workbench page", "#e8ecff", 13)
             + _t(155, 95, "prompts, checklist, notes", "#97a3d6", 12) + _t(155, 130, "stays on the live site", "#97a3d6", 12) + _t(155, 150, "(your ticks are saved here)", "#97a3d6", 12)
             + '<rect x="310" y="20" width="310" height="190" rx="10" fill="#141b33" stroke="#ffcf5a"/>'
             + _t(465, 45, "🪟 WINDOW B (right)", "#ffcf5a", 14, "middle", 700)
             + '<rect x="325" y="58" width="85" height="26" rx="6" fill="#26305a"/>' + _t(367, 76, "🪄 Flow", "#e8ecff", 12)
             + '<rect x="418" y="58" width="95" height="26" rx="6" fill="#26305a"/>' + _t(465, 76, "🌈 Higgsfield", "#e8ecff", 12)
             + '<rect x="521" y="58" width="85" height="26" rx="6" fill="#26305a"/>' + _t(563, 76, "🎛️ Studio", "#e8ecff", 12)
             + _t(465, 120, "tools only: at most 3 tabs", "#97a3d6", 12) + _t(465, 140, "pin them, never open more", "#97a3d6", 12)
             + '<path d="M255 190 H345" stroke="#4dd8ff" stroke-width="2" marker-end="url(#ar)"/>' + _t(300, 182, "copy → paste", "#4dd8ff", 11))
    return _svg(640, 230, inner, "Two windows: workbench on the left, tools on the right")


def build():
    st = step_by_code("S2-W")
    P = lambda s: s["prompt"] + " Style: " + D["style"]
    setup = [("W.s1", "🪟 <b>Window A:</b> open the live Workbench in a normal window and keep it. Use only this address so your ticks stay (they are saved per address).", openbtn("site", "🌐 Open live Workbench", "d2-site")),
             ("W.s2", "↔️ Snap Window A to the <b>left half</b> of the screen (hold the green button → Tile Window to Left, or drag it to the left edge).", ""),
             ("W.s3", "🪟 <b>Window B:</b> press <kbd>⌘ N</kbd> for a new window and snap it to the <b>right half</b>. This window is only for tools.", ""),
             ("W.s4", "🪄 In Window B open Google Flow and sign in. Right-click the tab → <b>Pin</b>.", openbtn("flow", "🪄 Open Flow", "d2-flow")),
             ("W.s5", "🎛️ In Window B open Remotion Studio (start it first: step below) and pin it.", openbtn("studio", "🎛️ Open Studio", "d2-studio") + copybtn("cd ~/projects/day-2/remotion && npm run studio", "📋 Copy: start Studio")),
             ("W.s6", "🌈 Optional: open Higgsfield as the third tab, only when you want a second take or a camera preset.", openbtn("higgs", "🌈 Open Higgsfield", "d2-higgs"))]
    def chk(key, text, extra=""):
        return f'<label class="card check"><input type="checkbox" data-check="{key}"> {text}{("<br>" + extra) if extra else ""}</label>'
    s_html = "".join(chk(k, t, e) for k, t, e in setup)
    pr = D.get("production", {})
    ico = {"missing": "⬜ missing", "placed": "🟡 placed", "synced": "✅ synced", "pending": "⬜ pending", "ready": "✅ ready", "rendered": "✅ rendered"}
    rows = "".join(f'<tr><td><b>{c}</b></td><td>{ico[v["clip"]]}</td><td>{ico[v["voice"]]}</td><td>{ico[v["render"]]}</td></tr>' for c, v in pr.get("clips", {}).items())
    prod_table = (f'<div class="tablewrap"><table class="cmp"><tr><th>Clip</th><th>🎞️ Clip file</th><th>🗣️ Voice timing</th><th>🎬 Render</th></tr>{rows}</table></div>'
                  f'<small>📅 last synced {E(pr.get("updated", "never"))}</small>') if rows else "<p>No status yet: run <code>python3 -I scripts/sync_status.py</code>.</p>"
    clips = ""
    for i, (c, s) in enumerate(CLIPS):
        hf = f"{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}"
        clips += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 🗣️ “{E(s["vo"])}”</div>'
                  f'<p class="prompt">{E(s["prompt"])}</p>'
                  f'{copybtn(P(s), "📋 1. Copy prompt + style")}{openbtn("flow", "🪄 2. Go to Flow", "d2-flow")}'
                  f'<ol class="why"><li>In Flow (Window B): new clip, <b>9:16</b>, paste, generate. Pick the best take.</li>'
                  f'<li>Download it and rename to <code>S2-04-{c}.mp4</code> in <code>~/Downloads/day-2/</code>.</li></ol>'
                  f'<label class="check"><input type="checkbox" data-check="W.gen.{c}"> 🎞️ generated a take I like</label> '
                  f'<label class="check"><input type="checkbox" data-check="S2-04.{c}"> 💾 saved as <code>S2-04-{c}.mp4</code></label>'
                  f'<details><summary>🌈 Second opinion in Higgsfield ({E(s["hf_camera"])})</summary>{copybtn(hf, "📋 Copy Higgsfield prompt")}{openbtn("higgs", "🌈 Go to Higgsfield", "d2-higgs")}</details>'
                  f'{fb("S2-W." + c, "🧰 " + c + " in Flow: how did the take come out? what to change in the prompt?")}</div>')
    mv = "mkdir -p ~/projects/day-2/remotion/public/clips && cp ~/Downloads/day-2/S2-04-c*.mp4 ~/projects/day-2/remotion/public/clips/ && cd ~/projects/day-2/remotion && npm run sync && cd ~/projects/day-2 && python3 -I scripts/sync_status.py --commit"
    loop = "".join(chk(f"S2-06.{k}", t) for k, t in [("a", "🎞️ Last frame matches first frame"), ("b", "🗣️ Last word flows into first word"), ("c", "🥚 Tiny 9246 visible in the Queen on the 2nd watch"), ("d", "💬 Captions in safe area, large"), ("e", "⏱️ 45 s or less, 9:16")])
    body = step_head(st) + f"""<div class="card hero" id="next"><b>👉 Next up</b> <small>· every card has ✅ 🔧 ❌ and a 📋 Copy feedback button; paste it to Claude and I iterate</small><p id="next-txt">…</p><div class="bar-track"><div class="bar-fill" id="wbar" style="width:0%"></div></div><small id="wcount"></small><br><button id="goto">⬇️ Jump to it</button> <button id="wreset">↩️ Reset workbench ticks</button></div>
<h2>📁 Production status (from disk)</h2><div class="card">{prod_table}<p><small>Source: <code>assets/short.json › production</code>, written by <code>python3 -I scripts/sync_status.py</code> (also run by <code>npm run sync|studio|render</code>). Flow, Higgsfield and the render stay manual.</small></p>{copybtn("cd ~/projects/day-2 && python3 -I scripts/sync_status.py --commit", "📋 Copy: sync status + commit")}</div>
<h2>🪟 The two-window rule</h2>{layout_svg()}
<ul><li>🚫 Never open a third kind of tab. Close extras with <kbd>⌘ W</kbd>.</li><li>🔁 The buttons reuse the same tab each time, so you never pile up Flow tabs.</li><li>⌨️ <kbd>⌘ 1…9</kbd> jumps to a pinned tab, <kbd>⌘ ⌥ →</kbd> cycles tabs.</li>
<li>💾 Progress is saved on this device for this address. Ticks here also tick S2-04 and S2-06.</li></ul>
<h2>1️⃣ Set up once (5 minutes)</h2>{s_html}
{fb("S2-W.setup", "🧰 Setup: what was unclear?")}<h2>👁️ Hidden pages</h2><div class="card"><label class="check"><input type="checkbox" id="showHidden"> Show approved (hidden) pages in the top menu</label><p class="intro">Once you tick ✔️ I have reviewed this page on a page, its menu link disappears. Turn this on to bring all hidden pages back to the top menu; turn it off to hide them again. The same switch is in the top bar on every page (<button class="btn" type="button" onclick="document.getElementById('hidden-btn').click()">🙈 Hidden: n</button>), so you can always get back to a hidden page, even from a hidden page. Your choice is remembered on this device.</p></div><h2>2️⃣ Make the clips (the long part)</h2><p class="intro">Do one clip at a time: copy here, paste in Flow, download, tick. When both boxes of a clip are ticked, move to the next.</p>{clips}
<h2>3️⃣ Bring the clips into the video</h2>
{chk("W.move", "📂 Move the downloads into the project and refresh the sync (one command, in Terminal).", copybtn(mv, "📋 Copy move + sync command"))}
{chk("W.studio", "🎛️ In the Studio tab press reload (<kbd>⌘ R</kbd>) and watch it once with sound.", openbtn("studio", "🎛️ Go to Studio", "d2-studio"))}
{fb("S2-W.bring", "🧰 Bringing clips into Studio: problems?")}<h2>4️⃣ Loop and bait check</h2>{loop}
<h2>5️⃣ Export and publish</h2>
{chk("W.render", "🎬 Render the final video.", copybtn("cd ~/projects/day-2/remotion && npm run render", "📋 Copy render command"))}
{chk("W.publish", '📤 Add title, description and hashtags, upload, then paste the numbers on S2-08. <a href="s2-07.html">Open S2-07</a>')}
<p class="intro">🧭 Boxes marked 📁 are proven by the files on disk (<code>assets/short.json › production</code>), so they survive a new browser or device. The other ticks still live in this browser.</p>
{fb('S2-W', '🧰 Workbench: what was confusing or missing?')}
<script>document.addEventListener("DOMContentLoaded",function(){{
var boxes=[].slice.call(document.querySelectorAll("main input[data-check]"));
function upd(){{var n=boxes.filter(function(b){{return b.checked}}).length,nx=boxes.filter(function(b){{return !b.checked}})[0];
document.getElementById("wbar").style.width=Math.round(100*n/boxes.length)+"%";document.getElementById("wcount").textContent=n+" / "+boxes.length+" steps done";
var t=document.getElementById("next-txt");
if(!nx){{t.textContent="🎉 Everything is ticked. Time to publish and watch the numbers.";window.__nx=null;}}
else{{var l=nx.closest("label");var c=l.cloneNode(true);[].slice.call(c.querySelectorAll("a,button")).forEach(function(x){{x.remove()}});t.textContent=Array.from(c.textContent.replace(/\\s+/g," ").trim()).slice(0,150).join("");window.__nx=l;}}}}
document.addEventListener("change",upd);upd();
document.getElementById("goto").onclick=function(){{if(window.__nx)window.__nx.scrollIntoView({{block:"center",behavior:"smooth"}});}};
document.getElementById("wreset").onclick=function(){{if(confirm("Clear all workbench ticks on this device?")){{boxes.forEach(function(b){{b.checked=false;try{{var k="d2fb:chk:"+b.dataset.check;localStorage.setItem(k,JSON.stringify({{v:false}}))}}catch(e){{}}}});upd();}}}};
}});</script>"""
    page("s2-w.html", "S2-W Workbench", body)
