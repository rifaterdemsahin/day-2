"""S2-03b Flow vs Higgsfield page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
