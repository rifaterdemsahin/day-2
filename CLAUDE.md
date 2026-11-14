# CLAUDE.md: day-2 (45 s Short "From Numbers to Meaning") briefing

Read this, not the whole spec. Facts live in data; pages are generated; keep answers short, with emojis.

## Standing rules
1. 😀 Emojis in chat, on the site, in the spec.
2. 🌳 Trunk-based: only `main`, small commits, push and deploy after every change. Undo with `git revert`, never rewrite pushed history.
3. 🔁 Every round adds ONE entry at the top of `assets/iterations.json` (v, date, emoji, codes, change, why = the owner's words, status).
4. 📝 Every page keeps its ✅🔧❌ + 📋 Copy feedback buttons (`fb(...)` helper). Do not guess feedback: the owner pastes it.
5. 🔒 Public repo: no keys, tokens, emails or media. Never print secrets. Never commit `*.mp4 *.wav *.mov *.zip`.
6. 🙋 Google Flow has no API: the owner pastes the prompts you write. Flow, Higgsfield and the Remotion render stay manual and local.
7. 🌐 Open local apps with `open -a "Google Chrome" <url>`.

## Reading the owner's notes
A note may contain element references made by the 🎯 picker: `🎯 [s2-x.html › #xgo] <button> "▶️ Compute" · section: …`. Page `s2-x.html` = module `pages/s2_x.py` (`-` → `_`; `index.html` = `pages/index.py`). Grep the module for the quoted text or the id; edit data in `assets/*.json` when the text comes from there. Never edit built HTML.

## Where things are
- `assets/short.json`: ALL facts (scenes, voice lines, steps, prompts, sprite, deploy, production status). Edit data here first.
- `pages/*.py`: one module per page (`pages/s2_x.py` builds s2-x.html); `pages/_lib.py` shared helpers (page, fb, copybtn, nav).
- `scripts/build_short_site.py`: build entry (imports every page module). `scripts/build_spec.py`: joins `spec/*.md`.
- `spec/rules.md` (rules + contents), `spec/part-a-long.md` (long form), `spec/part-b-short.md` (shorts, pipeline B2, retrain log B6).
- `app.js`, `style.css`: vanilla JS and CSS (notes panel, ticks, footer). No React, no JS build chain.
- `assets/iterations.json`, `assets/recommendations.json`, `assets/similar_videos.json`, `assets/sandbox_pride.json`: page data.
- `scripts/notes_runner.py` (🚀 runner on the laptop), `scripts/sprite_check.py`, `scripts/sync_status.py`, `scripts/deploy_and_wait.py`, `scripts/serve_local.py`, `evals/run_evals.py`.
- Generated, git-ignored, never edit: `site/`, `MASTER_SPEC.md`, `deployed.json`. Tracked root `index.html` is only the GitHub Pages redirect to Fly.

## Spec: load ONE file, only if the task needs it
Do NOT read `MASTER_SPEC.md` (generated, ~30k tokens). Rules in this file are enough for most notes. Otherwise open exactly one: a short-form or pipeline question → `spec/part-b-short.md`; long-form video → `spec/part-a-long.md`; deep rules/contents → `spec/rules.md`. Grep first, read a section, not the file.

## Commands
- Build: `python3 -I scripts/build_short_site.py` (under 1 s; writes `site/`)
- Checks: `python3 evals/run_evals.py` (offline); `--live`, `--e2e` need the sprite and Key Vault
- Deploy: `python3 scripts/deploy_and_wait.py [page.html]` (builds, `fly deploy`, opens Chrome); CI deploys on push to `main`
- Local site + runner: `python3 -I scripts/serve_local.py` (http://127.0.0.1:8950/)
- Sync production status from disk: `python3 -I scripts/sync_status.py`

## Working on the sprite (when run by the 🚀 runner)
You are in a fresh clone. Edit data/modules, run the build, add the iterations entry. Do NOT commit, push, deploy or touch secrets: the runner does that and returns your patch.
