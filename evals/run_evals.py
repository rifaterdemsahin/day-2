#!/usr/bin/env python3
"""Evals for the site, the notes runner and the notes → sprite → redeploy loop.

  python3 evals/run_evals.py            # offline: build, pages, stubs, security, command syntax (seconds)
  python3 evals/run_evals.py --live     # + Fly.io pages, Pages redirects, sprite reachable, agent dry run
  python3 evals/run_evals.py --e2e      # + one real note through the runner, verified live, then reverted

Writes evals/results.json (the S2-EV page shows it). Exit code 1 if any check fails.
"""
import shutil, argparse, json, os, pathlib, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error

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
    skipped = ok and str(detail).startswith("SKIP")
    print(("⏭️" if skipped else "✅" if ok else "❌"), f"[{group}]", name, ("— " + str(detail)[:160]) if detail and (not ok or skipped) else "")


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
        import hashlib

        def tree():
            return {str(p.relative_to(ROOT / "site")): hashlib.md5(p.read_bytes()).hexdigest()
                    for p in sorted((ROOT / "site").rglob("*")) if p.is_file() and p.name != "deployed.json"}
        before = tree()
        sh([sys.executable, "-I", "scripts/build_short_site.py"])
        after = tree()
        return before == after and len(before) > 30, f"second build changed: {[k for k in after if before.get(k) != after[k]][:3]}"
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
        h = (ROOT / "index.html").read_text(encoding="utf-8")
        tracked = sh(["git", "ls-files", "*.html"])[1].split()
        ok = FLY in h and "refresh" in h and tracked == ["index.html"]
        return ok, f"index.html redirects: {FLY in h and 'refresh' in h}; tracked html: {tracked}"
    check("redirect", "the only tracked html is the root index.html that redirects to the Fly.io site", stubs)

    def untracked_generated():
        t = sh(["git", "ls-files"])[1].split("\n")
        bad = [x for x in t if x.startswith("site/") or x == "MASTER_SPEC.md" or x == "deployed.json"]
        return not bad, "tracked generated files: " + ", ".join(bad[:5])
    check("refactor", "generated files (site/, MASTER_SPEC.md, deployed.json) are not tracked", untracked_generated)

    def spec_split():
        p = ROOT / "spec"
        names = sorted(x.name for x in p.glob("*.md"))
        full = (ROOT / "MASTER_SPEC.md").read_text(encoding="utf-8")
        ok = names == ["part-a-long.md", "part-b-short.md", "rules.md"] and "GENERATED" in full[:200] and "B7." not in "".join((p / n).read_text(encoding="utf-8") for n in names)
        return ok, f"spec files {names}"
    check("refactor", "spec is split into 3 files, B7 removed, MASTER_SPEC.md is generated", spec_split)

    def briefing():
        s = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        toks = len(s) // 4
        need = ["short.json", "spec/rules.md", "spec/part-b-short.md", "Do NOT read `MASTER_SPEC.md`"]
        return toks <= 1500 and all(x in s for x in need), f"{toks} tokens (limit 1500); missing: {[x for x in need if x not in s]}"
    check("refactor", "CLAUDE.md is at most ~1.5k tokens and points to short.json and one spec file at a time", briefing)

    def page_modules():
        import re
        mods = sorted((ROOT / "pages").glob("*.py"))
        bad = [m.name for m in mods if m.name not in ("__init__.py", "_lib.py") and "def build():" not in m.read_text(encoding="utf-8")]
        biggest = max(len(m.read_text(encoding="utf-8")) // 4 for m in mods)
        return not bad and len(mods) >= 20 and biggest < 7000, f"{len(mods)} modules, largest ~{biggest} tokens, without build(): {bad}"
    check("refactor", "one module per page under pages/ (each with build()), none larger than ~7k tokens", page_modules)

    def routing():
        import notes_runner as nr
        small = nr.route("📄 S2-07 Pinned comment: end it with the word Hint")
        med = nr.route("x " * 400)  # 800 chars, no structural words
        big = nr.route("x " * 1500)
        heavy = nr.route("Please refactor the Dockerfile and the generator")
        man = nr.route("short note", "claude", "haiku")
        ok = (small[:2] == ("kilo", "default") and med[:2] == ("claude", "haiku") and big[:2] == ("claude", "default")
              and heavy[:2] == ("claude", "default") and man == ("claude", "haiku", "manual choice"))
        return ok, f"small={small[:2]} medium={med[:2]} big={big[:2]} heavy={heavy[:2]} manual={man[:2]}"
    check("runner", "size-based routing: small to kilo, medium to claude haiku, large/structural to claude, manual override wins", routing)

    def claude_json():
        import notes_runner as nr
        c = nr.agent_cmd("claude", False, "haiku")
        return "--output-format json" in c and "--model claude-haiku-5-5" in c and "--output-format json" in nr.agent_cmd("claude", False), c[:160]
    check("runner", "claude runs with --output-format json (and the cheap model when routed)", claude_json)

    def usage_in_report():
        import notes_runner as nr
        out = []
        nr.report({"agent": "claude", "model": "haiku", "why": "t", "usage": {"in": 2, "out": 4, "cache_read": 9074, "cache_write": 11140, "usd": 0.0455, "turns": 1}}, None, out.append)
        t = "\n".join(out)
        return "tokens: input 2" in t and "$0.0455" in t and "RESULT" in t, t[-200:]
    check("runner", "RESULT block prints input/output tokens and USD cost", usage_in_report)

    def workflows():
        w = ROOT / ".github/workflows"
        d = (w / "deploy.yml").read_text(encoding="utf-8")
        h = (w / "health.yml").read_text(encoding="utf-8")
        ok = ("secrets.FLY_API_TOKEN" in d and "flyctl deploy" in d and "branches: [main]" in d
              and "schedule:" in h and "run_evals.py --live" in h and "sprite_check.py" in h)
        return ok, "deploy.yml needs FLY_API_TOKEN + push to main; health.yml needs schedule + live evals + sprite_check"
    check("ci", "deploy-on-push and scheduled health workflows exist", workflows)

    def production_status():
        import subprocess as sp
        d = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
        pr = d.get("production", {})
        cl = pr.get("clips", {})
        ids = [s["clips"][0] for s in d["scenes"]]
        shape = sorted(cl) == sorted(ids) and all(set(v) == {"clip", "voice", "render"} for v in cl.values())
        r = sp.run([sys.executable, "-I", str(ROOT / "scripts/sync_status.py")], cwd=ROOT, capture_output=True, text=True)
        html = (ROOT / "site/s2-w.html").read_text(encoding="utf-8")
        return shape and r.returncode == 0 and "window.PROD=" in html and "Production status" in html, f"shape ok: {shape}; sync exit {r.returncode}; page shows status: {'Production status' in html}"
    check("production", "per-clip clip/voice/render status lives in short.json, syncs from disk and shows on the Workbench", production_status)

    def sync_hook():
        p = json.loads((ROOT / "remotion/package.json").read_text(encoding="utf-8"))["scripts"]
        return "sync_status.py" in p["sync"] and "npm run sync" in p["studio"] and "npm run sync" in p["render"], "remotion scripts must call sync_status.py"
    check("production", "npm run sync|studio|render refreshes the production status", sync_hook)

    def race_guard():
        import notes_runner as nr
        d = tempfile.mkdtemp()
        sh(["git", "init", "-q", "-b", "main"], cwd=d)
        sh(["git", "-c", "user.email=e@e", "-c", "user.name=e", "commit", "-q", "--allow-empty", "-m", "a"], cwd=d)
        base = sh(["git", "rev-parse", "HEAD"], cwd=d)[1].strip()
        clean = nr.repo_unchanged(base, d)[0]
        pathlib.Path(d, "x.txt").write_text("dirty")
        dirty = nr.repo_unchanged(base, d)[0]
        sh(["git", "add", "-A"], cwd=d)
        sh(["git", "-c", "user.email=e@e", "-c", "user.name=e", "commit", "-q", "-m", "b"], cwd=d)
        moved = nr.repo_unchanged(base, d)[0]
        shutil.rmtree(d)
        return clean and not dirty and not moved, f"clean={clean} dirty={dirty} moved={moved}"
    check("runner", "a patch is not applied if the repo changed (dirty or new commit) while the agent worked", race_guard)

    def no_conflicts():
        files = sh(["git", "ls-files"])[1].split("\n")
        bad = []
        for f in files:
            p = ROOT / f
            if not p.is_file() or p.suffix not in (".json", ".py", ".md", ".js", ".css", ".yml", ".html"):
                continue
            t = p.read_text(encoding="utf-8", errors="ignore")
            if "\n<<<<<<< " in t or "\n>>>>>>> " in t:
                bad.append(f)
            if p.suffix == ".json":
                try:
                    json.loads(t)
                except Exception:
                    bad.append(f + " (invalid JSON)")
        return not bad, "conflict markers or invalid JSON: " + ", ".join(bad[:5])
    check("build", "no merge-conflict markers and every tracked JSON file parses", no_conflicts)

    def preview_mode():
        import notes_runner as nr
        src = (ROOT / "scripts/notes_runner.py").read_text(encoding="utf-8")
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        p = nr.task_prompt("PREVIEW-NOTE", False)
        return ("body.get(\"preview\")" in src and "PREVIEW-NOTE" in p and "d2send" in js and "pclear" in js), "preview endpoint, Send/Cancel box and Clear notes button must exist"
    check("runner", "run shows the exact prompt first (preview mode + Send/Cancel) and the panel has Clear notes", preview_mode)

    def picker():
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        fb = (ROOT / "site/feedback.html").read_text(encoding="utf-8")
        cm = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        return all(x in js for x in ("ppick", "refOf", "pickbar")) and "Object picker" in fb and "🎯" in cm and len(cm) // 4 <= 1500, "picker code, feedback-page docs and CLAUDE.md note must exist"
    check("feedback", "object picker exists, is documented on the feedback page and in CLAUDE.md", picker)

    def docker_builds_site():
        d = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        return "build_short_site.py" in d and "COPY --from=build" in d, "Dockerfile must compile site/ in a build stage"
    check("refactor", "Dockerfile compiles site/ inside the image", docker_builds_site)

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
        s, h = get(OLD)
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
    check("sprite", "sprite is reachable (sprite exec)", sprite_up if shutil.which("sprite") else (lambda: (True, "SKIP: sprite CLI not available here (CI)")))

    def vault_ok():
        c, o = sh(["az", "keyvault", "secret", "show", "--vault-name", "dp-kv-deliverypilot", "--name", "kilo-api-key", "--query", "attributes.enabled", "-o", "tsv"])
        return o.strip() == "true", o[-100:]
    check("sprite", "agent key is readable from Azure Key Vault (value never printed)", vault_ok if shutil.which("az") else (lambda: (True, "SKIP: az CLI not available here (CI)")))

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
    check("agent", "agent (kilo) runs on the sprite in plan mode and returns", dry_run if shutil.which("sprite") else (lambda: (True, "SKIP: sprite CLI not available here (CI)")))

    def installs():
        c, o = sh([sys.executable, "-I", str(ROOT / "scripts/sprite_check.py")])
        return c == 0, o[-300:]
    check("agent", "claude, kilo and antigravity (agy) CLIs are installed on the sprite", installs if shutil.which("sprite") else (lambda: (True, "SKIP: sprite CLI not available here (CI)")))


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
