# MASTER SPEC v4.0: 🎬 long-form (Part A) and 📱 short-form (Part B) video

| Part | Format | Made with | Where |
|---|---|---|---|
| 🅰️ **Part A: long form** | 16:9, 1920x1080, screen recordings + voice | ffmpeg, Whisper, Remotion | the rest of this file, from "Contents" down to section 11 |
| 🅱️ **Part B: short form** | 9:16, 1080x1920, 45 s, AI-generated clips | **Google Flow** (by hand), CapCut or ffmpeg | [Part B at the end of this file](#part-b-short-form-google-flow) |

## 🔁 Standing rules (both parts, never skip)

1. 😀 **Emojis everywhere:** in chat replies, in every website page, in the menu and in this spec.
2. 🚀 **Update, push and deploy every time:** after every change, update this spec and the website, commit, push to `main`, deploy to Fly.io (`python3 scripts/deploy_and_wait.py`; GitHub Pages only redirects to it) and confirm it answers 200, then open the pages in Google Chrome (`open -a "Google Chrome" <url>`). Do not wait to be asked.
3. 💬 **Collect feedback from the owner on the deployed website, after they review it:** after every deploy, Claude opens the deployed site (`https://<user>.github.io/<repo>/`) in Google Chrome on the owner's machine (`open -a "Google Chrome" <url>`) and asks the owner to review it. The owner writes feedback in the page boxes and uses the 📋 copy-to-clipboard buttons (per card, or 📋 Copy all on the 💬 All feedback page), then pastes the copied text back to Claude. Claude does not guess feedback: it waits for the owner's review, applies the pasted notes, and redeploys. **After every change also open the 🧰 Workbench page (`s2-w.html`) in Chrome** (reuse its tab) and make sure it carries feedback buttons (✅ 🔧 ❌ + 📋 Copy feedback on every card and section) so the owner can feed back to Claude and we iterate on the workbench itself. Each piece of feedback carries its pipeline code (for example `S2-03`). If Pages is not live yet, open the local files (`file://<repo>/index.html`) and say so.
4. 🔁 **We always iterate, and every round is documented on one page:** the 🔁 Iterations page (`iterations.html`, data in `assets/iterations.json`, newest first). Each round adds one entry (version, date, what changed, why/which feedback, pipeline codes, status) before the deploy. Also update `README.md` (live links and pipeline) when the structure changes.
5. ✔️ **Review UX is part of every site (owner's requirement):** (a) every page has a **floating 📝 notes button** (bottom right, key `N`) opening a panel with ✅ approve / 🔧 change / ❌ cut, a quick page note, **📋 Copy this page** and **📋 Copy all**; (b) every page has an **"I have reviewed this page" check box**; a reviewed page shows a **✔️ check mark in the menu**; (c) the hub and the 💬 All feedback page show **review progress** (`n / total pages reviewed`, a bar and a list); (d) notes and marks persist in the browser; (e) **highlight to comment:** the owner can select any text on any page, a **💬 Note on this** pop-up appears at the selection, and the note (with optional ✅ / 🔧 / ❌) is saved against that exact passage, which stays highlighted (CSS Custom Highlight API, no change to the page text), listed in the 📝 panel with 🔎 jump and ✖️ delete, and included in 📋 Copy this page and 📋 Copy all as `💬 [page › section] “quoted text” → note`. Notes must be reachable from anywhere on the page without scrolling: never only at the bottom.
6. 🧠 **This spec is the project's memory and is copied into every new project, and we retrain ourselves:** copy `MASTER_SPEC.md` (and the site generator in `scripts/`, plus the empty data templates) into each new project first. After every project, fold what was learned back into this file (new rules, UX fixes, lessons, pipeline changes) in the **🧠 Retrain log** (Part B, B6) so the next project starts smarter. Anything the owner asks us to "remember" goes here, not only in chat.
7. 🔒 **Public repo:** never put personal account details (the owner's Gmail address), keys, or media in the repo or on the site.
8. 🌳 **Trunk-based development:** one branch, `main`. Small commits straight to `main` (no long-lived branches, no pull-request queue), each one built, evals-checked (`python3 evals/run_evals.py`), pushed (separate commit and push commands) and deployed right away. Undo with a new `git revert` commit, never by rewriting pushed history. The runner and the sprite also work on `main` only. Every owner update is listed on the 🔁 Iterations page (`assets/iterations.json`), so each round still adds its iteration entry.

<!--TOC-->
## 📑 Contents

1. [♻️ Reuse first (standing rule, read before changing anything)](#-reuse-first-standing-rule-read-before-changing-anything)
2. [⚙️ `project.json` (the one config per video)](#-projectjson-the-one-config-per-video)
3. [▶ Prompt to execute (paste into Claude Code, fill the `<…>`)](#-prompt-to-execute-paste-into-claude-code-fill-the-)
4. [Get what is needed (so a video starts in minutes)](#get-what-is-needed-so-a-video-starts-in-minutes)
5. [0. Brief (fill in per video)](#0-brief-fill-in-per-video)
6. [0. Architecture and token budget (read first)](#0-architecture-and-token-budget-read-first)
7. [0b. Environment (check it before you start)](#0b-environment-check-it-before-you-start)
8. [0a. Fast start: the kit on Google Drive](#0a-fast-start-the-kit-on-google-drive)
9. [0c. Save raw footage and source artifacts to Azure Storage (per-video container)](#0c-save-raw-footage-and-source-artifacts-to-azure-storage-per-video-container)
10. [1. Pipeline](#1-pipeline)
11. [2. Repo layout](#2-repo-layout)
12. [3. Sync clips to the voice recording](#3-sync-clips-to-the-voice-recording)
13. [4. Render the base video (ffmpeg)](#4-render-the-base-video-ffmpeg)
14. [5. Transcript, chapters, title and description](#5-transcript-chapters-title-and-description)
15. [6. Remotion (long form)](#6-remotion-long-form)
16. [6a. Cuts (repetitive parts)](#6a-cuts-repetitive-parts)
17. [6b. Animated subtitles](#6b-animated-subtitles)
18. [6c. Recorder UI and image overlays](#6c-recorder-ui-and-image-overlays)
19. [6d. Run it (links and commands)](#6d-run-it-links-and-commands)
20. [6e. Speed-ups, slides, blur boxes (editing personal or slow parts)](#6e-speed-ups-slides-blur-boxes-editing-personal-or-slow-parts)
21. [6f. Export render and the player's version switch](#6f-export-render-and-the-players-version-switch)
22. [6g. EDL: the edit decision list (record every decision)](#6g-edl-the-edit-decision-list-record-every-decision)
23. [6h. Audio: remove steady noise (hoover, fan)](#6h-audio-remove-steady-noise-hoover-fan)
24. [6i. Ending: summary and community call to action](#6i-ending-summary-and-community-call-to-action)
25. [6j. OKRs and value recognition (in the Pre-prod page)](#6j-okrs-and-value-recognition-in-the-pre-prod-page)
26. [6k. Artifacts page (every added element, clickable)](#6k-artifacts-page-every-added-element-clickable)
27. [6l. Export versions (every export is numbered)](#6l-export-versions-every-export-is-numbered)
28. [6m. Cuts with an apology card, lower thirds, manual blurs](#6m-cuts-with-an-apology-card-lower-thirds-manual-blurs)
29. [6n. Script page and subtitle quality (find it, fix it, record it)](#6n-script-page-and-subtitle-quality-find-it-fix-it-record-it)
30. [6o. Changelog page (everything that happened, with emojis)](#6o-changelog-page-everything-that-happened-with-emojis)
31. [6p. Notes on the Artifacts page](#6p-notes-on-the-artifacts-page)
32. [6q. README and the contents table (navigation)](#6q-readme-and-the-contents-table-navigation)
33. [6r. Platforms: separate renders, the Publish page, Azure storage](#6r-platforms-separate-renders-the-publish-page-azure-storage)
34. [6s. Completion time: stages, order, who, and how to prepare](#6s-completion-time-stages-order-who-and-how-to-prepare)
35. [6t. The pipeline drawn with tldraw](#6t-the-pipeline-drawn-with-tldraw)
36. [6u. Evals: can the spec recreate this project?](#6u-evals-can-the-spec-recreate-this-project)
37. [6v. Post-publish performance analytics and value reconciliation](#6v-post-publish-performance-analytics-and-value-reconciliation)
38. [6w. AI-assisted curiosity thumbnail generation (fal.ai / FLUX / subagents)](#6w-ai-assisted-curiosity-thumbnail-generation-falai--flux--subagents)
39. [7. Website (GitHub Pages)](#7-website-github-pages)
40. [7a. Publish: GitHub Pages (do this for every project, do not forget)](#7a-publish-github-pages-do-this-for-every-project-do-not-forget)
41. [7b. Always back up to Google Drive](#7b-always-back-up-to-google-drive)
42. [7c. Build the whole website (every page, from the kit)](#7c-build-the-whole-website-every-page-from-the-kit)
43. [8. Sanity check (before publishing)](#8-sanity-check-before-publishing)
44. [9. Delivery checklist](#9-delivery-checklist)
45. [10. Lessons learned (this project)](#10-lessons-learned-this-project)
46. [11. Start prompt for a new Claude session (short form; the full prompt is at the top of this file)](#11-start-prompt-for-a-new-claude-session-short-form-the-full-prompt-is-at-the-top-of-this-file)
<!--/TOC-->
