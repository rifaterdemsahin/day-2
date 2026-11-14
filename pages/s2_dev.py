"""S2-DEV Development page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-DEV")
    py_path = ROOT / "scripts/development_embeddings_demo.py"
    py_code = py_path.read_text(encoding="utf-8") if py_path.exists() else ""

    beats = [
        ("Clip c1 · 0–8.8 s",
         "Tokens are just numbers. This one, nine-two-four-six, is a word. But to the AI, it means nothing yet.",
         "🔢 Token ID & Lookup Table",
         """# 1. The vocabulary dictionary maps discrete words to arbitrary integer IDs
VOCABULARY = {
    "king": 9246, "queen": 9247, "man": 512, "woman": 513,
    "crown": 9248, "apple": 2048, "pear": 2049, "grape": 2050
}
token_id = VOCABULARY["king"]  # 9246""",
         "A computer cannot perform math directly on letters. Text is split by a tokenizer into tokens, each assigned an integer index from a fixed vocabulary. The integer 9246 is just an index in a dictionary (like a page number). By itself, 9246 carries no meaning, no semantic relationship to other words, and no understanding."),

        ("Clip c2 · 8.8–14.62 s",
         "So it gets unfolded. One number becomes fifteen hundred and thirty-six coordinates.",
         "🌌 Unfolding into High-Dimensional Vectors",
         """# 2. Embedding matrix: table of size (Vocabulary Size x Embedding Dimension)
# In production models (e.g. OpenAI text-embedding-3-small), D = 1,536 coordinates
# In our toy model, we inspect 4 intuitive semantic dimensions:
# [Royalty, Femininity, Fruit/Edible, Power/Status]
EMBEDDINGS = {
    "king":  [ 0.90, -0.75,  0.02,  0.95],
    "queen": [ 0.92,  0.80,  0.01,  0.94],
    "apple": [-0.85,  0.00,  0.95, -0.60]
}
vector_king = EMBEDDINGS["king"]  # 1 integer -> list of 4 (or 1,536) coordinates""",
         "The model maintains a lookup table (embedding matrix) where every row corresponds to a token ID. Looking up row 9246 yields a list of floating-point numbers. That single integer 'unfolds' into a point in high-dimensional hyperspace. OpenAI's ada-002 and text-embedding-3-small use 1,536 dimensions; larger models use 3,072 or 4,096."),

        ("Clip c3 · 14.62–23.92 s",
         "And meaning becomes distance. Apples, pears, grapes gather here. Kings, queens, crowns, over there.",
         "🧲 Meaning as Distance (Cosine Similarity)",
         """# 3. Closeness in vector space is calculated using Cosine Similarity:
# cosine_similarity(u, v) = (u · v) / (||u|| * ||v||)
def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2)

sim_fruit   = cosine_similarity(EMBEDDINGS["apple"], EMBEDDINGS["pear"])   # +1.0000 (Close cluster)
sim_royalty = cosine_similarity(EMBEDDINGS["king"], EMBEDDINGS["queen"])   # +0.4828 (Close cluster)
sim_mixed   = cosine_similarity(EMBEDDINGS["apple"], EMBEDDINGS["king"])   # -0.6192 (Far apart)""",
         "During training, neural networks learn word vectors such that words appearing in similar sentence contexts end up physically close to each other. Closeness is computed using standard geometry (dot product divided by magnitudes). Fruit words cluster in one area; royal words cluster in another. That geometry is why semantic search and RAG work without keyword matching."),

        ("Clip c4 · 23.92–29.08 s",
         "Now watch. Take king. Subtract man. Add woman.",
         "➕ Vector Arithmetic & Conceptual Directions",
         """# 4. Semantic direction vectors:
# (woman - man) isolates the grammatical/semantic gender direction:
gender_offset = [w - m for w, m in zip(EMBEDDINGS["woman"], EMBEDDINGS["man"])]
# gender_offset = [+0.01, +1.58, 0.00, 0.00] -> purely points in female direction!

# king - man isolates royalty/monarch concept; + woman adds female aspect:
target_vector = [k - m + w for k, m, w in zip(EMBEDDINGS["king"], EMBEDDINGS["man"], EMBEDDINGS["woman"])]
# target_vector = [0.91, 0.83, 0.02, 0.95]""",
         "Because directions in embedding space correspond to semantic concepts, vector arithmetic works directly on meaning! Vector subtraction isolates relational features (e.g., 'woman' minus 'man' creates a vector pointing along the feminine concept). Adding that offset vector to 'king' shifts the position while preserving royalty and power."),

        ("Clip c5 · 29.08–34.98 s",
         "And you land exactly on queen. No one told it. It's just geometry.",
         "👑 Landing on Queen via Nearest Neighbor Search",
         """# 5. Query the dictionary for the nearest coordinate to target_vector:
# Exclude the query words ('man', 'woman'):
# Nearest neighbors to [0.91, 0.83, 0.02, 0.95]:
#   Rank 1: 'queen' (cosine similarity: 0.9998, Euclidean distance: 0.0346) -> 👑 LANDED ON QUEEN!
#   Rank 2: 'crown' (cosine similarity: 0.8457, Euclidean distance: 0.8353)
#   Rank 3: 'king'  (cosine similarity: 0.4685, Euclidean distance: 1.5800)
#   Rank 4: 'grape' (cosine similarity: -0.5953, Euclidean distance: 2.5797)""",
         "When we scan the vocabulary to see which known vector is closest to our target coordinate, the #1 result is 'queen' with 0.9998 similarity! Nobody programmed a rule stating 'queen is female monarch'. The relationship emerged entirely as a geometric property of training on language."),

        ("Clip c6 · 34.98–37.66 s",
         "But how do these vectors talk to each other?",
         "🕸️ Preview of Attention (From Static to Contextual)",
         """# 6. Static vs Dynamic Context (Day 3 Teaser)
# An embedding table provides a static starting vector for each word.
# But 'bank' in 'river bank' != 'bank' in 'bank account'.
# Transformers solve this using Attention:
#   Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V
# In Day 3, vectors dynamically exchange information across the sentence!""",
         "Static embeddings give a word like 'bank' a single fixed point in space. But human words are polysemous: their meaning depends on the sentence. Attention is the mechanism that lets word vectors interact, pulling context from adjacent words and shifting dynamically. This question loops the video and sets up Day 3.")
    ]

    beat_cards = ""
    for clip, say, title, code, expl in beats:
        beat_cards += (f'<div class="card research"><div class="meta">🎬 {clip} · 🗣️ “{E(say)}”</div>'
                       f'<h2 style="margin-top:6px">{title}</h2>'
                       f'<pre><code>{E(code)}</code></pre>'
                       f'<p>{E(expl)}</p>'
                       f'{copybtn(code, "📋 Copy code snippet")}'
                       f'{fb("S2-DEV." + clip[:2], "💻 " + clip[:2] + " code explanation")}</div>')

    interactive_widget = """
<div class="card hero">
  <h2 style="margin-top:0">⚡ Interactive Embeddings Playground</h2>
  <p class="intro">Test the exact mathematical principles from the short directly in your browser. Click words, calculate similarities, and run live vector arithmetic.</p>
  
  <div style="margin: 16px 0; padding: 12px; background: var(--bg); border-radius: 10px; border: 1px solid var(--line);">
    <h3 style="margin-top:0">1. 🔢 Token Lookup & Dimension Unfolding (Clips c1 & c2)</h3>
    <p>Click any token to inspect its integer ID and unfold it into its 4D coordinates <code>[Royalty, Femininity, Fruit, Power]</code>:</p>
    <div id="token-buttons" style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px;"></div>
    <div id="token-display" style="padding:10px; background:var(--panel); border:1px solid var(--line); border-radius:8px; font-family:ui-monospace,Menlo,monospace; font-size:14px;"></div>
  </div>

  <div style="margin: 16px 0; padding: 12px; background: var(--bg); border-radius: 10px; border: 1px solid var(--line);">
    <h3 style="margin-top:0">2. 🧲 Distance & Semantic Clusters (Clip c3)</h3>
    <p>Compare cosine similarity between any two words. Notice how fruits cluster together, royalty cluster together, and cross-cluster words are far apart:</p>
    <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px;">
      <select id="sim-w1" style="background:var(--panel); color:var(--fg); border:1px solid var(--line); border-radius:6px; padding:6px 10px; font-size:14px;"></select>
      <span>↔️</span>
      <select id="sim-w2" style="background:var(--panel); color:var(--fg); border:1px solid var(--line); border-radius:6px; padding:6px 10px; font-size:14px;"></select>
      <button id="btn-compare" class="primary" style="margin:0;">Calculate Distance</button>
      <button id="preset-fruit" style="margin:0;">🍎 apple ↔ 🍐 pear</button>
      <button id="preset-royal" style="margin:0;">👑 king ↔ 👸 queen</button>
      <button id="preset-mixed" style="margin:0;">🍎 apple ↔ 👑 king</button>
    </div>
    <div id="sim-display" style="padding:10px; background:var(--panel); border:1px solid var(--line); border-radius:8px; font-family:ui-monospace,Menlo,monospace; font-size:14px;"></div>
  </div>

  <div style="margin: 16px 0; padding: 12px; background: var(--bg); border-radius: 10px; border: 1px solid var(--line);">
    <h3 style="margin-top:0">3. 👑 Live Vector Arithmetic: king − man + woman (Clips c4 & c5)</h3>
    <p>Perform live linear algebra on word vectors: <code>v_target = v_king - v_man + v_woman</code>, then query the dictionary for the nearest neighbor:</p>
    <button id="btn-arith" class="primary" style="font-size:15px; padding:8px 16px;">⚡ Compute king − man + woman</button>
    <div id="arith-display" style="margin-top:12px; padding:10px; background:var(--panel); border:1px solid var(--line); border-radius:8px; font-family:ui-monospace,Menlo,monospace; font-size:14px; display:none;"></div>
  </div>
</div>

<script>
(function() {
  const VOCAB = {
    "king":  { id: 9246, vec: [ 0.90, -0.75,  0.02,  0.95], icon: "👑" },
    "queen": { id: 9247, vec: [ 0.92,  0.80,  0.01,  0.94], icon: "👸" },
    "man":   { id: 512,  vec: [ 0.05, -0.80,  0.00,  0.20], icon: "👨" },
    "woman": { id: 513,  vec: [ 0.06,  0.78,  0.00,  0.20], icon: "👩" },
    "crown": { id: 9248, vec: [ 0.85,  0.00,  0.00,  0.88], icon: "💎" },
    "apple": { id: 2048, vec: [-0.85,  0.00,  0.95, -0.60], icon: "🍎" },
    "pear":  { id: 2049, vec: [-0.82,  0.00,  0.93, -0.58], icon: "🍐" },
    "grape": { id: 2050, vec: [-0.80,  0.00,  0.91, -0.55], icon: "🍇" }
  };
  const DIMS = ["Royalty", "Femininity", "Fruit", "Power"];

  function dot(a, b) { return a.reduce((sum, val, i) => sum + val * b[i], 0); }
  function norm(a) { return Math.sqrt(a.reduce((sum, val) => sum + val * val, 0)); }
  function cosSim(a, b) { const na = norm(a), nb = norm(b); return (na === 0 || nb === 0) ? 0 : dot(a, b) / (na * nb); }
  function euclid(a, b) { return Math.sqrt(a.reduce((sum, val, i) => sum + Math.pow(val - b[i], 2), 0)); }

  // 1. Setup token lookup buttons
  const btnWrap = document.getElementById("token-buttons");
  const tokenDisp = document.getElementById("token-display");
  const sel1 = document.getElementById("sim-w1");
  const sel2 = document.getElementById("sim-w2");

  Object.keys(VOCAB).forEach(word => {
    const item = VOCAB[word];
    const b = document.createElement("button");
    b.innerHTML = `${item.icon} ${word} <small>(${item.id})</small>`;
    b.onclick = () => renderToken(word);
    btnWrap.appendChild(b);

    const o1 = document.createElement("option"); o1.value = word; o1.text = `${item.icon} ${word}`; sel1.appendChild(o1);
    const o2 = document.createElement("option"); o2.value = word; o2.text = `${item.icon} ${word}`; sel2.appendChild(o2);
  });
  sel1.value = "apple";
  sel2.value = "pear";

  function renderToken(word) {
    const it = VOCAB[word];
    let html = `<div style="margin-bottom:6px;"><b>Token:</b> '${word}' &nbsp;|&nbsp; <b>Token ID:</b> <span class="code">${it.id}</span> &nbsp;|&nbsp; <b>Coordinates:</b> [${it.vec.map(v => v.toFixed(2)).join(", ")}]</div>`;
    html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px; margin-top:8px;">';
    DIMS.forEach((d, i) => {
      const v = it.vec[i];
      const pct = Math.round(Math.abs(v) * 100);
      const color = v > 0 ? "var(--acc)" : "var(--chg)";
      html += `<div style="border:1px solid var(--line); border-radius:6px; padding:6px; background:var(--bg);">
        <small style="color:var(--mut);">${d}</small><br><b>${v > 0 ? "+" : ""}${v.toFixed(2)}</b>
        <div style="height:6px; background:var(--line); border-radius:3px; margin-top:4px; overflow:hidden;">
          <div style="height:100%; width:${pct}%; background:${color};"></div>
        </div>
      </div>`;
    });
    html += '</div>';
    tokenDisp.innerHTML = html;
  }
  renderToken("king");

  // 2. Similarity
  function renderSim(w1, w2) {
    sel1.value = w1; sel2.value = w2;
    const v1 = VOCAB[w1].vec, v2 = VOCAB[w2].vec;
    const sim = cosSim(v1, v2);
    const dist = euclid(v1, v2);
    let tag = sim > 0.8 ? "🟢 Very Close Cluster" : (sim > 0.3 ? "🟡 Moderate Semantic Link" : "🔴 Far Apart (Different Meanings)");
    let color = sim > 0.8 ? "var(--ok)" : (sim > 0.3 ? "var(--gold)" : "var(--cut)");
    document.getElementById("sim-display").innerHTML = `
      <div><b>Comparing:</b> ${VOCAB[w1].icon} <b>${w1}</b> &nbsp;↔️&nbsp; ${VOCAB[w2].icon} <b>${w2}</b></div>
      <div style="margin-top:6px; font-size:16px;"><b>Cosine Similarity:</b> <span style="color:${color}; font-weight:700;">${sim.toFixed(4)}</span> &nbsp;|&nbsp; <b>Euclidean Distance:</b> ${dist.toFixed(4)}</div>
      <div style="margin-top:4px; color:${color}; font-weight:600;">${tag}</div>
      <small style="color:var(--mut);">Formula: cos(θ) = (v1 · v2) / (||v1|| * ||v2||). Values near 1.0 indicate identical semantic direction.</small>
    `;
  }
  document.getElementById("btn-compare").onclick = () => renderSim(sel1.value, sel2.value);
  document.getElementById("preset-fruit").onclick = () => renderSim("apple", "pear");
  document.getElementById("preset-royal").onclick = () => renderSim("king", "queen");
  document.getElementById("preset-mixed").onclick = () => renderSim("apple", "king");
  renderSim("apple", "pear");

  // 3. Vector arithmetic
  document.getElementById("btn-arith").onclick = function() {
    const vk = VOCAB["king"].vec;
    const vm = VOCAB["man"].vec;
    const vw = VOCAB["woman"].vec;
    const target = vk.map((k, i) => k - vm[i] + vw[i]);

    // calculate all similarities
    const scored = Object.keys(VOCAB).map(w => ({
      word: w,
      sim: cosSim(target, VOCAB[w].vec),
      dist: euclid(target, VOCAB[w].vec)
    }));
    scored.sort((a, b) => b.sim - a.sim);

    let html = `<div><b>Step 1: King vector</b> &nbsp; = [${vk.map(v => v.toFixed(2)).join(", ")}]</div>`;
    html += `<div><b>Step 2: − Man vector</b>  = [${vm.map(v => (-v).toFixed(2)).join(", ")}]</div>`;
    html += `<div><b>Step 3: + Woman vector</b>= [${vw.map(v => (v > 0 ? "+" : "") + v.toFixed(2)).join(", ")}]</div>`;
    html += `<div style="border-top:1px dashed var(--line); margin:6px 0; padding-top:6px; color:var(--acc);"><b>= Target vector</b> &nbsp; &nbsp;= [${target.map(v => v.toFixed(2)).join(", ")}]</div>`;
    html += '<h4 style="margin:12px 0 6px 0;">Ranked Nearest Neighbors in Vocabulary:</h4>';
    html += '<table style="margin-top:6px;"><tr><th>Rank</th><th>Word</th><th>Cosine Sim</th><th>Distance</th><th>Outcome</th></tr>';
    scored.forEach((it, idx) => {
      const isQueen = it.word === "queen";
      const highlight = isQueen ? "style='background:rgba(255,207,90,0.15); font-weight:700;'" : "";
      html += `<tr ${highlight}><td>#${idx + 1}</td><td>${VOCAB[it.word].icon} ${it.word}</td><td>${it.word === "man" || it.word === "woman" ? it.sim.toFixed(4) + " <small>(input word)</small>" : it.sim.toFixed(4)}</td><td>${it.dist.toFixed(4)}</td><td>${isQueen ? "👑 <b>LANDED ON QUEEN!</b>" : (idx === 1 ? "💎 Close Royal Match" : "")}</td></tr>`;
    });
    html += '</table>';
    html += '<div style="margin-top:10px; color:var(--gold); font-weight:600;">🎯 Result: The nearest non-input vector in the entire vocabulary is QUEEN! Vector math navigated the semantic space without any hardcoded rules.</div>';

    const disp = document.getElementById("arith-display");
    disp.innerHTML = html;
    disp.style.display = "block";
  };
})();
</script>
"""

    why_dev = [
        ("🔢 Integers have no meaning", "Assigning 9246 to 'king' is like giving a book an ISBN number. The number tells you which item it is, but zero information about its contents. This is why language models cannot work directly on token IDs."),
        ("📐 High dimensions create expressive space", "In 1D, words would collide on a single line. In 1,536 dimensions, there is ample geometric room for subtle nuances: royalty, tense, tone, gender, edible items, and scientific terms all have orthogonal axes."),
        ("🧭 Relationships are directions", "Because neural networks learn from context windows, word pairs sharing grammatical or semantic roles develop parallel displacement vectors: (king → queen) is parallel to (man → woman) and (actor → actress)."),
        ("⚡ Geometry replaces hardcoded rules", "You do not need to code thousands of dictionary rules for synonyms, antonyms, or analogies. Vector dot products naturally solve analogies and search queries through matrix multiplication.")
    ]
    why_html = "".join(f'<li><b>{title}</b><br>{desc}</li>' for title, desc in why_dev)

    body = step_head(st) + f"""<div class="card hero">
<b>🧭 The Code in One Paragraph</b>
<p>A language model does arithmetic, not reading. To run the video script in software, we need only four core functions: (1) mapping text to token IDs (<code>king = 9246</code>), (2) looking up that ID in an embedding table to unfold it into coordinates, (3) computing cosine distance between coordinates so related meanings sit close together, and (4) performing vector addition and subtraction (<code>v_king - v_man + v_woman ≈ v_queen</code>). Anyone who understands this code understands the exact mechanics of the short.</p>
{copybtn("A language model does arithmetic, not reading. Discrete words are mapped to token IDs, unfolded into high-dimensional coordinates, and compared with cosine distance. Vector arithmetic (king - man + woman = queen) works because directions in learned vector space encode semantic concepts.", "📋 Copy summary")}
</div>

{interactive_widget}

<h2>🎬 The Script, Beat by Beat (Code Implementation)</h2>
<p class="intro">Each card connects one spoken line from the video script to the exact lines of code that implement it, explaining why the short's script was written this way.</p>
{beat_cards}

<h2>🌍 Why Code & Geometry Matter for AI Developers</h2>
<ol class="why">{why_html}</ol>

<div class="card hero">
<b>💻 Standalone Python Implementation</b>
<p>A clean, zero-dependency Python script implementing the entire pipeline. Run it locally in your terminal:</p>
<code>python3 scripts/development_embeddings_demo.py</code>
<br><br>
{copybtn(py_code, "📋 Copy Python script (scripts/development_embeddings_demo.py)")}
{copybtn("python3 scripts/development_embeddings_demo.py", "📋 Copy command")}
<pre><code>{E(py_code)}</code></pre>
</div>

<div class="card hero"><b>🔗 Sample project</b>
<p>A live build of this same vector-math short, running end to end: <a href="https://token-lens-6a52e9.fly.dev/" target="_blank" rel="noopener">https://token-lens-6a52e9.fly.dev/</a></p>
{copybtn("https://token-lens-6a52e9.fly.dev/", "📋 Copy sample project URL")}
</div>

{fb('S2-DEV', '💻 Development overall: what to add, clarify, or fix?')}"""

    page("development.html", "S2-DEV Development", body)
