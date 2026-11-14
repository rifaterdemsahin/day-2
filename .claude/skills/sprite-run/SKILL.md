---
name: sprite-run
description: Run a task on the Fly.io Sprite (day-2) with the kilo, claude or antigravity CLI, using agent keys from Azure Key Vault, and bring the result back as a patch. Use when the owner says "execute my notes", "run on the sprite", or wants the site fixed from notes and redeployed.
---

# 🛰️ sprite-run

Runs an AI CLI on a Fly.io Sprite in a fresh clone of this repo, then applies the result locally, pushes and redeploys the site to Fly.io. The owner's notes (🚀 button in the notes panel) are the task.

## Normal path (the button)
1. `python3 scripts/notes_runner.py` (127.0.0.1:8947, keep it running). Needs `az login` and `sprite` authenticated.
2. Owner presses 🚀 in the 📝 panel on any page. The page streams the log.
3. Runner: checks repo clean + equal to origin/main → reads the agent key from Key Vault `dp-kv-deliverypilot` into memory → pipes a script to `sprite exec -s day-2 --stdin -- bash -l -s` (key only on stdin) → agent edits in the sprite clone and runs the build → runner receives a **patch of source files only** (no `site/`, no root `*.html`) → `git apply --3way`, rebuild, commit, push main → `fly deploy` → verify 200.

## Without the button (same thing by hand)
```bash
sprite exec -s day-2 --no-stdin -- bash -lc 'echo ok'        # reachable?
python3 evals/run_evals.py --live                              # dry run of the agent, no changes
python3 evals/run_evals.py --e2e                               # one real note, deployed, then reverted
```

## Agents (pick in the panel; default in assets/short.json › sprite › default_agent)
| agent | command on the sprite | key |
|---|---|---|
| kilo (default) | `kilo run -m kilo/kilo-auto/free --auto "<task>"` | Key Vault `kilo-api-key` → `KILO_API_KEY`. The account has no credits, so only free models work |
| claude | `claude -p "<task>" --permission-mode acceptEdits --allowedTools …` | No key sent: uses its own `/login` on the sprite (done 2026-11-14). Do not inject `ANTHROPIC_API_KEY`: the vault key returns 401 and overrides the login ("Invalid API key") |
| antigravity | `antigravity -z "<task>"` | none; unverified on the sprite (locally it is the hermes CLI) |

## Rules
- Never print, log or commit a key; read with `az keyvault secret show … --query value -o tsv` straight into a variable or stdin. Never pass a key as a command-line argument.
- No GitHub token goes to the sprite: it only returns a patch.
- Agents must run with `</dev/null` (kilo otherwise swallows the piped script).
- One run at a time; notes max 20,000 characters; the runner accepts only the site's own origins.
- Check the sprite with `sprite list`; the CLI is logged in with the Key Vault secret `sprite-api-token` (`sprite auth setup --token …`).
