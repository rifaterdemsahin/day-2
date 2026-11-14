#!/usr/bin/env python3
"""Import assets/short.json as the first dictionary term (idempotent).

  python3 -I scripts/migrate_short_json.py [--db PATH] [--force]

Second run = no change. An existing term is never overwritten unless --force
(so edits made in the database are safe). Every written field goes to history.
"""
import argparse, datetime, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from api.db import connect  # noqa: E402

SLUG = "tokenization-embeddings"
TERM_FIELDS = ["term", "status", "hook", "definition", "analogy", "chosen_title", "title_options", "voice_lines"]


def term_row(d):
    return {
        "term": d["title"].split(":")[-1].strip(),
        "status": "script",  # script and voice exist, Flow clips are still missing
        "hook": d["hook"],
        "definition": d["metadata"]["description"],
        "analogy": "",  # not in short.json: left for the owner to write
        "chosen_title": d["title_selected"],
        "title_options": json.dumps(d["titles"], ensure_ascii=False),
        "voice_lines": json.dumps([s["vo"] for s in d["scenes"]], ensure_ascii=False),
    }


def scene_rows(d):
    clips = d.get("production", {}).get("clips", {})
    out = []
    for i, s in enumerate(d["scenes"], 1):  # position, not s["n"] (n repeats: one scene has two clips)
        cid = (s.get("clips") or [""])[0]
        ready = clips.get(cid, {}).get("clip") == "ready"
        out.append({"n": i, "start": s["start"], "end": s["end"], "vo": s["vo"], "visual": s["visual"],
                    "on_screen_text": s["text"], "prompt": s["prompt"], "hf_camera": s["hf_camera"],
                    "clip_status": "ready" if ready else "missing"})
    return out


def migrate(con, d, force=False):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    if con.execute("SELECT 1 FROM terms WHERE slug=?", (SLUG,)).fetchone() and not force:
        return "unchanged"
    row, scenes = term_row(d), scene_rows(d)
    with con:
        old = con.execute("SELECT * FROM terms WHERE slug=?", (SLUG,)).fetchone()
        con.execute("INSERT INTO terms (slug, updated_at, " + ", ".join(TERM_FIELDS) + ") VALUES (?,?," +
                    ",".join("?" * len(TERM_FIELDS)) + ") ON CONFLICT(slug) DO UPDATE SET updated_at=excluded.updated_at, " +
                    ", ".join(f"{f}=excluded.{f}" for f in TERM_FIELDS),
                    (SLUG, now, *[row[f] for f in TERM_FIELDS]))
        for f in TERM_FIELDS:
            o = old[f] if old else None
            if o != row[f]:
                con.execute("INSERT INTO history (term_slug, field, old, new, source, at) VALUES (?,?,?,?,?,?)",
                            (SLUG, f, o, row[f], "migration", now))
        con.execute("DELETE FROM scenes WHERE term_slug=?", (SLUG,))
        for s in scenes:
            con.execute('INSERT INTO scenes (term_slug, n, start, "end", vo, visual, on_screen_text, prompt, hf_camera, clip_status) '
                        "VALUES (:t,:n,:start,:end,:vo,:visual,:on_screen_text,:prompt,:hf_camera,:clip_status)", {"t": SLUG, **s})
    return "updated" if old else "inserted"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db")
    ap.add_argument("--force", action="store_true", help="overwrite the term with short.json again")
    a = ap.parse_args()
    d = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
    con = connect(a.db)
    r = migrate(con, d, a.force)
    n_t, n_s, n_h = (con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("terms", "scenes", "history"))
    print(f"🗄️ {r}: {SLUG} · terms {n_t} · scenes {n_s} · history rows {n_h}")


if __name__ == "__main__":
    main()
