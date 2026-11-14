"""S2-EV Evals page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-EV")
    rp = ROOT / "evals/results.json"
    if rp.exists():
        r = json.loads(rp.read_text(encoding="utf-8"))
        rows = "".join(f'<tr><td>{"✅" if x["ok"] else "❌"}</td><td><code>{E(x["group"])}</code></td><td>{E(x["name"])}</td><td>{x["s"]} s</td></tr>' for x in r["results"])
        head = f'<div class="card hero"><b>{"🎉" if r["passed"] == r["total"] else "⚠️"} {r["passed"]} / {r["total"]} checks passed</b> · mode <code>{E(r["mode"])}</code> · 📅 {E(r["when"])}</div>'
        tbl = f'{head}<div class="tablewrap"><table class="cmp"><tr><th></th><th>Group</th><th>Check</th><th>Time</th></tr>{rows}</table></div>'
    else:
        tbl = "<p>No run yet.</p>"
    cmds = "".join(f'<div class="card">{copybtn(c, "📋 Copy")} <code>{E(c)}</code> <small>{E(n)}</small></div>' for c, n in [
        ("python3 evals/run_evals.py", "offline, seconds: build, pages, stubs, security, command syntax, runner access rules"),
        ("python3 evals/run_evals.py --live", "adds Fly.io pages, Pages redirect, sprite reachable, Key Vault readable, agent dry run"),
        ("python3 evals/run_evals.py --e2e", "adds one real note through sprite → patch → push → Fly deploy, verified live, then reverted")])
    body = step_head(st) + tbl + "<h2>▶️ Run them</h2>" + cmds + fb("S2-EV", "🧪 Evals: what else should be checked?")
    page("s2-ev.html", "S2-EV Evals", body)
