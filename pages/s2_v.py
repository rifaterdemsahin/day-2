"""S2-V Similar videos page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-V")
    v = json.loads((ROOT / "assets/similar_videos.json").read_text(encoding="utf-8"))
    rows = "".join(f'<tr><td>{x["rank"]}</td><td><a href="{x["search"]}" target="d2-yt" rel="noopener">▶️ {E(x["title"])}</a><br><small>{E(x["note"])}</small></td><td>{E(x["channel"])}</td><td><b>{E(x["views"])}</b></td><td>{E(x["age"])}</td><td>{E(x["length"])}</td></tr>' for x in v["videos"])
    txt = "Similar YouTube videos (" + v["when"] + ")\n" + "\n".join(f'{x["rank"]}. {x["title"]} | {x["channel"]} | {x["views"]} views | {x["age"]}' for x in v["videos"])
    head = step_head(st).replace("</h1>", "</h1><p>🔍 Data: first page of one YouTube search on 2026-11-14, views are rounded.</p>", 1)
    body = head + f"""<div class="card hero"><b>📊 Top 10 similar videos</b> · 📅 {E(v["when"])}<p>{E(v["how"])}</p>{copybtn(txt, "📋 Copy list")}</div>
<div class="tablewrap"><table class="cmp"><tr><th>#</th><th>Video (opens a YouTube search for it)</th><th>Channel</th><th>👁️ Views</th><th>Age</th><th>Length</th></tr>{rows}</table></div>
<h2>🔎 What the numbers say</h2><ul>
<li>📉 The topic is crowded but small: 9 of 10 have 6k views or fewer; only one old tutorial is large (247k, 5 years old).</li>
<li>🆕 Four of the ten are under 3 months old: new uploads keep coming, so timing and a clear hook matter more than being first.</li>
<li>⏱️ Almost all are long form. Only two are about two minutes, and none is a vertical Short in this list: our 45 s vertical format is the gap.</li>
<li>🏷️ Titles lead with the exact equation. Ours does too, plus the 🤯 and #shorts.</li>
<li>🧩 Most add chapters and name CBOW/Skip-gram. Ours stays on one idea, then ties it to Day 1 (tokens) and Day 3.</li></ul>
<h2>⚠️ Honest limits</h2><ul><li>This is the first page of one search, not all of YouTube. Views are rounded and change daily.</li>
<li>Links open a YouTube search for each title and channel (the page text had no video IDs), so check the top result.</li>
<li>YouTube Shorts were not in the list; search Shorts yourself to compare with a vertical benchmark.</li></ul>""" + fb("S2-V", "📊 Similar videos: what should we copy or avoid?")
    page("s2-v.html", "S2-V Similar videos", body)
