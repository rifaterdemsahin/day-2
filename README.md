> 🌐 **Live site:** https://rifaterdemsahin.github.io/day-2/ · [📖 Master spec](https://rifaterdemsahin.github.io/day-2/spec.html) · [🔁 Iterations](https://rifaterdemsahin.github.io/day-2/iterations.html) · [💬 Feedback](https://rifaterdemsahin.github.io/day-2/feedback.html)

# 📱 day-2: From Numbers to Meaning

🎯 45 s vertical short (9:16), sequel to Day 1 (tokens). Made with **Google Flow by hand** (no API): Claude writes the prompts, the owner creates the clips. Goal: 200%+ watch time through a seamless loop and a hidden rewatch detail.

## 🔢 Pipeline (numbered, one site page each)

| Code | Step | Page |
|---|---|---|
| `S2-00` | 🧭 Brief, hook, loop | [open](https://rifaterdemsahin.github.io/day-2/s2-00.html) |
| `S2-01` | 📝 Script | [open](https://rifaterdemsahin.github.io/day-2/s2-01.html) |
| `S2-02` | 🗺️ Storyboard | [open](https://rifaterdemsahin.github.io/day-2/s2-02.html) |
| `S2-03` | 🪄 Flow prompts | [open](https://rifaterdemsahin.github.io/day-2/s2-03.html) |
| `S2-04` | 🎞️ Generate in Flow | [open](https://rifaterdemsahin.github.io/day-2/s2-04.html) |
| `S2-05` | 🎙️ Voice-over | [open](https://rifaterdemsahin.github.io/day-2/s2-05.html) |
| `S2-06` | ✂️ Assemble and loop check | [open](https://rifaterdemsahin.github.io/day-2/s2-06.html) |
| `S2-07` | 💬 Captions, title, description | [open](https://rifaterdemsahin.github.io/day-2/s2-07.html) |
| `S2-08` | 📈 Publish and analytics | [open](https://rifaterdemsahin.github.io/day-2/s2-08.html) |

## 🔁 How we work

Deploy → open the site in Chrome → owner reviews and copies feedback with the 📋 buttons → pastes it to Claude → Claude updates the spec, the site and the [🔁 Iterations](https://rifaterdemsahin.github.io/day-2/iterations.html) log → redeploy. Rules live in [MASTER_SPEC.md](MASTER_SPEC.md) (Part B is short form).

## 🛠️ Build

`python3 -I scripts/build_short_site.py` regenerates every page from `assets/short.json` and `assets/iterations.json`. Never commit media.

🎛️ **Remotion (S2-06):** `cd remotion && npm install && npm run studio` → http://localhost:3001 (see Master spec B2b).

---

## 📝 Original script draft (owner's source of truth for the beats)

From Numbers to Meaning: High-Dimensional Embeddings
"Tokens are just numbers. How does an AI know that 'king' minus 'man' plus 'woman' equals 'queen'?"
🎬 Visual Mental Model
3D vector space floating in dark space. Word coordinates shifting live as vector arithmetic (+/-) pulls vectors toward 'Queen'.

📋 Scene Breakdown (45s)
Scene 1: Token ID 9246 gets passed into a lookup table
Scene 2: Expanding from 1 integer to 1,536 coordinates
Scene 3: Semantic clustering: Fruit cluster vs Royalty cluster
Scene 4: The King - Man + Woman = Queen vector math live
Scene 5: Teaser: How do these vectors talk to each other?
🔗 Token Tie-in: Direct sequel to Day 1: Maps token IDs into geometric space.
