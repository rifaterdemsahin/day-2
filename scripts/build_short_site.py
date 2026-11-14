#!/usr/bin/env python3
"""Build the short-form site from assets/short.json (facts live in data, not code).
Run: python3 -I scripts/build_short_site.py
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
E = html.escape


def clip_label(i, s):
    return f"🎬 Clip {s['clips'][0]} · {s['start']}–{s['end']} s"


CLIPS = [(s["clips"][0], s) for s in D["scenes"]]
SCENE_NAMES = {s["clips"][0]: s["readme"] for s in D["scenes"]}
FULL_VO = " ".join(s["vo"] for s in D["scenes"])

NAV = [("index.html", "🏠 Hub")] + [(f"{st['slug']}.html", f"{st['emoji']} {st['code']} {st['name']}") for st in D["steps"]] + [
    ("iterations.html", "🔁 Iterations"), ("feedback.html", "💬 All feedback"), ("spec.html", "📖 Master spec"), ("readme.html", "📄 Script (README)")]


def nav(active):
    items = "".join(
        f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>' for h, t in NAV)
    return (f'<header><button id="menu-btn" aria-expanded="true">▾ Menu</button>'
            f'<b class="brand">📱 {E(D["code"])} · {E(D["title"])}</b>'
            f'<nav id="nav">{items}</nav></header>')


def page(fname, title, body, extra_head=""):
    pages = json.dumps(NAV, ensure_ascii=False)
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<link rel="stylesheet" href="style.css">{extra_head}
</head><body>
{nav(fname)}
<main>{body}</main>
<footer>🔁 Update → deploy → feedback. Copy your feedback with 📋 and paste it back to Claude.</footer>
<script>window.PAGES={pages};</script>
<script src="app.js"></script>
</body></html>"""
    (ROOT / fname).write_text(out, encoding="utf-8")


def copybtn(text, label="📋 Copy"):
    return f'<button class="copy" data-copy="{E(text, quote=True)}">{label}</button>'


FB_IDS = []


def fb(fid, label):
    FB_IDS.append((fid, label))
    return f'<div class="fb" data-fb="{E(fid)}" data-label="{E(label, quote=True)}"></div>'


def step_head(st):
    return f'<h1>{st["emoji"]} <span class="code">{st["code"]}</span> {E(st["name"])}</h1><p class="intro">{E(st["intro"])}</p>'


def step_by_code(c):
    return next(s for s in D["steps"] if s["code"] == c)



def thumb_svg():
    th = D["thumbnail"]
    seed = [7]
    def rnd():
        seed[0] = (seed[0] * 1103515245 + 12345) & 0x7fffffff
        return seed[0] / 0x7fffffff
    dots = "".join(f'<circle cx="{int(rnd()*1080)}" cy="{int(rnd()*1920)}" r="{1+rnd()*3:.1f}" fill="#fff" opacity="{0.2+rnd()*0.6:.2f}"/>' for _ in range(90))
    def cluster(cx, cy, col, n):
        return "".join(f'<circle cx="{cx+(rnd()-.5)*280:.0f}" cy="{cy+(rnd()-.5)*280:.0f}" r="{8+rnd()*10:.0f}" fill="{col}" opacity=".9"/>' for _ in range(n))
    return f'''<svg class="thumb" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Thumbnail: {E(th["line1"])} {E(th["line2"])}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#050816"/><stop offset=".6" stop-color="#1a1250"/><stop offset="1" stop-color="#2b0f4a"/></linearGradient>
<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="14"/></filter></defs>
<rect width="1080" height="1920" fill="url(#bg)"/>{dots}
<g>{cluster(300, 1450, "#ff8a3d", 14)}</g><g>{cluster(780, 1060, "#ffcf5a", 14)}</g>
<path d="M330 1420 C 480 1180, 620 1180, 760 1070" stroke="#4dd8ff" stroke-width="10" fill="none" stroke-linecap="round"/>
<circle cx="780" cy="1060" r="46" fill="#ffcf5a" filter="url(#gl)"/><circle cx="780" cy="1060" r="30" fill="#fff6c8"/>
<circle cx="780" cy="1060" r="5" fill="#4dd8ff"/>
<g font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-weight="900" text-anchor="middle">
<text x="540" y="470" font-size="140" fill="#4dd8ff" filter="url(#gl)" opacity=".7">{E(th["line1"])}</text>
<text x="540" y="470" font-size="140" fill="#fff">{E(th["line1"])}</text>
<text x="540" y="680" font-size="140" fill="#ffcf5a">{E(th["line2"])}</text>
<rect x="60" y="80" rx="26" width="260" height="92" fill="#4dd8ff"/><text x="190" y="146" font-size="62" fill="#001">{E(th["badge"])}</text>
<text x="540" y="1790" font-size="84" fill="#fff">{E(th["sub"])}</text></g></svg>'''


def title_thumb_block(compact=False):
    th = D["thumbnail"]
    titles = "".join(f'<li class="ttl"><b>{"⭐ " if i == 0 else ""}{E(t)}</b><br>{copybtn(t, "📋 Copy title")}{fb("S2-00.title" + str(i + 1), "🏷️ Title option " + str(i + 1))}</li>' for i, t in enumerate(D["titles"]))
    return (f'<div class="card hero tt"><div class="tt-img">{thumb_svg()}'
            f'<p class="intro">🖼️ Thumbnail draft</p>{copybtn(th["prompt"], "📋 Copy thumbnail prompt")}</div>'
            f'<div class="tt-txt"><h2 style="margin-top:0">🏷️ Title options</h2><ol class="why">{titles}</ol>'
            f'<p class="intro">{E(th["note"])}</p>{fb("S2-00.thumb", "🖼️ Thumbnail")}</div></div>')

# ---------- hub
def hub():
    rows = "".join(
        f'<a class="card step" href="{s["slug"]}.html"><span class="code">{s["code"]}</span>'
        f'<b>{s["emoji"]} {E(s["name"])}</b><small>{E(s["intro"])}</small></a>' for s in D["steps"])
    body = f"""<h1>📱 {E(D['title'])}</h1>
<p class="intro">🎯 {E(D['series'])} · ⏱️ {D['length_s']} s · 📐 {E(D['format'])} · 🛠️ Google Flow (by hand, no API)</p>
<div class="card hero"><b>🪝 Hook</b><p>{E(D['hook'])}</p>
<b>🔄 Why people will rewatch</b><p>{E(D['loop']['plan'])}</p><p>🥚 {E(D['loop']['bait'])}</p></div>
{title_thumb_block()}
<h2>✔️ Review progress</h2><div id="progress" class="card"></div>
<h2>🔢 Numbered production pipeline</h2><div class="grid">{rows}</div>
<h2>👉 How to give feedback</h2>
<ol><li>Open a step page (start with 📝 S2-01 Script).</li>
<li>Press 📝 (bottom right, or the key <b>N</b>) on any page to write a quick note, then tick ✔️ <b>I have reviewed this page</b>: a check mark appears in the menu.</li><li>On any card you can also tap ✅ approve, 🔧 change or ❌ cut and type what you want.</li>
<li>Tap 📋 Copy, or go to 💬 All feedback and tap 📋 Copy all, then paste it to Claude.</li></ol>
{fb('S2', '🏠 Overall')}"""
    page("index.html", f"{D['code']} Short Hub", body)


# ---------- steps
def s00():
    st = step_by_code("S2-00")
    m = D["scenes"]
    w = D["why"]
    pts = "".join(f'<li><b>{x["emoji"]} {E(x["principle"])}</b><br>{E(x["meaning"])}</li>' for x in w["points"])
    wtxt = w["title"] + "\n" + "\n".join(f'- {x["principle"]} {x["meaning"]}' for x in w["points"])
    why = (f'<div class="card hero"><h2 style="margin-top:0">🧭 {E(w["title"])}</h2><p class="intro">{E(w["note"])}</p>'
           f'<ol class="why">{pts}</ol>{copybtn(wtxt, "📋 Copy why")}{fb("S2-00.why", "🧭 Why (first principles)")}</div>')
    body = step_head(st) + title_thumb_block() + why + f"""
<div class="card"><b>🪝 Hook (first second)</b><p id="hook">{E(D['hook'])}</p>{copybtn(D['hook'])}</div>
<div class="card"><b>🔄 Loop plan</b><p>{E(D['loop']['plan'])}</p>{copybtn(D['loop']['plan'])}</div>
<div class="card"><b>🥚 Rewatch bait</b><p>{E(D['loop']['bait'])}</p>{copybtn(D['loop']['bait'])}</div>
<div class="card"><b>🎨 Style line (same on every Flow prompt)</b><p>{E(D['style'])}</p>{copybtn(D['style'])}</div>
<h2>🔁 Rewatch rules</h2><ol>
<li>⚡ Hook in the first second.</li><li>🔄 Seamless loop: last line leads into the first.</li>
<li>🥚 One detail you only see the second time.</li><li>🎞️ A visual change every 2–3 s.</li>
<li>🏁 Payoff in the last third, teaser last.</li><li>💬 Captions always on, in the safe area.</li></ol>
{fb('S2-00.hook', '🪝 Hook')}{fb('S2-00.loop', '🔄 Loop plan & bait')}"""
    page("s2-00.html", "S2-00 Brief", body)


def s01():
    st = step_by_code("S2-01")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)} · {E(s["readme"])}</div>'
        f'<p class="vo">“{E(s["vo"])}”</p>{copybtn(s["vo"])}{fb("S2-01." + c, "📝 " + c + " VO")}</div>'
        for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + f"""<p>⚠️ Draft by Claude from the README beats. Edit freely.</p>
<div class="card"><b>🗣️ Full voice-over (loop-ready)</b><p>{E(FULL_VO)}</p>{copybtn(FULL_VO, "📋 Copy full VO")}</div>
{cards}{fb('S2-01', '📝 Script overall')}"""
    page("s2-01.html", "S2-01 Script", body)


def s02():
    st = step_by_code("S2-02")
    cards = "".join(
        f'<div class="card"><div class="meta">{clip_label(i, s)}</div><p>👀 {E(s["visual"])}</p>'
        f'<p>🔤 On-screen text: <code>{E(s["text"])}</code></p>{copybtn(s["visual"] + " | text: " + s["text"])}'
        f'{fb("S2-02." + c, "🗺️ " + c + " storyboard")}</div>' for i, (c, s) in enumerate(CLIPS))
    body = step_head(st) + cards + fb('S2-02', '🗺️ Storyboard overall')
    page("s2-02.html", "S2-02 Storyboard", body)


def s03():
    st = step_by_code("S2-03")
    cards = ""
    for i, (c, s) in enumerate(CLIPS):
        full = s["prompt"] + " Style: " + D["style"]
        cards += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 📄 file <code>S2-04-{c}.mp4</code></div>'
                  f'<p class="prompt">{E(s["prompt"])}</p>'
                  f'{copybtn(s["prompt"], "📋 Copy prompt")}{copybtn(full, "📋 Copy prompt + style")}'
                  f'{fb("S2-03." + c, "🪄 " + c + " prompt")}</div>')
    cards += (f'<div class="card"><div class="meta">🖼️ Thumbnail (still image) · 📄 file <code>S2-04-thumb.png</code></div>'
              f'<p class="prompt">{E(D["thumbnail"]["prompt"])}</p>{copybtn(D["thumbnail"]["prompt"], "📋 Copy prompt")}{fb("S2-03.thumb", "🖼️ thumbnail prompt")}</div>')
    allp = "\n\n".join(f"CLIP {c} ({s['start']}-{s['end']} s)\n{s['prompt']} Style: {D['style']}" for c, s in CLIPS)
    body = step_head(st) + f"""<div class="card hero"><b>📦 All {len(CLIPS)} clip prompts in one go</b><p>Each already has the style line added. Paste one clip at a time into Flow.</p>{copybtn(allp, "📋 Copy ALL prompts (+ style)")}<p>🆚 Not sure which tool? See <a href="s2-03b.html">S2-03b Flow vs Higgsfield</a>.</p></div>
<div class="card"><b>🎨 Style line</b><p>{E(D['style'])}</p>{copybtn(D['style'], "📋 Copy style")}</div>
<p>🙋 Flow has no API: paste into Flow with your own Google account. Choose vertical 9:16, about 8 s.</p>{cards}{fb('S2-03', '🪄 Prompts overall')}"""
    page("s2-03.html", "S2-03 Flow prompts", body)


def s03b():
    st = step_by_code("S2-03b")
    rows = [
        ("🧩 What it is", "Google's AI film studio around the Veo models (Scene Builder, Ingredients to Video, Frames to Video, clip extension).", "Multi-model video platform: Kling, Seedance, Wan, and premium models such as Sora 2 and Veo 3.1 under one login, plus its own camera model (DoP)."),
        ("🎥 Camera control", "Plain-language camera words in the prompt, plus Flow's camera controls.", "Named camera presets (sources say 70 to 100+) from the DoP model: dolly, orbit, crane, push-in. Pick, don't describe."),
        ("⏱️ Clip length", "4, 6 or 8 s (Quality tier: 8 s only). Matches our ~8 s beats.", "Varies by model, typically 5 s or more. Check the model you pick against our 8.8 s and 9.3 s scenes."),
        ("🔊 Audio", "Veo 3.x makes native sound. We do not need it: the voice is ElevenLabs (S2-05), so mute or drop the clip audio.", "Not needed either. Voice and captions come from S2-05 and Remotion."),
        ("🧬 Consistency", "Ingredients to Video keeps a character or object the same across clips.", "Character locking, plus image-to-video from our own stills."),
        ("🪄 Extras", "Scene Builder to chain clips. Natural-language edits.", "Upscaling (up to 8K), frame interpolation (up to 120 fps), lip sync, video editing. Mostly beyond what a 9:16 abstract short needs."),
        ("🤖 Automation", "No usable API (standing assumption B1). Pasted by hand.", "Public API launched Sept 2026, pay per generation. Could automate step S2-04 and remove the manual paste."),
        ("💰 Cost", "Free tier: 50 daily credits, no rollover. Plus ~200, Pro ~1,000, Ultra 10,000+ credits a month. Veo 3.1 Lite ≈ 10 credits, Fast ≈ 20, Quality ≈ 100 per clip.", "Plans roughly $15–19 up to $84+ a month (sources disagree). API per second: Kling 3.0 from $0.084, Seedance 2.0 from $0.141, Seedance 2.5 from $0.206. Rejected-but-usable takes are still charged."),
        ("🎯 Fits this short", "✅ Default. 8 s beats, strong dark cinematic look, free credits for 6 clips. Hand paste is acceptable for 6 clips.", "✅ Worth a trial for camera presets (orbit in c3, push-in in c5) and to test other models on the same prompt. ⚠️ Verify plan, credits and API terms live before paying."),
    ]
    tbl = "".join(f"<tr><th>{a}</th><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in rows)
    cards = ""
    for i, (c, s) in enumerate(CLIPS):
        hf = f"{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}"
        cards += (f'<div class="card"><div class="meta">{clip_label(i, s)} · 🎥 preset idea: <b>{E(s["hf_camera"])}</b></div>'
                  f'<p class="prompt">{E(hf)}</p>{copybtn(hf, "📋 Copy Higgsfield prompt")}{fb("S2-03b." + c, "🆚 " + c + " Higgsfield prompt")}</div>')
    allhf = "\n\n".join(f"CLIP {c}\n{s['prompt']} Camera preset: {s['hf_camera']}. Style: {D['style']}" for c, s in CLIPS)
    body = step_head(st) + f"""<div class="card hero"><b>📌 Short answer</b>
<p>Keep <b>Google Flow</b> as the default for S2-04 (free credits, 8 s clips, great dark look). Use <b>Higgsfield</b> as a second opinion: same prompt, a camera preset, a different model, and compare the takes. If you like it, its API is the one way to stop pasting by hand.</p></div>
<h2>🆚 Side by side</h2>
<div class="tablewrap"><table class="cmp"><tr><th>🔎</th><th>🪄 Google Flow</th><th>🌈 Higgsfield</th></tr>{tbl}</table></div>
<p class="intro">🕒 Researched 2026-11-14 from public pages and reviews; prices and plan names changed several times in 2026 and sources disagree, so confirm on the live pricing pages before paying.</p>
<h2>🧪 What you can do with Higgsfield for this short</h2><ol class="why">
<li><b>🎥 Camera presets:</b> choose dolly-in for c1, orbit for c3, push-in for c5 instead of describing them.</li>
<li><b>🔀 Model shootout:</b> run the same c3 prompt on Kling, Seedance and Veo 3.1 and keep the best (the take that matches the style line).</li>
<li><b>🖼️ Image to video:</b> turn the thumbnail still (S2-03 thumb prompt) into the opening shot so frame 1 matches the loop end.</li>
<li><b>🔁 Loop frame:</b> use the c1 first frame as the last frame target of c6 to make the seam invisible.</li>
<li><b>🤖 API:</b> script S2-04 later (pay per generation, no subscription). Today's standing rule B1 still says by hand.</li></ol>
<h2>🪄 Higgsfield prompts (same story, camera preset added)</h2>
<div class="card"><b>📦 All prompts</b><br>{copybtn(allhf, "📋 Copy ALL Higgsfield prompts")}</div>{cards}
<h2>🔗 Sources</h2><ul>
<li><a href="https://higgsfield.ai/blog/ai-video-api-pricing-vs-subscriptions">Higgsfield: API pricing vs subscriptions</a></li>
<li><a href="https://apiframe.ai/guides/higgsfield-api-guide">Higgsfield API guide (third party)</a></li>
<li><a href="https://www.saasodds.com/blog/higgsfield-ai-video-generator">Higgsfield features and fit</a></li>
<li><a href="https://www.mindstudio.ai/blog/google-flow-pricing-credits-tiers-explained">Google Flow credits and tiers</a></li>
<li><a href="https://dev.to/neuraitool/google-flow-explained-googles-ai-video-studio-credits-and-who-its-for-42ad">Google Flow explained</a></li></ul>
{fb('S2-03b', '🆚 Which tool do we use, and why?')}"""
    page("s2-03b.html", "S2-03b Flow vs Higgsfield", body)


def s04():
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


def s05():
    st = step_by_code("S2-05")
    subs = "".join(
        f'<label class="card check"><input type="checkbox" data-check="{x["code"]}"> <span class="code">{x["code"]}</span> <b>{x["emoji"]} {E(x["text"])}</b>'
        + (f'<br><code>{E(x["cmd"])}</code><br>{copybtn(x["cmd"], "📋 Copy command")}' if x.get("cmd") else "") + '</label>'
        for x in st.get("substeps", []))
    body = step_head(st) + f"""<h2>🔢 Steps to follow (tick each one)</h2>{subs}
<div class="card"><b>🗣️ Voice-over text</b><p>{E(FULL_VO)}</p>{copybtn(FULL_VO, "📋 Copy full VO")}</div>
<div class="card hero"><b>🤖 Generate with ElevenLabs on fal.ai</b>
<p>Voice <b>{E(D['voice']['voice'])}</b> · model <code>{E(D['voice']['endpoint'])}</code> · {len(FULL_VO)} characters (a few cents of fal credit). Change the voice in <code>assets/short.json › voice</code>.</p>
<p>🔑 Use a <b>7-day key</b> (steps below). The key is read from the macOS Keychain (service <code>fal-key</code>) or the <code>FAL_KEY</code> environment variable, and is never printed or saved in the repo.</p>
<p>➡️ Writes <code>remotion/public/S2-05-vo.wav</code> and <code>assets/words.json</code> (word timings), so the animated captions in Remotion follow the real speech.</p></div>
<ul><li>🎤 Calm, curious, slightly fast. Target 44 s.</li><li>🔇 No silence at the end: the last word must flow into the first word on replay.</li>
<li>📄 Save as <code>S2-05-vo.wav</code>.</li></ul>{fb('S2-05', '🎙️ Voice: own voice or AI voice? Tone notes?')}"""
    page("s2-05.html", "S2-05 Voice", body)


def s06():
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


def s07():
    st = step_by_code("S2-07")
    m = D["metadata"]
    cards = "".join(f'<div class="card"><b>{lab}</b><p>{E(m[k])}</p>{copybtn(m[k])}{fb("S2-07." + k, lab)}</div>'
                    for k, lab in [("title", "🏷️ Title"), ("description", "📄 Description"), ("tags", "#️⃣ Hashtags"), ("pinned", "📌 Pinned comment")])
    body = step_head(st) + cards
    page("s2-07.html", "S2-07 Metadata", body)


def s08():
    st = step_by_code("S2-08")
    body = step_head(st) + """<ul><li>📈 Average percentage viewed (target: <b>200%+</b>)</li><li>🔁 Loops per view</li>
<li>⏱️ Swipe-away in the first 3 s</li><li>💬 Comments mentioning the hidden number 9246</li></ul>
<p>📝 Paste the numbers below and into the next short's S3-00 brief.</p>""" + fb('S2-08', '📈 Numbers after 24 h / 7 days')
    page("s2-08.html", "S2-08 Analytics", body)


# ---------- feedback gather
def feedback():
    ids = json.dumps(FB_IDS, ensure_ascii=False)
    body = f"""<h1>💬 All feedback</h1><p class="intro">Everything you wrote on any page, in pipeline order. 📋 Copy all and paste it to Claude.</p>
<div id="progress" class="card"></div>
<div class="bar"><button id="copy-all" class="primary">📋 Copy all feedback</button><button id="clear-all">🗑️ Clear all</button><span id="count"></span></div>
<pre id="all"></pre>
<script>window.FB_IDS={ids};</script>"""
    page("feedback.html", "All feedback", body)


# ---------- iterations (one page documents every round)
def iterations():
    its = json.loads((ROOT / "assets/iterations.json").read_text(encoding="utf-8"))
    rows = ""
    for it in its:
        codes = " ".join(f'<span class="code">{c}</span>' for c in it["codes"])
        txt = f'{it["v"]} ({it["date"]}) {it["change"]} Why: {it["why"]}'
        rows += (f'<div class="card"><div class="meta">{it["emoji"]} <b>{E(it["v"])}</b> · 📅 {E(it["date"])} · {E(it["status"])}</div>'
                 f'<p>🔧 {E(it["change"])}</p><p>🎯 <i>{E(it["why"])}</i></p><p>{codes}</p>{copybtn(txt)}</div>')
    body = f"""<h1>🔁 Iterations</h1><p class="intro">We always iterate. Every round (your feedback → my change → deploy) is logged here, newest first. 📋 Copy any entry to reference it.</p>
<div class="card hero"><b>🔄 The loop</b><p>1️⃣ Claude deploys and opens the site in Chrome → 2️⃣ you review and copy feedback with 📋 → 3️⃣ you paste it to Claude → 4️⃣ Claude changes the spec and site, adds a row here, redeploys → back to 1️⃣</p></div>
{rows}{fb('S2-iter', '🔁 Iteration process')}"""
    page("iterations.html", "Iterations", body)


# ---------- spec + readme pages (markdown rendered in browser)
def md_page(fname, title, src, emoji):
    text = (ROOT / src).read_text(encoding="utf-8")
    data = json.dumps(text).replace("</", "<\\/")
    body = f'<h1>{emoji} {E(title)}</h1><article id="md"></article><script>window.MD={data};</script><script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script><script>document.getElementById("md").innerHTML=window.marked?marked.parse(window.MD):"<pre>"+window.MD.replace(/</g,"&lt;")+"</pre>";</script>'
    page(fname, title, body)


hub(); s00(); s01(); s02(); s03(); s03b(); s04(); s05(); s06(); s07(); s08(); iterations(); feedback()
md_page("spec.html", "Master spec", "MASTER_SPEC.md", "📖")
md_page("readme.html", "Script draft (README)", "README.md", "📄")
(ROOT / ".nojekyll").write_text("")
print("built", 5 + len(D["steps"]), "pages;", len(FB_IDS), "feedback boxes")
