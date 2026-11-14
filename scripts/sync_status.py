#!/usr/bin/env python3
"""Sync the production status in assets/short.json with the files on disk.

  python3 -I scripts/sync_status.py [--commit]

Looks at: remotion/public/clips/S2-04-<clip>.mp4 (clip placed), remotion/public/available.json (clip synced),
remotion/public/S2-05-vo.wav + assets/scene_timing.json (voice ready), remotion/out/S2-06-final.mp4 (rendered).
Writes ONLY the "production" block of assets/short.json (per clip: clip / voice / render, plus "checks", the
workbench boxes the disk proves). The site reads it, so progress survives browsers, devices and addresses.
`npm run sync|studio|render` in remotion/ calls this, so the status follows the files by itself.
--commit also commits and pushes that one file (separate commands). Flow, Higgsfield and the render stay manual.
"""
import datetime, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "assets/short.json"
raw = P.read_text(encoding="utf-8")
D = json.loads(raw)
clips_dir = ROOT / "remotion/public/clips"
avail = ROOT / "remotion/public/available.json"
synced = set(json.loads(avail.read_text(encoding="utf-8")).get("clips", [])) if avail.exists() else set()
wav = ROOT / "remotion/public/S2-05-vo.wav"
timing = ROOT / "assets/scene_timing.json"
final = ROOT / "remotion/out/S2-06-final.mp4"
timed = {r["clip"] for r in json.loads(timing.read_text(encoding="utf-8"))["scenes"]} if timing.exists() else set()

clips, checks, newest = {}, {}, 0.0
voice_ok = wav.exists() and bool(timed)
for s in D["scenes"]:
    c = s["clips"][0]
    f = clips_dir / f"S2-04-{c}.mp4"
    st = "missing" if not f.exists() else ("synced" if f.name in synced else "placed")
    if f.exists():
        newest = max(newest, f.stat().st_mtime)
    clips[c] = {"clip": st, "voice": "ready" if voice_ok and c in timed else "pending", "render": "pending"}
    checks[f"S2-04.{c}"] = st != "missing"
if voice_ok:
    newest = max(newest, wav.stat().st_mtime)
rendered = final.exists() and final.stat().st_mtime >= newest and all(v["clip"] != "missing" for v in clips.values())
for v in clips.values():
    v["render"] = "rendered" if rendered and v["clip"] != "missing" else "pending"
checks["S2-05.4"] = voice_ok
checks["W.move"] = all(v["clip"] != "missing" for v in clips.values())
checks["W.render"] = rendered
new = {"clips": clips, "checks": {k: v for k, v in checks.items() if v}}  # only proven ticks; never untick a human tick
old = D.get("production", {})
changed = {k: old.get(k) for k in ("clips", "checks")} != new
if changed:
    D["production"] = {"updated": datetime.date.today().isoformat(), **new}
    P.write_text(json.dumps(D, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = lambda key, val: sum(1 for v in clips.values() if v[key] == val)
print(("📁 production status UPDATED" if changed else "📁 production status unchanged") +
      f": clips {len(clips) - n('clip', 'missing')}/{len(clips)} on disk, voice {n('voice', 'ready')}/{len(clips)}, rendered {n('render', 'rendered')}/{len(clips)}")
dirty = subprocess.run(["git", "status", "--porcelain", "assets/short.json"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
if "--commit" in sys.argv and dirty:
    subprocess.run(["git", "add", "assets/short.json"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "🎞️ Production status synced from disk\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "-q", "origin", "main"], cwd=ROOT, check=True)
    print("⬆️ committed and pushed (deploy: python3 scripts/deploy_and_wait.py, or the push workflow)")
elif dirty:
    print("ℹ️ commit assets/short.json and deploy to show it on the site (or run with --commit)")
