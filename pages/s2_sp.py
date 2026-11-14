"""S2-SP Sprite setup page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-SP")
    subs = "".join(
        f'<label class="card check"><input type="checkbox" data-check="{x["code"]}"> <span class="code">{x["code"]}</span> <b>{x["emoji"]} {E(x["text"])}</b>'
        + (f'<br><code>{E(x["cmd"])}</code><br>{copybtn(x["cmd"], "📋 Copy command")}' if x.get("cmd") else "") + '</label>' for x in st["substeps"])

    ck = ROOT / "assets/sprite_check.json"
    LINKS = {"claude": ("https://docs.claude.com/en/docs/claude-code/overview", "https://claude.ai/code", "claude  (then /login)"),
             "kilo": ("https://kilo.ai/docs", "https://app.kilo.ai", "kilo auth login"),
             "antigravity": ("https://antigravity.google", "https://antigravity.google/download", "agy  (paste the code it prints)")}
    if ck.exists():
        c = json.loads(ck.read_text(encoding="utf-8"))
        rows = "".join(f'<tr><td>{"✅" if a["ready"] else "⚠️"}</td><td><b>{E(a["agent"])}</b></td><td><code>{E(a["cli"])}</code></td><td>{E(a["version"] or "-")}</td><td>{E(a["note"])}</td>'
                       f'<td><a href="{LINKS[a["agent"]][0]}" target="d2-docs" rel="noopener">📚 docs</a> <a href="{LINKS[a["agent"]][1]}" target="d2-docs" rel="noopener">🔗 site</a></td>'
                       f'<td><code>sprite console -s {E(c["sprite"])}</code> → <code>{E(LINKS[a["agent"]][2])}</code></td></tr>' for a in c["agents"])
        chk = f'<div class="card hero"><b>🧪 Agent CLIs on the sprite</b> · 📅 {E(c["when"])}<div class="tablewrap"><table class="cmp"><tr><th></th><th>Agent</th><th>CLI</th><th>Version</th><th>State</th><th>Verify</th><th>Sign in (once)</th></tr>{rows}</table></div>' \
              f'<p>Re-test: {copybtn("python3 -I scripts/sprite_check.py", "📋 Copy test command")} <code>python3 -I scripts/sprite_check.py</code></p>' \
              '<small>A sprite can only complete a task with an agent that is ✅ ready. Sign-in happens in a live shell on the sprite (opens a browser code flow); the check never uses or prints a key. Docs links are from memory: open them to verify.</small></div>'
    else:
        chk = "<p>No agent check yet: run <code>python3 -I scripts/sprite_check.py</code>.</p>"
    sd = D["sprite_doc"]
    did = '<ol class="why">' + "".join(f'<li><b>{x[0]} {E(x[1])}</b><br>👉 <i>Why:</i> {E(x[2])}</li>' for x in sd["did"]) + "</ol>"
    whyv = '<div class="card hero"><ol class="why">' + "".join(f'<li><b>{x[0]} {E(x[1])}</b><br>{E(x[2])}</li>' for x in sd["why_video"]) + "</ol></div>"
    body = step_head(st) + chk + f"""<div class="card hero"><b>🚀 What the notes button does</b>
<p>Press <b>🚀 Run</b> in the 📝 panel. The local runner reads the agent key from Azure Key Vault, runs the agent (<b>kilo</b>, claude or antigravity) on the sprite <code>{E(D['sprite']['name'])}</code> with your notes as the task, brings back a <b>patch</b>, applies it here, rebuilds, commits, pushes main and deploys to Fly.io. The log streams into the panel.</p>
<p>🔒 No secret is on the site. The key goes to the sprite only on stdin for that run, and no GitHub token goes to the sprite at all (it returns a patch). The runner listens on 127.0.0.1 only and accepts only this site's origin.</p>
<p>⚠️ Only your own notes should go in: they become the agent's instructions.</p></div>
<h2>🔢 Steps to follow (tick each one)</h2>{subs}
<ul><li>🔁 The runner refuses to start a run unless this repo is clean and equal to origin/main, so the patch always applies.</li>
<li>🧾 Sprite name and folder come from <code>assets/short.json › sprite</code>.</li></ul>
<h2>🛠️ What was done, and why</h2>{did}
<h2>🎬 Why this matters in video production</h2>{whyv}{fb('S2-SP', '🛰️ Sprite setup: what failed or was unclear?')}"""
    page("s2-sp.html", "S2-SP Sprite setup", body)
