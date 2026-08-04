/* ================================================================
   ENG1237 — Intersectional Machines
   Shared behaviour: theme toggle + read-aloud (text-to-speech)
   ================================================================ */
(function () {
  "use strict";

  /* ---------------- Theme (light / dark) ---------------- */
  var root = document.documentElement;
  var STORE_KEY = "chs-ib-theme";

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function currentTheme() {
    var attr = root.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    return systemPrefersDark() ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem(STORE_KEY, theme); } catch (e) {}
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var isDark = theme === "dark";
      btn.setAttribute("aria-pressed", String(isDark));
      var lbl = btn.querySelector(".label");
      if (lbl) lbl.textContent = isDark ? "Light mode" : "Dark mode";
      btn.setAttribute("title", isDark ? "Switch to light mode" : "Switch to dark mode");
      var sun = btn.querySelector(".icon-sun");
      var moon = btn.querySelector(".icon-moon");
      if (sun && moon) {
        sun.style.display = isDark ? "" : "none";
        moon.style.display = isDark ? "none" : "";
      }
    }
  }

  // Initialise from stored preference (set as early as possible)
  var stored = null;
  try { stored = localStorage.getItem(STORE_KEY); } catch (e) {}
  if (stored === "light" || stored === "dark") {
    root.setAttribute("data-theme", stored);
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(currentTheme());

    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        applyTheme(currentTheme() === "dark" ? "light" : "dark");
      });
    }

    // Close the sections dropdown when clicking outside / pressing Escape
    var menu = document.getElementById("sections-menu");
    if (menu) {
      document.addEventListener("click", function (e) {
        if (menu.open && !menu.contains(e.target)) menu.open = false;
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && menu.open) menu.open = false;
      });
    }

    setupReader();
    setupLotus();
    setupDrill();
    setupConcepts();
  });

  /* ---------------- Concept leaves (home page) ----------------
     Each leaf around the flower pops a bubble with a short prelude of the
     theories and authors behind that concept.                               */
  function setupConcepts() {
    var pads = document.querySelectorAll(".pad[data-concept]");
    if (!pads.length) return;
    var bubble = document.getElementById("concept-bubble");
    var body = document.getElementById("bubble-body");
    var closeBtn = document.getElementById("bubble-close");
    if (!bubble || !body) return;
    var current = null;

    function place(pad) {
      // Anchor the bubble right beside the clicked term, then clamp on-screen.
      var term = pad.querySelector(".pad-label-in") || pad;
      var lr = term.getBoundingClientRect();
      var br = bubble.getBoundingClientRect();
      var vw = document.documentElement.clientWidth;
      var vh = document.documentElement.clientHeight;
      var gap = 8;
      // put it on whichever side of the term has room
      var left = (lr.left + lr.width / 2 > vw / 2) ? lr.left - br.width - gap : lr.right + gap;
      if (left < 8) left = lr.right + gap;
      if (left + br.width > vw - 8) left = lr.left - br.width - gap;
      var top = lr.top + lr.height / 2 - br.height / 2;   // vertically centered on the term
      left = Math.max(8, Math.min(left, vw - br.width - 8));
      top = Math.max(76, Math.min(top, vh - br.height - 8));
      bubble.style.left = left + "px";
      bubble.style.top = top + "px";
    }

    function open(pad) {
      var id = pad.getAttribute("data-concept");
      var src = document.getElementById("src-" + id);
      if (!src) return;
      if (current) current.setAttribute("aria-expanded", "false");
      body.innerHTML = src.innerHTML;
      bubble.hidden = false;
      // measure once shown, then position
      bubble.style.left = "-9999px"; bubble.style.top = "0";
      place(pad);
      pad.setAttribute("aria-expanded", "true");
      current = pad;
      var h = bubble.querySelector("h3");
      if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    }

    function close() {
      bubble.hidden = true;
      if (current) { current.setAttribute("aria-expanded", "false"); current.focus(); current = null; }
    }

    pads.forEach(function (pad) {
      pad.addEventListener("click", function (e) {
        e.stopPropagation();
        if (current === pad) { close(); } else { open(pad); }
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", close);
    document.addEventListener("click", function (e) {
      if (!bubble.hidden && !bubble.contains(e.target) && !e.target.closest(".pad")) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !bubble.hidden) close();
    });
    window.addEventListener("resize", function () { if (current) place(current); });
  }

  /* ---------------- Petal drill-down (sections 4, 5, 9) ---------------- */
  function setupDrill() {
    var petals = document.querySelectorAll(".petal[data-drill]");
    if (!petals.length) return;

    function closeAll(except) {
      document.querySelectorAll(".drill-panel").forEach(function (pnl) {
        if (pnl === except) return;
        pnl.hidden = true;
      });
      document.querySelectorAll(".petal[data-drill]").forEach(function (pt) {
        if (except && pt.getAttribute("data-drill") === except.id.replace("drill-", "")) return;
        pt.setAttribute("aria-expanded", "false");
      });
    }

    petals.forEach(function (pt) {
      pt.addEventListener("click", function (e) {
        var id = "drill-" + pt.getAttribute("data-drill");
        var panel = document.getElementById(id);
        if (!panel) return;                 // no panel -> let the link work
        e.preventDefault();
        var opening = panel.hidden;
        closeAll(opening ? panel : null);
        panel.hidden = !opening;
        pt.setAttribute("aria-expanded", String(opening));
        if (opening) {
          panel.scrollIntoView({ behavior: "smooth", block: "start" });
          var h = panel.querySelector("h3");
          if (h) { h.setAttribute("tabindex", "-1"); h.focus(); }
        }
      });
    });

    document.querySelectorAll(".drill-close").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-close");
        var panel = document.getElementById("drill-" + id);
        if (panel) panel.hidden = true;
        var pt = document.querySelector('.petal[data-drill="' + id + '"]');
        if (pt) { pt.setAttribute("aria-expanded", "false"); pt.focus(); }
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeAll(null);
    });
  }

  /* ---------------- Lotus flower (home page) ----------------
     A closed bud that blooms open when the student clicks it, revealing
     the syllabus-section petals. Click again to fold it back.          */
  function setupLotus() {
    var stage = document.getElementById("lotus-stage");
    if (!stage) return;
    var center = document.getElementById("lotus-center");
    var hint = document.getElementById("lotus-hint");

    function setOpen(open) {
      if (open) stage.setAttribute("data-open", "");
      else stage.removeAttribute("data-open");
      if (center) center.setAttribute("aria-expanded", String(open));
      if (hint) hint.textContent = open ? "Tap to close" : "Tap to open the syllabus";
    }
    function isOpen() { return stage.hasAttribute("data-open"); }

    if (center) center.addEventListener("click", function () { setOpen(!isOpen()); });

    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // Start closed (a bud) so the student opens it. Reduced-motion users
    // get it already open so the sections are visible without animation.
    setOpen(!!reduce);
  }

  /* ---------------- Read aloud (text-to-speech) ---------------- */
  var synth = window.speechSynthesis;
  var chunks = [];        // array of {el, text}
  var idx = 0;
  var reading = false;
  var paused = false;
  var voices = [];

  function setupReader() {
    var bar = document.getElementById("reader-bar");
    var startBtn = document.getElementById("read-aloud");
    if (!startBtn) return;

    if (!synth || typeof SpeechSynthesisUtterance === "undefined") {
      // Unsupported browser: hide the feature gracefully
      startBtn.disabled = true;
      startBtn.title = "Read-aloud is not supported in this browser";
      startBtn.style.display = "none";
      return;
    }

    loadVoices();
    if (synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = loadVoices;
    }

    startBtn.addEventListener("click", function () {
      if (reading) { stopReading(); } else { startReading(); }
    });

    byId("reader-playpause", function (b) { b.addEventListener("click", togglePause); });
    byId("reader-stop", function (b) { b.addEventListener("click", stopReading); });
    byId("reader-restart", function (b) { b.addEventListener("click", function () { stopReading(); startReading(); }); });

    var rate = document.getElementById("reader-rate");
    if (rate) {
      rate.addEventListener("change", function () {
        if (reading) { // apply new rate from the current sentence
          var resumeAt = idx;
          synth.cancel();
          idx = resumeAt;
          speakFrom(idx);
        }
      });
    }
    var voiceSel = document.getElementById("reader-voice");
    if (voiceSel) {
      voiceSel.addEventListener("change", function () {
        if (reading) {
          var resumeAt = idx;
          synth.cancel();
          idx = resumeAt;
          speakFrom(idx);
        }
      });
    }

    // Stop speech if the user leaves the page
    window.addEventListener("beforeunload", function () { if (synth) synth.cancel(); });
  }

  function byId(id, fn) { var el = document.getElementById(id); if (el) fn(el); }

  function loadVoices() {
    voices = synth.getVoices() || [];
    var sel = document.getElementById("reader-voice");
    if (!sel || !voices.length) return;
    var prev = sel.value;
    sel.innerHTML = "";
    var enVoices = voices.filter(function (v) { return /^en/i.test(v.lang); });
    var list = enVoices.length ? enVoices : voices;
    list.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v.name;
      o.textContent = v.name + " (" + v.lang + ")";
      sel.appendChild(o);
    });
    if (prev) sel.value = prev;
  }

  function chosenVoice() {
    var sel = document.getElementById("reader-voice");
    if (sel && sel.value) {
      for (var i = 0; i < voices.length; i++) {
        if (voices[i].name === sel.value) return voices[i];
      }
    }
    // sensible default: first English voice
    for (var j = 0; j < voices.length; j++) {
      if (/^en/i.test(voices[j].lang)) return voices[j];
    }
    return voices[0] || null;
  }

  // Break the main content into readable chunks, one per block element.
  function buildChunks() {
    chunks = [];
    var main = document.getElementById("main") || document.querySelector("main");
    if (!main) return;
    var selector = "h1, h2, h3, h4, p, li, dt, dd, caption, .due, th, td";
    var nodes = main.querySelectorAll(selector);
    nodes.forEach(function (el) {
      if (el.closest("[data-no-read]")) return;
      // Skip elements nested inside another already-captured block (e.g. <li> inside <p>)
      var txt = (el.textContent || "").replace(/\s+/g, " ").trim();
      if (!txt) return;
      chunks.push({ el: el, text: txt });
    });
  }

  function startReading() {
    buildChunks();
    if (!chunks.length) return;
    idx = 0;
    reading = true;
    paused = false;
    document.getElementById("reader-bar").classList.add("active");
    updateStartBtn(true);
    setStatus("Reading…");
    setPauseLabel();
    speakFrom(0);
  }

  function speakFrom(startIdx) {
    if (startIdx >= chunks.length) { finishReading(); return; }
    idx = startIdx;
    clearHighlight();
    var chunk = chunks[idx];
    highlight(chunk.el);
    var u = new SpeechSynthesisUtterance(chunk.text);
    var v = chosenVoice();
    if (v) { u.voice = v; u.lang = v.lang; }
    var rate = document.getElementById("reader-rate");
    u.rate = rate ? parseFloat(rate.value) || 1 : 1;
    u.onend = function () {
      if (!reading || paused) return;
      idx++;
      setStatus("Reading… (" + Math.min(idx + 1, chunks.length) + " / " + chunks.length + ")");
      speakFrom(idx);
    };
    u.onerror = function () {
      if (!reading) return;
      idx++;
      speakFrom(idx);
    };
    synth.speak(u);
  }

  function togglePause() {
    if (!reading) return;
    if (paused) {
      paused = false;
      synth.resume();
      setStatus("Reading…");
      setPauseLabel();
    } else {
      paused = true;
      synth.pause();
      setStatus("Paused");
      setPauseLabel();
    }
  }

  function stopReading() {
    reading = false;
    paused = false;
    if (synth) synth.cancel();
    clearHighlight();
    var bar = document.getElementById("reader-bar");
    if (bar) bar.classList.remove("active");
    updateStartBtn(false);
    setStatus("");
  }

  function finishReading() {
    reading = false;
    paused = false;
    clearHighlight();
    setStatus("Finished");
    setPauseLabel();
    updateStartBtn(false);
    setTimeout(function () {
      var bar = document.getElementById("reader-bar");
      if (bar && !reading) bar.classList.remove("active");
    }, 2500);
  }

  function setPauseLabel() {
    var b = document.getElementById("reader-playpause");
    if (b) b.textContent = paused ? "▶ Resume" : "⏸ Pause";
  }

  function updateStartBtn(active) {
    var b = document.getElementById("read-aloud");
    if (!b) return;
    b.setAttribute("aria-pressed", String(active));
    var lbl = b.querySelector(".label");
    if (lbl) lbl.textContent = active ? "Stop reading" : "Read aloud";
  }

  function setStatus(msg) {
    var s = document.getElementById("reader-status");
    if (s) s.textContent = msg;
  }

  var lastEl = null;
  function highlight(el) {
    lastEl = el;
    el.classList.add("tts-reading");
    try { el.scrollIntoView({ block: "center", behavior: "smooth" }); } catch (e) {}
  }
  function clearHighlight() {
    if (lastEl) { lastEl.classList.remove("tts-reading"); lastEl = null; }
    var any = document.querySelectorAll(".tts-reading");
    any.forEach(function (n) { n.classList.remove("tts-reading"); });
  }
})();

/* ---- Copy-to-clipboard for citations (all pages) ---------------------- */
(function () {
  function textOf(btn) {
    var row = btn.closest('.cite-row') || btn.closest('.mini-row');
    if (!row) return '';
    var t = row.querySelector('.cite-text, .mini-text');
    if (!t) return '';
    return (t.innerText || t.textContent).replace(/\s+/g, ' ').trim();
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.copy-btn');
    if (!btn) return;
    var txt = textOf(btn);
    if (!txt) return;
    var done = function () {
      var old = btn.dataset.label || btn.textContent;
      btn.dataset.label = old;
      btn.textContent = 'Copied';
      btn.classList.add('copied');
      setTimeout(function () {
        btn.textContent = btn.dataset.label;
        btn.classList.remove('copied');
      }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(done, done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = txt; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (err) {}
      document.body.removeChild(ta); done();
    }
  });
})();

/* ---- Citation size toggle -------------------------------------------- */
(function () {
  var KEY = 'chs-ib-cites';
  var btn = document.getElementById('cite-size');
  if (!btn) return;
  function apply(state) {
    var big = state === 'large';
    document.documentElement.setAttribute('data-cites', big ? 'large' : 'small');
    btn.setAttribute('aria-pressed', big ? 'true' : 'false');
    var l = btn.querySelector('.label');
    if (l) l.textContent = big ? 'Small citations' : 'Bigger citations';
  }
  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) {}
  apply(stored === 'large' ? 'large' : 'small');
  btn.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-cites') === 'large' ? 'small' : 'large';
    try { localStorage.setItem(KEY, next); } catch (e) {}
    apply(next);
  });
})();

/* ---- Notebooks: divider tabs + page flipping (any number per page) ---- */
(function () {
  var books = document.querySelectorAll('.notebook');
  if (!books.length) return;

  books.forEach(function (bookEl) {
    var tabs  = Array.prototype.slice.call(bookEl.querySelectorAll('.nb-tab'));
    var pages = Array.prototype.slice.call(bookEl.querySelectorAll('.nb-page'));
    // Scope controls to this notebook; the home page uses ids, quarters use classes.
    var prev  = bookEl.querySelector('.nb-prev')  || bookEl.querySelector('#nb-prev');
    var next  = bookEl.querySelector('.nb-next')  || bookEl.querySelector('#nb-next');
    var count = bookEl.querySelector('.nb-count') || bookEl.querySelector('#nb-count');
    var noun  = bookEl.classList.contains('notebook-quarters') ? 'Quarter' : 'Page';
    if (!tabs.length || tabs.length !== pages.length) return;
    var at = 0;

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var book = bookEl.querySelector('.nb-book');

    function peel() {
      // A ghost sheet that lifts off the spine while the new page settles.
      if (reduce || !book) return;
      var old = book.querySelector('.nb-sheet');
      if (old) old.remove();
      var sheet = document.createElement('div');
      sheet.className = 'nb-sheet';
      book.appendChild(sheet);
      sheet.addEventListener('animationend', function () { sheet.remove(); });
    }

    function show(i, focusTab, animate) {
      var from = at;
      at = Math.max(0, Math.min(pages.length - 1, i));
      if (animate !== false && at !== from) {
        bookEl.setAttribute('data-dir', at > from ? 'fwd' : 'back');
        peel();
      }
      tabs.forEach(function (t, n) {
        var on = n === at;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
      });
      pages.forEach(function (p, n) {
        p.hidden = n !== at;
        p.classList.remove('is-active');
      });
      // restart the animation on the page that just became visible
      void pages[at].offsetWidth;
      pages[at].classList.add('is-active');
      if (prev) prev.disabled = at === 0;
      if (next) next.disabled = at === pages.length - 1;
      if (count) count.textContent = noun + ' ' + (at + 1) + ' of ' + pages.length;
      if (focusTab) tabs[at].focus();
    }

    tabs.forEach(function (t, n) {
      t.addEventListener('click', function () { show(n); });
    });
    if (prev) prev.addEventListener('click', function () { show(at - 1); });
    if (next) next.addEventListener('click', function () { show(at + 1); });

    bookEl.querySelector('.nb-tabs').addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowDown' || k === 'ArrowRight') { e.preventDefault(); show(at + 1, true); }
      else if (k === 'ArrowUp' || k === 'ArrowLeft') { e.preventDefault(); show(at - 1, true); }
      else if (k === 'Home') { e.preventDefault(); show(0, true); }
      else if (k === 'End') { e.preventDefault(); show(pages.length - 1, true); }
    });

    // Global arrows drive a notebook only when it is the only one on the page.
    if (books.length === 1) {
      document.addEventListener('keydown', function (e) {
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        var t = e.target.tagName;
        if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT' || t === 'A') return;
        if (e.target.closest('.nb-tabs')) return;
        if (e.key === 'ArrowRight') show(at + 1);
        else if (e.key === 'ArrowLeft') show(at - 1);
      });
    }

    show(0, false, false);
  });
})();
