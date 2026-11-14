#!/usr/bin/env python3
"""Build the site, deploy it to Fly.io, verify HTTP 200, open it in Google Chrome.

  python3 scripts/deploy_and_wait.py [page.html]

The real site lives in site/ (built by scripts/build_short_site.py) and is served from Fly.io
(app and URL in assets/short.json > deploy). The old GitHub Pages address only holds redirect
stubs, so `git push origin main` keeps them in sync but is not what publishes the site.
"""
import json, pathlib, subprocess, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEP = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))["deploy"]


def run(cmd):
    print("▶️", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"❌ {cmd[0]} failed ({r.returncode})")


def ok(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "DeployCheck/1.0"}), timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    url = DEP["url"] + (sys.argv[1].lstrip("/") if len(sys.argv) > 1 else "s2-w.html")
    run([sys.executable, "-I", "scripts/build_short_site.py"])
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import stamp
    print("🕒 deploy stamp", stamp.write_stamp()["at"])
    run(["fly", "deploy", "--remote-only", "-a", DEP["fly_app"]])
    print(f"🌐 Verifying {url} …")
    for _ in range(10):
        if ok(url):
            print("✅ HTTP 200")
            break
        time.sleep(3)
    else:
        print("⚠️ not 200 yet, opening anyway")
    subprocess.run(["open", "-a", "Google Chrome", url])
    print("✨ Done. Remember: git commit + push main keeps the repo and the Pages redirect stubs current.")


if __name__ == "__main__":
    main()
