#!/usr/bin/env python3
"""Write assets/terms/<slug>.json from the term database (nightly or on demand).

  python3 -I scripts/export_terms.py [--db PATH | --api URL] [--out DIR] [--check]

--db   read a local SQLite file (default data/terms.db, or D2_DB)
--api  read the live API instead (GET /api/export, public): this is how the Fly database is backed up to git
--check  change nothing; exit 1 if the files differ from the database
Files that did not change are not rewritten, and files of terms that no longer exist are removed.
"""
import argparse, json, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from api.export import all_docs, dumps  # noqa: E402


def fetch_api(url):
    req = urllib.request.Request(url.rstrip("/") + "/api/export", headers={"User-Agent": "day-2-export"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def sync(docs, out, check=False):
    """Make `out` match docs. Returns (written, removed, unchanged) slug lists."""
    out.mkdir(parents=True, exist_ok=True)
    written, removed, same = [], [], []
    for slug, doc in docs.items():
        f, text = out / f"{slug}.json", dumps(doc)
        if f.exists() and f.read_text(encoding="utf-8") == text:
            same.append(slug)
            continue
        written.append(slug)
        if not check:
            f.write_text(text, encoding="utf-8")
    for f in sorted(out.glob("*.json")):
        if f.stem not in docs:
            removed.append(f.stem)
            if not check:
                f.unlink()
    return written, removed, same


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db")
    ap.add_argument("--api")
    ap.add_argument("--out", default=str(ROOT / "assets/terms"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.api:
        docs = fetch_api(a.api)
    else:
        from api.db import connect
        docs = all_docs(connect(a.db))
    if not docs and not a.check:
        sys.exit("🛑 the source has no terms: refusing to delete the exported files")
    w, r, s = sync(docs, pathlib.Path(a.out), a.check)
    print(f"📦 {'would write' if a.check else 'wrote'} {len(w)} · removed {len(r)} · unchanged {len(s)} → {pathlib.Path(a.out).relative_to(ROOT) if pathlib.Path(a.out).is_relative_to(ROOT) else a.out}")
    if a.check and (w or r):
        print("❌ out of date: " + ", ".join(w + r))
        sys.exit(1)


if __name__ == "__main__":
    main()
