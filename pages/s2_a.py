"""S2-A Analytics page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-A")

    table_rows = [
        ("How LLMs Actually Read: Tokenization Explained (Day 1)", "0:47", "247.1%", "1:56", "134", "1.9 h", "2", True),
        ("Elon Says Work Is Ending. The Data Says Otherwise.", "9:23", "23.6%", "2:13", "348", "5.1 h", "2", False),
        ("The New Professional Standard: Navigating the AI...", "15:37", "12.4%", "1:56", "236", "7.6 h", "6", False),
        ("Become a Delivery Pilot: Why AI Is Building AI", "25:49", "11.3%", "2:54", "115", "3.0 h", "1", False),
        ("How to Build an AI to Automate LinkedIn Job Hunt", "15:28", "10.1%", "1:34", "264", "6.9 h", "4", False),
        ("How to Actually Learn AI: The Visual Construction...", "16:59", "8.1%", "1:22", "111", "2.4 h", "1", False),
        ("AI No-Code: Build Your Own AI Solutions", "24:54", "7.6%", "1:53", "447", "14.1 h", "5", False),
        ("The Agentic Era: How to Build a Digital Workforce", "19:51", "7.4%", "1:28", "419", "10.2 h", "6", False),
        ("RAISE Your AI SKILLS: Build a RAG Application", "20:56", "7.4%", "1:32", "357", "9.2 h", "2", False),
    ]

    t_html = ""
    for title, dur, pct, vdur, views, wtime, subs, is_day1 in table_rows:
        hl = ' style="background:rgba(255,207,90,0.15); font-weight:700; border-left:4px solid var(--gold);"' if is_day1 else ''
        badge = ' <span style="background:var(--gold); color:#001; border-radius:4px; padding:1px 6px; font-size:11px; margin-left:6px;">⭐ TARGET (DAY 1)</span>' if is_day1 else ''
        t_html += f"""<tr{hl}>
            <td><b>{E(title)}</b>{badge}</td>
            <td><code>{dur}</code></td>
            <td style="color:{'var(--gold)' if is_day1 else 'inherit'}; font-size:{'16px' if is_day1 else '14px'};"><b>{pct}</b></td>
            <td><code>{vdur}</code></td>
            <td>{views}</td>
            <td>{wtime}</td>
            <td>+{subs}</td>
        </tr>"""

    reasons = [
        ("🚀 1. The Algorithmic Loop Threshold (>100% Retention = Viral Distribution)",
         "In short-form recommendation algorithms (YouTube Shorts, TikTok, Reels), retention above 100% is the ultimate gold standard. A view rate of <b>247.1%</b> signals to the algorithm that viewers are not swiping away — they are looping the content. The algorithm rewards content that keeps users on the platform 2.5 times longer than the video's actual duration."),

        ("🔄 2. Real Viewers Watch 2.5 Times Back-to-Back (1:56 on a 47 s Clip)",
         "On a 47-second short, an average duration of <b>1 minute 56 seconds</b> proves that viewers did not just watch once: they let it play through <b>2.47 times</b>. This proves the concept of <i>seamless loop design</i> and <i>high-density visual pacing</i> where every second delivers essential substance."),

        ("🧱 3. The Natural Conceptual Bridge to Day 2",
         "Day 1 was <i>How LLMs Actually Read: Tokenization Explained</i>. It taught viewers that words become integer numbers ('Tokens are just numbers. 9246 is a word'). This creates the immediate, burning question: <b>If words are just numbers, how does an AI know king − man + woman = queen?</b> Day 2 is the natural, irresistible sequel to Day 1's winning narrative."),

        ("⚖️ 4. 47-Second Micro-Education Crushes 25-Minute Overload",
         "The data clearly exposes viewer fatigue on long-form tutorials: 20–25 minute deep dives experience <b>7.4% to 7.6% average view duration</b> (~1.5 minutes viewed before abandoning). In contrast, a 47-second short captured <b>1.9 minutes of undivided attention</b>! The audience prefers dense, bite-sized, visual clarity over 25 minutes of talking head screen shares."),

        ("🎯 5. The Exact Retention Blueprint for Day 2 (S2)",
         "Day 2 is engineered directly around the Day 1 analytics: <ul><li>⏱️ <b>Hard 45 s runtime limit:</b> Never exceed 45 seconds.</li><li>🔄 <b>Audio & visual loop:</b> Last line leads into the first ('…how do these vectors talk to each other? Tokens are just numbers…').</li><li>🥚 <b>Rewatch bait:</b> Token 9246 hidden inside the Queen vector in Scene 4, rewarding viewers who loop.</li><li>🎞️ <b>Pacing:</b> A visual motion change every 2–3 seconds to reset attention.</li></ul>")
    ]
    r_html = "".join(f"<li><b>{t}</b><br>{d}</li>" for t, d in reasons)

    summary_txt = "Why I focus on this video: Day 1 analytics show 247.1% average percentage viewed and 1:56 average view duration on a 47-second video. Micro-runtime educational shorts outperform 25-minute long tutorials by 24x on retention. Day 2 is the direct sequel to this winning formula."

    body = step_head(st) + f"""<div class="card hero">
<b>🎯 Why I Focus on This Video in One Paragraph</b>
<p>YouTube's algorithm prioritizes one metric above all others: <b>Average Percentage Viewed</b>. While the channel's 15–25 minute tutorials average <b>7.4%–11.3%</b> retention, our 47-second Day 1 short (<i>How LLMs Actually Read: Tokenization Explained</i>) achieved an unprecedented <b>247.1% average percentage viewed</b> with an average view duration of <b>1:56</b> (2.47 loops per viewer). This proves that fast-paced, visually dense, seamlessly looping AI shorts are the channel's single highest-leverage format. Day 2 exists to capitalize on this exact audience appetite.</p>
{copybtn(summary_txt, "📋 Copy analytics summary")}
</div>

<h2>📊 The Evidence: YouTube Studio Analytics</h2>
<div class="card">
  <div style="text-align:center;">
    <img src="assets/day1-youtube-analytics.jpeg" alt="YouTube Analytics for Rifat Erdem Sahin channel showing 247.1% retention on Day 1 short" style="width:100%; max-width:820px; border-radius:12px; border:1px solid var(--line); display:block; margin:0 auto; box-shadow:0 8px 30px rgba(0,0,0,0.5);">
    <p class="intro" style="margin-top:10px;">📸 <b>Figure 1:</b> Advanced Mode YouTube Analytics (Last 365 days). The bright green arrow points directly to Day 1: <b>247.1%</b> retention, <b>1:56</b> average view duration on a 47-second video.</p>
  </div>
</div>

<h2>📈 Key Metrics at a Glance</h2>
<div class="grid">
  <div class="card" style="border-color:var(--gold); text-align:center;">
    <small style="color:var(--mut);">Average Percentage Viewed</small>
    <div style="font-size:36px; font-weight:800; color:var(--gold); margin:6px 0;">247.1%</div>
    <small><b>24.5×</b> higher than the channel average (10.1%)</small>
  </div>
  <div class="card" style="border-color:var(--acc); text-align:center;">
    <small style="color:var(--mut);">Average View Duration</small>
    <div style="font-size:36px; font-weight:800; color:var(--acc); margin:6px 0;">1:56</div>
    <small>On a <b>0:47</b> video = <b>2.47 full loops</b> per viewer</small>
  </div>
  <div class="card" style="text-align:center;">
    <small style="color:var(--mut);">Video Runtime</small>
    <div style="font-size:36px; font-weight:800; color:var(--fg); margin:6px 0;">0:47</div>
    <small>Micro-runtime, maximum information density</small>
  </div>
  <div class="card" style="text-align:center;">
    <small style="color:var(--mut);">Algorithmic Status</small>
    <div style="font-size:36px; font-weight:800; color:var(--ok); margin:6px 0;">VIRAL FIT</div>
    <small>>100% threshold achieved organically</small>
  </div>
</div>

<h2>📋 Channel Content Comparison (From Studio Screenshot)</h2>
<p class="intro">Comparing Day 1 against long-form and medium-form videos across the channel:</p>
<div class="tablewrap">
<table class="cmp">
  <thead>
    <tr>
      <th>Video Title</th>
      <th>Duration</th>
      <th>Avg % Viewed</th>
      <th>Avg View Duration</th>
      <th>Views</th>
      <th>Watch Time</th>
      <th>Subs</th>
    </tr>
  </thead>
  <tbody>
    {t_html}
  </tbody>
</table>
</div>
<p class="intro">💡 <b>The Contrast:</b> A 25-minute video gets ~1.5 to 2.5 minutes of view time (7%–11% retention). A 47-second video gets <b>1.9 minutes</b> of view time (247% retention). Viewers give you roughly 2 minutes regardless of video length — make those 2 minutes loop twice!</p>

<h2>🔍 Why I Focus On This Video: 5 Strategic Takeaways</h2>
<ol class="why">{r_html}</ol>

<div class="card hero">
<b>📐 The Day 2 Blueprint (Derived from Day 1 Data)</b>
<p>To replicate and beat Day 1's 247.1% view rate, Day 2 commits to four strict rules:</p>
<ol>
  <li>⚡ <b>Sub-45s duration:</b> Exactly 44.5 s so a 2x rewatch fits comfortably under 2 minutes.</li>
  <li>🔄 <b>Audio handoff:</b> The final spoken question (<i>"But how do these vectors talk to each other?"</i>) flows grammatically into the first hook (<i>"Tokens are just numbers…"</i>).</li>
  <li>🥚 <b>Visual easter egg:</b> The glowing token 9246 returns as a hidden dot inside Queen in Scene 4, rewarding the 2nd loop.</li>
  <li>🚀 <b>Pacing:</b> Dynamic vector math animation every 2–3 seconds to prevent swipe-away.</li>
</ol>
</div>

{fb('S2-A', '📊 Analytics overall: strategy & takeaways')}"""

    page("analytics.html", "S2-A YouTube Analytics", body)
