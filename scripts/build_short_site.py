#!/usr/bin/env python3
"""Build the short-form site from assets/short.json (facts live in data, not code).

  python3 -I scripts/build_short_site.py

One module per page in pages/ (pages/s2_x.py builds s2-x.html); shared helpers in pages/_lib.py.
Output: site/ (generated, git-ignored; built again inside the Docker image) and the single tracked
root index.html that redirects the old GitHub Pages address to Fly.io.
"""
import importlib, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # -I drops the script folder from the path; pages/ is a package at the repo root
subprocess.run([sys.executable, "-I", str(ROOT / "scripts/build_spec.py")], check=True, stdout=subprocess.DEVNULL)  # MASTER_SPEC.md from spec/*.md

from pages import _lib  # noqa: E402

ORDER = ['index', 's2_w', 's2_sp', 's2_ev', 's2_r', 's2_v', 's2_x', 's2_rc', 's2_dev', 's2_a', 's2_00', 's2_01', 's2_02', 's2_03', 's2_03b', 's2_04', 's2_05', 's2_06', 's2_07', 's2_08', 'iterations', 'feedback']  # build order = feedback-box order

for name in ORDER:
    importlib.import_module(f"pages.{name}").build()
_lib.md_page("spec.html", "Master spec", "MASTER_SPEC.md", "📖")
_lib.md_page("readme.html", "Script draft (README)", "README.md", "📄")
(ROOT / ".nojekyll").write_text("")

# ---- assets next to the real pages
SITE = _lib.SITE
for f in ("style.css", "app.js"):
    shutil.copy2(ROOT / f, SITE / f)
shutil.copytree(ROOT / "assets", SITE / "assets", dirs_exist_ok=True)
stamp = ROOT / "deployed.json"  # written by scripts/stamp.py just before a deploy (git-ignored)
if stamp.exists():
    shutil.copy2(stamp, SITE / "deployed.json")

# ---- the ONE tracked redirect for the old GitHub Pages address
FLY = _lib.FLY
(ROOT / "index.html").write_text(
    f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved to Fly.io</title>'
    f'<meta name="viewport" content="width=device-width,initial-scale=1"><link rel="canonical" href="{FLY}">'
    f'<meta http-equiv="refresh" content="0; url={FLY}"><script>location.replace("{FLY}"+location.hash)</script></head>'
    f'<body style="font:16px system-ui;background:#0b1020;color:#e8ecff;padding:2rem">'
    f'<p>🛫 This site moved to Fly.io. <a style="color:#4dd8ff" href="{FLY}">Continue to {FLY}</a></p></body></html>', encoding="utf-8")
print("built", len(_lib.WRITTEN), "real pages in site/ + 1 root redirect (index.html);", len(_lib.FB_IDS), "feedback boxes")
