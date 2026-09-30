// Product-demonstration revision approved by the user; source: VIDEO-BRIEF §9.
export const product = {
    brand: 'Diode Sentinel', team: 'samarags', fps: 30, width: 1920, height: 1080, duration: 1560,
    qualifier: 'Recorded software · Synthetic replay',
    intro: { line: 'Traffic. Turned into evidence.', eyebrow: 'Network intrusion detection' },
    live: { title: 'Watch the signal take shape.', label: 'Live packet analysis', callouts: ['Incoming packets', 'Observed signals', 'Alert queue'] },
    evidence: { title: 'Open the alert. See the evidence.', label: 'Evidence-backed alerts', callouts: ['Severity', 'Detector score', 'Observed measurements'] },
    sources: { title: 'Follow the source. Connect the signals.', label: 'Source attribution & correlation', callouts: ['Source filter', 'Related signals'], support: [{ name: 'LightGBM', role: 'Flow-level scoring' }, { name: 'Isolation Forest', role: 'Anomaly corroboration' }] },
    modelCards: [
        { id: 'dns', clip: 'dns', title: 'Patterns in domain names.', name: 'Character CNN', role: 'DGA analysis', features: ['Query strings', 'Character patterns'], note: 'Model role · rules remain enabled' },
        { id: 'encrypted', clip: 'encrypted', title: 'Signals inside encrypted sessions.', name: 'Sequence CNN + XGBoost', role: 'Encrypted-session analysis', features: ['Packet sizes & timing', 'TLS / QUIC metadata'], note: 'Model role · rules remain enabled' },
        { id: 'scan', clip: 'scan', title: 'Reveal scanning patterns.', name: 'Random Forest', role: 'Reconnaissance analysis', features: ['Destination fan-out', 'Port fan-out'], note: 'Model role · rules remain enabled' },
        { id: 'exfil', clip: 'exfil', title: 'Spot unusual transfers.', name: 'XGBoost', role: 'Exfiltration analysis', features: ['Transfer volume', 'Host baseline & novelty'], note: 'Model role · rules remain enabled' },
    ],
    passive: { title: 'Observe. Without a probe.', label: 'Passive one-way monitoring', source: 'Received packets', diode: 'Hardware data diode', sensor: 'Diode Sentinel' },
    closing: { line: 'Traffic. Turned into evidence.', by: 'Built by', event: 'SIH 2026 · PS-26145' },
} as const;
