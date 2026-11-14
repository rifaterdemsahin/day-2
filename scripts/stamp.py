#!/usr/bin/env python3
"""Write site/deployed.json (when, which commit, links) just before a Fly deploy.

Used by deploy_and_wait.py and notes_runner.py. The file is git-ignored on purpose: it changes
on every deploy and would otherwise dirty the repo. The page footer reads it.
"""
import datetime, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


def write_stamp():
    d = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))["deploy"]
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    repo = d.get("repo_url") or "https://github.com/rifaterdemsahin/day-2"
    st = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "epoch_ms": int(now.timestamp() * 1000), "commit": r.stdout.strip(),
          "commit_url": f"{repo}/commit/{r.stdout.strip()}", "site": d["url"]}
    (ROOT / "site").mkdir(exist_ok=True)
    (ROOT / "site/deployed.json").write_text(json.dumps(st, indent=1) + "\n")
    return st
