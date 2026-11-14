// Shared behaviour: menu fold, copy buttons, per-card feedback, floating notes panel,
// review check marks (per page), progress, copy-all. All state in localStorage.
(function () {
  var P = "d2fb:";
  var PAGE = (location.pathname.split("/").pop() || "index.html");
  var PAGES = window.PAGES || [];
  function pname(h) { var p = PAGES.filter(function (x) { return x[0] === h; })[0]; return p ? p[1] : h; }
  function get(k) { try { return JSON.parse(localStorage.getItem(P + k)) || {}; } catch (e) { return {}; } }
  function set(k, v) { try { localStorage.setItem(P + k, JSON.stringify(v)); } catch (e) {} }
  function flash(btn, txt) { var o = btn.textContent; btn.textContent = txt; btn.classList.add("copied"); setTimeout(function () { btn.textContent = o; btn.classList.remove("copied"); }, 1200); }
  function copy(text, btn) {
    function fallback() { var t = document.createElement("textarea"); t.value = text; document.body.appendChild(t); t.select(); try { document.execCommand("copy"); flash(btn, "✅ Copied!"); } catch (e) { flash(btn, "⚠️ Copy failed"); } t.remove(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { flash(btn, "✅ Copied!"); }, fallback); else fallback();
  }
  var ST = { ok: "✅ approve", chg: "🔧 change", cut: "❌ cut" };
  function line(id, label, d) {
    if (!d.text && !d.s) return "";
    return "💬 [" + id + "] " + label + (d.s ? " — " + ST[d.s] : "") + (d.text ? "\n" + d.text : "");
  }
  function reviewed(h) { return !!get("rev:" + h).v || get("page:" + h).s === "ok"; }
  function pageNote(h) { return get("page:" + h); }

  // ---- menu fold
  var nav = document.getElementById("nav"), mb = document.getElementById("menu-btn");
  try { if (localStorage.getItem("d2menu") === "closed") nav.classList.add("closed"); } catch (e) {}
  if (mb) mb.onclick = function () { var c = nav.classList.toggle("closed"); mb.setAttribute("aria-expanded", !c); try { localStorage.setItem("d2menu", c ? "closed" : "open"); } catch (e) {} };

  // ---- copy buttons
  document.querySelectorAll("button.copy").forEach(function (b) { b.onclick = function () { copy(b.getAttribute("data-copy"), b); }; });

  // ---- per-card feedback boxes
  document.querySelectorAll(".fb").forEach(function (box) {
    var id = box.dataset.fb, label = box.dataset.label, d = get(id);
    box.innerHTML = '<div class="st"><button data-s="ok">✅ Approve</button><button data-s="chg">🔧 Change</button><button data-s="cut">❌ Cut</button></div>' +
      '<textarea placeholder="💬 Your feedback for ' + id + '…"></textarea><button class="fcopy">📋 Copy feedback</button>';
    var ta = box.querySelector("textarea"); ta.value = d.text || "";
    function paint() { box.querySelectorAll(".st button").forEach(function (b) { b.classList.toggle("on", b.dataset.s === d.s); }); }
    paint();
    box.querySelectorAll(".st button").forEach(function (b) { b.onclick = function () { d.s = (d.s === b.dataset.s) ? "" : b.dataset.s; set(id, d); paint(); }; });
    ta.oninput = function () { d.text = ta.value; set(id, d); };
    box.querySelector(".fcopy").onclick = function () { copy(line(id, label, d) || ("💬 [" + id + "] " + label + " — (no comment)"), this); };
  });

  // ---- checklists
  document.querySelectorAll("input[data-check]").forEach(function (c) {
    var k = "chk:" + c.dataset.check; c.checked = !!get(k).v; c.onchange = function () { set(k, { v: c.checked }); };
    // durable state: what the files on disk prove (assets/short.json › production, written by scripts/sync_status.py) wins over this browser
    if (window.PROD && PROD.checks && PROD.checks[c.dataset.check]) { c.checked = true; c.title = "📁 proven by the files on disk (short.json › production)"; var lb = c.closest("label"); if (lb && !lb.querySelector(".disk")) { var sp = document.createElement("small"); sp.className = "disk"; sp.textContent = " 📁 from disk"; lb.appendChild(sp); } }
  });

  // ---- review check marks in the menu (approved pages are hidden; the 👁️ button in the header brings them back)
  var hiddenBtn = document.getElementById("hidden-btn");
  function showHidden() { return localStorage.getItem("d2showHidden") === "1"; }
  function hiddenCount() { return PAGES.filter(function (x) { return x[0] !== "feedback.html" && reviewed(x[0]); }).length; }
  function paintHiddenBtn() {
    if (!hiddenBtn) return;
    var on = showHidden(), n = hiddenCount();
    hiddenBtn.setAttribute("aria-pressed", on ? "true" : "false");
    hiddenBtn.textContent = (on ? "👁️ " : "🙈 ") + "Hidden: " + n;
    hiddenBtn.title = on ? "Approved pages are shown in the menu again (click to hide them)" : "Show the " + n + " approved page(s) that are hidden from the menu";
    hiddenBtn.classList.toggle("on", on);
  }
  function setShowHidden(on) {
    try { localStorage.setItem("d2showHidden", on ? "1" : ""); } catch (e) {}
    var sh = document.getElementById("showHidden"); if (sh) sh.checked = on;
    paintNav(); paintHiddenBtn();
  }
  function paintNav() {
    var force = showHidden();
    document.querySelectorAll("#nav a").forEach(function (a) {
      var h = a.getAttribute("href"), done = reviewed(h);
      a.classList.toggle("done", done);
      if (!a.dataset.t) a.dataset.t = a.textContent;
      a.textContent = (done ? "✔️ " : "") + a.dataset.t;
      // owner feedback: approved pages are hidden from the top menu (shown again if un-reviewed or when 🙈 Hidden is on)
      a.style.display = (done && !force) ? "none" : "";
      a.classList.toggle("was-hidden", done && force);
    });
    paintHiddenBtn();
  }

  // ---- progress (hub + feedback page)
  function paintProgress() {
    var el = document.getElementById("progress"); if (!el) return;
    var list = PAGES.filter(function (x) { return x[0] !== "feedback.html"; });
    var n = list.filter(function (x) { return reviewed(x[0]); }).length;
    el.innerHTML = '<div class="bar-track"><div class="bar-fill" style="width:' + Math.round(100 * n / list.length) + '%"></div></div>' +
      '<b>' + (n === list.length ? "🎉 " : "👀 ") + n + " / " + list.length + " pages reviewed</b><ul class=\"rv\">" +
      list.map(function (x) { return '<li><a href="' + x[0] + '">' + (reviewed(x[0]) ? "✅" : "⬜") + " " + x[1] + "</a></li>"; }).join("") + "</ul>";
  }

  // ---- highlight notes: select any text, attach a note, it stays highlighted
  var root = document.querySelector("main");
  var HL = get("hl:" + PAGE); if (!HL.list) HL.list = [];
  function saveHL() { set("hl:" + PAGE, HL); }
  function hlRead(h) { var d = get("hl:" + h); return d.list || []; }
  function oneLine(t) { return String(t).replace(/\s+/g, " ").trim(); }
  function hlLine(h, it) { return "💬 [" + pname(h) + (it.sec ? " › " + it.sec : "") + "] “" + oneLine(it.quote) + "”" + (it.s ? " — " + ST[it.s] : "") + (it.note ? " → " + it.note : ""); }
  function hlLines(h) { return hlRead(h).map(function (it) { return hlLine(h, it); }); }
  function excluded(el) { return !el || !el.closest || el.closest("textarea,script,style,.fb,button,#panel,#fab,.hlpop,header,footer"); }
  function tnodes() {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: function (n) { return excluded(n.parentElement) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; } });
    var a = [], n, cum = 0; while ((n = w.nextNode())) { a.push({ node: n, start: cum, len: n.nodeValue.length }); cum += n.nodeValue.length; }
    return { list: a, text: a.map(function (x) { return x.node.nodeValue; }).join("") };
  }
  function anchorOf(range) {
    var T = tnodes(), st = -1, en = -1;
    T.list.forEach(function (x) {
      if (!range.intersectsNode(x.node)) return;
      var s0 = x.node === range.startContainer ? x.start + range.startOffset : x.start;
      var e0 = x.node === range.endContainer ? x.start + range.endOffset : x.start + x.len;
      if (st < 0) st = s0; en = e0;
    });
    if (st < 0 || en <= st) return null;
    var quote = T.text.slice(st, en), occ = 0, i = -1;
    while ((i = T.text.indexOf(quote, i + 1)) >= 0 && i < st) occ++;
    return { quote: quote, occ: occ };
  }
  function rangeOf(it, T) {
    var i = -1, k = 0; while (k <= (it.occ || 0)) { i = T.text.indexOf(it.quote, i + 1); if (i < 0) return null; k++; }
    var e = i + it.quote.length, r = document.createRange(), a = false, b = false;
    T.list.forEach(function (x) {
      if (!a && i >= x.start && i <= x.start + x.len && (i < x.start + x.len || x.len === 0)) { r.setStart(x.node, i - x.start); a = true; }
      if (!b && e > x.start && e <= x.start + x.len) { r.setEnd(x.node, e - x.start); b = true; }
    });
    return a && b ? r : null;
  }
  function sectionOf(node) {
    var el = node.nodeType === 1 ? node : node.parentElement, c = el && el.closest(".card");
    if (c) { var m = c.querySelector(".meta,b,h2"); if (m) return oneLine(m.textContent).slice(0, 60); }
    var h = el; while (h && h !== root) { var p = h.previousElementSibling; while (p) { if (/^H[12]$/.test(p.tagName)) return oneLine(p.textContent).slice(0, 60); p = p.previousElementSibling; } h = h.parentElement; }
    var h1 = root.querySelector("h1"); return h1 ? oneLine(h1.textContent).slice(0, 60) : "";
  }
  function paintHL() {
    if (window.CSS && CSS.highlights && window.Highlight) {
      var T = tnodes(), rs = []; HL.list.forEach(function (it) { var r = rangeOf(it, T); if (r) rs.push(r); });
      var hh = new Highlight(); rs.forEach(function (r) { hh.add(r); }); CSS.highlights.set("d2note", hh);
    }
  }
  function jumpHL(it) { var r = rangeOf(it, tnodes()); if (r) { var el = r.startContainer.parentElement; el.scrollIntoView({ block: "center", behavior: "smooth" }); } }
  var pop = document.createElement("div"); pop.className = "hlpop"; pop.hidden = true; document.body.appendChild(pop);
  var pending = null;
  function hidePop() { pop.hidden = true; pending = null; }
  function showPop(rect) {
    pop.innerHTML = '<button class="hladd">💬 Note on this</button>';
    pop.hidden = false;
    var top = rect.top + window.scrollY - 46; if (top < window.scrollY + 56) top = rect.bottom + window.scrollY + 8;
    pop.style.top = top + "px"; pop.style.left = Math.max(8, Math.min(window.scrollX + rect.left, window.scrollX + document.documentElement.clientWidth - 300)) + "px";
    pop.querySelector(".hladd").onclick = openForm;
  }
  function openForm() {
    var q = pending && pending.quote; if (!q) return;
    pop.innerHTML = '<div class="hlq">“' + oneLine(q).slice(0, 120).replace(/</g, "&lt;") + (oneLine(q).length > 120 ? "…" : "") + '”</div>' +
      '<div class="st"><button data-s="ok">✅</button><button data-s="chg">🔧</button><button data-s="cut">❌</button></div>' +
      '<textarea placeholder="💬 Your note on this passage…"></textarea><div><button class="primary hlsave">💾 Save</button><button class="hlcancel">Cancel</button></div>';
    var s = "", ta = pop.querySelector("textarea");
    pop.querySelectorAll(".st button").forEach(function (b) { b.onclick = function () { s = (s === b.dataset.s) ? "" : b.dataset.s; pop.querySelectorAll(".st button").forEach(function (x) { x.classList.toggle("on", x.dataset.s === s); }); }; });
    pop.querySelector(".hlcancel").onclick = hidePop;
    pop.querySelector(".hlsave").onclick = function () {
      HL.list.push({ id: Date.now(), quote: pending.quote, occ: pending.occ, sec: pending.sec, note: ta.value.trim(), s: s });
      saveHL(); hidePop(); try { getSelection().removeAllRanges(); } catch (e) {} paintHL(); renderHL();
    };
    ta.focus();
  }
  function onSel() {
    if (pop.contains(document.activeElement) && !pop.hidden && pop.querySelector("textarea")) return;
    var sel = getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { if (!pop.querySelector("textarea")) hidePop(); return; }
    var r = sel.getRangeAt(0);
    if (!root.contains(r.commonAncestorContainer) || excluded(r.commonAncestorContainer.nodeType === 1 ? r.commonAncestorContainer : r.commonAncestorContainer.parentElement)) return;
    var an = anchorOf(r); if (!an || oneLine(an.quote).length < 3) return;
    an.sec = sectionOf(r.startContainer); pending = an; showPop(r.getBoundingClientRect());
  }
  var selT; ["mouseup", "keyup", "touchend"].forEach(function (ev) { document.addEventListener(ev, function () { clearTimeout(selT); selT = setTimeout(onSel, 30); }); });
  document.addEventListener("mousedown", function (e) { if (!pop.contains(e.target)) hidePop(); });
  pop.addEventListener("mousedown", function (e) { if (e.target.tagName !== "TEXTAREA") e.preventDefault(); });
  var renderHL = function () {};

  // ---- text of this page's feedback (page note + every card on it)
  function pageText() {
    var parts = [], pn = pageNote(PAGE), l = line("page:" + PAGE, "📄 " + pname(PAGE), pn);
    if (l) parts.push(l);
    document.querySelectorAll(".fb").forEach(function (b) { var s = line(b.dataset.fb, b.dataset.label, get(b.dataset.fb)); if (s) parts.push(s); });
    hlLines(PAGE).forEach(function (x) { parts.push(x); });
    return (reviewed(PAGE) ? "✅ Reviewed: " : "📄 ") + pname(PAGE) + (parts.length ? "\n\n" + parts.join("\n\n") : "\n(no comments)");
  }

  // ---- 🚀 Run on sprite: build one Terminal command that sends the notes to Claude on the Fly.io Sprite
  function spriteCmd(notes) {
    var S = window.SPRITE || {}, name = S.name || "day-2", dir = S.dir || "~/day-2", pages = S.pages || "";
    var prompt = "You are on the Sprite with the day-2 repo as the current folder. Do this in order:\n" +
      "1. git pull --rebase origin main. The briefing is CLAUDE.md (do NOT read MASTER_SPEC.md; open at most one spec/*.md file if needed).\n" +
      "2. Apply the owner's feedback below. Facts live in assets/short.json and scripts/, never hand-edit generated pages; add emojis; keep every page's feedback buttons.\n" +
      "3. Run: python3 -I scripts/build_short_site.py\n" +
      "4. Edit the matching spec/*.md and README.md if a rule changed, and add one new entry at the top of assets/iterations.json, then rebuild.\n" +
      "5. git add -A, commit with an emoji message, git push origin main.\n" +
      "6. Check " + pages + " answers HTTP 200 and report what changed in 5 lines.\n" +
      "Never commit media or secrets. Do not run destructive commands.\n\nOWNER FEEDBACK:\n" + notes;
    return "sprite exec -s " + name + " --stdin -- bash -lc 'cd " + dir + " && claude -p \"$(cat)\" --permission-mode acceptEdits --allowedTools \"Bash(git:*) Bash(python3:*) Bash(curl:*) Bash(ls:*) Edit Write Read Glob Grep\"' <<'D2FEEDBACK'\n" + prompt + "\nD2FEEDBACK\n";
  }

  // ---- refresh banner: shown after a 🚀 run deploys, or when a newer deploy is live than the one this page loaded
  function showBanner(text) {
    var b = document.getElementById("rbanner");
    if (!b) { b = document.createElement("div"); b.id = "rbanner"; document.body.appendChild(b); }
    b.innerHTML = '<span id="rbtext"></span> <button id="rbgo" class="primary">🔄 Refresh now</button> <button id="rbx" aria-label="Dismiss">✖️</button>';
    b.querySelector("#rbtext").textContent = text; b.hidden = false;
    b.querySelector("#rbgo").onclick = function () { location.reload(); };
    b.querySelector("#rbx").onclick = function () { b.hidden = true; };
  }
  (function watchDeploys() {
    var seen = null;
    function check() { fetch("deployed.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      if (!d) return; if (seen === null) { seen = d.at; return; }
      if (d.at !== seen) { seen = d.at; showBanner("🆕 A newer version is live (deployed " + d.at.replace("T", " ").replace("Z", " UTC") + ")."); }
    }).catch(function () {}); }
    check(); setInterval(check, 45000);
  })();

  // ---- shared: stream a run from the local runner into a <pre>
  // step 1 of a run: show the exact prompt (task + your notes) and the routing, and send only after "Send"
  function runAgent(notes, btn, agent, out, msg) {
    var port = (window.SPRITE && window.SPRITE.runner_port) || 8947;
    if (/\(no comments\)|No comments written yet/.test(notes)) { msg.textContent = "✍️ Write a note first (the 📝 panel, a card, or highlight text), then press 🚀."; return; }
    var old = document.getElementById("d2prev"); if (old) old.remove();
    var box = document.createElement("div"); box.id = "d2prev"; box.className = "card"; out.parentNode.insertBefore(box, out);
    box.innerHTML = "<b>👀 Prompt to send</b> <small id=\"d2pm\">asking the runner…</small><pre id=\"d2pp\"></pre><div class=\"bar\"><button id=\"d2send\" class=\"primary\" disabled>🚀 Send</button><button id=\"d2cancel\">✖️ Cancel</button><button id=\"d2copy\">📋 Copy prompt</button></div>";
    var pp = box.querySelector("#d2pp"), pm = box.querySelector("#d2pm"), send = box.querySelector("#d2send"), prompt = "";
    box.querySelector("#d2cancel").onclick = function () { box.remove(); msg.textContent = "Cancelled: nothing was sent."; };
    box.querySelector("#d2copy").onclick = function () { copy(prompt || notes, this); };
    fetch("http://127.0.0.1:" + port + "/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes: notes, agent: agent.split(":")[0], model: agent.split(":")[1] || undefined, preview: true }) })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (j) { prompt = j.prompt; pp.textContent = j.prompt; pm.textContent = "🧭 " + j.agent + (j.model_id ? " (" + j.model_id + ")" : "") + " · " + j.why + " · " + j.chars.toLocaleString() + " characters"; send.disabled = false; })
      .catch(function () { pp.textContent = "(runner not reachable, so this is only your notes)\n\n" + notes; pm.textContent = "❌ start it: python3 scripts/notes_runner.py"; });
    send.onclick = function () { box.remove(); doRun(notes, btn, agent, out, msg); };
  }
  function doRun(notes, btn, agent, out, msg) {
    var port = (window.SPRITE && window.SPRITE.runner_port) || 8947;
    out.hidden = false; out.textContent = "⏳ connecting to the runner on 127.0.0.1:" + port + " …\n"; btn.disabled = true;
    fetch("http://127.0.0.1:" + port + "/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes: notes, agent: agent.split(":")[0], model: agent.split(":")[1] || undefined }) })
      .then(function (r) {
        if (!r.ok) throw new Error("runner answered " + r.status);
        var rd = r.body.getReader(), dec = new TextDecoder();
        function pump() { return rd.read().then(function (x) { if (x.done) return; out.textContent += dec.decode(x.value, { stream: true }); out.scrollTop = out.scrollHeight; return pump(); }); }
        return pump();
      })
      .then(function () { if (/🎉 DONE \(changed\)/.test(out.textContent)) showBanner("✅ Your note was applied, pushed and deployed. Refresh to see the new version."); msg.innerHTML = /🎉 DONE \(changed\)/.test(out.textContent) ? '✅ Deployed. <a href="" onclick="location.reload();return false">🔄 Reload this page</a>' : (/❌/.test(out.textContent) ? "❌ Run failed, see the log." : "ℹ️ Finished."); })
      .catch(function () { out.textContent += "\n❌ Runner not reachable. Start it in Terminal: python3 scripts/notes_runner.py   (or press 📋 command and paste that instead)"; })
      .then(function () { btn.disabled = false; });
  }
  function previewCmd() {
    var S = window.SPRITE || {};
    return "sprite exec -s " + (S.name || "day-2") + " --no-stdin -- sprite-env services restart " + (S.preview_service || "preview");
  }

  // ---- floating notes panel (every page except the feedback summary)
  function allText() {
    var parts = [], n = 0;
    PAGES.forEach(function (x) { if (reviewed(x[0])) n++; var l = line("page:" + x[0], "📄 " + x[1], pageNote(x[0])); if (l) parts.push(l); hlLines(x[0]).forEach(function (y) { parts.push(y); }); });
    (window.FB_IDS || []).forEach(function (x) { var l = line(x[0], x[1], get(x[0])); if (l) parts.push(l); });
    return "🎬 Feedback on the S2 short · ✅ " + n + "/" + PAGES.filter(function (x) { return x[0] !== "feedback.html"; }).length + " pages reviewed\n\n" +
      (parts.length ? parts.join("\n\n") : "🫥 No comments written yet.");
  }
  if (PAGE !== "feedback.html") {
    var fab = document.createElement("button"); fab.id = "fab"; fab.title = "Notes (press N)"; fab.textContent = "📝";
    var panel = document.createElement("div"); panel.id = "panel"; panel.hidden = true;
    panel.innerHTML = '<div class="ph"><b>📝 Notes · ' + pname(PAGE) + '</b><span><button id="pbig" title="Big centered view (Esc to shrink)" aria-label="Big view">⤢ Big</button> <button id="pclose" aria-label="Close">✖️</button></span></div>' +
      '<div class="st"><button data-s="ok">✅ Approve</button><button data-s="chg">🔧 Change</button><button data-s="cut">❌ Cut</button></div>' +
      '<textarea id="pnote" placeholder="💬 Quick note about this whole page…"></textarea>' +
      '<div class="hltitle">✨ Highlight notes on this page <small>(select any text to add one)</small></div><div id="hlist"></div>' +
      '<label class="rvchk"><input type="checkbox" id="prev"> ✔️ I have reviewed this page</label>' +
      '<div class="pb"><button id="pcopy" class="primary">📋 Copy this page</button><button id="pall">📋 Copy all</button><button id="pclear" title="Clears this page\'s note, status and highlight notes (asks twice)">🗑️ Clear notes</button><a href="feedback.html">💬 Summary</a></div>' +
      '<div class="pb"><select id="pagent" title="auto picks by note size: small to kilo (free), medium to claude haiku, larger to claude"><option value="auto">🧭 auto (by size)</option><option value="kilo">🧠 kilo (free)</option><option value="claude:haiku">🤖 claude haiku (cheap)</option><option value="claude">🤖 claude (primary)</option><option value="antigravity">🪐 antigravity</option></select><button id="psp" class="primary" title="Sends this page\'s notes to the agent on your Fly.io Sprite, then pushes and redeploys">🚀 Run: this page</button><button id="pspa">🚀 all notes</button></div>' +
      '<div class="pb"><button id="pspc" title="Copies a Terminal command instead (no runner needed)">📋 command</button><a href="s2-sp.html">🛰️ Setup</a></div>' +
      '<small id="pspmsg">Start the runner once: <code>python3 scripts/notes_runner.py</code>, then press 🚀. The agent edits, the runner pushes and redeploys.</small><pre id="pspout" hidden></pre>';
    var pback = document.createElement("div"); pback.id = "pback";
    document.body.appendChild(pback); document.body.appendChild(fab); document.body.appendChild(panel);
    function setBig(on) { panel.classList.toggle("big", on); document.body.classList.toggle("pbig", on); var b = panel.querySelector("#pbig"); b.textContent = on ? "⤡ Small" : "⤢ Big"; try { localStorage.setItem("d2big", on ? "1" : "0"); } catch (e) {} if (on) { panel.hidden = false; panel.querySelector("#pnote").focus(); } }
    panel.querySelector("#pbig").onclick = function () { setBig(!panel.classList.contains("big")); };
    pback.onclick = function () { setBig(false); };
    var pd = pageNote(PAGE), pn = panel.querySelector("#pnote"), pr = panel.querySelector("#prev");
    pn.value = pd.text || ""; pr.checked = reviewed(PAGE);
    function paintP() { panel.querySelectorAll(".st button").forEach(function (b) { b.classList.toggle("on", b.dataset.s === pd.s); }); fab.classList.toggle("done", reviewed(PAGE)); fab.textContent = reviewed(PAGE) ? "✅" : (pd.text || pd.s || HL.list.length ? "📝●" : "📝"); }
    paintP();
    renderHL = function () {
      var el = panel.querySelector("#hlist"); el.innerHTML = HL.list.length ? "" : '<small>None yet.</small>';
      HL.list.forEach(function (it) {
        var d = document.createElement("div"); d.className = "hli";
        d.innerHTML = '<span class="hlt">' + (it.s ? { ok: "✅ ", chg: "🔧 ", cut: "❌ " }[it.s] : "") + "“" + oneLine(it.quote).slice(0, 70).replace(/</g, "&lt;") + '”' + (it.note ? "<br>→ " + it.note.replace(/</g, "&lt;") : "") + '</span><button title="Jump">🔎</button><button title="Delete">✖️</button>';
        var bs = d.querySelectorAll("button"); bs[0].onclick = function () { jumpHL(it); }; bs[1].onclick = function () { HL.list = HL.list.filter(function (x) { return x.id !== it.id; }); saveHL(); paintHL(); renderHL(); paintP(); };
        el.appendChild(d);
      });
      paintP();
    };
    renderHL();
    function toggle(open) { panel.hidden = open === undefined ? !panel.hidden : !open; try { localStorage.setItem("d2panel", panel.hidden ? "0" : "1"); } catch (e) {} if (panel.hidden) { panel.classList.remove("big"); document.body.classList.remove("pbig"); panel.querySelector("#pbig").textContent = "⤢ Big"; } if (!panel.hidden) pn.focus(); }
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("big")) { e.preventDefault(); setBig(false); } });
    fab.onclick = function () { toggle(); };
    panel.querySelector("#pclose").onclick = function () { toggle(false); };
    panel.querySelectorAll(".st button").forEach(function (b) { b.onclick = function () { pd.s = (pd.s === b.dataset.s) ? "" : b.dataset.s; set("page:" + PAGE, pd); pr.checked = reviewed(PAGE); paintP(); paintNav(); paintProgress(); }; });
    pn.oninput = function () { pd.text = pn.value; set("page:" + PAGE, pd); paintP(); };
    pr.onchange = function () { set("rev:" + PAGE, { v: pr.checked }); if (!pr.checked && pd.s === "ok") { pd.s = ""; set("page:" + PAGE, pd); } paintP(); paintNav(); paintProgress(); };
    panel.querySelector("#pcopy").onclick = function () { copy(pageText(), this); };
    panel.querySelector("#pall").onclick = function () { copy(allText(), this); };
    var pclr = panel.querySelector("#pclear"), clrT;
    function clrReset() { pclr.dataset.sure = ""; pclr.textContent = "🗑️ Clear notes"; clearTimeout(clrT); }
    pclr.onclick = function () {
      if (!pclr.dataset.sure) { pclr.dataset.sure = "1"; pclr.textContent = "⚠️ Click again to clear"; clrT = setTimeout(clrReset, 4000); return; }
      pd.text = ""; pd.s = ""; pn.value = ""; set("page:" + PAGE, pd); HL.list = []; saveHL(); paintHL(); renderHL(); paintP(); clrReset();
      var m = document.getElementById("pspmsg"); if (m) m.textContent = "🗑️ Cleared this page's notes (note, status and highlights).";
    };
    var pagent = panel.querySelector("#pagent"); pagent.value = (window.SPRITE && window.SPRITE.default_agent) || "kilo";
    function runOnSprite(notes, btn) { runAgent(notes, btn, pagent.value, panel.querySelector("#pspout"), document.getElementById("pspmsg")); }
    panel.querySelector("#psp").onclick = function () { runOnSprite(pageText(), this); };
    panel.querySelector("#pspa").onclick = function () { runOnSprite(allText(), this); };
    panel.querySelector("#pspc").onclick = function () { copy(spriteCmd(pageText()), this); document.getElementById("pspmsg").textContent = "✅ Command copied. Paste it in Terminal (needs S2-SP setup done once)."; };
    document.addEventListener("keydown", function (e) {
      var t = (e.target.tagName || "").toLowerCase();
      if (t === "textarea" || t === "input" || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "n" || e.key === "N") { e.preventDefault(); toggle(); } else if (e.key === "Escape") { if (panel.classList.contains("big")) setBig(false); else toggle(false); }
    });
    try { if (localStorage.getItem("d2panel") === "1") panel.hidden = false; if (localStorage.getItem("d2big") === "1" && !panel.hidden) setBig(true); } catch (e) {}
  }

  // ---- footer: when this was last deployed (site/deployed.json is written at deploy time)
  (function () {
    var el = document.getElementById("deployed"); if (!el) return;
    function ago(ms) { var s = Math.max(0, Math.round((Date.now() - ms) / 1000)); if (s < 60) return s + " s"; var m = Math.round(s / 60); if (m < 60) return m + " min"; var h = Math.floor(m / 60); if (h < 48) return h + " h " + (m % 60) + " min"; return Math.floor(h / 24) + " days"; }
    fetch("deployed.json", { cache: "no-store" }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
      function paint() { el.innerHTML = "🕒 Last deployed: <b>" + d.at.replace("T", " ").replace("Z", " UTC") + "</b> · <b>" + ago(d.epoch_ms) + " ago</b> · 🔗 <a href=\"" + d.site + "\">" + d.site.replace("https://", "") + "</a> · <a href=\"" + d.commit_url + "\" target=\"d2-commit\" rel=\"noopener\">commit " + d.commit + "</a>"; }
      paint(); setInterval(paint, 30000);
    }).catch(function () { el.textContent = "🕒 Not deployed from here (local copy): no deploy stamp."; });
  })();

  paintNav(); paintProgress(); paintHL();
  if (hiddenBtn) hiddenBtn.onclick = function () { setShowHidden(!showHidden()); };
  var sh = document.getElementById("showHidden");
  if (sh) { sh.checked = showHidden(); sh.onchange = function () { setShowHidden(sh.checked); }; }
  window.addEventListener("storage", function (e) { if (e.key === "d2showHidden") { var c = document.getElementById("showHidden"); if (c) c.checked = showHidden(); paintNav(); } });

  // ---- feedback page
  if (window.FB_IDS) {
    var pre = document.getElementById("all"), cnt = document.getElementById("count");
    function build() { var t = allText(); cnt.textContent = ""; pre.textContent = t; return t; }
    build();
    document.getElementById("copy-all").onclick = function () { copy(build(), this); };
    var fa = document.getElementById("fagent"); if (fa) {
      fa.value = (window.SPRITE && window.SPRITE.default_agent) || "kilo";
      var fo = document.getElementById("fspout"), fm = document.getElementById("fspmsg");
      document.getElementById("fsp").onclick = function () { runAgent(build(), this, fa.value, fo, fm); };
      document.getElementById("fspc").onclick = function () { copy(spriteCmd(build()), this); fm.textContent = "✅ Execute command copied. Paste it in Terminal."; };
      document.getElementById("fprc").onclick = function () { copy(previewCmd(), this); fm.textContent = "✅ Preview restart command copied (it pulls main, rebuilds, serves on the sprite)."; };
      var S0 = window.SPRITE || {}, sn = S0.name || "day-2", fd = document.getElementById("fdash"); if (fd && S0.dashboard_url) fd.href = S0.dashboard_url;
      document.getElementById("fterm").onclick = function () { copy("sprite console -s " + sn, this); fm.textContent = "✅ Copied. Paste in Terminal for a live shell on the sprite."; };
      document.getElementById("flog").onclick = function () { copy("sprite exec -s " + sn + " --no-stdin -- tail -n 50 -f /.sprite/logs/services/" + (S0.preview_service || "preview") + ".log", this); fm.textContent = "✅ Copied. Paste in Terminal to watch the preview server log."; };
      var pl = document.getElementById("fprev"); if (pl && window.SPRITE && window.SPRITE.preview_url) pl.href = window.SPRITE.preview_url;
    }
    document.getElementById("clear-all").onclick = function () {
      if (confirm("Delete all saved feedback and review marks in this browser?")) {
        try { Object.keys(localStorage).filter(function (k) { return k.indexOf(P) === 0 && k.indexOf(P + "chk:") !== 0; }).forEach(function (k) { localStorage.removeItem(k); }); } catch (e) {}
        build(); paintNav(); paintProgress();
      }
    };
  }
})();
