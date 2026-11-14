"""S2-RC Recommendations page: build() writes the page. Data: assets/recommendations.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-RC")
    r = json.loads((ROOT / "assets/recommendations.json").read_text(encoding="utf-8"))
    scan = "".join(f"<tr><td><code>{E(a)}</code></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in r["scan"])
    done = sum(1 for x in r["recs"] if x[3] == "✅")
    badge = lambda s: f'<span class="code">{s}</span>'
    recs = '<ol class="why">' + "".join(f"<li><b>{e} {E(t)}</b> {badge(s)}<br>{E(x)}<br><small>{E(n)}</small></li>" for e, t, x, s, n in r["recs"]) + "</ol>"
    tech = '<ol class="why">' + "".join(f"<li><b>{e} {E(t)}</b><br>{E(x)}</li>" for e, t, x in r["tech"]) + f'</ol><p>{E(r["tech_status"])}</p>'
    li = lambda k: "<ul>" + "".join(f"<li>{s} {E(x)}</li>" for s, x in r[k]) + "</ul>"
    sv = r["savings"]
    savings = f'<p>{E(sv["headline"])}</p><div class="tablewrap"><table class="cmp"><tr><th>What</th><th>Before</th><th>Now</th></tr>' + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in sv["rows"]) + "</table></div>"
    groups, order = {}, []
    for e, g, t, x in r["producer"]:
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append((e, t, x))
    prod = "".join(f'<h3>{E(g)}</h3><ol class="why">' + "".join(f"<li><b>{e} {E(t)}</b><br>{E(x)}</li>" for e, t, x in groups[g]) + "</ol>" for g in order)
    ptxt = "Producer recommendations\n" + "\n".join(f"- [{g}] {t}: {x}" for e, g, t, x in r["producer"])
    body = step_head(st) + f"""<div class="card hero"><b>🧭 Where we are</b><p>✅ <b>{done} of {len(r["recs"])}</b> recommendations are implemented; the two 🟡 ones are written and wait for a step only you can do (a secret in GitHub). The new <a href="#producer">🎬 producer recommendations</a> are at the bottom.</p><small>📅 {E(r["when"])} · status checked against the repo, the Docker build, the evals and one real runner run.</small></div>
<h2>🔍 What the scan found (before)</h2><div class="tablewrap"><table class="cmp"><tr><th>Item</th><th>Size</th><th>Why it matters</th></tr>{scan}</table></div>
<h2>💾 Token savings setup (after)</h2><div class="card hero">{savings}</div>
<h2>✅ Recommendations: status</h2><div class="card hero">{recs}</div>
<h2>🗄️ SQLite and React</h2><div class="card hero">{tech}</div>
<h2>🎬 For video production: status</h2>{li("video_status")}
<h2>🧹 Housekeeping: status</h2>{li("house_status")}
<h2 id="producer">🎬 New: recommendations for a high quality, high retention, high value video</h2>
<div class="card hero"><p>{E(r["producer_intro"])}</p>{copybtn(ptxt, "📋 Copy the producer list")}{prod}</div>""" + fb("S2-RC", "💡 Recommendations: which do you want next?")
    page("s2-rc.html", "S2-RC Recommendations", body)
