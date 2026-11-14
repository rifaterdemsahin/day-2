#!/usr/bin/env python3
"""Restore: load assets/terms/*.json into a database that has no such terms yet.

  python3 -I scripts/import_terms.py [--db PATH] [--src DIR]

Existing terms are never overwritten. (On Fly the same happens automatically on the first start
with an empty volume.)
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from api.db import connect  # noqa: E402
from api.export import import_docs  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--db")
ap.add_argument("--src", default=str(ROOT / "assets/terms"))
a = ap.parse_args()
docs = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(pathlib.Path(a.src).glob("*.json"))}
added = import_docs(connect(a.db), docs, "restore")
print(f"🌱 added {len(added)} of {len(docs)} term(s)" + (": " + ", ".join(added) if added else " (all already in the database)"))
