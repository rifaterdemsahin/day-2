# Part B: 📱 Short form (Google Flow)

## B0. 🎯 What a short is (and how it differs from Part A)

| | 🅰️ Long form | 🅱️ Short form |
|---|---|---|
| Length | whatever the voice is (minutes) | **45 s or less** |
| Frame | 16:9, 1920x1080 | **9:16, 1080x1920** |
| Footage | screen recordings + own voice | **AI-generated clips from Google Flow** |
| Tools | ffmpeg, Whisper, Remotion | Flow (by hand), then CapCut or ffmpeg to assemble |
| Success | chapters, retention at minutes | **watch time of 200%+: people loop and rewatch** |

The first draft of each short's script lives in the repo `README.md` (title, visual mental model, scene breakdown). The site is built from it.

## B1. 🙋 Google Flow has no API (standing assumption)

- Assume **Flow cannot be automated**. Claude writes every Flow prompt in the site (page `S2-03`), with a 📋 copy button per prompt.
- The **owner creates the clips by hand** in Flow, logged in with their own personal Google account, then downloads each clip and names it by its code (`S2-04-c1.mp4`, `c2`, ...). The account address is never written in the repo (public).
- Flow clips are about 8 s each: plan **one clip per beat of at most 8 s** (a longer scene gets two clips).
- If Flow gets an official API later, replace only step `S2-04` with a script; keep every other step.
- Never commit media. Clips live in `~/Downloads/<slug>/` and in a private cloud folder.
- 🆚 **Alternative tool (page `S2-03b`):** Higgsfield is a multi-model platform (Kling, Seedance, Wan, Sora 2, Veo 3.1) with named camera presets and a public API (launched Sept 2026, pay per generation). Flow stays the default (free daily credits, 8 s clips); Higgsfield is the second opinion and the only route to automating `S2-04`. Each scene in `short.json` carries `hf_camera` (a preset idea) used for the Higgsfield prompts. Prices and plan names change often: re-check live pages before paying, and refresh the comparison each project.

## B2. 🔢 The numbered pipeline (`S2` = short number 2; the next short uses `S3-xx`)

| Code | Step | Output | Who |
|---|---|---|---|
| `S2-EV` | 🧪 **Evals:** `evals/run_evals.py` (offline / `--live` / `--e2e`) with results on a site page | pass/fail table | Claude |
| `S2-SP` | 🛰️ **Sprite + runner setup:** Fly.io Sprite `day-2`, sprite CLI signed in with the Key Vault token, `scripts/notes_runner.py` behind the notes panel's 🚀 button (agent kilo/claude/antigravity on the sprite, key from Azure Key Vault on stdin, patch back, push, Fly deploy); skill `.claude/skills/sprite-run` | runner ready | owner |
| `S2-W` | 🧰 **Workbench:** guided checklist for the manual work with the two-Chrome-windows setup (A = site, B = Flow/Higgsfield/Studio pinned), per-clip copy/paste/download/tick, next-up banner, progress in localStorage (shared with S2-04 and S2-06 ticks) | workbench page | owner |
| `S2-R` | 🔬 **Research first:** the script explained beat by beat with inline-SVG diagrams, honest notes on what the short simplifies, why the topic matters, sources | research page | Claude |
| `S2-V` | 📊 **Similar videos:** top 10 similar YouTube videos with views, age, length and what the numbers say (data in `assets/similar_videos.json`, refreshed from a YouTube search read in Chrome) | similar-videos page | Claude |
| `S2-RC` | 💡 **Recommendations:** project scan, token drivers, ranked fixes, SQLite/React view, video-production and housekeeping notes (data `assets/recommendations.json`) | recommendations page | Claude |
| `S2-X` | 🪞 **Sandbox: pride & vanity:** the king/queen vector trick replayed with other words in an in-browser sandbox (data `assets/sandbox_pride.json`, toy hand-written vectors, honest limits; real-model script `scripts/pride_vanity_real.py`) | sandbox page | Claude |
| `S2-DEV` | 💻 **Development:** runnable code, interactive browser playground (token lookup, cosine distance, king − man + woman live vector arithmetic), and beat-by-beat code mapping to the script | development page & demo script | Claude |
| `S2-A` | 📊 **YouTube Analytics:** why we focus on Day 1 (247.1% view rate anomaly, 1:56 on 47 s short, 24x vs channel average), studio screenshot, comparative table, and Day 2 retention rules | analytics page | Claude + owner |
| `S2-00` | 🧭 **Title + thumbnail first**, Why (first principles, producer only), brief, hook and loop design | title options, thumbnail draft, why section, loop plan | Claude + owner |
| `S2-01` | 📝 Script (voice-over lines per scene) | VO text with timings | Claude, owner reviews |
| `S2-02` | 🗺️ Storyboard (scenes, camera, on-screen text) | scene cards | Claude, owner reviews |
| `S2-03` | 🪄 Flow prompts (one per clip) | copy-paste prompts | Claude |
| `S2-03b` | 🆚 Flow vs Higgsfield (tool choice + Higgsfield prompts with camera presets) | comparison, prompts | Claude |
| `S2-04` | 🎞️ Generate in Flow (manual) | clips `S2-04-cN.mp4` | owner |
| `S2-05` | 🎙️ Voice-over | `S2-05-vo.wav` | owner or TTS |
| `S2-06` | ✂️ Assemble and loop check | `S2-06-final.mp4` | owner, Claude advises |
| `S2-07` | 💬 Captions, title, description, hashtags | `metadata` | Claude |
| `S2-08` | 📈 Publish and analytics (rewatch rate) | numbers back into the next short | owner |

Every page on the site carries its code in the menu and the heading. Feedback is always tagged with the code.

### B2b. 🎛️ Remotion assembly (optional, step `S2-06`)

- Each short has a `remotion/` project (1080x1920, 30 fps, length from `assets/short.json`). Start it with `cd remotion && npm run studio` (Studio on **port 3001**: port 3000 may already be used by another project's Studio, check with `lsof -iTCP:3000`), render with `npm run render` → `out/S2-06-final.mp4`.
- `scripts/sync.mjs` copies `assets/short.json` next to the code and records which `S2-04-cN.mp4` clips and `S2-05-vo.wav` exist; **a missing clip renders as a placeholder card**, so the timeline, captions and loop can be reviewed before any Flow clip exists.
- 💬 **Animated captions (standing for every short):** word-by-word TikTok-style captions (`remotion/src/Captions.tsx`): each word **pops in** with a spring, the **word being spoken is highlighted** (gold glow, slightly larger), spoken words turn white, pages of about 4 words (a page also ends at . ? ! ,), heavy uppercase font with a dark stroke, placed in the safe area (bottom 20% and right 15% free). Style lives in data: `assets/short.json` → `captions` (`words_per_page`, `font_size`, `active_color`, `text_color`, `stroke`, `pop_frames`, `lead_s`, `tail_s`).
- ⏱️ **Word timing:** with no voice yet, words are spread over the scene by length (an estimate, good enough to review style). Once the voice exists (`S2-05`), run Whisper with word timestamps and save `assets/words.json` as `[{"word","start","end"}]` in seconds on the final timeline; `sync.mjs` picks it up and the captions follow the real speech.
- Hard cuts, no transitions. Facts stay in data: change `assets/short.json`, never the components.
- Clips, voice and `out/` are never committed (`remotion/.gitignore`). Pinned: remotion + cli 4.0.250, react 18.3.1, typescript 5.6.3 (same as Part A).
- Renders and stills use **Google Chrome** (`--browser-executable`, already in the npm scripts): Remotion's own downloaded headless shell failed to start here (`spawn` error -88).
- When asked to "open Remotion": open this project's Studio on 3001 in Google Chrome, not another project's.

### B2c. 🎙️ Voice-over with ElevenLabs on fal.ai (step `S2-05`)

- Default: `python3 -I scripts/make_voice.py` calls **`fal-ai/elevenlabs/tts/eleven-v3`** through fal's queue API (`https://queue.fal.run/<endpoint>`, header `Authorization: Key <key>`), with the full voice-over text from `assets/short.json` (all `scenes[].vo`) and the settings in its `voice` block (`voice`, `stability`, `output_format`, `language_code`). Inputs the endpoint documents: `text`, `voice`, `stability`, `timestamps`, `language_code`, `apply_text_normalization`, `output_format` (not `speed` or `style`).
- Output: `remotion/public/S2-05-vo.wav` (+ the `.mp3` original) and `assets/words.json` (word timings in seconds). Timings come from the endpoint's `timestamps`; if their shape is not recognised the script runs local Whisper on the audio instead. Remotion's animated captions read `words.json` automatically.
- 🔑 **Key handling (short-lived keys):** create a **fal.ai key with a 7-day expiry**, keep it in the macOS Keychain (service `fal-key`, added in the owner's own Terminal so it never touches chat or shell history) or in `FAL_KEY` for one command. Never in the repo, the site, chat logs or a file. Revoke it in the fal.ai dashboard and delete the Keychain item (`security delete-generic-password -s fal-key`) when the voice is final. `--dry-run` prints the request and calls nothing; run it first. `--timing-only` redoes the word timings from the existing audio with no key and no cost.
- 🎯 **The voice drives the cuts:** `make_voice.py` aligns the real word timings onto the script's own words (so captions keep the script's spelling) and writes `assets/scene_timing.json`: each scene starts when its first word is spoken. `remotion/scripts/sync.mjs` overlays it on `short.json`, so the Remotion timeline length and cuts follow the voice. A scene longer than about 8 s is longer than one Flow clip: speed it up or make two clips.

**`S2-05` sub-steps (numbered; each is a tick-box on the S2-05 page):** `S2-05.1` 🔑 create a 7-day key · `.2` 🗝️ store it in the Keychain · `.3` 🧪 dry run · `.4` 🎙️ generate · `.5` ✅ read the report · `.6` 🔁 free re-timing · `.7` 🎛️ check captions in Studio · `.8` 🗑️ revoke the key and delete the Keychain item · `.9` 📝 owner review and log.
- ⚠️ After generating, check the report the script prints: total length must be at most the short's length, and each scene's first word should land near its scene start. If the single take drifts from the clip cuts, tighten the script (S2-01) or generate per scene.
- Cost is per character (a 45 s script is about 450 characters); regenerate on purpose, not in a loop.

## B3. 🔄 Rewatch rules (why people watch twice)

1. **Hook in the first second:** a question or a strange image, never a logo or intro.
2. **Seamless loop:** the last line leads into the first line, and the last frame matches the first frame, so the replay does not feel like a restart.
3. **Rewatch bait:** one small detail seen only the second time (a number or object that returns).
4. **Density:** a visual change every 2 to 3 seconds; one idea per short.
5. **Payoff late, teaser last:** the aha moment sits in the last third; the final beat opens a question the next short answers (series tie-in).
6. **Animated captions always on** (word pop-in and highlight, see B2b), large, in the safe area (not under the platform buttons).

## B4. 🌐 The short-form website

- Built by `scripts/build_short_site.py` from `assets/short.json` (all facts in data, none in code, as in Part A).
- Pages: 🏠 hub, one page per pipeline code, 🔁 the Iterations log (one entry per round, see standing rule 4), 💬 a feedback page that gathers everything with one 📋 copy-all button, 📖 the master spec.
- Each scene/prompt card has its own feedback box with ✅ approve, 🔧 change, ❌ cut, and a 📋 copy button.
- Feedback is saved in the browser (localStorage); it only reaches Claude when the owner pastes it back. Review loop: deploy → Claude opens the deployed site in Chrome → owner reviews and copies feedback with the 📋 buttons → owner pastes it to Claude → Claude updates the spec and site and redeploys.
- Deploy: push to `main`, GitHub Pages from `main` and `/`, keep an empty `.nojekyll`.

## B5. ✅ Short-form checklist

- [ ] 🖼️ **Title options and a thumbnail draft are shown at the very start** (top of the hub and `S2-00`), with copy buttons, before any other work; the lead title is reused in the metadata step
- [ ] 🧭 `S2-00` has next a **Why section: first principles of why this short matters to the producer** (not audience copy), owner-reviewed
- [ ] 9:16 at 1080x1920, 45 s or less, captions on
- [ ] Hook visible in the first second
- [ ] Last frame matches the first; last line flows into the first line
- [ ] One rewatch-bait detail placed and listed on `S2-06`
- [ ] No private data, no media in git, no personal address in the repo
- [ ] Site updated, pushed to `main`, Pages live, opened in Chrome (standing rules)

## B6. 🧠 Retrain log (lessons folded back into the spec; copy this file to new projects)

| # | Date | Lesson | Rule it created |
|---|---|---|---|
| 1 | 2026-11-12 | Owner reviews on the deployed site and pastes feedback back | Standing rule 3: review loop with 📋 copy buttons |
| 2 | 2026-11-12 | One page documents every round | Standing rule 4: 🔁 Iterations page |
| 3 | 2026-11-12 | Per-card feedback boxes at the bottom of a long page are hard to use; the owner wants to see when a document is finished | Standing rule 5: floating 📝 notes, ✔️ reviewed check marks, progress |
| 4 | 2026-11-12 | The permission system blocked a chained commit + push + Pages call | Run commit and push as separate commands; if blocked, give the owner the `!` command |
| 5 | 2026-11-12 | Flow has no API | B1: Claude writes prompts, the owner creates clips by hand |

| 6 | 2026-11-12 | The brief page needs the reason before the plan; decisions are cheaper when the producer's first principles are written down | B2/B5: every project's `S0-00`-style brief page starts with a 🧭 Why section (first principles, producer only) |

| 7 | 2026-11-12 | The owner judges a short by its title and thumbnail first, so they must be visible at the start | B2/B5: title options + thumbnail draft on the hub and the first step, before the Why; prompt for the still in the Flow step |

| 8 | 2026-11-12 | Feedback on a card or a whole page is too coarse; the owner wants to point at the exact words | Standing rule 5(e): highlight-to-comment with quote + section in the copied feedback |

| 9 | 2026-11-12 | "Open Remotion" would have opened another project's Studio on port 3000 | B2b: each short has its own `remotion/` and Studio on port 3001; check the port and the project before opening |

| 10 | 2026-11-12 | Remotion's downloaded headless shell would not spawn (error -88) | B2b: always pass the local Chrome as the browser for render and still |

| 11 | 2026-11-12 | Plain caption boxes are static; shorts need captions that move with the voice | B2b/B3: animated word-by-word captions, styled from data, timed from Whisper words when available |

| 12 | 2026-11-12 | Voice should be generated, not recorded by hand, and the key must not leak | B2c: ElevenLabs on fal.ai via `make_voice.py`, key from env or Keychain only, dry run first, word timings feed the captions |

| 13 | 2026-11-12 | An API key should not outlive its job; Whisper mishears numbers and words, which would put typos in captions; the real voice was shorter than the planned timeline | B2c: 7-day keys revoked after use; align timings onto the script's words; scene cuts follow the voice (`scene_timing.json`) |

| 14 | 2026-11-14 | One video tool is a single point of failure and a manual chore | B1/`S2-03b`: keep a Flow vs Higgsfield comparison page per short, re-researched each project; per-scene `hf_camera` in data |

| 15 | 2026-11-14 | A short is only as good as the producer's understanding of the topic, and a script simplifies | B2: `S2-R` research page first in every pipeline (data in `short.json › research`, diagrams in the site generator), each beat with an honest-note on what the short simplifies |

| 16 | 2026-11-14 | Switching between many tabs (site, Flow, Higgsfield, Studio) breaks the flow of manual steps | B2: `S2-W` workbench; the **two-window rule** (Window A site, Window B tools, at most 3 pinned tabs); buttons use named targets so a tool tab is reused, never duplicated; ticks use the same localStorage keys as the step pages |
| 17 | 2026-11-14 | Explaining math in voice-over alone leaves technical viewers skeptical; developers need to see runnable code matching the script | B2: `S2-DEV` Development page after Research with runnable Python (`development_embeddings_demo.py`), interactive playground, and beat-by-beat code mapping; plus page-specific related favicons for quick visual tab navigation |
| 18 | 2026-11-14 | Creators guess what topic to produce instead of listening to channel retention outliers | B2: `S2-A` YouTube Analytics page; anchor every sequel directly in the channel's highest-retention asset (Day 1 Tokenization: 247.1% view rate, 1:56 duration on 0:47 video) and use its loop & brevity metrics as hard design constraints |

| 17 | 2026-11-14 | The workbench is where the owner spends their time, so it is where feedback is most needed | Standing rule 3: open the workbench after every deploy; every workbench card/section has feedback buttons; iterate on it each round |

| 18 | 2026-11-14 | Fixing the site from notes should not need a chat session, but a public page cannot hold a secret | Notes panel 🚀 button builds one `sprite exec` command (notes + fix/redeploy instructions) the owner pastes in Terminal; runs Claude on the Sprite configured in `short.json › sprite`; repo-scoped 7-day push token, revoked after; no tokens on the site |

| 19 | 2026-11-14 | GitHub Pages is a second system to wait for and keep; the owner already runs on Fly.io | Part B hosts on Fly.io (`site/` + Dockerfile + fly.toml), GitHub Pages only redirects; deploy script builds, deploys, verifies 200, opens Chrome; localStorage ticks reset when the address changes |

| 20 | 2026-11-14 | A button that runs an agent needs proof it works end to end, and bugs hide in the seams (kilo swallowed the piped script on stdin; ports 8787/8791 were taken; the vault's Anthropic keys returned 401) | Evals: offline/live/e2e with the e2e note reverted afterwards; agents run with stdin from /dev/null; check a port is free and a key is valid (HTTP status only) before relying on them; patch-only return so no git token reaches the sprite; sprite-run skill documents it |
| 21 | 2026-11-14 | A preview of what the sprite runs must stay current and private | The sprite runs a `preview` service (sprite-env services, port 8080: git reset to origin/main, build, serve site/); its URL is members-only (auth "sprite"), linked from the feedback page next to the execute buttons; restart it with `sprite exec -s day-2 --no-stdin -- sprite-env services restart preview` |
| 22 | 2026-11-14 | Local and hosted must behave the same | `python3 scripts/serve_local.py` serves the built site on 127.0.0.1:8950 with the runner; the runner allows that origin as well as Fly and the old Pages address |
| 23 | 2026-11-14 | Never assume a CLI name or login: the "antigravity" agent is `agy` on the sprite, claude and agy need a one-time interactive sign-in | `scripts/sprite_check.py` tests installed/version/signed-in per agent and feeds the S2-SP table; run it before relying on an agent; a run failure must show the failing step (runner RESULT block) |

**How to retrain:** at the end of each project add rows here, then copy the whole file to the next project. Keep rows short: lesson, then the rule.
