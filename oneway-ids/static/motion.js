/* ==========================================================================
   Diode Sentinel — motion bootstrap.

   app.js rebuilds the KPI row and other lists via innerHTML on every 2-second
   poll, so a pure-CSS entrance animation would replay on every refresh. This
   file is the smallest thing that prevents that: it keeps a `.motion-boot`
   marker on <body> for the first render only, which gates the entrance rules
   in animations.css to run exactly once. It also performs the one-time KPI
   count-up, which CSS cannot do for values the app writes as text.

   It is deliberately isolated from the application: it does not read or
   change app state, data, events, routing, or DOM structure. Its only DOM
   effects are (1) toggling one class on <body>, and (2) briefly rewriting the
   text of the existing .kpi-value nodes, restoring the app's exact string at
   the end. It bails out entirely if <html> carries .no-motion or if
   animations.css (id="motion-css") is not loaded.
   ========================================================================== */
(function () {
  'use strict';

  if (document.documentElement.classList.contains('no-motion')) return;
  if (!document.getElementById('motion-css')) return;
  if (!document.body) return;

  document.body.classList.add('motion-boot');

  var settled = false;
  function settle() {
    if (settled) return;
    settled = true;
    // Long enough for the slowest stagger (460ms delay + 400ms duration),
    // yet always well under the 2s poll, so the next refresh renders with the
    // marker already gone and no entrance can replay.
    window.setTimeout(function () {
      document.body.classList.remove('motion-boot');
    }, 1100);
  }

  function countUp(card) {
    var el = card.querySelector('.kpi-value');
    if (!el) return;
    var raw = el.textContent.trim();
    if (!/^[\d,]+$/.test(raw)) return;            // '—' or any non-numeric value
    var target = parseInt(raw.replace(/,/g, ''), 10);
    if (!isFinite(target) || target <= 0) return; // nothing to count
    var started = performance.now();
    var duration = 600;
    function frame(now) {
      var p = Math.min(1, (now - started) / duration);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString('en-US');
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = raw;                  // restore the app's string
    }
    requestAnimationFrame(frame);
  }

  var kpis = document.getElementById('kpis');
  if (!kpis) return;

  function firstRender() {
    Array.prototype.forEach.call(kpis.querySelectorAll('.kpi'), countUp);
    settle();
  }

  if (kpis.querySelector('.kpi')) {
    firstRender();                                // already rendered (unlikely)
  } else {
    var observer = new MutationObserver(function () {
      if (!kpis.querySelector('.kpi')) return;
      observer.disconnect();
      firstRender();
    });
    observer.observe(kpis, { childList: true });
  }

  // Safety net: if the backend never responds, still release the marker.
  window.setTimeout(settle, 3000);
})();
