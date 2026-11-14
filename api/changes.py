"""Validation, preview, apply and undo of change sets (stdlib only, no web framework).

A change is {slug, field, value}. field is a term field ("hook") or a scene field
("scenes.3.vo"). Preview validates and returns a per-row diff old -> new and writes
nothing. Apply only accepts a change set whose preview_id it recomputes from the
CURRENT database, so an unseen or stale set is refused. Undo reverts via history.
"""
import datetime, hashlib, json, re, secrets, sqlite3
from .db import STATUSES, CLIP_STATUSES

MAX_CHANGES = 500
TEXT_LIMITS = {"term": 120, "hook": 400, "definition": 2000, "analogy": 1000, "chosen_title": 150}
SCENE_TEXT_LIMITS = {"vo": 600, "visual": 1000, "on_screen_text": 80, "prompt": 1500, "hf_camera": 200}
LIST_FIELDS = {"title_options": (10, 150), "voice_lines": (6, 600)}  # (max items, max chars per item)
NUM_FIELDS = {"rewatch_pct": (float, 0, 1000), "views": (int, 0, 10**10)}
SCENE_NUM = {"start": (0, 600), "end": (0, 600)}
TERM_FIELDS = list(TEXT_LIMITS) + list(LIST_FIELDS) + list(NUM_FIELDS) + ["status", "publish_date", "youtube_url"]
SCENE_FIELDS = list(SCENE_TEXT_LIMITS) + list(SCENE_NUM) + ["clip_status"]
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YT_RE = re.compile(r"^https://(www\.)?(youtube\.com|youtu\.be)/\S{1,200}$")
SCENE_RE = re.compile(r"^scenes\.([1-6])\.(\w+)$")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def dump(v):
    return json.dumps(v, ensure_ascii=False)


def check_value(field, value):
    """Return (normalized_value, error). Does not touch the database."""
    m = SCENE_RE.match(field)
    if m:
        f = m.group(2)
        if f in SCENE_TEXT_LIMITS:
            return _text(value, SCENE_TEXT_LIMITS[f])
        if f in SCENE_NUM:
            lo, hi = SCENE_NUM[f]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= value <= hi:
                return None, f"{f} must be a number {lo}..{hi}"
            return value, None
        if f == "clip_status":
            return (value, None) if value in CLIP_STATUSES else (None, f"clip_status must be one of {list(CLIP_STATUSES)}")
        return None, f"unknown scene field '{f}' (allowed: {SCENE_FIELDS})"
    if field in TEXT_LIMITS:
        v, e = _text(value, TEXT_LIMITS[field])
        return (None, "term must not be empty") if not e and field == "term" and not v.strip() else (v, e)
    if field == "status":
        return (value, None) if value in STATUSES else (None, f"status must be one of {list(STATUSES)}")
    if field in LIST_FIELDS:
        mx, per = LIST_FIELDS[field]
        if not isinstance(value, list) or len(value) > mx or not all(isinstance(x, str) and len(x) <= per for x in value):
            return None, f"{field} must be a list of at most {mx} strings of at most {per} characters"
        return value, None
    if field in NUM_FIELDS:
        typ, lo, hi = NUM_FIELDS[field]
        if value is None:
            return None, None
        if isinstance(value, bool) or not isinstance(value, (int, float)) or (typ is int and value != int(value)) or not lo <= value <= hi:
            return None, f"{field} must be a number {lo}..{hi} or null"
        return typ(value), None
    if field == "publish_date":
        return (value, None) if value is None or (isinstance(value, str) and DATE_RE.match(value)) else (None, "publish_date must be YYYY-MM-DD or null")
    if field == "youtube_url":
        return (value, None) if value is None or (isinstance(value, str) and YT_RE.match(value)) else (None, "youtube_url must be an https youtube.com / youtu.be link or null")
    return None, f"unknown field '{field}' (allowed: {TERM_FIELDS} or scenes.1-6.{SCENE_FIELDS})"


def _text(value, limit):
    if not isinstance(value, str):
        return None, "must be text"
    if len(value) > limit:
        return None, f"too long: {len(value)} > {limit} characters"
    return value, None


def current(con, slug, field):
    """Stored value of a field, JSON-decoded for list columns. Raises KeyError if missing."""
    m = SCENE_RE.match(field)
    if m:
        col = m.group(2)
        r = con.execute(f'SELECT "{col}" FROM scenes WHERE term_slug=? AND n=?', (slug, int(m.group(1)))).fetchone()
    else:
        r = con.execute(f'SELECT "{field}" FROM terms WHERE slug=?', (slug,)).fetchone()
    if r is None:
        raise KeyError(slug)
    v = r[0]
    return json.loads(v) if field in LIST_FIELDS and v is not None else v


def preview(con, changes):
    """Validate and diff. Writes nothing. Returns {ok, rows, preview_id, count, errors}."""
    if not isinstance(changes, list) or not changes:
        return {"ok": False, "rows": [], "errors": 1, "preview_id": None, "count": 0, "error": "changes must be a non-empty list"}
    if len(changes) > MAX_CHANGES:
        return {"ok": False, "rows": [], "errors": 1, "preview_id": None, "count": len(changes), "error": f"too many changes (max {MAX_CHANGES})"}
    rows, seen = [], set()
    for i, c in enumerate(changes):
        row = {"i": i, "slug": None, "field": None, "old": None, "new": None, "error": None, "changed": False}
        rows.append(row)
        if not isinstance(c, dict) or set(c) != {"slug", "field", "value"}:
            row["error"] = "each change needs exactly slug, field, value"
            continue
        row["slug"], row["field"] = c["slug"], c["field"]
        if not isinstance(c["slug"], str) or not SLUG_RE.match(c["slug"]) or not isinstance(c["field"], str):
            row["error"] = "bad slug or field"
            continue
        if (c["slug"], c["field"]) in seen:
            row["error"] = "the same field appears twice in one change set"
            continue
        seen.add((c["slug"], c["field"]))
        val, err = check_value(c["field"], c["value"])
        if err:
            row["error"] = err
            continue
        try:
            row["old"] = current(con, c["slug"], c["field"])
        except KeyError:
            row["error"] = "term not found" if not con.execute("SELECT 1 FROM terms WHERE slug=?", (c["slug"],)).fetchone() else "scene not found"
            continue
        row["new"] = val
        row["changed"] = row["old"] != val
    errors = sum(1 for r in rows if r["error"])
    pid = None
    if not errors:
        pid = hashlib.sha256(dump([[r["slug"], r["field"], r["old"], r["new"]] for r in rows]).encode()).hexdigest()[:20]
    return {"ok": errors == 0, "rows": rows, "errors": errors, "preview_id": pid, "count": len(rows),
            "unchanged": sum(1 for r in rows if not r["error"] and not r["changed"])}


def apply(con, changes, preview_id, source="api"):
    """Apply a previewed change set in ONE transaction. Raises ValueError if it was not previewed
    (preview_id missing or no longer matches the database) or has errors."""
    p = preview(con, changes)
    if not p["ok"]:
        raise ValueError("change set has errors: run preview and fix them")
    if not preview_id or not secrets.compare_digest(preview_id, p["preview_id"]):
        raise ValueError("not previewed, or the data changed since the preview: run preview again")
    cs, at = "cs-" + secrets.token_hex(6), now()
    with con:
        n = 0
        for r in p["rows"]:
            if not r["changed"]:
                continue
            _write(con, r["slug"], r["field"], r["new"], at)
            con.execute("INSERT INTO history (term_slug, field, old, new, source, at, change_set) VALUES (?,?,?,?,?,?,?)",
                        (r["slug"], r["field"], dump(r["old"]), dump(r["new"]), source, at, cs))
            n += 1
        for slug in {r["slug"] for r in p["rows"] if r["changed"]}:
            con.execute("UPDATE terms SET updated_at=? WHERE slug=?", (at, slug))
    return {"change_set": cs, "applied": n, "unchanged": p["count"] - n}


def _write(con, slug, field, value, at=None):
    m = SCENE_RE.match(field)
    if m:
        con.execute(f'UPDATE scenes SET "{m.group(2)}"=? WHERE term_slug=? AND n=?', (value, slug, int(m.group(1))))
    else:
        con.execute(f'UPDATE terms SET "{field}"=? WHERE slug=?', (dump(value) if field in LIST_FIELDS else value, slug))


def undo(con, change_set):
    """Revert a change set from history. Refuses if it was already undone or a field was changed
    again since (conflict), so nothing is overwritten silently."""
    rows = con.execute("SELECT * FROM history WHERE change_set=? ORDER BY id DESC", (change_set,)).fetchall()
    if not rows:
        raise LookupError("unknown change set")
    ucs = "undo-" + change_set
    if con.execute("SELECT 1 FROM history WHERE change_set=?", (ucs,)).fetchone():
        raise ValueError("this change set was already undone")
    for r in rows:
        if dump(current(con, r["term_slug"], r["field"])) != r["new"]:
            raise ValueError(f"conflict: {r['term_slug']} {r['field']} changed after this change set; undo the newer one first")
    at = now()
    with con:
        for r in rows:
            _write(con, r["term_slug"], r["field"], json.loads(r["old"]))
            con.execute("INSERT INTO history (term_slug, field, old, new, source, at, change_set) VALUES (?,?,?,?,?,?,?)",
                        (r["term_slug"], r["field"], r["new"], r["old"], "undo", at, ucs))
        for slug in {r["term_slug"] for r in rows}:
            con.execute("UPDATE terms SET updated_at=? WHERE slug=?", (at, slug))
    return {"change_set": ucs, "reverted": len(rows)}


def create_term(con, slug, term, fields=None, source="api"):
    if not isinstance(slug, str) or not SLUG_RE.match(slug):
        raise ValueError("slug must be lowercase letters, digits and dashes (max 64)")
    t, e = check_value("term", term)
    if e:
        raise ValueError("term: " + e)
    if con.execute("SELECT 1 FROM terms WHERE slug=?", (slug,)).fetchone():
        raise FileExistsError("slug already exists")
    at = now()
    with con:
        con.execute("INSERT INTO terms (slug, term, updated_at) VALUES (?,?,?)", (slug, t, at))
        for n in range(1, 7):
            con.execute("INSERT INTO scenes (term_slug, n) VALUES (?,?)", (slug, n))
        con.execute("INSERT INTO history (term_slug, field, old, new, source, at, change_set) VALUES (?,?,?,?,?,?,?)",
                    (slug, "_created", None, dump(t), source, at, "cs-" + secrets.token_hex(6)))
    if fields:
        changes = [{"slug": slug, "field": k, "value": v} for k, v in fields.items()]
        p = preview(con, changes)
        if not p["ok"]:
            raise ValueError("; ".join(f"{r['field']}: {r['error']}" for r in p["rows"] if r["error"]))
        apply(con, changes, p["preview_id"], source)
    return slug
