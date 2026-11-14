"""S2-06 Assemble and loop check page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-06")
    tp = ROOT / "assets/scene_timing.json"
    tm = {r["clip"]: r for r in json.loads(tp.read_text())["scenes"]} if tp.exists() else {}
    trows = "".join(f"<tr><td>{c}</td><td>{tm.get(c, s)['start']}–{tm.get(c, s)['end']} s{' 🎙️' if c in tm else ''}</td><td>{E(s['text'])}</td></tr>" for c, s in CLIPS)
    body = step_head(st) + f"""<table><tr><th>🎬 Clip</th><th>⏱️ Time</th><th>🔤 Caption</th></tr>{trows}</table>
<h2>🔄 Loop and bait checklist</h2>
<label class="card check"><input type="checkbox" data-check="S2-06.a"> 🎞️ Last frame matches first frame</label>
<label class="card check"><input type="checkbox" data-check="S2-06.b"> 🗣️ Last word flows into first word</label>
<label class="card check"><input type="checkbox" data-check="S2-06.c"> 🥚 Tiny 9246 visible in the Queen on the 2nd watch</label>
<label class="card check"><input type="checkbox" data-check="S2-06.d"> 💬 Captions in safe area, large</label>
<label class="card check"><input type="checkbox" data-check="S2-06.e"> ⏱️ 45 s or less, 9:16</label>
<div class="card hero"><b>🎛️ Remotion Studio (assembly in code)</b>
<p>Opens a 9:16, 45 s timeline from <code>assets/short.json</code>: clips that exist are used, missing ones show a placeholder card, captions sit in the safe area, voice is added when <code>S2-05-vo.wav</code> exists.</p>
<p>▶️ <a href="http://localhost:3001" target="_blank">http://localhost:3001</a> (only works while Studio runs on your Mac)</p>
{copybtn("cd ~/projects/day-2/remotion && npm run studio", "📋 Copy: start Studio")}{copybtn("cd ~/projects/day-2/remotion && npm run render", "📋 Copy: render S2-06-final.mp4")}
<p>📁 Put clips in <code>remotion/public/clips/S2-04-cN.mp4</code> and the voice in <code>remotion/public/S2-05-vo.wav</code> (never committed).</p></div>
<p>💬 <b>Animated captions:</b> each word pops in, the spoken word glows gold. Style comes from <code>assets/short.json › captions</code>; timing is estimated until <code>assets/words.json</code> (Whisper words) exists.</p>
<p>🛠️ Or assemble in CapCut or ffmpeg: hard cuts, no transitions, captions from the table, voice from S2-05. Export <code>S2-06-final.mp4</code>.</p>
{fb('S2-06', '✂️ Edit notes (pace, cuts, loop feel)')}"""
    page("s2-06.html", "S2-06 Assemble", body)
