#!/usr/bin/env python3
"""Run the review site locally (loopback only), with the notes runner beside it.

  python3 -I scripts/serve_local.py [--port 8950] [--no-runner] [--no-open]

Builds site/ then serves it at http://127.0.0.1:8950/ and starts scripts/notes_runner.py
(port from assets/short.json sprite.runner_port) so the 🚀 buttons work from the local page.
Opens Google Chrome. Ctrl+C stops both.
"""
import argparse, functools, http.server, json, pathlib, subprocess, sys, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=8950)
ap.add_argument("--no-runner", action="store_true")
ap.add_argument("--no-open", action="store_true")
a = ap.parse_args()

subprocess.run([sys.executable, "-I", str(ROOT / "scripts/build_short_site.py")], check=True)
runner = None
if not a.no_runner:
    runner = subprocess.Popen([sys.executable, "-I", str(ROOT / "scripts/notes_runner.py")], cwd=ROOT)
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "site"))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), h)
url = f"http://127.0.0.1:{a.port}/"
print(f"🖥️ local site {url} · runner {'on' if runner else 'off'} · Ctrl+C to stop")
if not a.no_open:
    threading.Timer(0.5, lambda: subprocess.run(["open", "-a", "Google Chrome", url + "feedback.html"])).start()
try:
    srv.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    if runner:
        runner.terminate()
