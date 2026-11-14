"""S2-RC Recommendations page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-RC")
    r = json.loads((ROOT / "assets/recommendations.json").read_text(encoding="utf-8"))
    scan = "".join(f"<tr><td><code>{E(a)}</code></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in r["scan"])
    recs = '<ol class="why">' + "".join(f"<li><b>{e} {E(t)}</b><br>{E(x)}</li>" for e, t, x in r["recs"]) + "</ol>"
    tech = '<ol class="why">' + "".join(f"<li><b>{e} {E(t)}</b><br>{E(x)}</li>" for e, t, x in r["tech"]) + "</ol>"
    li = lambda k: "<ul>" + "".join(f"<li>{E(x)}</li>" for x in r[k]) + "</ul>"
    body = step_head(st) + f"""<div class="card hero"><b>🧭 Start here</b><p>{E(r["first"])}</p><small>📅 {E(r["when"])} · from a scan of about 145 tracked files. Recommendations only: nothing here is built yet.</small></div>
<h2>🔍 What the scan found</h2><div class="tablewrap"><table class="cmp"><tr><th>Item</th><th>Size</th><th>Why it matters</th></tr>{scan}</table></div>
<h2>✅ Recommendations, best value first</h2><div class="card hero">{recs}</div>
<h2>🗄️ SQLite and React</h2><div class="card hero">{tech}</div>
<h2>🎬 For video production specifically</h2>{li("video")}
<h2>🧹 Housekeeping</h2>{li("house")}""" + fb("S2-RC", "💡 Recommendations: which do you want first?")
    page("s2-rc.html", "S2-RC Recommendations", body)
