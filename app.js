// Shared behaviour: menu fold, copy buttons, per-card feedback (localStorage), copy-all.
(function () {
  var P = "d2fb:";
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

  // menu fold
  var nav = document.getElementById("nav"), mb = document.getElementById("menu-btn");
  try { if (localStorage.getItem("d2menu") === "closed") nav.classList.add("closed"); } catch (e) {}
  if (mb) mb.onclick = function () { var c = nav.classList.toggle("closed"); mb.setAttribute("aria-expanded", !c); try { localStorage.setItem("d2menu", c ? "closed" : "open"); } catch (e) {} };

  // copy buttons
  document.querySelectorAll("button.copy").forEach(function (b) { b.onclick = function () { copy(b.getAttribute("data-copy"), b); }; });

  // feedback boxes
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

  // checklists
  document.querySelectorAll("input[data-check]").forEach(function (c) {
    var k = "chk:" + c.dataset.check; c.checked = !!get(k).v; c.onchange = function () { set(k, { v: c.checked }); };
  });

  // feedback page
  if (window.FB_IDS) {
    var pre = document.getElementById("all"), cnt = document.getElementById("count");
    function build() { var parts = []; FB_IDS.forEach(function (x) { var l = line(x[0], x[1], get(x[0])); if (l) parts.push(l); }); cnt.textContent = parts.length + " comment(s)"; pre.textContent = parts.length ? "🎬 Feedback on the S2 short\n\n" + parts.join("\n\n") : "🫥 Nothing yet. Open a step page and write feedback."; return pre.textContent; }
    build();
    document.getElementById("copy-all").onclick = function () { copy(build(), this); };
    document.getElementById("clear-all").onclick = function () { if (confirm("Delete all saved feedback in this browser?")) { FB_IDS.forEach(function (x) { try { localStorage.removeItem(P + x[0]); } catch (e) {} }); build(); } };
  }
})();
