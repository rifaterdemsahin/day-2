#!/usr/bin/env python3
"""Local runner behind the 🚀 button in the notes panel.

  python3 scripts/notes_runner.py            # listens on 127.0.0.1:8947

Flow for one run (everything streams back to the notes panel):
  1. checks this repo is clean and in sync with origin/main
  2. reads the agent's key from Azure Key Vault (az login) into memory only
  3. runs the agent (claude | kilo | antigravity) on the Fly.io Sprite, in a fresh clone, with the
     notes as the task; the key travels on stdin, never in a command line or a file
  4. brings back only a patch (no git token goes to the sprite)
  5. applies it here, rebuilds, commits, pushes main, deploys to Fly.io, verifies HTTP 200

Safety: binds to loopback only, accepts only the site's own origins (CORS + Origin check),
checks the Host header, one run at a time, notes capped, secrets scrubbed from streamed output.
"""
import argparse, base64, json, pathlib, shlex, subprocess, sys, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
DEP, SPR = DATA["deploy"], DATA["sprite"]
VAULT = "dp-kv-deliverypilot"
KEYS = {"claude": (None, None),  # uses its own /login on the sprite; the vault key returned 401 and would override that login
         "kilo": ("KILO_API_KEY", "kilo-api-key"), "antigravity": (None, None)}
MAX_NOTES = 20000
LOCK = threading.Lock()


def origin_of(url):
    u = urlparse(url)
    return f"{u.scheme}://{u.netloc}"


LOCAL_PORT = 8950  # scripts/serve_local.py
ALLOWED = {origin_of(DEP["url"]), origin_of(DEP["old_pages"]),
           f"http://127.0.0.1:{LOCAL_PORT}", f"http://localhost:{LOCAL_PORT}"}


def agent_cmd(agent, dry):
    if agent == "claude":
        mode = "plan" if dry else "acceptEdits"
        tools = '"Edit Write Read Glob Grep Bash(python3:*) Bash(git status:*) Bash(git diff:*) Bash(ls:*) Bash(cat:*)"'
        return f'claude -p "$(cat /tmp/d2prompt.txt)" --permission-mode {mode} --allowedTools {tools}'
    if agent == "kilo":
        ag = "--agent plan" if dry else "--auto"
        return ('export PATH=$(npm prefix -g)/bin:$PATH; command -v kilo >/dev/null || npm i -g @kilocode/cli >/dev/null 2>&1; '
                f'kilo run -m {SPR.get("kilo_model", "kilo/kilo-auto/free")} {ag} "$(cat /tmp/d2prompt.txt)"')
    if agent == "antigravity":
        mode = "plan" if dry else "accept-edits"
        return f'agy -p "$(cat /tmp/d2prompt.txt)" --mode {mode}'
    raise ValueError(agent)


def task_prompt(notes, dry):
    return f"""You are working in a fresh clone of the day-2 repo (current folder). Do this:
1. Read MASTER_SPEC.md (standing rules and Part B). Facts live in assets/short.json and scripts/build_short_site.py; never hand-edit generated files (site/, root *.html).
2. Apply the owner's feedback below with the smallest correct change. Keep emojis and the feedback buttons on every page.
3. Run: python3 -I scripts/build_short_site.py and fix any error.
4. Add ONE new entry at the top of assets/iterations.json (next version number, today's date, codes, change, why = the owner's feedback, status "🚀 deployed"), update MASTER_SPEC.md / README.md only if a rule changed, then rebuild.
5. Do NOT commit, push or deploy: the runner does that. Never touch secrets or media.
6. Finish with 5 lines: what changed and in which files.
{"DRY RUN: plan only, change nothing." if dry else ""}

OWNER FEEDBACK:
{notes}
"""


def vault_secret(name):
    r = subprocess.run(["az", "keyvault", "secret", "show", "--vault-name", VAULT, "--name", name, "--query", "value", "-o", "tsv"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode or not r.stdout.strip():
        raise RuntimeError(f"Key Vault: could not read {name} (is `az login` valid?)")
    return r.stdout.strip()


def sh(cmd, cwd=ROOT, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()


PATCH_EXCLUDES = "':!site' ':!*.html' ':!404.html'"


def build_script(notes, agent, dry, prelude=""):
    """The bash script piped to `sprite exec ... bash -l -s` (secrets only in `prelude`, only on stdin)."""
    return (prelude + "set -e\nexport CI=1\nD=$HOME/day-2\n"
            f"[ -d $D/.git ] || git clone -q {SPR['repo']} $D\ncd $D\n"
            "git fetch -q origin main && git reset -q --hard origin/main && git clean -fdq\n"
            "cat > /tmp/d2prompt.txt <<'D2PROMPT'\n" + task_prompt(notes, dry) + "D2PROMPT\n"
            + agent_cmd(agent, dry) + " </dev/null\n"
            "echo '===AGENT-DONE==='\ngit add -A\n"
            f"git diff --cached --binary -- . {PATCH_EXCLUDES} | base64 -w0 > /tmp/d2patch.b64\n"
            "echo '===PATCH-BEGIN==='; cat /tmp/d2patch.b64; echo; echo '===PATCH-END==='\n")


def run_job(notes, agent, dry, say, st=None):
    st = st if st is not None else {}
    secrets = []

    def out(s):
        for sec in secrets:
            s = s.replace(sec, "<redacted>")
        say(s)

    # 1. local state
    st["stage"] = "1/6 check local repo"
    code, o = sh(["git", "status", "--porcelain"])
    if o:
        raise RuntimeError("working tree has local changes; commit or stash first:\n" + o[:400])
    sh(["git", "fetch", "-q", "origin", "main"])
    if sh(["git", "rev-parse", "HEAD"])[1] != sh(["git", "rev-parse", "origin/main"])[1]:
        raise RuntimeError("local main is not equal to origin/main; pull or push first")
    out(f"✅ 1/6 repo clean and in sync ({sh(['git', 'rev-parse', '--short', 'HEAD'])[1]})")

    # 2. key
    env_name, secret_name = KEYS[agent]
    prelude = ""
    if secret_name:
        val = vault_secret(secret_name)
        secrets.append(val)
        prelude = f"export {env_name}={shlex.quote(val)}\n"
        out(f"🔑 2/6 {secret_name} read from Key Vault {VAULT} (memory only)")
    else:
        out("🔑 2/6 no key needed for this agent (it uses its own login on the sprite)")

    # 3. agent on the sprite
    st["stage"] = "3/6 agent on the sprite"
    script = build_script(notes, agent, dry, prelude)
    out(f"🛰️ 3/6 running {agent} on sprite {SPR['name']} …")
    p = subprocess.Popen(["sprite", "exec", "-s", SPR["name"], "--stdin", "--", "bash", "-l", "-s"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    p.stdin.write(script)
    p.stdin.close()
    patch_b64, in_patch = [], False
    for line in p.stdout:
        line = line.rstrip("\n")
        if "bind: warning" in line:
            continue
        if line == "===PATCH-BEGIN===":
            in_patch = True
            continue
        if line == "===PATCH-END===":
            in_patch = False
            continue
        if in_patch:
            patch_b64.append(line)
        else:
            out("   " + line)
    if p.wait() != 0:
        raise RuntimeError(f"sprite run failed (exit {p.returncode})")
    b64 = "".join(patch_b64).strip()
    if dry:
        out(f"🧪 dry run finished; patch bytes would be {len(b64)}; nothing applied")
        return {"changed": False}
    if not b64:
        out("ℹ️ the agent made no change; nothing to apply")
        return {"changed": False}
    patch = base64.b64decode(b64)
    out(f"📦 4/6 patch received ({len(patch)} bytes)")

    # 5. apply, build, commit, push
    st["stage"] = "5/6 apply patch, build, commit, push"
    pf = ROOT / ".notes.patch"
    pf.write_bytes(patch)
    try:
        code, o = sh(["git", "apply", "--3way", "--index", str(pf)])
        if code:
            raise RuntimeError("patch did not apply:\n" + o[:600])
    finally:
        pf.unlink(missing_ok=True)
    code, o = sh([sys.executable, "-I", "scripts/build_short_site.py"])
    if code:
        sh(["git", "reset", "-q", "--hard", "HEAD"])
        raise RuntimeError("build failed after the patch, reverted:\n" + o[-600:])
    first = next((l for l in notes.splitlines() if l.strip()), "notes")[:70]
    sh(["git", "add", "-A"])
    code, o = sh(["git", "commit", "-q", "-m", f"🛰️ Notes via sprite ({agent}): {first}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"])
    if code:
        raise RuntimeError("commit failed:\n" + o[-400:])
    code, o = sh(["git", "push", "origin", "main"])
    if code:
        raise RuntimeError("push failed:\n" + o[-400:])
    st["commit"] = sh(["git", "log", "-1", "--format=%h %s"])[1]
    st["stat"] = sh(["git", "show", "--stat", "--format=", "HEAD"])[1]
    sh(["git", "fetch", "-q", "origin", "main"])
    st["pushed"] = sh(["git", "rev-parse", "HEAD"])[1] == sh(["git", "rev-parse", "origin/main"])[1]
    out(f"✅ 5/6 committed and pushed {sh(['git', 'rev-parse', '--short', 'HEAD'])[1]}")

    # 6. deploy + verify
    st["stage"] = "6/6 fly deploy + verify"
    sys.path.insert(0, str(ROOT / "scripts"))
    import stamp
    stamp.write_stamp()
    code, o = sh(["fly", "deploy", "--remote-only", "-a", DEP["fly_app"]], timeout=900)
    if code:
        raise RuntimeError("fly deploy failed:\n" + o[-600:])
    for _ in range(10):
        try:
            with urllib.request.urlopen(DEP["url"] + "index.html", timeout=15) as r:
                if r.status == 200:
                    st["deployed"] = True
                    out(f"✅ 6/6 deployed to Fly.io and answering 200: {DEP['url']}")
                    return {"changed": True}
        except Exception:
            time.sleep(3)
    raise RuntimeError("deployed but the site did not answer 200")


def report(st, err, say):
    say("\n━━━━━━━━ 📋 RESULT ━━━━━━━━")
    say(("❌ FAILED at " + st.get("stage", "?")) if err else "✅ SUCCEEDED")
    say("🧾 git commit: " + (st.get("commit") or "none (no commit was made)"))
    if st.get("stat"):
        say(st["stat"])
    nochg = not err and not st.get("commit")
    say("⬆️ git push:   " + ("✅ completed, origin/main == HEAD" if st.get("pushed") else ("➖ nothing to push (no change)" if nochg else "❌ not pushed")))
    say("🌐 fly deploy: " + ("✅ live, answering 200" if st.get("deployed") else ("➖ nothing to deploy (no change)" if nochg else "❌ not deployed / not verified")))
    if err:
        say("🔎 error: " + err[:600])
    say("━━━━━━━━━━━━━━━━━━━━━━━━━━")


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def _origin_ok(self):
        o = self.headers.get("Origin", "")
        host = (self.headers.get("Host") or "").split(":")[0]
        return o in ALLOWED and host in ("127.0.0.1", "localhost"), o

    def _cors(self, o):
        self.send_header("Access-Control-Allow-Origin", o)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Vary", "Origin")

    def do_OPTIONS(self):
        ok, o = self._origin_ok()
        self.send_response(204 if ok else 403)
        if ok:
            self._cors(o)
        self.end_headers()

    def do_GET(self):
        ok, o = self._origin_ok()
        if not ok and self.headers.get("Origin"):
            self.send_response(403)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        if ok:
            self._cors(o)
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "sprite": SPR["name"], "agents": list(KEYS), "busy": LOCK.locked()}).encode())

    def do_POST(self):
        ok, o = self._origin_ok()
        if not ok or urlparse(self.path).path != "/run" or "application/json" not in self.headers.get("Content-Type", ""):
            self.send_response(403)
            self.end_headers()
            return
        try:
            body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 100000)))
            notes, agent, dry = str(body.get("notes", "")).strip(), body.get("agent", "claude"), bool(body.get("dry"))
            assert notes and len(notes) <= MAX_NOTES and agent in KEYS
        except Exception:
            self.send_response(400)
            self._cors(o)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self._cors(o)
        self.end_headers()

        def say(s):
            try:
                self.wfile.write((s + "\n").encode())
                self.wfile.flush()
            except Exception:
                pass

        if not LOCK.acquire(blocking=False):
            say("⏳ another run is in progress; wait for it to finish")
            return
        st = {}
        try:
            res = run_job(notes, agent, dry, say, st)
            err = None
        except Exception as e:
            res, err = {}, str(e)
            say("❌ ERROR at step " + st.get("stage", "?") + ":\n" + err)
        try:
            report(st, err, say)
            if err is None:
                say("🎉 DONE" + (" (changed)" if res.get("changed") else ""))
        finally:
            LOCK.release()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=SPR.get("runner_port", 8947))
    a = ap.parse_args()
    print(f"🚀 notes runner on http://127.0.0.1:{a.port} · sprite {SPR['name']} · origins {sorted(ALLOWED)} · Ctrl+C to stop")
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
