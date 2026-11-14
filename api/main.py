"""FastAPI backend for the term dictionary.

  EDIT_TOKEN=... uvicorn api.main:app --port 8960

Reads are public. EVERY write (and bulk preview) needs  Authorization: Bearer <EDIT_TOKEN>.
If EDIT_TOKEN is not set, all write endpoints answer 503 (fail closed).
"""
import hmac, json, os, pathlib
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import changes as ch
from .export import all_docs, seed_if_empty
from .db import STATUSES, connect

app = FastAPI(title="day-2 dictionary", docs_url="/api/docs", openapi_url="/api/openapi.json")
_origins = [o for o in os.environ.get("D2_CORS", "").split(",") if o]
if _origins:
    app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST", "PUT"], allow_headers=["Authorization", "Content-Type"])


ROOT = pathlib.Path(__file__).resolve().parent.parent


@app.on_event("startup")
def seed():
    """First start on an empty volume: load the committed export (assets/terms/*.json, or D2_SEED)."""
    con = connect()
    try:
        added = seed_if_empty(con, os.environ.get("D2_SEED") or ROOT / "assets/terms")
        if added:
            print(f"🌱 seeded {len(added)} term(s) from the export: {', '.join(added)}")
    finally:
        con.close()


def db():
    con = connect()
    try:
        yield con
    finally:
        con.close()


def auth(authorization: str = Header(default="")):
    token = os.environ.get("EDIT_TOKEN", "")
    if not token:
        raise HTTPException(503, "writes are disabled: EDIT_TOKEN is not set on the server")
    if not hmac.compare_digest(authorization.encode(), f"Bearer {token}".encode()):
        raise HTTPException(401, "missing or wrong token")


def _term(con, slug):
    r = con.execute("SELECT * FROM terms WHERE slug=?", (slug,)).fetchone()
    if not r:
        raise HTTPException(404, "term not found")
    d = dict(r)
    d["title_options"], d["voice_lines"] = json.loads(d["title_options"]), json.loads(d["voice_lines"])
    d["scenes"] = [dict(s) for s in con.execute("SELECT * FROM scenes WHERE term_slug=? ORDER BY n", (slug,))]
    return d


@app.get("/api/health")
def health(con=Depends(db)):
    return {"ok": True, "terms": con.execute("SELECT COUNT(*) FROM terms").fetchone()[0], "writes_enabled": bool(os.environ.get("EDIT_TOKEN"))}


@app.get("/api/terms")
def list_terms(status: str | None = None, con=Depends(db)):
    if status is not None and status not in STATUSES:
        raise HTTPException(422, f"status must be one of {list(STATUSES)}")
    counts = {s: 0 for s in STATUSES}
    for r in con.execute("SELECT status, COUNT(*) c FROM terms GROUP BY status"):
        counts[r["status"]] = r["c"]
    q, a = "SELECT slug, term, status, hook, chosen_title, rewatch_pct, views, publish_date, youtube_url, updated_at FROM terms", ()
    if status:
        q, a = q + " WHERE status=?", (status,)
    return {"counts": counts, "terms": [dict(r) for r in con.execute(q + " ORDER BY slug", a)]}


@app.get("/api/export")
def export(con=Depends(db)):
    """Every term as the documents written to assets/terms/ (public, like the other reads)."""
    return all_docs(con)


@app.get("/api/terms/{slug}")
def get_term(slug: str, con=Depends(db)):
    return _term(con, slug)


@app.post("/api/terms", status_code=201, dependencies=[Depends(auth)])
def create(body: dict = Body(...), con=Depends(db)):
    body = dict(body)
    slug, term = body.pop("slug", None), body.pop("term", None)
    try:
        ch.create_term(con, slug, term, body or None, source="api")
    except FileExistsError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))
    return _term(con, slug)


@app.put("/api/terms/{slug}", dependencies=[Depends(auth)])
def update(slug: str, body: dict = Body(...), con=Depends(db)):
    """Edit one term. Body = {field: value, ...}; scene fields as "scenes.2.vo". One change set, undoable."""
    _term(con, slug)
    changes = [{"slug": slug, "field": k, "value": v} for k, v in body.items()]
    p = ch.preview(con, changes)
    if not p["ok"]:
        raise HTTPException(422, p)
    return ch.apply(con, changes, p["preview_id"], source="api")


@app.post("/api/bulk/preview", dependencies=[Depends(auth)])
def bulk_preview(body: dict = Body(...), con=Depends(db)):
    """Body = {"changes": [{slug, field, value}, ...]}. Validates and returns the diff. Writes nothing."""
    return ch.preview(con, body.get("changes"))


@app.post("/api/bulk/apply", dependencies=[Depends(auth)])
def bulk_apply(body: dict = Body(...), con=Depends(db)):
    """Body = {"changes": [...], "preview_id": "..."}; the preview_id from /api/bulk/preview is required."""
    try:
        return ch.apply(con, body.get("changes"), body.get("preview_id"), source=str(body.get("source") or "bulk")[:40])
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post("/api/bulk/undo/{change_set_id}", dependencies=[Depends(auth)])
def bulk_undo(change_set_id: str, con=Depends(db)):
    try:
        return ch.undo(con, change_set_id)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))


# The generated site is served by the same process (one machine, one origin, no CORS). Must stay LAST.
_site = pathlib.Path(os.environ.get("D2_SITE") or ROOT / "site")
if _site.is_dir():
    app.mount("/", StaticFiles(directory=_site, html=True), name="site")
