/* ==========================================================================
   One-Way NIDS — dashboard client

   Polls /api/alerts and renders the KPI row, the two charts, the filterable
   alert stream, the side panels and the evidence modal. One file, no build
   step: the same stdlib server that tails alerts.jsonl serves it.
   ========================================================================== */
'use strict';

const POLL_MS = 2000;
const SEVERITIES = ['critical', 'high', 'medium', 'low'];

const CLASS_LABEL = {
  udp_burst_fanout:        'UDP burst across destinations',
  udp_target_burst:        'UDP burst at one destination',
  ddos_volumetric_spoofed: 'DDoS volumetric (spoofed)',
  ddos_syn_flood:          'DDoS SYN flood',
  c2_beaconing:            'C2 beaconing',
  dga_domain:              'DGA domain',
  dns_tunneling:          'DNS tunnelling',
  encrypted_session_malware: 'Encrypted-session anomaly',
  recon_model_scan:       'Reconnaissance model',
  data_exfiltration_model: 'Exfiltration model',
  tls_known_malware:       'TLS local indicator match',
  tls_novel_fingerprint:   'TLS/QUIC novel fingerprint',
  recon_vertical_scan:     'Recon vertical scan',
  recon_horizontal_scan:   'Recon horizontal scan',
  recon_rolling_vertical_scan: 'Rolling recon · one destination',
  recon_rolling_horizontal_scan: 'Rolling recon · many destinations',
  data_exfiltration:       'Data exfiltration',
  confirmed_exfiltration:  'Correlated transfer signals',
  confirmed_c2_implant:    'Correlated TLS and periodicity',
  botnet_c2_with_dga:      'Correlated periodicity and DNS',
  multi_signal_fusion:     'multi-signal',
  ml_flow_suspicious:      'Suspicious flow',
};

const FUSED_CLASSES = new Set(['confirmed_exfiltration', 'confirmed_c2_implant',
                               'botnet_c2_with_dga', 'multi_signal_fusion']);

const state = {
  severity: new Set(),
  cls: new Set(),
  q: '',
  source: '',
  kind: '',
  from: '',
  to: '',
  sort: 'newest',
  limit: 400,
  paused: false,
  firstLoad: true,
  seen: new Set(),
  live: 'connecting',
};

let timelineChart = null;
let mixChart = null;
let mixClasses = [];

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
      animation: false,
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
    type: 'bar',
    data: { labels: [], datasets: [{ data: [], backgroundColor: cssVar('--accent'),
      borderRadius: 2, maxBarThickness: 12 }] },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      onClick: (event, elements) => {
        if (!elements.length) return;
        const cls = mixClasses[elements[0].index];
        state.cls = new Set([cls]);
        $('class-select').value = cls;
        poll();
        $('alerts').scrollIntoView({ block: 'start' });
      },
      animation: false,
      plugins: { legend: { display: false }, tooltip: chartTheme().tooltip },
      scales: {
        x: { beginAtZero: true, grid: { color: cssVar('--line') },
             ticks: { color: cssVar('--dim'), precision: 0 }, border: { display: false } },
        y: { grid: { display: false }, ticks: { color: cssVar('--muted'), font: { size: 10 } },
             border: { display: false } },
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
    mixChart.data.datasets[0].backgroundColor = cssVar('--accent');
    mixChart.options.scales.x.grid.color = theme.grid;
    mixChart.options.scales.x.ticks.color = theme.text;
    mixChart.options.scales.y.ticks.color = theme.text;
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
  const h = s.health || {};
  const counts = h.counts || {};
  const count = (key) => counts[key] == null ? 'Unknown' : fmtInt(counts[key]);
  const state = h.status || 'unknown';
  const mode = {interface: 'Interface capture', pcap_stream: 'Packet stream', offline: 'Offline replay'}[h.mode];
  const states = {active: 'Active', idle: 'Idle · waiting for packets', completed: 'Completed',
    stopped: 'Stopped', failed: 'Failed', stale: 'Stale · heartbeat missing', unknown: 'Unknown', starting: 'Starting'};
  const items = [
    sensorItem('Sensor', states[state] || 'Unknown', ['stale', 'failed', 'stopped'].includes(state) ? 'warn' : ''),
    sensorItem('Mode', mode || h.mode || s.mode || 'Unknown'),
    sensorItem('Source', h.interface || h.path || 'Unknown'),
    sensorItem('Last packet received · UTC', h.last_packet_at ? fmtClock(h.last_packet_at) : 'Not observed'),
    sensorItem('Heartbeat', h.heartbeat_age_seconds == null ? 'Unknown' : h.heartbeat_age_seconds + 's ago'),
    sensorItem('Seen', count('seen')),
    sensorItem('Analyzed', count('analyzed')),
    sensorItem('Sampled out', count('sampled_out')),
    sensorItem('Malformed', count('malformed')),
    sensorItem('Kernel drops', count('kernel_drops'), counts.kernel_drops > 0 ? 'warn' : ''),
  ];
  if (h.error) items.push(sensorItem('Error', h.error, 'warn'));
  $('sensor-strip').innerHTML = items.join('');
  $('demo-notice').hidden = !stats.synthetic_demo;
  $('capture-range').textContent = stats.first_alert
    ? stats.first_alert.slice(0, 10) + ' · ' + fmtClock(stats.first_alert) + ' – ' + (stats.last_alert?.slice(0, 10) !== stats.first_alert.slice(0, 10)
      ? stats.last_alert?.slice(0, 10) + ' ' : '') + fmtClock(stats.last_alert)
    : 'No alerts recorded';
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
  const counts = stats.signals || {};
  const cards = [
    ['Rule signals', counts.rule_records, 'Deterministic detector records'],
    ['Critical rule signals', counts.critical_rule_records, 'Subset of rule signals'],
    ['Model signals', counts.model_records, 'Model-led alerts; not certainty'],
    ['Correlations', counts.correlation_records, 'Derived from other signals'],
    ['Sources with alerts', counts.source_count, 'Excludes unattributed records'],
    ['Authorised transfers', counts.authorised_records, 'Registry-matched alert records'],
  ];
  $('kpis').innerHTML = cards.map(([label, count, note]) =>
    kpiCard(label, count == null ? '—' : fmtInt(count), cssVar('--text'), 0, note)).join('');
  $('signal-scope').textContent = fmtInt(stats.total) + ' total records across the loaded feed' +
    (counts.unknown_records ? ' · ' + fmtInt(counts.unknown_records) + ' unclassified' : '') +
    '. Correlations reuse detector evidence; these counts are not unique incidents. Scores are not calibrated probabilities of compromise.';
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
  const entries = Object.entries(byClass).sort((a, b) => b[1] - a[1]).slice(0, 6);
  mixClasses = entries.map(([cls]) => cls);
  mixChart.data.labels = entries.map(([cls]) => classLabel(cls));
  mixChart.data.datasets[0].data = entries.map(([, n]) => n);
  mixChart.data.datasets[0].backgroundColor = cssVar('--accent');
  mixChart.update();
  $('mix-hint').textContent = entries.length
    ? 'All records · select a bar to filter'
    : 'by threat class';
}

function confCell(a) {
  if (a.confidence == null || !Number.isFinite(Number(a.confidence))) return '<span class="conf">—</span>';
  const conf = Number(a.confidence);
  return '<span class="conf">' +
    '<span class="conf-track"><i style="width:' + (conf * 100).toFixed(0) + '%"></i></span>' +
    conf.toFixed(2) + '</span>';
}

function classCell(cls, triage) {
  const kind = triage?.kind || (FUSED_CLASSES.has(cls) ? 'correlation' : 'unknown');
  return '<span class="detection-name">' + esc(triage?.label || classLabel(cls)) + '</span>' +
    '<span class="tag ' + (kind === 'model' ? 'ml' : '') + '">' + esc(kind) + '</span>';
}

function bodyKey() { return document.activeElement?.closest('#alert-rows tr')?.dataset.key; }

function renderTable(data) {
  const rows = (data.alerts || []).slice();
  if (state.sort !== 'severity') rows.sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)));
  $('queue-count').textContent = fmtInt(data.matched);
  const focusedKey = bodyKey();
  const body = $('alert-rows');
  $('stream-hint').textContent = state.paused
    ? 'Updates paused'
    : 'Showing ' + rows.length + ' of ' + data.matched + ' matched · ' + (state.sort === 'severity' ? 'severity first' : 'newest first');

  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="6"><div class="empty">No alerts match the ' +
      'current filters.</div></td></tr>';
    return;
  }

  body.innerHTML = rows.map((a, index) => {
    const key = a.timestamp + '|' + a.src + '|' + a.threat_class + '|' + a.confidence;
    const isNew = !state.firstLoad && !state.seen.has(key);
    state.seen.add(key);
    const evidence = a.evidence || {};
    const signal = a.triage?.summary || 'Measurements not recorded';
    return '<tr class="sev-row-' + esc(a.severity) + (isNew ? ' is-new' : '') +
      '" tabindex="0" data-index="' + index + '" aria-label="Inspect ' + esc(classLabel(a.threat_class)) + '" data-key="' + esc(key) + '">' +
      '<td class="mono cell-time">' + esc(fmtClock(a.timestamp)) + '</td>' +
      '<td><span class="badge badge-sm sev-' + esc(a.severity) + '">' +
        esc(a.severity) + '</span></td>' +
      '<td>' + classCell(a.threat_class, a.triage) + '</td>' +
      '<td class="mono cell-route">' + esc(a.src || '*') +
        '<span class="cell-arrow">→</span>' + esc(a.dst || '*') + '</td>' +
      '<td title="' + esc(a.triage?.score_label || 'Detector score') + ' · not a calibrated probability">' + confCell(a) + '</td>' +
      '<td class="cell-signal" title="' + esc(signal) + '">' + esc(signal) + '</td>' +
      '</tr>';
  }).join('');

  body.querySelectorAll('tr[data-key]').forEach((tr) => {
    const inspect = () => openDetail(rows[Number(tr.dataset.index)]);
    tr.addEventListener('click', inspect);
    tr.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); inspect(); }
    });
    if (focusedKey === tr.dataset.key) tr.focus({ preventScroll: true });
  });
  state.seen = new Set(rows.map(a => a.timestamp + '|' + a.src + '|' + a.threat_class + '|' + a.confidence));
}

function renderSources(data) {
  const sources = data.sources || [];
  const box = $('top-sources');
  if (!sources.length) {
    box.innerHTML = '<div class="empty">No sources match the current filters.</div>';
    return;
  }
  const max = Math.max.apply(null, sources.map((s) => s.n));
  box.innerHTML = sources.map((s, i) => {
    const color = sevColor(s.worst);
    const share = max ? (s.n / max) * 100 : 0;
    return '<button type="button" class="entity" data-source="' + esc(s.src) + '" aria-label="Filter alerts for ' + esc(s.src) + '" style="--sev-color:' + color + '">' +
      '<div class="entity-rank">' + (i + 1) + '</div>' +
      '<div class="entity-body">' +
        '<div class="entity-ip">' + esc(s.src === '*' ? 'Unattributed' : s.src) + '</div>' +
        '<div class="entity-meta">' + fmtInt(s.signals?.rule_records) + ' rule · ' +
          fmtInt(s.signals?.model_records) + ' model · ' + fmtInt(s.signals?.correlation_records) + ' correlated</div>' +
      '</div>' +
      '<div class="entity-count">' + s.n + '</div>' +
      '<div class="entity-bar"><i style="width:' + share.toFixed(1) + '%"></i></div>' +
      '</button>';
  }).join('');
  box.querySelectorAll('[data-source]').forEach(button => button.addEventListener('click', () => {
    state.source = button.dataset.source;
    updateSourceFilter();
    poll();
    $('alerts').scrollIntoView({ block: 'start' });
  }));
}

function updateSourceFilter() {
  $('source-filter').hidden = !state.source;
  $('source-filter-label').textContent = 'Source: ' + (state.source === '*' ? 'Unattributed' : state.source);
}

function displayValue(value) {
  if (value === true) return 'Yes';
  if (value === false) return 'No';
  if (Array.isArray(value)) return value.map(displayValue).join(', ');
  if (value && typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function renderCoverage(stats) {
  const coverage = stats.coverage || [];
  const hits = coverage.filter((c) => c.count > 0).length;
  $('coverage-hint').textContent = hits + ' / ' + coverage.length + ' with alerts';
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
  const triage = a.triage || {};
  const sev = $('detail-sev');
  sev.className = 'badge sev-' + a.severity;
  sev.textContent = a.severity;
  $('detail-class').textContent = triage.label || classLabel(a.threat_class);
  $('detail-why').textContent = triage.summary || 'Measurements not recorded';

  const meta = [
    ['timestamp', a.timestamp],
    ['Recorded flow key (not a session ID)', a.flow_id],
    ['Detector identifier', a.threat_class],
    ['Signal origin', triage.kind || 'Not classified'],
    ['source', a.src],
    ['destination', a.dst],
    [triage.score_label || 'Detector score', a.confidence == null ? 'Not recorded' : Number(a.confidence).toFixed(3)],
    ['severity', a.severity],
  ];
  $('detail-meta').innerHTML = meta.map(([k, v]) =>
    '<div><dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd></div>').join('');

  $('detail-facts').innerHTML = (triage.facts || []).map(fact =>
    '<div><dt>' + esc(fact.label) + '</dt><dd>' + esc(displayValue(fact.value)) + '</dd></div>').join('') ||
    '<div><dt>Evidence</dt><dd>No typed measurements recorded; inspect original evidence below.</dd></div>';
  $('detail-caveat').textContent = (triage.caveat || 'Interpretation context is not recorded.') +
    ' Detector scores are not calibrated probabilities of compromise.';
  $('detail-next-step').textContent = triage.next_step || 'Inspect the original record and detector documentation before assigning a verdict.';
  const related = triage.related || [];
  $('detail-related-section').hidden = !related.length;
  $('detail-related').innerHTML = related.map(signal =>
    '<div class="related-signal"><strong>' + esc(classLabel(signal.label)) + '</strong><span>' +
    (signal.age_seconds == null ? 'Age not recorded' : esc(signal.age_seconds) + ' s before correlation') +
    ' · ' + esc(signal.destination || 'Destination not attributed') +
    (signal.effective_score == null ? '' : ' · weighted score ' + esc(signal.effective_score)) +
    '</span></div>').join('');
  $('detail-evidence').textContent = JSON.stringify(evidence, null, 2);
  $('export-alert').dataset.record = triage.export_key || '';
  $('export-alert').disabled = !triage.export_key;
  $('export-status').textContent = triage.export_key
    ? 'One selected alert · active filters recorded'
    : 'Export key unavailable; refresh the queue';

  const modal = $('detail-modal');
  if (typeof modal.showModal === 'function') modal.showModal();
  else modal.setAttribute('open', '');
}

async function exportSelectedAlert() {
  const button = $('export-alert');
  const key = button.dataset.record;
  if (!key) return;
  button.disabled = true;
  $('export-status').textContent = 'Preparing evidence export…';
  try {
    const params = new URLSearchParams(query());
    params.set('record', key);
    const response = await fetch('/api/export?' + params.toString(), {cache: 'no-store'});
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.error || 'HTTP ' + response.status);
    }
    const blob = await response.blob();
    const disposition = response.headers.get('Content-Disposition') || '';
    const match = disposition.match(/filename="([^"]+)"/);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = match ? match[1] : 'diode-alert-evidence.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    $('export-status').textContent = 'Evidence bundle downloaded';
  } catch (error) {
    $('export-status').textContent = 'Export failed: ' + error.message;
  } finally {
    button.disabled = false;
  }
}

/* --------------------------------------------------------------- filters --- */

/* Built once and then only updated in place: rebuilding the toolbar on every
   poll would blow away focus mid-typing in the search box. */
let filtersBuilt = false;
let classKey = null;

function severityChip(sev, count) {
  return '<button type="button" class="chip" data-sev="' + sev + '" ' +
    'aria-pressed="' + (state.severity.has(sev) ? 'true' : 'false') + '" ' +
    'style="--chip-color:var(--sev-' + sev + ')">' +
    '<span class="chip-dot"></span>' + esc(sev) +
    '<span class="chip-count">' + count + '</span></button>';
}

function buildFilters() {
  if (filtersBuilt) return;
  $('filters').innerHTML =
    SEVERITIES.map((s) => severityChip(s, 0)).join('') +
    '<input class="search" id="search" type="search" aria-label="Search alerts" placeholder="Search IP address, detection or evidence…">' +
    '<select class="select" id="class-select" aria-label="Detection class"><option value="">All detections</option></select>' +
    '<select class="select" id="limit-select" aria-label="Maximum displayed alerts">' +
      [100, 400, 1000].map((n) => '<option value="' + n + '"' +
        (state.limit === n ? ' selected' : '') + '>Show up to ' + n + '</option>').join('') +
    '</select>' +
    '<select class="select" id="kind-select" aria-label="Signal origin"><option value="">All signal origins</option><option value="rule">Rule signals</option><option value="model">Model signals</option><option value="correlation">Correlations</option><option value="unknown">Unclassified</option></select>' +
    '<select class="select" id="sort-select" aria-label="Queue ordering"><option value="newest">Newest first</option><option value="severity">Severity first</option></select>';

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

  $('kind-select').addEventListener('change', event => { state.kind = event.target.value; poll(); });
  $('sort-select').addEventListener('change', event => { state.sort = event.target.value; poll(); });
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
  select.innerHTML = '<option value="">All detections</option>' +
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
  if (state.source) params.set('src', state.source);
  if (state.kind) params.set('kind', state.kind);
  if (state.from) params.set('from', state.from);
  if (state.to) params.set('to', state.to);
  params.set('sort', state.sort);
  return params.toString();
}

let latestRequest = 0;
let activeRequest = null;
async function poll() {
  const request = ++latestRequest;
  if (activeRequest) activeRequest.abort();
  activeRequest = new AbortController();
  try {
    const res = await fetch('/api/alerts?' + query(), { cache: 'no-store', signal: activeRequest.signal });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.error || 'HTTP ' + res.status);
    }
    const data = await res.json();
    if (request !== latestRequest) return;
    $('connection-notice').hidden = true;
    updateFilters(data.stats);
    renderStats(data.stats);
    renderTimeline(data.timeline);
    renderMix(data.stats);
    renderTable(data);
    renderSources(data);
    setLive(state.paused ? 'paused' : 'live');
    state.firstLoad = false;
  } catch (err) {
    if (err.name === 'AbortError' || request !== latestRequest) return;
    setLive('down');
    $('connection-notice').hidden = false;
    $('connection-notice').textContent = 'Unable to refresh: ' + err.message + '. Displayed data may be out of date.';
    $('stream-hint').textContent = 'Feed unavailable · last successful data retained';
  } finally {
    if (request === latestRequest) activeRequest = null;
  }
}

function setLive(mode) {
  if (state.live === mode) return;
  state.live = mode;
  const pill = $('live-pill');
  pill.classList.toggle('paused', mode === 'paused');
  pill.classList.toggle('down', mode === 'down');
  $('live-label').textContent =
    mode === 'live' ? 'Auto-refresh · 2s'
  : mode === 'paused' ? 'Updates paused'
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
  startClock();
  buildFilters();
  press($('export-alert'), exportSelectedAlert);
  $('clear-source').addEventListener('click', () => { state.source = ''; updateSourceFilter(); poll(); });
  const utc = value => value ? value + (value.length === 16 ? ':00Z' : 'Z') : '';
  ['from', 'to'].forEach(bound => $('time-' + bound).addEventListener('change', event => {
    state[bound] = utc(event.target.value); poll();
  }));
  $('clear-time').addEventListener('click', () => {
    $('time-from').value = $('time-to').value = state.from = state.to = ''; poll();
  });
  const updateNav = () => document.querySelectorAll('.nav-link').forEach(link => {
    const active = link.hash === (location.hash || '#overview');
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  window.addEventListener('hashchange', updateNav);
  updateNav();

  press($('pause-btn'), () => {
    state.paused = !state.paused;
    $('pause-btn').textContent = state.paused ? 'Resume updates' : 'Pause updates';
    if (state.paused) {
      ++latestRequest;
      if (activeRequest) activeRequest.abort();
      activeRequest = null;
      setLive('paused');
      $('stream-hint').textContent = 'Updates paused';
    } else poll();
  });

  press($('refresh-btn'), () => poll());

  press($('theme-btn'), () => {
    const root = document.documentElement;
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    $('theme-btn').textContent = next === 'dark' ? 'Light theme' : 'Dark theme';
    try { localStorage.setItem('nids-theme', next); } catch (e) { /* private mode */ }
    restyleCharts();
  });

  try {
    const saved = localStorage.getItem('nids-theme');
    if (saved === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      $('theme-btn').textContent = 'Dark theme';
    }
  } catch (e) { /* private mode */ }

  initCharts();
  poll();
  setInterval(() => { if (!state.paused && !activeRequest) poll(); }, POLL_MS);
  $('footer-version').textContent = 'All event times in UTC · Refresh interval ' + (POLL_MS / 1000) + 's';
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
