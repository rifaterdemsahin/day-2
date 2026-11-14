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

  // ---- phase sections (PREPROD, PROD, POSTPROD, Site) fold
  document.querySelectorAll(".navsec").forEach(function (sec) {
    var phase = sec.getAttribute("data-phase");
    var phaseEl = document.querySelector('.navphase[data-phase="' + phase + '"]');
    var key = "d2phase:" + phase;
    try { if (localStorage.getItem(key) === "closed") { phaseEl.classList.add("collapsed"); sec.setAttribute("aria-expanded", "false"); } } catch (e) {}
    function toggle() {
      var c = phaseEl.classList.toggle("collapsed");
      sec.setAttribute("aria-expanded", c ? "false" : "true");
      try { localStorage.setItem(key, c ? "closed" : "open"); } catch (e) {}
    }
    sec.onclick = toggle;
    sec.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } };
  });

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
  // ---- log window: toolbar with ⛶ Full screen (browser full screen, with a fixed overlay as fallback) and 📋 Copy log
  function logFull(out, on) {
    out.classList.toggle("logfull", on);
    var b = out.previousElementSibling; if (b && b.classList.contains("logbar")) { b.querySelector(".lfs").textContent = on ? "⤡ Exit full screen" : "⛶ Full screen"; b.classList.toggle("onfull", on); }
    if (on && out.requestFullscreen) { out.requestFullscreen().catch(function () {}); }
    else if (!on && document.fullscreenElement) { document.exitFullscreen().catch(function () {}); }
  }
  document.addEventListener("fullscreenchange", function () { if (!document.fullscreenElement) document.querySelectorAll(".logfull").forEach(function (o) { logFull(o, false); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") document.querySelectorAll(".logfull").forEach(function (o) { logFull(o, false); }); }, true);
  function ensureLogBar(out) {
    var p = out.previousElementSibling; if (p && p.classList.contains("logbar")) return;
    var bar = document.createElement("div"); bar.className = "logbar";
    bar.innerHTML = '<button class="lfs" title="Show the log full screen (Esc to leave)">⛶ Full screen</button><button class="lcp">📋 Copy log</button><small>run log</small>';
    out.parentNode.insertBefore(bar, out);
    bar.querySelector(".lfs").onclick = function () { logFull(out, !out.classList.contains("logfull")); };
    bar.querySelector(".lcp").onclick = function () { copy(out.textContent, this); };
  }
  var maximize = function () {};
  // step 1 of a run: show the exact prompt (task + your notes) and the routing, and send only after "Send"
  function runAgent(notes, btn, agent, out, msg) {
    var port = (window.SPRITE && window.SPRITE.runner_port) || 8947;
    if (/\(no comments\)|No comments written yet/.test(notes)) { msg.textContent = "✍️ Write a note first (the 📝 panel, a card, or highlight text), then press 🚀."; return; }
    var old = document.getElementById("d2prev"); if (old) old.remove();
    var oldB = document.getElementById("d2back"); if (oldB) oldB.remove();
    var box = document.createElement("div"); box.id = "d2prev"; box.className = "card"; out.parentNode.insertBefore(box, out);
    // maximize: the notes panel becomes the big centered window; on the feedback page the preview itself becomes a modal
    if (document.getElementById("panel")) maximize(); else { box.classList.add("modal"); var bk = document.createElement("div"); bk.id = "d2back"; document.body.appendChild(bk); }
    var pnl = document.getElementById("panel"); if (pnl) pnl.classList.add("previewing");
    setTimeout(function () { box.scrollIntoView({ block: "nearest", behavior: "smooth" }); }, 50);
    function closeBox() { if (pnl) pnl.classList.remove("previewing"); box.remove(); var b = document.getElementById("d2back"); if (b) b.remove(); document.removeEventListener("keydown", escKey, true); }
    function escKey(ev) { if (ev.key === "Escape" && box.classList.contains("modal")) { ev.preventDefault(); closeBox(); msg.textContent = "Cancelled: nothing was sent."; } }
    document.addEventListener("keydown", escKey, true);
    var enh = true; try { enh = localStorage.getItem("d2enh") !== "0"; } catch (e) {}
    box.innerHTML = "<b>👀 Prompt to send</b> <small id=\"d2pm\">asking the runner…</small><div id=\"d2en\" class=\"enh\"></div>" +
      "<label class=\"check\"><input type=\"checkbox\" id=\"d2enh\"" + (enh ? " checked" : "") + "> ✨ Improve with DeepSeek (product-manager rewrite) before sending</label>" +
      "<details id=\"d2orig\"><summary>📝 Your original notes</summary><pre id=\"d2po\"></pre></details>" +
      "<details id=\"d2wrap\"><summary>🧰 Task instructions the runner adds (read only)</summary><pre id=\"d2pw\"></pre></details>" +
      "<div><b>✏️ Enhanced prompt: edit it before sending</b> <small id=\"d2cc\"></small></div><textarea id=\"d2pp\" spellcheck=\"false\" disabled></textarea>" +
      "<div class=\"bar\"><button id=\"d2send\" class=\"primary\" disabled>🚀 Send</button><button id=\"d2cancel\">✖️ Cancel</button><button id=\"d2copy\">📋 Copy full prompt</button><button id=\"d2reset\">↩️ Reset to enhanced</button></div>";
    var pp = box.querySelector("#d2pp"), pm = box.querySelector("#d2pm"), send = box.querySelector("#d2send"), en = box.querySelector("#d2en"), cc = box.querySelector("#d2cc"),
        wrapper = "", base = notes, sendAgent = agent, enhBy = null;
    function full() { return wrapper + "OWNER FEEDBACK:\n" + pp.value.trim() + "\n"; }
    function count() { var ed = pp.value.trim() !== base.trim(); cc.textContent = pp.value.length.toLocaleString() + " characters" + (ed ? " · ✏️ edited by you" : ""); }
    pp.oninput = count;
    box.querySelector("#d2po").textContent = notes;
    box.querySelector("#d2cancel").onclick = function () { closeBox(); msg.textContent = "Cancelled: nothing was sent."; };
    box.querySelector("#d2copy").onclick = function () { copy(wrapper ? full() : pp.value, this); };
    box.querySelector("#d2reset").onclick = function () { pp.value = base; count(); };
    function ask() {
      send.disabled = true; pp.disabled = true; pm.textContent = "asking the runner…"; en.textContent = "";
      var on = box.querySelector("#d2enh").checked; try { localStorage.setItem("d2enh", on ? "1" : "0"); } catch (e) {}
      fetch("http://127.0.0.1:" + port + "/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes: notes, agent: agent.split(":")[0], model: agent.split(":")[1] || undefined, preview: true, enhance: on }) })
        .then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (j) {
          var i = j.prompt.indexOf("OWNER FEEDBACK:\n"); wrapper = i >= 0 ? j.prompt.slice(0, i) : "";
          box.querySelector("#d2pw").textContent = wrapper;
          base = j.improved || notes; pp.value = base; pp.disabled = false; count(); enhBy = j.enhanced_by || null;
          sendAgent = j.agent + (j.agent === "claude" && j.model && j.model !== "default" ? ":" + j.model : "");
          pm.textContent = "🧭 " + j.agent + (j.model_id ? " (" + j.model_id + ")" : "") + " · " + j.why;
          en.innerHTML = j.enhanced_by ? "✨ <b>Prompt enhanced with " + (j.enhancer || "DeepSeek") + " (" + j.enhanced_by + ")</b> as a product manager (Role · Context · Rules · Constraints). Your notes were sent to " + (j.enhancer || "DeepSeek") + " to do this. <b>Edit the text below if you want, then press Send.</b>"
            : (j.enhance_error ? "⚠️ Not enhanced (" + j.enhance_error.replace(/</g, "&lt;") + "): your original notes are used. You can still edit them below." : "➖ Enhancement is off: your original notes are used. You can still edit them below.");
          send.disabled = false;
        })
        .catch(function () { pp.value = notes; pm.textContent = "❌ runner not reachable: start it with python3 scripts/notes_runner.py"; });
    }
    box.querySelector("#d2enh").onchange = ask; ask();
    send.onclick = function () { var txt = pp.value.trim(); if (!txt) { pm.textContent = "✍️ The prompt is empty."; return; } var ed = txt !== base.trim(); closeBox(); doRun(txt, btn, sendAgent, out, msg, enhBy, ed); };
  }
  function doRun(notes, btn, agent, out, msg, enhBy, edited) {
    var port = (window.SPRITE && window.SPRITE.runner_port) || 8947;
    out.hidden = false; ensureLogBar(out); out.textContent = "⏳ connecting to the runner on 127.0.0.1:" + port + " …\n"; btn.disabled = true;
    fetch("http://127.0.0.1:" + port + "/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes: notes, agent: agent.split(":")[0], model: agent.split(":")[1] || undefined, enhanced_by: enhBy || undefined, edited: edited || undefined }) })
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
      '<div class="pb"><button id="ppick" title="Click any element on the page: its reference (page + id or selector + text) is copied and added to your note">🎯 Pick element</button><small id="ppickmsg">point at anything to add its reference</small></div>' +
      '<div class="pb"><select id="pagent" title="auto picks by note size: small to kilo (free), medium to claude haiku, larger to claude"><option value="auto">🧭 auto (by size)</option><option value="kilo">🧠 kilo (free)</option><option value="claude:haiku">🤖 claude haiku (cheap)</option><option value="claude">🤖 claude (primary)</option><option value="antigravity">🪐 antigravity</option></select><button id="psp" class="primary" title="Sends this page\'s notes to the agent on your Fly.io Sprite, then pushes and redeploys">🚀 Sprite Implement</button><button id="pspa">🚀 all notes</button></div>' +
      '<div class="pb"><button id="pspc" title="Copies a Terminal command instead (no runner needed)">📋 command</button><a href="s2-sp.html">🛰️ Setup</a></div>' +
      '<small id="pspmsg">Start the runner once: <code>python3 scripts/notes_runner.py</code>, then press 🚀. The agent edits, the runner pushes and redeploys.</small><pre id="pspout" hidden></pre>';
    var pback = document.createElement("div"); pback.id = "pback";
    document.body.appendChild(pback); document.body.appendChild(fab); document.body.appendChild(panel);
    function setBig(on) { panel.classList.toggle("big", on); document.body.classList.toggle("pbig", on); var b = panel.querySelector("#pbig"); b.textContent = on ? "⤡ Small" : "⤢ Big"; try { localStorage.setItem("d2big", on ? "1" : "0"); } catch (e) {} if (on) { panel.hidden = false; panel.querySelector("#pnote").focus(); } }
    maximize = function () { setBig(true); };
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

    // ---- 🎯 object picker: point at any element; copies "[page › #id or selector] <tag> "text" · section: …" and adds it to the note
    var picking = false, pbox = null, pbar = null, hover = null, wasHidden = false;
    function inUI(el) { return el.closest && el.closest("#panel,#fab,#pickbar,#rbanner,#pback,#nav,#menu"); }
    function esc(s) { return window.CSS && CSS.escape ? CSS.escape(s) : s.replace(/[^\w-]/g, "\\$&"); }
    function selectorOf(el) {
      if (el.id) return "#" + esc(el.id);
      var ds = ["data-fb", "data-check", "data-s", "data-copy"]; for (var i = 0; i < ds.length; i++) { var v = el.getAttribute && el.getAttribute(ds[i]); if (v) return "[" + ds[i] + "=\"" + v + "\"]"; }
      var parts = [], n = el;
      while (n && n !== document.body && parts.length < 5) {
        if (n.id) { parts.unshift("#" + esc(n.id)); break; }
        var tag = n.tagName.toLowerCase(), sib = n.parentNode ? [].slice.call(n.parentNode.children).filter(function (x) { return x.tagName === n.tagName; }) : [];
        parts.unshift(tag + (sib.length > 1 ? ":nth-of-type(" + (sib.indexOf(n) + 1) + ")" : "")); n = n.parentNode;
      }
      return parts.join(" > ");
    }
    function sectionOf(el) {
      var h = null, n = el;
      while (n && n !== document.body && !h) {
        var p = n; while (p && !h) { p = p.previousElementSibling; if (p && /^H[1-4]$/.test(p.tagName)) h = p; else if (p && p.querySelector) { var hh = p.querySelectorAll("h2,h3"); if (hh.length) h = hh[hh.length - 1]; } }
        n = n.parentNode;
      }
      return h ? oneLine(h.textContent).slice(0, 60) : "";
    }
    function refOf(el) {
      var txt = oneLine(el.innerText || el.value || el.alt || el.title || "").slice(0, 60), sec = sectionOf(el);
      return "🎯 [" + PAGE + " › " + selectorOf(el) + "] <" + el.tagName.toLowerCase() + ">" + (txt ? ' "' + txt + '"' : "") + (sec ? " · section: " + sec : "");
    }
    function pickMove(e) {
      var el = e.target; if (!el || inUI(el)) { pbox.style.display = "none"; hover = null; return; }
      hover = el; var r = el.getBoundingClientRect();
      pbox.style.cssText = "display:block;left:" + r.left + "px;top:" + r.top + "px;width:" + r.width + "px;height:" + r.height + "px";
      pbar.querySelector("span").textContent = "🎯 " + selectorOf(el) + " · click to pick · Esc to cancel";
    }
    function pickEnd(el) {
      picking = false; document.body.classList.remove("picking");
      document.removeEventListener("mousemove", pickMove, true); document.removeEventListener("click", pickClick, true); document.removeEventListener("keydown", pickKey, true);
      if (pbox) pbox.remove(); if (pbar) pbar.remove(); pbox = pbar = null;
      if (!wasHidden) panel.hidden = false;
      var m = document.getElementById("ppickmsg");
      if (el) {
        var ref = refOf(el); try { navigator.clipboard && navigator.clipboard.writeText(ref); } catch (e) {}
        pd.text = (pd.text ? pd.text.replace(/\s+$/, "") + "\n" : "") + ref + "\n→ "; pn.value = pd.text; set("page:" + PAGE, pd); paintP(); pn.focus();
        if (m) m.textContent = "✅ Added and copied: " + ref.slice(0, 80);
      } else if (m) m.textContent = "Cancelled.";
    }
    function pickClick(e) { if (inUI(e.target)) return; e.preventDefault(); e.stopPropagation(); pickEnd(e.target); }
    function pickKey(e) { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); pickEnd(null); } }
    panel.querySelector("#ppick").onclick = function () {
      if (picking) return; picking = true; wasHidden = panel.hidden; panel.hidden = true; document.body.classList.add("picking");
      pbox = document.createElement("div"); pbox.id = "pickbox"; document.body.appendChild(pbox);
      pbar = document.createElement("div"); pbar.id = "pickbar"; pbar.innerHTML = "<span>🎯 Move over the page, click the thing you mean</span> <button>✖️ Cancel</button>"; document.body.appendChild(pbar);
      pbar.querySelector("button").onclick = function () { pickEnd(null); };
      document.addEventListener("mousemove", pickMove, true); document.addEventListener("click", pickClick, true); document.addEventListener("keydown", pickKey, true);
    };
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

  // ---- dictionary: status board, term editor, bulk update (talks to api/main.py)
  if (document.getElementById("d2conn")) {
    var DC = window.DICT || {}, STE = DC.statuses || {}, STS = Object.keys(STE);
    function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k) || ""; if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} return ""; }
    function el(tag, attrs, kids) {
      var n = document.createElement(tag);
      Object.keys(attrs || {}).forEach(function (k) { if (k === "text") n.textContent = attrs[k]; else if (k === "onclick") n.onclick = attrs[k]; else n.setAttribute(k, attrs[k]); });
      (kids || []).forEach(function (c) { n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
      return n;
    }
    function apiBase() { var b = ls("d2api").trim(); if (b) return b.replace(/\/$/, ""); return /^(127\.0\.0\.1|localhost)$/.test(location.hostname) ? DC.local_api : ""; }
    function api(method, path, body) {
      var h = { "Content-Type": "application/json" }, t = ls("d2token");
      if (method !== "GET" && t) h.Authorization = "Bearer " + t;
      return fetch(apiBase() + path, { method: method, headers: h, body: body === undefined ? undefined : JSON.stringify(body) }).then(function (r) {
        return r.text().then(function (tx) {
          var j = null; try { j = JSON.parse(tx); } catch (e) {}
          if (!r.ok) { var d = j && j.detail; throw new Error(r.status + " " + (typeof d === "string" ? d : d && d.rows ? d.rows.filter(function (x) { return x.error; }).map(function (x) { return x.field + ": " + x.error; }).join("; ") : d ? JSON.stringify(d).slice(0, 300) : tx.slice(0, 120))); }
          return j;
        });
      });
    }
    function writeNeedsToken() { if (!ls("d2token")) throw new Error("Enter the edit token first (🔌 Connection)."); }
    var cmsg = document.getElementById("d2cmsg"), ia = document.getElementById("d2api"), it = document.getElementById("d2tok");
    ia.value = ls("d2api"); it.value = ls("d2token");
    function test() {
      cmsg.textContent = "…";
      return api("GET", "/api/health").then(function (h) {
        cmsg.textContent = "✅ API reachable · " + h.terms + " term(s) · writes " + (h.writes_enabled ? "enabled on the server" : "DISABLED on the server (no EDIT_TOKEN)") + (ls("d2token") ? " · token saved in this browser" : " · no token yet (read only)");
        return true;
      }, function (e) { cmsg.textContent = "⚠️ API not reachable at “" + (apiBase() || "this site") + "”: " + e.message + ". Start it (see CLAUDE.md) or set the address."; return false; });
    }
    document.getElementById("d2save").onclick = function () { ls("d2api", ia.value.trim() || null); if (it.value) ls("d2token", it.value.trim()); it.value = ls("d2token"); start(); };
    document.getElementById("d2forget").onclick = function () { ls("d2token", null); it.value = ""; test(); };
    function msgBox(parent) { var m = el("div", { "class": "dmsg", role: "status" }); parent.appendChild(m); return function (txt, ok) { m.textContent = txt; m.className = "dmsg " + (ok === false ? "bad" : ok ? "good" : ""); }; }
    function lastCs(v) { return v === undefined ? ls("d2lastcs") : ls("d2lastcs", v); }

    // ---- diff table (used by bulk preview)
    function diffTable(p) {
      var t = el("table", { "class": "cmp" }, [el("tr", {}, ["#", "Term", "Field", "Old", "→ New", "Result"].map(function (x) { return el("th", { text: x }); }))]);
      function show(v) { var s = v === null || v === undefined ? "∅" : (typeof v === "string" ? v : JSON.stringify(v)); return s.length > 140 ? s.slice(0, 140) + "…" : s; }
      p.rows.forEach(function (r) {
        t.appendChild(el("tr", { "class": r.error ? "rbad" : r.changed ? "rchg" : "" }, [r.i + 1, r.slug, r.field, show(r.old), show(r.new), r.error ? "❌ " + r.error : r.changed ? "🔧 change" : "➖ same"].map(function (x) { return el("td", { text: String(x) }); })));
      });
      return el("div", { "class": "tablewrap" }, [t]);
    }

    // ---- index page: status board + term list + new term + bulk
    var host = document.getElementById("d2terms");
    function renderIndex() {
      host.textContent = "";
      var filter = ls("d2filter") || "";
      api("GET", "/api/terms").then(function (d) {
        var board = el("div", { "class": "board" }), total = d.terms.length;
        function chip(key, label, n) { board.appendChild(el("button", { "class": "chip" + (filter === key ? " on" : ""), onclick: function () { ls("d2filter", key || null); renderIndex(); }, text: label + " " + n })); }
        chip("", "📚 all", total);
        STS.forEach(function (s) { chip(s, STE[s] + " " + s, d.counts[s] || 0); });
        host.appendChild(el("h2", { text: "📊 Status board" })); host.appendChild(board);
        var rows = d.terms.filter(function (x) { return !filter || x.status === filter; });
        var tb = el("table", { "class": "cmp" }, [el("tr", {}, ["Term", "Status", "Hook", "Views", "Rewatch %", "Published"].map(function (x) { return el("th", { text: x }); }))]);
        rows.forEach(function (x) {
          tb.appendChild(el("tr", {}, [el("td", {}, [el("a", { href: "term.html?slug=" + encodeURIComponent(x.slug), text: x.term }), el("br"), el("small", { text: x.slug })]),
            el("td", { text: (STE[x.status] || "") + " " + x.status }), el("td", { text: x.hook }), el("td", { text: x.views == null ? "" : String(x.views) }), el("td", { text: x.rewatch_pct == null ? "" : String(x.rewatch_pct) }), el("td", { text: x.publish_date || "" })]));
        });
        host.appendChild(rows.length ? el("div", { "class": "tablewrap" }, [tb]) : el("p", { "class": "intro", text: "No terms with this status." }));
        newTerm(); bulk();
      }, function (e) { host.appendChild(el("p", { "class": "dmsg bad", text: "⚠️ " + e.message })); });
    }
    function newTerm() {
      var c = el("div", { "class": "card" }), say = null;
      var s = el("input", { id: "ntslug", placeholder: "slug, e.g. attention" }), t = el("input", { id: "ntterm", placeholder: "Term, e.g. Attention" });
      c.appendChild(el("h3", { text: "➕ New term" }));
      c.appendChild(el("div", { "class": "frow" }, [el("label", {}, ["Slug", s]), el("label", {}, ["Term", t])]));
      c.appendChild(el("button", { "class": "primary", text: "➕ Create (status idea)", onclick: function () {
        try { writeNeedsToken(); } catch (e) { return say(e.message, false); }
        api("POST", "/api/terms", { slug: s.value.trim(), term: t.value.trim() }).then(function () { location.href = "term.html?slug=" + encodeURIComponent(s.value.trim()); }, function (e) { say("⚠️ " + e.message, false); });
      } }));
      say = msgBox(c); host.appendChild(c);
    }
    function bulk() {
      var c = el("div", { "class": "card hero", id: "d2bulk" }), say = null, prev = null, prevText = null;
      c.appendChild(el("h3", { text: "🛰️ Bulk update" }));
      c.appendChild(el("p", { "class": "intro", text: "Paste or upload a changes list: [{slug, field, value}, …]. Preview shows the diff and writes nothing. Apply is only possible after a clean preview of exactly this text. Undo reverts a whole change set." }));
      var ta = el("textarea", { id: "d2bulkta", rows: "8", placeholder: JSON.stringify(DC.example, null, 1), "class": "mono" });
      var file = el("input", { type: "file", accept: ".json,application/json" });
      var out = el("div", {}), bApply = el("button", { "class": "primary", text: "✅ Apply", disabled: "disabled" });
      var bPrev = el("button", { text: "👀 Preview" }), bUndo = el("button", { text: "↩️ Undo last" });
      var uid = el("input", { id: "d2undoid", placeholder: "change set id (cs-…)", value: lastCs() });
      function parse() { var j = JSON.parse(ta.value); return Array.isArray(j) ? j : j.changes; }
      file.onchange = function () { var f = file.files[0]; if (!f) return; var r = new FileReader(); r.onload = function () { ta.value = r.result; stale(); }; r.readAsText(f); };
      function stale() { prev = null; bApply.setAttribute("disabled", "disabled"); }
      ta.oninput = stale;
      bPrev.onclick = function () {
        out.textContent = ""; stale(); var ch;
        try { ch = parse(); } catch (e) { return say("⚠️ Not valid JSON: " + e.message, false); }
        try { writeNeedsToken(); } catch (e) { return say(e.message, false); }
        api("POST", "/api/bulk/preview", { changes: ch }).then(function (p) {
          if (p.error) return say("❌ " + p.error, false);
          out.appendChild(diffTable(p));
          if (p.ok) { prev = { p: p, ch: ch }; prevText = ta.value; bApply.removeAttribute("disabled"); say("✅ " + p.count + " row(s), " + (p.count - p.unchanged) + " would change. Nothing written yet. Check the table, then Apply.", true); }
          else say("❌ " + p.errors + " row(s) with errors. Fix them and preview again. Nothing was written.", false);
        }, function (e) { say("⚠️ " + e.message, false); });
      };
      bApply.onclick = function () {
        if (!prev || ta.value !== prevText) return say("⚠️ Preview this exact text first.", false);
        api("POST", "/api/bulk/apply", { changes: prev.ch, preview_id: prev.p.preview_id, source: "ui" }).then(function (r) {
          lastCs(r.change_set); uid.value = r.change_set; stale();
          say("✅ Applied " + r.applied + " change(s) as " + r.change_set + ". Undo reverts exactly this set.", true);
        }, function (e) { say("⚠️ " + e.message, false); });
      };
      bUndo.onclick = function () {
        var id = uid.value.trim(); if (!id) return say("⚠️ No change set id.", false);
        try { writeNeedsToken(); } catch (e) { return say(e.message, false); }
        api("POST", "/api/bulk/undo/" + encodeURIComponent(id)).then(function (r) { say("↩️ Reverted " + r.reverted + " change(s) of " + id + ".", true); stale(); }, function (e) { say("⚠️ " + e.message, false); });
      };
      [ta, el("div", {}, [el("label", {}, ["Or upload a .json file ", file])]), el("div", { "class": "bar" }, [bPrev, bApply]), out, el("div", { "class": "bar" }, [uid, bUndo])].forEach(function (x) { c.appendChild(x); });
      say = msgBox(c); host.appendChild(c);
    }

    // ---- term page
    var tp = document.getElementById("d2term");
    var TEXT = [["term", "Term", 1], ["hook", "Hook", 3], ["definition", "Definition", 4], ["analogy", "Analogy", 3], ["chosen_title", "Chosen title", 1]];
    var LISTS = [["title_options", "Title options (one per line, max 10)", 6], ["voice_lines", "Voice lines (one per line, max 6)", 6]];
    var OTHER = [["rewatch_pct", "Rewatch %", "number"], ["views", "Views", "number"], ["publish_date", "Publish date (YYYY-MM-DD)", "text"], ["youtube_url", "YouTube link", "text"]];
    var SC_TEXT = [["vo", "Voice-over", 2], ["visual", "Visual", 2], ["on_screen_text", "On-screen text", 1], ["prompt", "Flow prompt", 3], ["hf_camera", "Higgsfield camera", 1]];
    function field(label, ctl) { return el("label", { "class": "dfield" }, [label, ctl]); }
    function ctlText(id, val, rows) { var c = rows > 1 ? el("textarea", { id: id, rows: String(rows) }) : el("input", { id: id }); c.value = val == null ? "" : val; return c; }
    function ctlSel(id, opts, val) { var s = el("select", { id: id }); opts.forEach(function (o) { var op = el("option", { value: o, text: (STE[o] ? STE[o] + " " : "") + o }); if (o === val) op.selected = true; s.appendChild(op); }); return s; }
    function renderTerm(note) {
      var slug = new URLSearchParams(location.search).get("slug");
      if (!slug) { tp.appendChild(el("p", { "class": "dmsg bad", text: "No ?slug= in the address. Pick a term from the dictionary." })); return; }
      tp.textContent = "";
      api("GET", "/api/terms/" + encodeURIComponent(slug)).then(function (t) {
        document.getElementById("d2tname").textContent = t.term + " · " + t.slug;
        var form = el("div", { "class": "card" }), say, fields = {};
        form.appendChild(field("Status", fields.status = ctlSel("f-status", STS, t.status)));
        TEXT.forEach(function (f) { form.appendChild(field(f[1], fields[f[0]] = ctlText("f-" + f[0], t[f[0]], f[2]))); });
        LISTS.forEach(function (f) { form.appendChild(field(f[1], fields[f[0]] = ctlText("f-" + f[0], (t[f[0]] || []).join("\n"), f[2]))); });
        var fr = el("div", { "class": "frow" }); OTHER.forEach(function (f) { fr.appendChild(field(f[1], fields[f[0]] = ctlText("f-" + f[0], t[f[0]], 1))); }); form.appendChild(fr);
        var sc = {}; form.appendChild(el("h3", { text: "🎬 Scenes" }));
        t.scenes.forEach(function (s) {
          var box = el("div", { "class": "scene" }, [el("b", { text: "Scene " + s.n })]), r = el("div", { "class": "frow" });
          sc[s.n] = {};
          r.appendChild(field("Start (s)", sc[s.n].start = ctlText("s" + s.n + "-start", s.start, 1)));
          r.appendChild(field("End (s)", sc[s.n].end = ctlText("s" + s.n + "-end", s.end, 1)));
          r.appendChild(field("Clip", sc[s.n].clip_status = ctlSel("s" + s.n + "-clip", ["missing", "ready"], s.clip_status)));
          box.appendChild(r);
          SC_TEXT.forEach(function (f) { box.appendChild(field(f[1], sc[s.n][f[0]] = ctlText("s" + s.n + "-" + f[0], s[f[0]], f[2]))); });
          form.appendChild(box);
        });
        function changes() {
          var out = {};
          function put(name, val, old) { if (JSON.stringify(val) !== JSON.stringify(old == null ? null : old)) out[name] = val; }
          put("status", fields.status.value, t.status);
          TEXT.forEach(function (f) { put(f[0], fields[f[0]].value, t[f[0]]); });
          LISTS.forEach(function (f) { put(f[0], fields[f[0]].value.split("\n").map(function (x) { return x.trim(); }).filter(Boolean), t[f[0]]); });
          OTHER.forEach(function (f) { var v = fields[f[0]].value.trim(); put(f[0], v === "" ? null : f[2] === "number" ? Number(v) : v, t[f[0]]); });
          t.scenes.forEach(function (s) {
            ["start", "end"].forEach(function (k) { var v = sc[s.n][k].value.trim(); put("scenes." + s.n + "." + k, v === "" ? null : Number(v), s[k]); });
            put("scenes." + s.n + ".clip_status", sc[s.n].clip_status.value, s.clip_status);
            SC_TEXT.forEach(function (f) { put("scenes." + s.n + "." + f[0], sc[s.n][f[0]].value, s[f[0]]); });
          });
          return out;
        }
        var save = el("button", { "class": "primary", text: "💾 Save", onclick: function () {
          var ch = changes(), n = Object.keys(ch).length;
          if (!n) return say("➖ Nothing changed.", true);
          try { writeNeedsToken(); } catch (e) { return say(e.message, false); }
          api("PUT", "/api/terms/" + encodeURIComponent(slug), ch).then(function (r) {
            lastCs(r.change_set); renderTerm({ text: "✅ Saved " + r.applied + " change(s) as " + r.change_set + ".", cs: r.change_set });
          }, function (e) { say("⚠️ " + e.message, false); });
        } });
        form.appendChild(el("div", { "class": "bar" }, [save, el("button", { text: "🔄 Reload from server", onclick: function () { renderTerm(); } })]));
        say = msgBox(form); tp.appendChild(form);
        if (note) { say(note.text, true); if (note.cs) form.appendChild(el("button", { text: "↩️ Undo this save", onclick: function () { api("POST", "/api/bulk/undo/" + note.cs).then(function () { renderTerm({ text: "↩️ Reverted " + note.cs + ".", cs: null }); }, function (e) { say("⚠️ " + e.message, false); }); } })); }
      }, function (e) { tp.appendChild(el("p", { "class": "dmsg bad", text: "⚠️ " + e.message })); });
    }
    function start() { test().then(function (ok) { if (!ok) return; if (host) renderIndex(); if (tp) renderTerm(); }); }
    start();
  }
})();
