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

    def corrector():
        import http.server, threading, json as _j
        sys.path.insert(0, str(ROOT / "scripts"))
        import prompt_corrector as pc

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                req = _j.loads(self.rfile.read(n))
                if self.headers.get("Authorization") != "Bearer testkey":
                    self.send_response(401); self.end_headers(); return
                if "PAYMENT" in req["messages"][1]["content"]:
                    self.send_response(402); self.end_headers(); self.wfile.write(b"{}"); return
                out = _j.dumps({"choices": [{"message": {"content": "**Goal**: improved."}}], "usage": {"total_tokens": 9}}).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(out)
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        cfg = {"endpoint": f"http://127.0.0.1:{srv.server_port}/chat/completions", "model": "deepseek-flash"}
        ref = '🎯 [s2-x.html › #xgo] <button> "Compute"'
        ok1 = pc.enhance("make it nicer\n" + ref, "testkey", cfg)
        bad = pc.enhance("PAYMENT test", "testkey", cfg)
        rej = pc.enhance("x", "wrong", cfg)
        srv.shutdown()
        good = ok1["ok"] and ref in ok1["text"] and "improved" in ok1["text"]  # the element reference survives verbatim
        return good and not bad["ok"] and "402" in bad["error"] and not rej["ok"] and "401" in rej["error"], f"ok={ok1['ok']} ref kept={ref in ok1['text']} 402={bad['error']} 401={rej['error']}"
    check("runner", "prompt corrector (DeepSeek): rewrites, keeps 🎯 references, and falls back cleanly on 401/402", corrector)

    def framework():
        sys.path.insert(0, str(ROOT / "scripts"))
        import prompt_corrector as pc
        s = pc.SYSTEM
        return all(x in s for x in ("**Role**", "**Context**", "**Rules**", "**Constraints**", "product manager", "🎯 [")), "the corrector must ask for Role, Context, Rules, Constraints with Role = product manager and keep 🎯 references"
    check("runner", "prompt corrector uses the Role / Context / Rule / Constraint framework with Role = product manager", framework)

    def editable_prompt():
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        src = (ROOT / "scripts/notes_runner.py").read_text(encoding="utf-8")
        return all(x in js for x in ("maximize()", "<textarea id=\\\"d2pp\\\"", "d2reset", "edited by you")) and 'body.get("edited")' in src, "Sprite Implement must maximize the window and offer an editable enhanced prompt (reset, edited flag)"
    check("runner", "Sprite Implement maximizes the window and the enhanced prompt is editable before sending", editable_prompt)

    def log_fullscreen():
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "style.css").read_text(encoding="utf-8")
        return all(x in js for x in ("ensureLogBar", "requestFullscreen", "logFull")) and ".logfull" in css and ".logbar.onfull" in css, "the run log needs a full screen button, a fallback overlay and a visible exit button"
    check("runner", "the run log window has a full screen mode (button, Esc, visible exit, copy log)", log_fullscreen)

    def workbench_top():
        h = (ROOT / "site/s2-w.html").read_text(encoding="utf-8")
        i, j = h.find('id="wb-top"'), h.find("Do the work here")
        return 0 < i < j and "Sprite Implement" in h[i:j] and "evolves" in h[i:j] and 'data-fb="S2-W.top"' in h, "the Sprite-update and evolving-pipeline section must sit above the checklist intro with a feedback box"
    check("workbench", "workbench has the Sprite update and evolving pipeline section on top", workbench_top)

    def enhancer_wiring():
        src = (ROOT / "scripts/notes_runner.py").read_text(encoding="utf-8")
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        cfg = DATA["sprite"].get("enhancer", {})
        return ("DeepSeek" in cfg.get("model", "") and cfg.get("secret") == "day-2-deepinfra-api-key" and "prompt_corrector" in src
                and "Prompt enhanced with" in js and "d2enh" in js and "key" not in json.dumps(cfg).replace("secret", "").replace("api-key", "")), "enhancer config, runner call and the UI notice must exist; no key value in short.json"
    check("runner", "prompt enhancement is configured (model + Key Vault secret name), wired into the runner and shown in the UI", enhancer_wiring)

    def term_schema():
        import sqlite3, tempfile
        sys.path.insert(0, str(ROOT))
        from api.db import connect, STATUSES
        import migrate_short_json as mg
        db = pathlib.Path(tempfile.mkdtemp()) / "t.db"
        con = connect(db)
        r1 = mg.migrate(con, DATA)
        n1 = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("terms", "scenes", "history")]
        r2 = mg.migrate(con, DATA)
        n2 = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("terms", "scenes", "history")]
        bad = 0
        for q in ("INSERT INTO terms(slug,term,status,updated_at) VALUES('x','x','bogus','n')",
                  "INSERT INTO scenes(term_slug,n) VALUES('tokenization-embeddings',7)",
                  "INSERT INTO terms(slug,term,title_options,updated_at) VALUES('y','y','{bad','n')",
                  "INSERT INTO terms(slug,term,updated_at) VALUES('Bad Slug','x','n')"):
            try:
                con.execute(q); bad += 1
            except sqlite3.IntegrityError:
                pass
        ok = (r1 == "inserted" and r2 == "unchanged" and n1 == n2 and n1[:2] == [1, 6] and bad == 0
              and STATUSES == ("idea", "script", "clips", "voice", "rendered", "published"))
        return ok, f"migration {r1}/{r2}, counts {n1}->{n2}, constraints not enforced: {bad}"
    check("terms", "term database: schema constraints hold, short.json migrates once and is idempotent", term_schema)

    def db_not_in_git():
        c, o = sh(["git", "check-ignore", "data/terms.db"])
        return c == 0, "data/terms.db must be git-ignored"
    check("terms", "the database file is git-ignored", db_not_in_git)

    def bulk_core():
        import tempfile
        sys.path.insert(0, str(ROOT))
        from api.db import connect
        from api import changes as ch
        import migrate_short_json as mg
        con = connect(pathlib.Path(tempfile.mkdtemp()) / "t.db")
        mg.migrate(con, DATA)
        S = "tokenization-embeddings"
        good = [{"slug": S, "field": "status", "value": "clips"}, {"slug": S, "field": "scenes.1.vo", "value": "Hi"}, {"slug": S, "field": "title_options", "value": ["a", "b"]}]
        p = ch.preview(con, good)
        wrote = con.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        bad = ch.preview(con, good + [{"slug": S, "field": "status", "value": "live"}])
        refused = []
        for pid in (None, "0" * 20, bad["preview_id"]):
            try:
                ch.apply(con, good + [{"slug": S, "field": "status", "value": "live"}], pid); refused.append(False)
            except ValueError:
                refused.append(True)
        a = ch.apply(con, good, p["preview_id"], "eval")
        after = ch.current(con, S, "title_options"), ch.current(con, S, "status")
        ch.undo(con, a["change_set"])
        back = ch.current(con, S, "status"), ch.current(con, S, "scenes.1.vo") != "Hi", len(ch.current(con, S, "title_options")) == 5
        ok = (p["ok"] and not bad["ok"] and wrote == 8 and all(refused) and a["applied"] == 3 and after == (["a", "b"], "clips") and back == ("script", True, True))
        return ok, f"preview {p['ok']}, bad set refused {refused}, applied {a}, after {after}, undo {back}"
    check("terms", "bulk change set: preview writes nothing, apply needs the preview, one transaction, undo restores", bulk_core)

    def api_http():
        py = ROOT / ".venv/bin/python"
        if not py.exists():
            return True, "skipped: no .venv (python3 -m venv .venv && .venv/bin/pip install fastapi uvicorn httpx)"
        r = subprocess.run([str(py), str(ROOT / "evals/test_api.py")], capture_output=True, text=True, timeout=120)
        return r.returncode == 0, (r.stdout + r.stderr)[-500:]
    check("terms", "API over HTTP: public reads, token on every write, preview/apply/undo, conflicts, fail closed", api_http)

    def dict_pages():
        t, e = (ROOT / "site/terms.html").read_text(encoding="utf-8"), (ROOT / "site/term.html").read_text(encoding="utf-8")
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        leak = re.search(r"EDIT_TOKEN\s*=\s*[A-Za-z0-9]{8,}|Bearer [A-Za-z0-9_-]{8,}", t + e + js)
        ok = ('data-fb="S2-T"' in t and 'data-fb="S2-T.term"' in e and 'id="d2conn"' in t and 'id="d2term"' in e
              and all(x in js for x in ("/api/bulk/preview", "/api/bulk/apply", "/api/bulk/undo/", "d2token", "d2filter"))
              and "innerHTML" not in js[js.index("// ---- dictionary"):] and not leak)
        return ok, "dictionary pages need feedback boxes, the bulk calls, a token kept in localStorage, no innerHTML in the editor code (XSS) and no token in the files"
    check("terms", "dictionary pages: feedback boxes, bulk panel wiring, no innerHTML, no token in the site", dict_pages)

    def export_terms():
        import tempfile
        sys.path.insert(0, str(ROOT))
        from api.db import connect
        from api import changes as ch
        import migrate_short_json as mg, export_terms as ex
        from api.export import all_docs
        con = connect(pathlib.Path(tempfile.mkdtemp()) / "t.db")
        mg.migrate(con, DATA)
        out = pathlib.Path(tempfile.mkdtemp()) / "terms"
        (out.parent / "stale").mkdir()
        w1 = ex.sync(all_docs(con), out)
        w2 = ex.sync(all_docs(con), out)
        f = out / "tokenization-embeddings.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        ch.create_term(con, "attention", "Attention")
        drift = ex.sync(all_docs(con), out, check=True)[0]
        ex.sync(all_docs(con), out)
        (out / "gone.json").write_text("{}")
        removed = ex.sync(all_docs(con), out)[1]
        refuse = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/export_terms.py"), "--db", str(pathlib.Path(tempfile.mkdtemp()) / "empty.db"), "--out", str(out)], capture_output=True, text=True)
        committed = sorted((ROOT / "assets/terms").glob("*.json"))
        ok_files = bool(committed) and all(json.loads(x.read_text(encoding="utf-8")).get("slug") == x.stem and "Do not edit by hand" in x.read_text(encoding="utf-8") for x in committed)
        st = (ROOT / "site/terms.html").read_text(encoding="utf-8")
        ok = (w1[0] == ["tokenization-embeddings"] and w2 == ([], [], ["tokenization-embeddings"]) and doc["status"] == "script" and len(doc["scenes"]) == 6
              and "updated_at" not in doc and drift == ["attention"] and removed == ["gone"] and refuse.returncode != 0 and (out / "attention.json").exists()
              and ok_files and "Offline copy" in st and all(x.stem in st for x in committed))
        return ok, f"first {w1}, second {w2}, drift {drift}, removed {removed}, empty-db exit {refuse.returncode}, committed files ok {ok_files}"
    check("terms", "export: files match the database, unchanged files untouched, drift and stale files handled, empty source refused, site builds from them", export_terms)

    def fly_dictionary():
        import tempfile
        sys.path.insert(0, str(ROOT))
        from api.db import connect
        from api.export import all_docs, seed_if_empty, dumps
        ft, df = (ROOT / "fly.toml").read_text(encoding="utf-8"), (ROOT / "Dockerfile").read_text(encoding="utf-8")
        di, wf = (ROOT / ".dockerignore").read_text(encoding="utf-8"), (ROOT / ".github/workflows/backup-terms.yml").read_text(encoding="utf-8")
        deploys = [(ROOT / x).read_text(encoding="utf-8") for x in ("scripts/deploy_and_wait.py", "scripts/notes_runner.py", ".github/workflows/deploy.yml")]
        src = connect(pathlib.Path(tempfile.mkdtemp()) / "a.db")
        import migrate_short_json as mg
        mg.migrate(src, DATA)
        new_db = connect(pathlib.Path(tempfile.mkdtemp()) / "b.db")
        seeded = seed_if_empty(new_db, ROOT / "assets/terms")
        again = seed_if_empty(new_db, ROOT / "assets/terms")
        files = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "assets/terms").glob("*.json"))}
        same = [dumps(d) for d in all_docs(new_db).values()] == [dumps(files[k]) for k in sorted(files)]
        secrets_in_files = re.search(r"EDIT_TOKEN\s*=\s*[\"']?[A-Za-z0-9]{8,}", ft + df + wf)
        ok = ('destination = "/data"' in ft and "/api/health" in ft and "internal_port = 8080" in ft and "D2_DB=/data/terms.db" in df
              and "uvicorn" in df and "!api" in di and all("--ha=false" in x for x in deploys) and "export_terms.py --api" in wf
              and "contents: write" in wf and seeded == sorted(files) and again == [] and bool(seeded) and same and not secrets_in_files)
        return ok, f"volume+health+port in fly.toml, uvicorn image, --ha=false everywhere, nightly backup workflow, seed {seeded}/{again}, seeded export identical {same}"
    check("terms", "Fly setup: volume at /data, health check, one machine, API image, nightly backup, seed on empty volume, no token in files", fly_dictionary)

    def terms_bulk_core():
        import base64, socket, tempfile
        sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT))
        import terms_bulk as tb
        sentinel = "SENTINEL-TOKEN-0123456789abcdef"
        os.environ["D2_EDIT_TOKEN"] = sentinel
        try:
            exp = {"tokenization-embeddings": {"slug": "tokenization-embeddings", "term": "X"}}
            script = tb.build_terms_script("write analogies", exp, "echo agent")
            no_leak = sentinel not in script and "d2terms.json" in script and "d2-changes.json" in script and "tokenization-embeddings" in base64.b64decode(re.search(r"<<'D2B64'\n(.*)\nD2B64", script, re.S).group(1)).decode()
            b = lambda o: base64.b64encode(json.dumps(o).encode()).decode()
            fence = base64.b64encode(("```json\n" + json.dumps([{"slug": "a", "field": "hook", "value": "x"}]) + "\n```").encode()).decode()
            parse_ok = (len(tb.parse_changes(b([{"slug": "a", "field": "hook", "value": "x"}]))) == 1 and len(tb.parse_changes(b({"changes": [{"slug": "a"}]}))) == 1 and len(tb.parse_changes(fence)) == 1)
            bad = 0
            for x in ("", b([]), b("str"), base64.b64encode(b"{not json").decode(), base64.b64encode(b"x" * (tb.MAX_CHANGES_BYTES + 1)).decode()):
                try:
                    tb.parse_changes(x); bad += 1
                except ValueError:
                    pass
            hosts = []
            for u in ("https://evil.example.com", "http://day-2-short.fly.dev", "https://fly.dev.evil.com", "http://10.0.0.1:8960"):
                os.environ["D2_API"] = u
                try:
                    tb.api_base(); hosts.append(u)
                except RuntimeError:
                    pass
            os.environ["D2_API"] = "http://127.0.0.1:8960"
            fine = tb.api_base() == "http://127.0.0.1:8960"
            os.environ.pop("D2_API")
            fine = fine and tb.api_base().endswith(".fly.dev")
            base_ok = no_leak and parse_ok and bad == 0 and not hosts and fine
            py = ROOT / ".venv/bin/python"
            if not py.exists():
                return base_ok, f"(HTTP part skipped: no .venv) no_leak {no_leak}, parse {parse_ok}, bad inputs accepted {bad}, hosts accepted {hosts}"
            import migrate_short_json as mg
            from api.db import connect
            dbp = pathlib.Path(tempfile.mkdtemp()) / "t.db"
            mg.migrate(connect(dbp), DATA)
            sk = socket.socket(); sk.bind(("127.0.0.1", 0)); port = sk.getsockname()[1]; sk.close()
            env = dict(os.environ, D2_DB=str(dbp), EDIT_TOKEN=sentinel, D2_SITE=str(pathlib.Path(tempfile.mkdtemp())))
            srv = subprocess.Popen([str(py), "-m", "uvicorn", "api.main:app", "--port", str(port), "--log-level", "error"], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.environ["D2_API"] = f"http://127.0.0.1:{port}"
            try:
                for _ in range(40):
                    try:
                        urllib.request.urlopen(os.environ["D2_API"] + "/api/health", timeout=1); break
                    except Exception:
                        time.sleep(0.25)
                S = "tokenization-embeddings"
                got = tb.fetch_export()
                good = [{"slug": S, "field": "analogy", "value": "A map of meaning"}, {"slug": S, "field": "scenes.2.on_screen_text", "value": "1 → 1,536 DIMS"}]
                pid, prev = tb.stage(good, "test")
                lines = tb.diff_lines(prev)
                untouched = connect(dbp).execute("SELECT analogy FROM terms").fetchone()[0] == ""
                pend = tb.get_pending(pid)
                badpid, badprev = tb.stage([{"slug": S, "field": "status", "value": "live"}])
                r = tb.approve(pid)
                changed = connect(dbp).execute("SELECT analogy FROM terms").fetchone()[0] == "A map of meaning"
                twice = False
                try:
                    tb.approve(pid)
                except ValueError:
                    twice = True
                u = tb.undo(r["change_set"])
                back = connect(dbp).execute("SELECT analogy FROM terms").fetchone()[0] == ""
                pid2, _ = tb.stage(good)
                c2 = connect(dbp); c2.execute("UPDATE terms SET analogy='changed behind your back'"); c2.commit()
                stale = False
                try:
                    tb.approve(pid2)
                except ValueError:
                    stale = True
                nothing = connect(dbp).execute("SELECT analogy FROM terms").fetchone()[0] == "changed behind your back"
                pid3, _ = tb.stage(good)
                rj = tb.reject(pid3)["state"] == "rejected"
                rej_block = False
                try:
                    tb.approve(pid3)
                except ValueError:
                    rej_block = True
                ok = (base_ok and S in got and pid and len(lines) == 2 and untouched and pend["state"] == "pending" and badpid is None and not badprev["ok"]
                      and changed and twice and r["applied"] == 2 and back and u["reverted"] == 2 and stale and nothing and rj and rej_block)
                return ok, f"base {base_ok} got {S in got} pid {bool(pid)} lines {len(lines)} untouched {untouched} pend {pend['state']} bad {badpid is None and not badprev['ok']} applied {r['applied']} reverted {u['reverted']} | stage/apply/undo ok? changed {changed} twice-refused {twice} back {back} stale-refused {stale} nothing-written {nothing} reject {rj}/{rej_block}"
            finally:
                srv.terminate()
                os.environ.pop("D2_API", None)
        finally:
            os.environ.pop("D2_EDIT_TOKEN", None)
    check("terms", "sprite bulk updates: token never in the sprite script, proposal staged, owner approval required, stale/duplicate/rejected sets refused, undo works", terms_bulk_core)

    def terms_runner_wiring():
        src = (ROOT / "scripts/notes_runner.py").read_text(encoding="utf-8")
        js = (ROOT / "app.js").read_text(encoding="utf-8")
        sk = (ROOT / ".claude/skills/sprite-run/SKILL.md").read_text(encoding="utf-8")
        tbsrc = (ROOT / "scripts/terms_bulk.py").read_text(encoding="utf-8")
        ok = (all(x in src for x in ("/terms/run", "/terms/approve", "/terms/undo", "run_terms_job", "terms_token")) and all(x in js for x in ("/terms/run", "/terms/approve", "/terms/undo", "PENDING-ID"))
              and "Bulk dictionary updates" in sk and "never" in sk.split("Bulk dictionary updates")[1].lower()
              and "build_terms_script" in tbsrc and "Authorization" not in src and "Bearer" not in js[js.index("function sprite()"):js.index("function bulk()")])
        return ok, "runner endpoints, page buttons and the skill section must exist; the page code for the sprite flow never handles a token"
    check("terms", "sprite flow is wired: runner endpoints, Ask-the-Sprite card, skill section; no token handling in the sprite card", terms_runner_wiring)

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
