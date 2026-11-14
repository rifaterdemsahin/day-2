#!/usr/bin/env python3
"""Prompt corrector: rewrite the owner's raw notes as a product manager would (goal, changes, acceptance criteria)
with DeepSeek, before the prompt is shown for approval.

Only the standard library is used (urllib + json), so there is nothing to install. The API key comes from Azure Key
Vault inside notes_runner.py and is passed in memory; it is never printed, logged or put in a command line.
The endpoint is OpenAI-compatible (POST /chat/completions). Config: assets/short.json › sprite.enhancer.

  enhance(notes, key, cfg) -> {"ok": bool, "text": str, "model": str, "error": str, "usage": dict}

On any failure (no balance, timeout, bad key) it returns ok=False and the caller keeps the original notes.
"""
import json
import urllib.error
import urllib.request

SYSTEM = """You are a senior product manager. Rewrite the owner's raw feedback notes about a video-production review website into a clear, actionable work request for an engineer or AI coding agent.
Rules:
- Keep the owner's intent and every concrete detail. Do NOT invent requirements, pages or features.
- Keep every line that starts with "🎯 [" exactly as written (these are element references from the page).
- Keep emojis. Write in English. Be concise (under 250 words).
Format (markdown):
**Goal**: one sentence.
**Changes requested**: a numbered list; each item says what to change, where (use the page or the 🎯 reference if given) and the expected result.
**Acceptance criteria**: 2 to 5 checkable bullets.
**Out of scope**: only if the notes imply limits, otherwise leave this out.
Return only the rewritten request, no preface."""


def enhance(notes, key, cfg, timeout=60):
    model = cfg.get("model", "deepseek-flash")
    body = {"model": model, "temperature": 0.2, "max_tokens": int(cfg.get("max_tokens", 1200)),
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": notes}]}
    req = urllib.request.Request(cfg["endpoint"], data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            j = json.loads(r.read().decode())
        text = j["choices"][0]["message"]["content"].strip()
        if not text:
            raise ValueError("empty answer")
    except urllib.error.HTTPError as e:
        why = {401: "key rejected", 402: "no balance on the DeepSeek account (top it up)", 429: "rate limited"}.get(e.code, "")
        return {"ok": False, "text": "", "model": model, "error": f"DeepSeek HTTP {e.code}" + (f": {why}" if why else ""), "usage": {}}
    except Exception as e:  # network, timeout, bad JSON
        return {"ok": False, "text": "", "model": model, "error": f"{type(e).__name__}: {str(e)[:100]}", "usage": {}}
    # element references must survive the rewrite word for word
    refs = [l for l in notes.splitlines() if l.startswith("🎯 [")]
    missing = [l for l in refs if l not in text]
    if missing:
        text += "\n\n**Element references (verbatim)**:\n" + "\n".join(missing)
    return {"ok": True, "text": text, "model": model, "error": "", "usage": j.get("usage", {})}
