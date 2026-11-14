#!/usr/bin/env python3
"""Check the three agent CLIs on the Sprite: installed? version? signed in? smoke test.

  python3 -I scripts/sprite_check.py      (no key needed; kilo smoke test uses the free model)

Writes assets/sprite_check.json (shown on the S2-SP page). Prints a table. Never prints keys.
"""
import datetime, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
SPR = D["sprite"]
MODEL = SPR.get("kilo_model", "kilo/kilo-auto/free")

SCRIPT = r'''
export PATH="$PATH:$(npm prefix -g)/bin"
ver() { timeout 25 "$@" --version 2>&1 | tail -1; }
echo "claude|$(command -v claude >/dev/null && echo 1 || echo 0)|$(ver claude)|$(claude auth status 2>&1 | grep -o '"loggedIn": *[a-z]*' | head -1)"
echo "kilo|$(command -v kilo >/dev/null && echo 1 || echo 0)|$(ver kilo)|$(timeout 70 kilo run -m MODEL 'Reply with exactly: KILO-OK' </dev/null 2>&1 | grep -c KILO-OK)"
echo "antigravity|$(command -v agy >/dev/null && echo 1 || echo 0)|$(ver agy)|$(timeout 20 agy -p 'Reply with exactly: AGY-OK' </dev/null 2>&1 | grep -ci 'authentication')"
'''.replace("MODEL", MODEL)

p = subprocess.run(["sprite", "exec", "-s", SPR["name"], "--no-stdin", "--", "bash", "-lc", SCRIPT],
                   capture_output=True, text=True, timeout=300)
rows = {}
for line in p.stdout.splitlines():
    if line.count("|") == 3 and line.split("|")[0] in ("claude", "kilo", "antigravity"):
        n, inst, ver, probe = line.split("|")
        rows[n] = (inst == "1", ver.strip(), probe.strip())
out = []
for n in ("claude", "kilo", "antigravity"):
    inst, ver, probe = rows.get(n, (False, "", ""))
    if n == "claude":
        auth = probe.endswith("true")
    elif n == "kilo":
        auth = probe == "1"
    else:
        auth = probe == "0" and inst
    out.append({"agent": n, "cli": "agy" if n == "antigravity" else n, "installed": inst, "version": ver, "ready": bool(inst and auth),
                "note": ("ready: answered the smoke test" if n == "kilo" and auth else
                         "installed but not signed in" if inst and not auth else "not installed" if not inst else "ready")})
res = {"when": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "sprite": SPR["name"], "agents": out}
(ROOT / "assets/sprite_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
for a in out:
    print(("✅" if a["ready"] else "⚠️"), f'{a["agent"]:<12} cli={a["cli"]:<6} installed={a["installed"]!s:<5} {a["version"]:<22} {a["note"]}')
sys.exit(0 if all(a["installed"] for a in out) else 1)
