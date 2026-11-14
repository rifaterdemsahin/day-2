"""SQLite schema and connection for the AI-term dictionary (stdlib only).

The database file is never committed: it lives in data/terms.db locally and in
/data/terms.db on Fly (override with the D2_DB environment variable).
"""
import json, os, pathlib, sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATUSES = ("idea", "script", "clips", "voice", "rendered", "published")
CLIP_STATUSES = ("missing", "ready")

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS terms (
  slug          TEXT PRIMARY KEY CHECK (slug GLOB '[a-z0-9]*' AND slug NOT GLOB '*[^a-z0-9-]*'),
  term          TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'idea' CHECK (status IN ({", ".join(repr(s) for s in STATUSES)})),
  hook          TEXT NOT NULL DEFAULT '',
  definition    TEXT NOT NULL DEFAULT '',
  analogy       TEXT NOT NULL DEFAULT '',
  chosen_title  TEXT NOT NULL DEFAULT '',
  title_options TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(title_options)),
  voice_lines   TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(voice_lines)),
  rewatch_pct   REAL CHECK (rewatch_pct IS NULL OR rewatch_pct >= 0),
  views         INTEGER CHECK (views IS NULL OR views >= 0),
  publish_date  TEXT,
  youtube_url   TEXT,
  updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scenes (
  term_slug      TEXT NOT NULL REFERENCES terms(slug) ON DELETE CASCADE,
  n              INTEGER NOT NULL CHECK (n BETWEEN 1 AND 6),
  start          REAL,
  "end"          REAL,
  vo             TEXT NOT NULL DEFAULT '',
  visual         TEXT NOT NULL DEFAULT '',
  on_screen_text TEXT NOT NULL DEFAULT '',
  prompt         TEXT NOT NULL DEFAULT '',
  hf_camera      TEXT NOT NULL DEFAULT '',
  clip_status    TEXT NOT NULL DEFAULT 'missing' CHECK (clip_status IN ({", ".join(repr(s) for s in CLIP_STATUSES)})),
  PRIMARY KEY (term_slug, n)
);
CREATE TABLE IF NOT EXISTS history (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  term_slug TEXT NOT NULL,
  field     TEXT NOT NULL,
  old       TEXT,
  new       TEXT,
  source    TEXT NOT NULL,
  at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS history_slug ON history(term_slug, id);
CREATE INDEX IF NOT EXISTS terms_status ON terms(status);
"""


def db_path():
    return pathlib.Path(os.environ.get("D2_DB") or ROOT / "data" / "terms.db")


def connect(path=None):
    p = pathlib.Path(path) if path else db_path()
    if str(p) != ":memory:":
        p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    return con
