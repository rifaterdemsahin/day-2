#!/usr/bin/env python3
"""Keep MASTER_SPEC.md § B7 (every update the owner asked for) in step with assets/iterations.json.

  python3 -I scripts/sync_spec_log.py

Rewrites only the text between the <!--UPDATES--> and <!--/UPDATES--> markers. Run by deploy_and_wait.py.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = ROOT / "MASTER_SPEC.md"
its = json.loads((ROOT / "assets/iterations.json").read_text(encoding="utf-8"))


def short(s, n):
    s = re.sub(r"\s+", " ", s).replace("|", "/").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


rows = ["| Version | Date | Owner asked (why) | What changed | Codes |", "|---|---|---|---|---|"]
for x in its:
    rows.append(f'| {x["v"]} | {x["date"]} | {short(x["why"], 170)} | {x["emoji"]} {short(x["change"], 230)} | {", ".join(x.get("codes", []))} |')
block = "<!--UPDATES-->\n" + "\n".join(rows) + "\n<!--/UPDATES-->"
t = spec.read_text(encoding="utf-8")
if "<!--UPDATES-->" in t:
    t = re.sub(r"<!--UPDATES-->.*?<!--/UPDATES-->", lambda m: block, t, flags=re.S)
else:
    t = t.rstrip("\n") + "\n\n## B7. 📜 Every update the owner asked for (generated from `assets/iterations.json`, newest first)\n\n" + block + "\n"
spec.write_text(t, encoding="utf-8")
print(f"📜 MASTER_SPEC.md B7: {len(its)} updates listed")
