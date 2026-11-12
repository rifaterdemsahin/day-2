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
  function reviewed(h) { return !!get("rev:" + h).v; }
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
  });

  // ---- review check marks in the menu
  function paintNav() {
    document.querySelectorAll("#nav a").forEach(function (a) {
      var h = a.getAttribute("href"), done = reviewed(h);
      a.classList.toggle("done", done);
      if (!a.dataset.t) a.dataset.t = a.textContent;
      a.textContent = (done ? "✔️ " : "") + a.dataset.t;
    });
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
    panel.innerHTML = '<div class="ph"><b>📝 Notes · ' + pname(PAGE) + '</b><button id="pclose" aria-label="Close">✖️</button></div>' +
      '<div class="st"><button data-s="ok">✅ Approve</button><button data-s="chg">🔧 Change</button><button data-s="cut">❌ Cut</button></div>' +
      '<textarea id="pnote" placeholder="💬 Quick note about this whole page…"></textarea>' +
      '<div class="hltitle">✨ Highlight notes on this page <small>(select any text to add one)</small></div><div id="hlist"></div>' +
      '<label class="rvchk"><input type="checkbox" id="prev"> ✔️ I have reviewed this page</label>' +
      '<div class="pb"><button id="pcopy" class="primary">📋 Copy this page</button><button id="pall">📋 Copy all</button><a href="feedback.html">💬 Summary</a></div>';
    document.body.appendChild(fab); document.body.appendChild(panel);
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
    function toggle(open) { panel.hidden = open === undefined ? !panel.hidden : !open; try { localStorage.setItem("d2panel", panel.hidden ? "0" : "1"); } catch (e) {} if (!panel.hidden) pn.focus(); }
    fab.onclick = function () { toggle(); };
    panel.querySelector("#pclose").onclick = function () { toggle(false); };
    panel.querySelectorAll(".st button").forEach(function (b) { b.onclick = function () { pd.s = (pd.s === b.dataset.s) ? "" : b.dataset.s; set("page:" + PAGE, pd); paintP(); }; });
    pn.oninput = function () { pd.text = pn.value; set("page:" + PAGE, pd); paintP(); };
    pr.onchange = function () { set("rev:" + PAGE, { v: pr.checked }); paintP(); paintNav(); paintProgress(); };
    panel.querySelector("#pcopy").onclick = function () { copy(pageText(), this); };
    panel.querySelector("#pall").onclick = function () { copy(allText(), this); };
    document.addEventListener("keydown", function (e) {
      var t = (e.target.tagName || "").toLowerCase();
      if (t === "textarea" || t === "input" || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === "n" || e.key === "N") { e.preventDefault(); toggle(); } else if (e.key === "Escape") toggle(false);
    });
    try { if (localStorage.getItem("d2panel") === "1") panel.hidden = false; } catch (e) {}
  }

  paintNav(); paintProgress(); paintHL();

  // ---- feedback page
  if (window.FB_IDS) {
    var pre = document.getElementById("all"), cnt = document.getElementById("count");
    function build() { var t = allText(); cnt.textContent = ""; pre.textContent = t; return t; }
    build();
    document.getElementById("copy-all").onclick = function () { copy(build(), this); };
    document.getElementById("clear-all").onclick = function () {
      if (confirm("Delete all saved feedback and review marks in this browser?")) {
        try { Object.keys(localStorage).filter(function (k) { return k.indexOf(P) === 0 && k.indexOf(P + "chk:") !== 0; }).forEach(function (k) { localStorage.removeItem(k); }); } catch (e) {}
        build(); paintNav(); paintProgress();
      }
    };
  }
})();
