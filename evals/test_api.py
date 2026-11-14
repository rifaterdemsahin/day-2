"""HTTP-level tests of api/main.py with FastAPI's TestClient. Needs fastapi + httpx:
   .venv/bin/python evals/test_api.py      (exit 0 = all good, prints one line per check)"""
import json, os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
os.environ["D2_DB"] = str(pathlib.Path(tempfile.mkdtemp()) / "t.db")
os.environ["EDIT_TOKEN"] = "test-token-not-a-secret"
from fastapi.testclient import TestClient
from api.db import connect
import migrate_short_json as mg
mg.migrate(connect(), json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8")))
from api.main import app
c = TestClient(app)
H = {"Authorization": "Bearer " + os.environ["EDIT_TOKEN"]}
S = "tokenization-embeddings"
fails = []


def t(name, ok, extra=""):
    print(("✅ " if ok else "❌ ") + name + ("" if ok else f"  {extra}"))
    if not ok:
        fails.append(name)


t("GET /api/terms is public, counts per status", (lambda r: r.status_code == 200 and r.json()["counts"]["script"] == 1 and len(r.json()["terms"]) == 1)(c.get("/api/terms")))
t("GET /api/terms?status=bogus is 422", c.get("/api/terms?status=bogus").status_code == 422)
e = c.get("/api/export")
t("GET /api/export is public and returns every term as a document", e.status_code == 200 and list(e.json()) == [S] and e.json()[S]["scenes"][0]["n"] == 1 and "updated_at" not in e.json()[S])
r = c.get(f"/api/terms/{S}")
t("GET /api/terms/{slug} has 6 scenes and decoded lists", r.status_code == 200 and len(r.json()["scenes"]) == 6 and isinstance(r.json()["title_options"], list))
t("unknown slug is 404", c.get("/api/terms/nope").status_code == 404)
for m, u, b in [("put", f"/api/terms/{S}", {"hook": "x"}), ("post", "/api/terms", {"slug": "a", "term": "A"}), ("post", "/api/bulk/preview", {"changes": []}),
                ("post", "/api/bulk/apply", {}), ("post", "/api/bulk/undo/cs-x", {})]:
    t(f"{m.upper()} {u} without token is 401", getattr(c, m)(u, json=b).status_code == 401)
t("wrong token is 401", c.put(f"/api/terms/{S}", json={"hook": "x"}, headers={"Authorization": "Bearer nope"}).status_code == 401)

ch = [{"slug": S, "field": "hook", "value": "New hook"}, {"slug": S, "field": "status", "value": "clips"},
      {"slug": S, "field": "scenes.2.vo", "value": "New line"}, {"slug": S, "field": "views", "value": 120}]
p = c.post("/api/bulk/preview", json={"changes": ch}, headers=H).json()
t("preview returns a diff old -> new and a preview_id", p["ok"] and p["rows"][1]["old"] == "script" and p["rows"][1]["new"] == "clips" and p["preview_id"])
t("preview wrote nothing", c.get(f"/api/terms/{S}").json()["status"] == "script")
bad = c.post("/api/bulk/preview", json={"changes": [{"slug": S, "field": "status", "value": "live"}, {"slug": S, "field": "hook", "value": "x" * 401},
                                                     {"slug": S, "field": "nope", "value": 1}, {"slug": "zz", "field": "hook", "value": "x"}]}, headers=H).json()
t("preview flags bad enum, too long, unknown field, unknown term", not bad["ok"] and bad["errors"] == 4 and bad["preview_id"] is None, bad)
t("apply without preview_id is refused (409)", c.post("/api/bulk/apply", json={"changes": ch}, headers=H).status_code == 409)
t("apply with a forged preview_id is refused (409)", c.post("/api/bulk/apply", json={"changes": ch, "preview_id": "0" * 20}, headers=H).status_code == 409)
t("refused apply wrote nothing", c.get(f"/api/terms/{S}").json()["hook"] != "New hook")
a = c.post("/api/bulk/apply", json={"changes": ch, "preview_id": p["preview_id"], "source": "sprite"}, headers=H).json()
d = c.get(f"/api/terms/{S}").json()
t("apply writes all rows in one change set", a["applied"] == 4 and d["hook"] == "New hook" and d["status"] == "clips" and d["scenes"][1]["vo"] == "New line" and d["views"] == 120, a)
n = connect().execute("SELECT COUNT(*) FROM history WHERE change_set=? AND source='sprite'", (a["change_set"],)).fetchone()[0]
t("every change is in history with its source", n == 4)
t("re-applying the same preview is refused (data changed)", c.post("/api/bulk/apply", json={"changes": ch, "preview_id": p["preview_id"]}, headers=H).status_code == 409)
u = c.post(f"/api/bulk/undo/{a['change_set']}", headers=H)
d = c.get(f"/api/terms/{S}").json()
t("undo restores the old values", u.status_code == 200 and d["status"] == "script" and d["views"] is None and d["hook"].startswith("Tokens are just numbers"), u.text)
t("undo twice is refused (409)", c.post(f"/api/bulk/undo/{a['change_set']}", headers=H).status_code == 409)
t("undo unknown change set is 404", c.post("/api/bulk/undo/cs-nope", headers=H).status_code == 404)


def one(v):
    chg = [{"slug": S, "field": "hook", "value": v}]
    pid = c.post("/api/bulk/preview", json={"changes": chg}, headers=H).json()["preview_id"]
    return c.post("/api/bulk/apply", json={"changes": chg, "preview_id": pid}, headers=H).json()["change_set"]


A, B = one("A"), one("B")
t("undo refuses when a newer change touched the field", c.post(f"/api/bulk/undo/{A}", headers=H).status_code == 409)
t("undo newest first works", c.post(f"/api/bulk/undo/{B}", headers=H).status_code == 200 and c.post(f"/api/bulk/undo/{A}", headers=H).status_code == 200)

r = c.put(f"/api/terms/{S}", json={"analogy": "A map of meaning"}, headers=H)
t("PUT edits a term and returns a change set", r.status_code == 200 and c.get(f"/api/terms/{S}").json()["analogy"] == "A map of meaning")
t("PUT with an invalid value is 422 and writes nothing", c.put(f"/api/terms/{S}", json={"status": "bogus", "hook": "zzz"}, headers=H).status_code == 422 and c.get(f"/api/terms/{S}").json()["hook"] != "zzz")
r = c.post("/api/terms", json={"slug": "attention", "term": "Attention", "hook": "Why words look at each other"}, headers=H)
t("POST creates a term with 6 empty scenes, status idea", r.status_code == 201 and r.json()["status"] == "idea" and len(r.json()["scenes"]) == 6 and r.json()["hook"].startswith("Why"))
t("duplicate slug is 409", c.post("/api/terms", json={"slug": "attention", "term": "X"}, headers=H).status_code == 409)
t("bad slug is 422", c.post("/api/terms", json={"slug": "Bad Slug", "term": "X"}, headers=H).status_code == 422)
t("counts follow the data", c.get("/api/terms").json()["counts"] == {"idea": 1, "script": 1, "clips": 0, "voice": 0, "rendered": 0, "published": 0})
os.environ["EDIT_TOKEN"] = ""
t("no EDIT_TOKEN on the server: writes fail closed (503)", c.put(f"/api/terms/{S}", json={"hook": "x"}, headers=H).status_code == 503)
sys.exit(1 if fails else 0)
