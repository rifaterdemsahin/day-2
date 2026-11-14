#!/usr/bin/env python3
"""Evals for the site, the notes runner and the notes → sprite → redeploy loop.

  python3 evals/run_evals.py            # offline: build, pages, stubs, security, command syntax (seconds)
  python3 evals/run_evals.py --live     # + Fly.io pages, Pages redirects, sprite reachable, agent dry run
  python3 evals/run_evals.py --e2e      # + one real note through the runner, verified live, then reverted

Writes evals/results.json (the S2-EV page shows it). Exit code 1 if any check fails.
"""
import argparse, json, os, pathlib, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
DATA = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
FLY, OLD = DATA["deploy"]["url"], DATA["deploy"]["old_pages"]
RUNNER_PORT = DATA["sprite"]["runner_port"]
RESULTS = []


def check(group, name, fn):
    t = time.time()
    try:
        r = fn()
        ok, detail = (r if isinstance(r, tuple) else (bool(r), ""))
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    RESULTS.append({"group": group, "name": name, "ok": ok, "detail": str(detail)[:300], "s": round(time.time() - t, 1)})
    print(("✅" if ok else "❌"), f"[{group}]", name, ("— " + str(detail)[:160]) if detail and not ok else "")


def sh(cmd, **kw):
    r = subprocess.run(cmd, cwd=kw.pop("cwd", ROOT), capture_output=True, text=True, **kw)
    return r.returncode, (r.stdout + r.stderr)


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "evals/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def site_pages():
    return sorted(p.name for p in (ROOT / "site").glob("*.html"))


# ------------------------------------------------------------------ offline
def offline():
    import notes_runner as nr

    def build_idempotent():
        c, o = sh([sys.executable, "-I", "scripts/build_short_site.py"])
        if c:
            return False, o[-200:]
        before = sh(["git", "status", "--porcelain"])[1]
        sh([sys.executable, "-I", "scripts/build_short_site.py"])
        after = sh(["git", "status", "--porcelain"])[1]
        return before == after, "second build changed files"
    check("build", "builds without error and is idempotent", build_idempotent)

    def pages_have_core():
        bad = []
        for n in site_pages():
            h = (ROOT / "site" / n).read_text(encoding="utf-8")
            for need in ('id="nav"', "app.js", "<h1>"):
                if need not in h:
                    bad.append(f"{n} missing {need}")
        return not bad, "; ".join(bad[:4])
    check("pages", "every page has menu, notes script (app.js) and a heading", pages_have_core)

    def step_pages_have_feedback():
        bad = [n for n in site_pages() if n not in ("spec.html", "readme.html", "feedback.html", "analytics.html", "development.html")
               and 'class="fb"' not in (ROOT / "site" / n).read_text(encoding="utf-8")]
        return not bad, "no feedback box on: " + ", ".join(bad)
    check("pages", "every step page carries feedback buttons", step_pages_have_feedback)

    def emoji_headings():
        bad = [n for n in site_pages() if not re.search(r"<h1>[^<]*[\U0001F000-\U0001FAFF☀-➿]", (ROOT / "site" / n).read_text(encoding="utf-8"))]
        return not bad, "no emoji in h1: " + ", ".join(bad[:5])
    check("pages", "emojis in every heading (standing rule)", emoji_headings)

    def workbench():
        h = (ROOT / "site/s2-w.html").read_text(encoding="utf-8")
        return all(x in h for x in ('data-fb="S2-W.c1"', 'id="next"', 'data-check="S2-04.c1"', "target=\"d2-flow\"")), "workbench missing pieces"
    check("workbench", "workbench has next-up, per-clip feedback, shared ticks, reusable tab links", workbench)

    def stubs():
        bad = []
        for n in site_pages() + ["404.html"]:
            h = (ROOT / n).read_text(encoding="utf-8")
            if FLY not in h or "refresh" not in h:
                bad.append(n)
        return not bad, "stub not redirecting: " + ", ".join(bad[:5])
    check("redirect", "every root page is a stub redirecting to the Fly.io site", stubs)

    def panel_wired():
        a = (ROOT / "app.js").read_text(encoding="utf-8")
        return all(x in a for x in ("pagent", "runOnSprite", "127.0.0.1", "spriteCmd")) and "window.SPRITE" in (ROOT / "site/index.html").read_text(encoding="utf-8")
    check("notes", "notes panel has agent picker, 🚀 run, command fallback and the sprite config", panel_wired)

    def port_consistent():
        return f'"runner_port":{RUNNER_PORT}' in (ROOT / "site/index.html").read_text(encoding="utf-8").replace(" ", "")
    check("notes", "runner port in the page equals short.json", port_consistent)

    def no_secrets():
        pats = re.compile(r"(sk-ant-[A-Za-z0-9_-]{20,}|fal_sk_[0-9a-f]{8,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|[0-9a-f]{32}:[0-9a-f]{32}|erdem-391/[0-9a-z/-]{30,})")
        hits = []
        for f in sh(["git", "ls-files"])[1].splitlines():
            p = ROOT / f
            if p.suffix in (".png", ".jpeg", ".jpg", ".mp3", ".wav", ".mp4", ".lock") or not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            if pats.search(p.read_text(encoding="utf-8", errors="ignore")):
                hits.append(f)
        return not hits, "possible secret in: " + ", ".join(hits)
    check("security", "no API keys or tokens in tracked files", no_secrets)

    def argv_clean():
        src = (ROOT / "scripts/notes_runner.py").read_text(encoding="utf-8")
        bad = [m for m in re.findall(r"\[\"sprite\"[^\]]*\]", src) if "val" in m or "secret" in m]
        return "--env" not in src and "--token" not in src and not bad, "a secret may reach a command line"
    check("security", "runner never puts keys on a command line (stdin only)", argv_clean)

    def script_syntax():
        s = nr.build_script("note with 'quotes' and \"dq\" and $(echo no)", "kilo", False, "export KILO_API_KEY=dummy\n")
        c, o = sh(["bash", "-n"], input=s) if False else (subprocess.run(["bash", "-n"], input=s, text=True, capture_output=True).returncode, "")
        return c == 0, "bash -n failed"
    check("runner", "generated sprite script is valid bash and keeps quoted notes literal", script_syntax)

    def script_stdin_safe():
        for ag in ("kilo", "claude", "antigravity"):
            if "</dev/null" not in nr.build_script("x", ag, False):
                return False, f"{ag} may swallow the script on stdin"
        return True, ""
    check("runner", "agents run with stdin from /dev/null (regression: kilo swallowed the script)", script_stdin_safe)

    def patch_excludes():
        d = tempfile.mkdtemp()
        sh(["git", "init", "-q"], cwd=d)
        for f in ("assets", "site"):
            os.makedirs(f"{d}/{f}")
        pathlib.Path(d, "assets/short.json").write_text("{}")
        pathlib.Path(d, "site/index.html").write_text("a")
        pathlib.Path(d, "s2-01.html").write_text("a")
        sh(["git", "-c", "user.name=e", "-c", "user.email=e@e", "add", "-A"], cwd=d)
        sh(["git", "-c", "user.name=e", "-c", "user.email=e@e", "commit", "-qm", "i"], cwd=d)
        pathlib.Path(d, "assets/short.json").write_text('{"a":1}')
        pathlib.Path(d, "site/index.html").write_text("b")
        pathlib.Path(d, "s2-01.html").write_text("b")
        pathlib.Path(d, "new.txt").write_text("n")
        sh(["git", "add", "-A"], cwd=d)
        c, o = sh(["bash", "-c", f"git diff --cached --name-only -- . {nr.PATCH_EXCLUDES}"], cwd=d)
        shutil.rmtree(d)
        names = sorted(o.split())
        return names == ["assets/short.json", "new.txt"], f"got {names}"
    check("runner", "patch contains source changes only (no generated site/ or stub html)", patch_excludes)

    # runner HTTP security, on a throw-away port
    port = 8961
    p = subprocess.Popen([sys.executable, "scripts/notes_runner.py", "--port", str(port)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    try:
        def call(method, path="/", origin=None, host=None, body=None, ctype="application/json"):
            import http.client
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
            h = {"Content-Type": ctype}
            if origin:
                h["Origin"] = origin
            if host:
                h["Host"] = host
            c.request(method, path, body=body, headers=h)
            return c.getresponse().status
        good = FLY.rstrip("/")
        check("runner-http", "health answers the site's own origin", lambda: call("GET", "/", good) == 200)
        check("runner-http", "POST from a foreign origin is refused (403)", lambda: call("POST", "/run", "https://evil.example", body='{"notes":"x"}') == 403)
        check("runner-http", "POST without an Origin header is refused (403)", lambda: call("POST", "/run", None, body='{"notes":"x"}') == 403)
        check("runner-http", "wrong Host header is refused (DNS-rebinding guard)", lambda: call("POST", "/run", good, host="evil.example", body='{"notes":"x"}') == 403)
        check("runner-http", "non-JSON content type is refused", lambda: call("POST", "/run", good, body="notes=x", ctype="text/plain") == 403)
        check("runner-http", "empty notes are rejected (400)", lambda: call("POST", "/run", good, body='{"notes":"   "}') == 400)
        check("runner-http", "unknown agent is rejected (400)", lambda: call("POST", "/run", good, body='{"notes":"x","agent":"rm -rf"}') == 400)
        check("runner-http", "oversized notes are rejected (400)", lambda: call("POST", "/run", good, body=json.dumps({"notes": "x" * 30000})) == 400)
    finally:
        p.terminate()


# ------------------------------------------------------------------ live
def live():
    for n in ["", "s2-w.html", "s2-sp.html", "s2-r.html", "s2-07.html", "iterations.html", "style.css", "app.js", "assets/short.json"]:
        check("fly", f"Fly.io serves /{n}", lambda n=n: (get(FLY + n)[0] == 200, f"status {get(FLY + n)[0]}"))

    def pages_redirect():
        s, h = get(OLD + "s2-w.html")
        return s == 200 and FLY in h and "refresh" in h, f"status {s}, stub target present: {FLY in h}"
    check("redirect", "old GitHub Pages address redirects to Fly.io", pages_redirect)

    def deployed_matches_repo():
        s, h = get(FLY + "iterations.html")
        top = json.loads((ROOT / "assets/iterations.json").read_text(encoding="utf-8"))[0]["v"]
        return top in h, f"live page lacks latest iteration {top}"
    check("fly", "live site contains the latest iteration entry (deployed = repo)", deployed_matches_repo)

    def sprite_up():
        c, o = sh(["sprite", "exec", "-s", DATA["sprite"]["name"], "--no-stdin", "--", "bash", "-lc", "echo SPRITE_OK"], timeout=120)
        return "SPRITE_OK" in o, o[-120:]
    check("sprite", "sprite is reachable (sprite exec)", sprite_up)

    def vault_ok():
        c, o = sh(["az", "keyvault", "secret", "show", "--vault-name", "dp-kv-deliverypilot", "--name", "kilo-api-key", "--query", "attributes.enabled", "-o", "tsv"])
        return o.strip() == "true", o[-100:]
    check("sprite", "agent key is readable from Azure Key Vault (value never printed)", vault_ok)

    def dry_run():
        import notes_runner as nr
        lines = []
        nr.LOCK.acquire()
        nr.LOCK.release()
        try:
            res = nr.run_job("EVAL dry run: describe what S2-07 contains. Change nothing.", "kilo", True, lines.append)
        except Exception as e:
            return False, str(e)[:200]
        return any("dry run finished" in l for l in lines), "\n".join(lines[-3:])
    check("agent", "agent (kilo) runs on the sprite in plan mode and returns", dry_run)


# ------------------------------------------------------------------ end to end
def e2e():
    import notes_runner as nr
    cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))["e2e"]
    for case in cases:
        ts = str(int(time.time()))
        notes = case["notes"].replace("{ts}", ts)
        lines = []
        started = sh(["git", "rev-parse", "HEAD"])[1].strip()

        def run():
            nr.run_job(notes, case["agent"], False, lambda s: lines.append(s))
            return True, ""
        check("e2e", f"[{case['id']}] note → sprite agent → patch → build → commit → push → Fly deploy", run)
        for ex in case.get("expect_files", []):
            check("e2e", f"[{case['id']}] repo file {ex['file']} contains the change",
                  lambda ex=ex: (ex["contains"].replace("{ts}", ts) in (ROOT / ex["file"]).read_text(encoding="utf-8"), "not found"))
        for ex in case.get("expect_live", []):
            check("e2e", f"[{case['id']}] live {ex['page']} shows the change",
                  lambda ex=ex: (ex["contains"].replace("{ts}", ts) in get(FLY + ex["page"])[1], "not live"))
        if case.get("revert"):
            def revert():
                head = sh(["git", "rev-parse", "HEAD"])[1].strip()
                if head == started:
                    return False, "nothing to revert"
                c, o = sh(["git", "revert", "--no-edit", head])
                if c:
                    return False, o[-200:]
                sh([sys.executable, "-I", "scripts/build_short_site.py"])
                sh(["git", "add", "-A"])
                sh(["git", "commit", "-qm", "🧹 evals: rebuild after revert"])
                c, o = sh(["git", "push", "origin", "main"])
                c2, o2 = sh(["fly", "deploy", "--remote-only", "-a", DATA["deploy"]["fly_app"]], timeout=900)
                gone = ts not in get(FLY + case["expect_live"][0]["page"])[1]
                return c == 0 and c2 == 0 and gone, "revert pushed/deployed? " + o[-80:] + o2[-80:]
            check("e2e", f"[{case['id']}] eval change reverted and redeployed (no pollution)", revert)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--e2e", action="store_true")
    a = ap.parse_args()
    offline()
    if a.live or a.e2e:
        live()
    if a.e2e:
        e2e()
    ok = sum(r["ok"] for r in RESULTS)
    out = {"when": time.strftime("%Y-%m-%d %H:%M"), "mode": "e2e" if a.e2e else ("live" if a.live else "offline"), "passed": ok, "total": len(RESULTS), "results": RESULTS}
    (ROOT / "evals/results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{'🎉' if ok == len(RESULTS) else '⚠️'} {ok}/{len(RESULTS)} checks passed ({out['mode']})")
    sys.exit(0 if ok == len(RESULTS) else 1)
