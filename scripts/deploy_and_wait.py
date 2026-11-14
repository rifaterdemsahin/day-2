#!/usr/bin/env python3
"""
Deploy and wait for GitHub Pages build to complete before opening in Chrome.
Usage:
  python3 scripts/deploy_and_wait.py [optional_path]
"""

import json
import subprocess
import sys
import time
import urllib.request

REPO = "rifaterdemsahin/day-2"
BASE_URL = "https://rifaterdemsahin.github.io/day-2/"


def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip(), p.returncode


def get_head_sha():
    sha, code = run_cmd("git rev-parse HEAD")
    if code != 0 or not sha:
        raise RuntimeError("Failed to get HEAD SHA")
    return sha


def get_latest_build():
    out, code = run_cmd(f"gh api repos/{REPO}/pages/builds/latest")
    if code != 0 or not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def verify_http_200(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DeployCheck/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_for_pages_deployment(target_sha, timeout_s=120):
    print(f"⏳ Waiting for GitHub Pages deployment for commit {target_sha[:7]}...")
    start = time.time()
    
    while time.time() - start < timeout_s:
        build = get_latest_build()
        if build:
            build_commit = build.get("commit", "")
            status = build.get("status", "")
            
            if build_commit.startswith(target_sha[:7]) or target_sha.startswith(build_commit[:7]):
                if status == "built":
                    duration_s = build.get("duration", 0) / 1000.0
                    print(f"✅ GitHub Pages built successfully in {duration_s:.1f}s!")
                    return True
                elif status == "errored":
                    err = build.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"❌ GitHub Pages build failed: {err}")
                else:
                    print(f"   Building... status: '{status}' (elapsed: {int(time.time() - start)}s)")
            else:
                print(f"   Latest build is for {build_commit[:7]} (waiting for {target_sha[:7]}... elapsed: {int(time.time() - start)}s)")
        else:
            print("   Querying GitHub Pages API...")
        
        time.sleep(4)

    raise TimeoutError(f"GitHub Pages deployment timed out after {timeout_s}s")


def main():
    target_path = sys.argv[1] if len(sys.argv) > 1 else ""
    target_url = BASE_URL + target_path.lstrip("/")

    head_sha = get_head_sha()
    wait_for_pages_deployment(head_sha)

    # Verify HTTP 200 on live endpoint
    print(f"🌐 Verifying live HTTP response on {target_url}...")
    live_ok = False
    for _ in range(5):
        if verify_http_200(target_url):
            live_ok = True
            break
        time.sleep(2)

    if live_ok:
        print(f"✅ Live response confirmed (HTTP 200) on {target_url}!")
    else:
        print(f"⚠️ Warning: Endpoint returned non-200, opening anyway.")

    # Open in Google Chrome
    print(f"🚀 Opening {target_url} in Google Chrome...")
    subprocess.run(["open", "-a", "Google Chrome", target_url])
    print("✨ Done!")


if __name__ == "__main__":
    main()
