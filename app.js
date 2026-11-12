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

  // ---- text of this page's feedback (page note + every card on it)
  function pageText() {
    var parts = [], pn = pageNote(PAGE), l = line("page:" + PAGE, "📄 " + pname(PAGE), pn);
    if (l) parts.push(l);
    document.querySelectorAll(".fb").forEach(function (b) { var s = line(b.dataset.fb, b.dataset.label, get(b.dataset.fb)); if (s) parts.push(s); });
    return (reviewed(PAGE) ? "✅ Reviewed: " : "📄 ") + pname(PAGE) + (parts.length ? "\n\n" + parts.join("\n\n") : "\n(no comments)");
  }

  // ---- floating notes panel (every page except the feedback summary)
  function allText() {
    var parts = [], n = 0;
    PAGES.forEach(function (x) { if (reviewed(x[0])) n++; var l = line("page:" + x[0], "📄 " + x[1], pageNote(x[0])); if (l) parts.push(l); });
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
      '<label class="rvchk"><input type="checkbox" id="prev"> ✔️ I have reviewed this page</label>' +
      '<div class="pb"><button id="pcopy" class="primary">📋 Copy this page</button><button id="pall">📋 Copy all</button><a href="feedback.html">💬 Summary</a></div>';
    document.body.appendChild(fab); document.body.appendChild(panel);
    var pd = pageNote(PAGE), pn = panel.querySelector("#pnote"), pr = panel.querySelector("#prev");
    pn.value = pd.text || ""; pr.checked = reviewed(PAGE);
    function paintP() { panel.querySelectorAll(".st button").forEach(function (b) { b.classList.toggle("on", b.dataset.s === pd.s); }); fab.classList.toggle("done", reviewed(PAGE)); fab.textContent = reviewed(PAGE) ? "✅" : (pd.text || pd.s ? "📝●" : "📝"); }
    paintP();
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

  paintNav(); paintProgress();

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
