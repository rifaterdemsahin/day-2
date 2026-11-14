"""S2-03 Flow prompts page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
