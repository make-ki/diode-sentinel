/* ==========================================================================
   One-Way NIDS — dashboard client

   Polls /api/alerts and renders the KPI row, the two charts, the filterable
   alert stream, the side panels and the evidence modal. One file, no build
   step: the same stdlib server that tails alerts.jsonl serves it.
   ========================================================================== */
'use strict';

const POLL_MS = 2000;
const SEVERITIES = ['critical', 'high', 'medium', 'low'];

/* Class -> colour and label. Colours are grouped by PS class so related
   detections read as one family in the mix chart. */
const CLASS_COLOR = {
  ddos_volumetric_spoofed: '#ff4d6d',
  ddos_syn_flood:          '#ff8095',
  c2_beaconing:            '#ffab4a',
  dga_domain:              '#ffd166',
  tls_known_malware:       '#4ac7ff',
  tls_novel_fingerprint:   '#8fd8ff',
  recon_vertical_scan:     '#8b7dfb',
  recon_horizontal_scan:   '#b0a6ff',
  data_exfiltration:       '#57d9a3',
  confirmed_exfiltration:  '#c084fc',
  confirmed_c2_implant:    '#d6aaff',
  botnet_c2_with_dga:      '#e8c6ff',
  multi_signal_fusion:     '#b39ddb',
  ml_flow_suspicious:      '#2dd4bf',
};

const CLASS_LABEL = {
  ddos_volumetric_spoofed: 'DDoS volumetric (spoofed)',
  ddos_syn_flood:          'DDoS SYN flood',
  c2_beaconing:            'C2 beaconing',
  dga_domain:              'DGA / DNS tunnelling',
  tls_known_malware:       'TLS/QUIC known malware',
  tls_novel_fingerprint:   'TLS/QUIC novel fingerprint',
  recon_vertical_scan:     'Recon vertical scan',
  recon_horizontal_scan:   'Recon horizontal scan',
  data_exfiltration:       'Data exfiltration',
  confirmed_exfiltration:  'FUSED · confirmed exfiltration',
  confirmed_c2_implant:    'FUSED · confirmed C2 implant',
  botnet_c2_with_dga:      'FUSED · botnet C2 with DGA',
  multi_signal_fusion:     'FUSED · multi-signal',
  ml_flow_suspicious:      'ML tier · suspicious flow',
};

const CLASS_PS = {
  ddos_volumetric_spoofed: 'a', ddos_syn_flood: 'a',
  c2_beaconing: 'b',
  dga_domain: 'c',
  tls_known_malware: 'd', tls_novel_fingerprint: 'd',
  recon_vertical_scan: 'e', recon_horizontal_scan: 'e',
  data_exfiltration: 'f',
};

const FUSED_CLASSES = new Set(['confirmed_exfiltration', 'confirmed_c2_implant',
                               'botnet_c2_with_dga', 'multi_signal_fusion']);

const state = {
  severity: new Set(),
  cls: new Set(),
  q: '',
  limit: 400,
  paused: false,
  firstLoad: true,
  seen: new Set(),
  live: 'connecting',
};

let timelineChart = null;
let mixChart = null;

/* ------------------------------------------------------------- helpers --- */

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value === undefined || value === null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function cssVar(name, fallback) {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name).trim();
  return value || fallback;
}

const sevColor = (sev) => cssVar('--sev-' + sev, '#8fa3c8');
const classColor = (cls) => CLASS_COLOR[cls] || '#8fa3c8';
const classLabel = (cls) => CLASS_LABEL[cls] || String(cls).replace(/_/g, ' ');

function fmtInt(n) {
  return Number(n || 0).toLocaleString('en-US');
}

function fmtClock(iso) {
  if (!iso) return '--';
  const m = String(iso).match(/T(\d{2}:\d{2}:\d{2})/);
  return m ? m[1] : String(iso);
}

function fmtSpan(seconds) {
  const s = Math.round(seconds || 0);
  if (s < 60) return s + 's';
  const m = Math.floor(s / 60);
  return m + 'm ' + String(s % 60).padStart(2, '0') + 's';
}

function fmtBucket(size) {
  if (size >= 3600) return (size / 3600) + 'h';
  if (size >= 60) return (size / 60) + 'm';
  return size + 's';
}

/* --------------------------------------------------------------- charts --- */

function chartTheme() {
  const grid = cssVar('--line', 'rgba(120,150,200,.16)');
  const text = cssVar('--muted', '#7d8db0');
  return {
    grid,
    text,
    tooltip: {
      backgroundColor: cssVar('--panel-solid', '#0f172a'),
      borderColor: cssVar('--line-strong', 'rgba(120,150,200,.28)'),
      borderWidth: 1,
      titleColor: cssVar('--text', '#dbe4f0'),
      bodyColor: cssVar('--text', '#dbe4f0'),
      padding: 10,
      cornerRadius: 8,
      displayColors: true,
      boxWidth: 8,
      boxHeight: 8,
      usePointStyle: true,
    },
  };
}

function initCharts() {
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
  Chart.defaults.font.size = 10.5;

  timelineChart = new Chart($('timeline-chart'), {
    type: 'bar',
    data: { labels: [], datasets: SEVERITIES.map((sev) => ({
      label: sev,
      data: [],
      backgroundColor: sevColor(sev),
      borderRadius: 3,
      borderSkipped: false,
      maxBarThickness: 22,
    })) },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 320 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 9, boxHeight: 9, usePointStyle: true,
                    pointStyle: 'circle', padding: 14, color: cssVar('--muted') },
        },
        tooltip: chartTheme().tooltip,
      },
      scales: {
        x: { stacked: true, grid: { display: false },
             ticks: { color: cssVar('--dim'), maxRotation: 0, autoSkipPadding: 18 },
             border: { color: cssVar('--line') } },
        y: { stacked: true, beginAtZero: true,
             grid: { color: cssVar('--line'), drawTicks: false },
             ticks: { color: cssVar('--dim'), precision: 0, padding: 6 },
             border: { display: false } },
      },
    },
  });

  mixChart = new Chart($('mix-chart'), {
    type: 'doughnut',
    data: { labels: [], datasets: [{
      data: [], backgroundColor: [], borderWidth: 0, hoverOffset: 6,
    }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      animation: { duration: 320 },
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 9, boxHeight: 9, usePointStyle: true,
                    pointStyle: 'circle', padding: 9, color: cssVar('--muted'),
                    font: { size: 10.5 } },
        },
        tooltip: chartTheme().tooltip,
      },
    },
  });
}

function restyleCharts() {
  const theme = chartTheme();
  [timelineChart, mixChart].forEach((c) => { if (c) c.options.plugins.tooltip = theme.tooltip; });
  if (timelineChart) {
    timelineChart.data.datasets.forEach((ds, i) => { ds.backgroundColor = sevColor(SEVERITIES[i]); });
    timelineChart.options.plugins.legend.labels.color = theme.text;
    timelineChart.options.scales.x.ticks.color = cssVar('--dim');
    timelineChart.options.scales.x.border.color = theme.grid;
    timelineChart.options.scales.y.grid.color = theme.grid;
    timelineChart.options.scales.y.ticks.color = cssVar('--dim');
    timelineChart.update('none');
  }
  if (mixChart) {
    mixChart.options.plugins.legend.labels.color = theme.text;
    mixChart.update('none');
  }
}

/* ------------------------------------------------------------- renderers --- */

function sensorItem(label, value, cls) {
  return '<span class="sensor-item"><span>' + esc(label) + '</span>' +
         '<span class="' + (cls || '') + '">' + esc(value) + '</span></span>';
}

function renderSensor(stats) {
  const s = stats.sensor || {};
  const items = [
    sensorItem('mode', s.mode || 'unknown',
               s.mode === 'live' ? 'ok' : ''),
    sensorItem('parser', s.parser || 'n/a'),
    sensorItem('throughput', s.pkt_per_s ? fmtInt(s.pkt_per_s) + ' pkt/s' : '—'),
    sensorItem('hosts', fmtInt(stats.hosts)),
    sensorItem('span', fmtSpan(stats.span_seconds)),
    sensorItem('last alert', fmtClock(stats.last_alert)),
    sensorItem('allowlist', fmtInt(stats.suppressed) + ' suppressed', 'ok'),
  ];
  $('sensor-strip').innerHTML = items.join('');
}

function kpiCard(label, value, color, ratio, sub) {
  const pct = Math.max(0, Math.min(1, ratio || 0)) * 100;
  return '<article class="kpi" style="--kpi-color:' + color + '">' +
    '<div class="kpi-label">' + esc(label) + '</div>' +
    '<div class="kpi-value">' + value + '</div>' +
    '<div class="kpi-sub">' + esc(sub) + '</div>' +
    '<div class="kpi-bar"><i style="width:' + pct.toFixed(1) + '%"></i></div>' +
    '</article>';
}

function renderKpis(stats) {
  const total = stats.total || 0;
  const covered = (stats.coverage || []).filter((c) => c.count > 0).length;
  const psTotal = (stats.coverage || []).length || 6;
  const share = (n) => (total ? n / total : 0);
  $('kpis').innerHTML = [
    kpiCard('Alerts', fmtInt(total), cssVar('--accent', '#6ea8fe'), 1,
            total ? 'since ' + fmtClock(stats.first_alert) : 'no alerts yet'),
    kpiCard('Critical', fmtInt(stats.critical), sevColor('critical'),
            share(stats.critical), 'confidence ≥ 0.90'),
    kpiCard('High', fmtInt(stats.high), sevColor('high'),
            share(stats.high), 'confidence 0.70 – 0.89'),
    kpiCard('Medium', fmtInt(stats.medium), sevColor('medium'),
            share(stats.medium), 'confidence 0.50 – 0.69'),
    kpiCard('PS coverage', covered + ' / ' + psTotal, cssVar('--fused', '#c084fc'),
            psTotal ? covered / psTotal : 0, 'threat classes with a detection'),
    kpiCard('Allowlisted', fmtInt(stats.suppressed), sevColor('low'),
            total ? Math.min(1, stats.suppressed / (total + stats.suppressed)) : 0,
            'Tier-0 suppressed events'),
  ].join('');
}

function renderTimeline(timeline) {
  if (!timelineChart) return;
  timelineChart.data.labels = timeline.labels || [];
  SEVERITIES.forEach((sev, i) => {
    timelineChart.data.datasets[i].data = (timeline.series || {})[sev] || [];
  });
  timelineChart.update();
  $('timeline-hint').textContent = timeline.count
    ? '' + timeline.count + ' matched alerts · ' + fmtBucket(timeline.bucket_seconds) + ' buckets'
    : 'severity per time bucket';
}

function renderMix(stats) {
  if (!mixChart) return;
  const byClass = stats.by_class || {};
  const entries = Object.entries(byClass).sort((a, b) => b[1] - a[1]);
  mixChart.data.labels = entries.map(([cls]) => classLabel(cls));
  mixChart.data.datasets[0].data = entries.map(([, n]) => n);
  mixChart.data.datasets[0].backgroundColor = entries.map(([cls]) => classColor(cls));
  mixChart.update();
  $('mix-hint').textContent = entries.length
    ? entries.length + ' classes · ' + stats.total + ' alerts'
    : 'by threat class';
}

function confCell(a) {
  const conf = Number(a.confidence || 0);
  const color = sevColor(a.severity);
  return '<span class="conf" style="color:' + color + '">' +
    '<span class="conf-track"><i style="width:' + (conf * 100).toFixed(0) + '%"></i></span>' +
    conf.toFixed(2) + '</span>';
}

function classCell(cls) {
  const tag = FUSED_CLASSES.has(cls) ? '<span class="tag">FUSED</span>'
            : cls === 'ml_flow_suspicious' ? '<span class="tag ml">ML</span>' : '';
  const ps = CLASS_PS[cls] ? ' <span class="mono" style="color:var(--dim)">(' + CLASS_PS[cls] + ')</span>' : '';
  return esc(classLabel(cls)) + ps + tag;
}

function renderTable(data) {
  const rows = (data.alerts || []).slice().reverse();   // newest first
  const body = $('alert-rows');
  $('stream-hint').textContent = state.paused
    ? 'paused — feed is still appending'
    : data.matched + ' matched of ' + data.stats.total + ' alerts';

  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="6"><div class="empty">No alerts match the ' +
      'current filters.</div></td></tr>';
    return;
  }

  body.innerHTML = rows.map((a) => {
    const key = a.timestamp + '|' + a.src + '|' + a.threat_class + '|' + a.confidence;
    const isNew = !state.firstLoad && !state.seen.has(key);
    state.seen.add(key);
    const evidence = a.evidence || {};
    const signal = evidence.why || evidence.note || '—';
    return '<tr class="sev-row-' + esc(a.severity) + (isNew ? ' is-new' : '') +
      '" data-key="' + esc(key) + '">' +
      '<td class="mono cell-time">' + esc(fmtClock(a.timestamp)) + '</td>' +
      '<td><span class="badge badge-sm sev-' + esc(a.severity) + '">' +
        esc(a.severity) + '</span></td>' +
      '<td>' + classCell(a.threat_class) + '</td>' +
      '<td class="mono cell-route">' + esc(a.src || '*') +
        '<span class="cell-arrow">→</span>' + esc(a.dst || '*') + '</td>' +
      '<td>' + confCell(a) + '</td>' +
      '<td class="cell-signal" title="' + esc(signal) + '">' + esc(signal) + '</td>' +
      '</tr>';
  }).join('');

  Array.prototype.forEach.call(body.querySelectorAll('tr[data-key]'), (tr) => {
    tr.addEventListener('click', () => {
      const alert = rows.find((a) =>
        (a.timestamp + '|' + a.src + '|' + a.threat_class + '|' + a.confidence) === tr.dataset.key);
      if (alert) openDetail(alert);
    });
  });
}

function renderSources(data) {
  const sources = data.sources || [];
  const box = $('top-sources');
  if (!sources.length) {
    box.innerHTML = '<div class="empty">No offending sources in view.</div>';
    return;
  }
  const max = Math.max.apply(null, sources.map((s) => s.n));
  box.innerHTML = sources.map((s, i) => {
    const color = sevColor(s.worst);
    const share = max ? (s.n / max) * 100 : 0;
    return '<div class="entity" style="--sev-color:' + color + '">' +
      '<div class="entity-rank">' + (i + 1) + '</div>' +
      '<div class="entity-body">' +
        '<div class="entity-ip">' + esc(s.src) + '</div>' +
        '<div class="entity-meta">' + esc(classLabel(s.dominant)) +
          ' · worst ' + esc(s.worst) + '</div>' +
      '</div>' +
      '<div class="entity-count">' + s.n + '</div>' +
      '<div class="entity-bar"><i style="width:' + share.toFixed(1) + '%"></i></div>' +
      '</div>';
  }).join('');
}

function renderCoverage(stats) {
  const coverage = stats.coverage || [];
  const hits = coverage.filter((c) => c.count > 0).length;
  $('coverage-hint').textContent = hits + ' / ' + coverage.length + ' classes fired';
  $('coverage').innerHTML = coverage.map((c) =>
    '<div class="cov-row' + (c.count ? ' hit' : '') + '">' +
      '<div class="cov-key">(' + esc(c.key) + ')</div>' +
      '<div class="cov-label">' + esc(c.label) + '</div>' +
      '<div class="cov-count">' + (c.count || '—') + '</div>' +
    '</div>').join('');
}

/* ---------------------------------------------------------------- modal --- */

function openDetail(a) {
  const evidence = a.evidence || {};
  const color = sevColor(a.severity);
  const sev = $('detail-sev');
  sev.className = 'badge sev-' + a.severity;
  sev.textContent = a.severity;
  $('detail-class').textContent = classLabel(a.threat_class);
  $('detail-why').textContent = evidence.why || evidence.note ||
    'No human-readable rationale attached to this alert.';

  const meta = [
    ['timestamp', a.timestamp],
    ['flow id', a.flow_id],
    ['source', a.src],
    ['destination', a.dst],
    ['confidence', Number(a.confidence || 0).toFixed(3)],
    ['severity', a.severity + '  (' + color + ')'],
  ];
  $('detail-meta').innerHTML = meta.map(([k, v]) =>
    '<div><dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd></div>').join('');

  const rest = Object.entries(evidence).filter(([k]) => k !== 'why');
  $('detail-evidence').textContent = rest.length
    ? JSON.stringify(Object.fromEntries(rest), null, 2)
    : '(no extra evidence fields)';

  const modal = $('detail-modal');
  if (typeof modal.showModal === 'function') modal.showModal();
  else modal.setAttribute('open', '');
}

/* --------------------------------------------------------------- filters --- */

/* Built once and then only updated in place: rebuilding the toolbar on every
   poll would blow away focus mid-typing in the search box. */
let filtersBuilt = false;
let classKey = null;

function severityChip(sev, count) {
  return '<button type="button" class="chip" data-sev="' + sev + '" ' +
    'aria-pressed="' + (state.severity.has(sev) ? 'true' : 'false') + '" ' +
    'style="--chip-color:' + sevColor(sev) + '">' +
    '<span class="chip-dot"></span>' + esc(sev) +
    '<span class="chip-count">' + count + '</span></button>';
}

function buildFilters() {
  if (filtersBuilt) return;
  $('filters').innerHTML =
    SEVERITIES.map((s) => severityChip(s, 0)).join('') +
    '<input class="search" id="search" type="search" placeholder="filter by src, dst, class or evidence…">' +
    '<select class="select" id="class-select"><option value="">all classes</option></select>' +
    '<select class="select" id="limit-select">' +
      [100, 400, 1000].map((n) => '<option value="' + n + '"' +
        (state.limit === n ? ' selected' : '') + '>last ' + n + '</option>').join('') +
    '</select>';

  Array.prototype.forEach.call($('filters').querySelectorAll('.chip'), (chip) => {
    chip.addEventListener('click', () => {
      const sev = chip.dataset.sev;
      if (state.severity.has(sev)) state.severity.delete(sev);
      else state.severity.add(sev);
      chip.setAttribute('aria-pressed', state.severity.has(sev) ? 'true' : 'false');
      poll();
    });
  });

  const search = $('search');
  let searchTimer = null;
  search.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.q = search.value; poll(); }, 250);
  });

  $('class-select').addEventListener('change', (e) => {
    state.cls = new Set(e.target.value ? [e.target.value] : []);
    poll();
  });
  $('limit-select').addEventListener('change', (e) => {
    state.limit = Number(e.target.value);
    poll();
  });

  filtersBuilt = true;
}

function updateFilters(stats) {
  const counts = stats.by_severity || {};
  SEVERITIES.forEach((sev) => {
    const el = $('filters').querySelector('.chip[data-sev="' + sev + '"] .chip-count');
    if (el) el.textContent = counts[sev] || 0;
  });
  const classes = Object.keys(stats.by_class || {});
  const key = classes.join(',');
  if (key === classKey) return;
  classKey = key;
  const select = $('class-select');
  select.innerHTML = '<option value="">all classes</option>' +
    classes.map((c) => '<option value="' + esc(c) + '"' +
      (state.cls.has(c) ? ' selected' : '') + '>' + esc(classLabel(c)) + '</option>').join('');
}

function renderStats(stats) {
  renderSensor(stats);
  renderKpis(stats);
  renderCoverage(stats);
}

/* ------------------------------------------------------------------ poll --- */

function query() {
  const params = new URLSearchParams();
  params.set('limit', state.limit);
  if (state.severity.size) params.set('severity', Array.from(state.severity).join(','));
  if (state.cls.size) params.set('cls', Array.from(state.cls).join(','));
  if (state.q) params.set('q', state.q);
  return params.toString();
}

async function poll() {
  try {
    const res = await fetch('/api/alerts?' + query(), { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    updateFilters(data.stats);
    renderStats(data.stats);
    renderTimeline(data.timeline);
    renderMix(data.stats);
    renderTable(data);
    renderSources(data);
    if (!state.paused) setLive('live');
    state.firstLoad = false;
  } catch (err) {
    setLive('down');
    $('stream-hint').textContent = 'feed unavailable: ' + err.message;
  }
}

function setLive(mode) {
  if (state.live === mode) return;
  state.live = mode;
  const pill = $('live-pill');
  pill.classList.toggle('paused', mode === 'paused');
  pill.classList.toggle('down', mode === 'down');
  $('live-label').textContent =
    mode === 'live' ? 'live · tailing alerts.jsonl'
  : mode === 'paused' ? 'paused'
  : 'feed unavailable';
}

function clockLabel() {
  const d = new Date();
  const offset = -d.getTimezoneOffset();          // minutes east of UTC
  const pad = (n) => String(n).padStart(2, '0');
  const zone = offset === 0 ? 'UTC'
    : 'UTC' + (offset < 0 ? '-' : '+') + pad(Math.floor(Math.abs(offset) / 60)) +
      ':' + pad(Math.abs(offset) % 60);
  return d.toTimeString().slice(0, 8) + ' ' + zone;
}

/* -------------------------------------------------------------- chrome --- */

function startClock() {
  const tick = () => { $('clock').textContent = clockLabel(); };
  tick();
  setInterval(tick, 1000);
}

function press(btn, fn) { btn.addEventListener('click', fn); }

function main() {
  initCharts();
  startClock();
  buildFilters();

  press($('pause-btn'), () => {
    state.paused = !state.paused;
    $('pause-btn').textContent = state.paused ? 'Resume' : 'Pause';
    setLive(state.paused ? 'paused' : 'live');
    if (!state.paused) poll();
  });

  press($('refresh-btn'), () => poll());

  press($('theme-btn'), () => {
    const root = document.documentElement;
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    $('theme-btn').textContent = next === 'dark' ? 'Light' : 'Dark';
    try { localStorage.setItem('nids-theme', next); } catch (e) { /* private mode */ }
    restyleCharts();
  });

  try {
    const saved = localStorage.getItem('nids-theme');
    if (saved === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      $('theme-btn').textContent = 'Dark';
    }
  } catch (e) { /* private mode */ }

  poll();
  setInterval(() => { if (!state.paused) poll(); }, POLL_MS);
  $('footer-version').textContent = 'dashboard poll ' + (POLL_MS / 1000) + 's';
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
