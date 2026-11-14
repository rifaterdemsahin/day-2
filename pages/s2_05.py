"""S2-05 Voice-over page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
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
