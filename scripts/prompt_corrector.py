#!/usr/bin/env python3
"""Prompt corrector: rewrite the owner's raw notes with the Role / Context / Rule / Constraint framework (Role = product manager)
with DeepSeek (any OpenAI-compatible host: DeepInfra today), before the prompt is shown for approval.

Only the standard library is used (urllib + json), so there is nothing to install. The API key comes from Azure Key
Vault inside notes_runner.py and is passed in memory; it is never printed, logged or put in a command line.
The endpoint is OpenAI-compatible (POST /chat/completions); the provider and model are in the config. Config: assets/short.json › sprite.enhancer.

  enhance(notes, key, cfg) -> {"ok": bool, "text": str, "model": str, "error": str, "usage": dict}

On any failure (no balance, timeout, bad key) it returns ok=False and the caller keeps the original notes.
"""
import json
import urllib.error
import urllib.request

SYSTEM = """You improve prompts. Rewrite the owner's raw feedback notes about a video-production review website into a prompt for an AI coding agent, using the Role, Context, Rule, Constraint framework. The Role is product manager.
Output exactly these four markdown sections, in this order:
**Role**: You are a senior product manager. State in one or two sentences that you turn this feedback into precise, minimal, testable changes to the review website and have them implemented.
**Context**: What the owner wants and why, on which page (use the page name or the 🎯 reference), in 2 to 5 sentences. Use only what the notes say.
**Rules**: A numbered list of the concrete changes to make. Each item says what to change, where (page or 🎯 reference) and the expected result. Finish with 2 to 4 checkable acceptance bullets.
**Constraints**: Bullets with the limits: change only what the notes ask, nothing else on the page or elsewhere; no invented features, pages or copy; keep emojis; keep the feedback buttons. Add any limit the notes imply.
Always: keep every line that starts with "🎯 [" exactly as written somewhere in Context or Rules; do not invent requirements; write in English; stay under 300 words; return only the four sections, no preface."""


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
        why = {401: "key rejected", 402: "no balance on the provider account (top it up)", 429: "rate limited"}.get(e.code, "")
        return {"ok": False, "text": "", "model": model, "error": f"HTTP {e.code} from the model API" + (f": {why}" if why else ""), "usage": {}}
    except Exception as e:  # network, timeout, bad JSON
        return {"ok": False, "text": "", "model": model, "error": f"{type(e).__name__}: {str(e)[:100]}", "usage": {}}
    # element references must survive the rewrite word for word
    refs = [l for l in notes.splitlines() if l.startswith("🎯 [")]
    missing = [l for l in refs if l not in text]
    if missing:
        text += "\n\n**Element references (verbatim)**:\n" + "\n".join(missing)
    return {"ok": True, "text": text, "model": model, "error": "", "usage": j.get("usage", {})}
