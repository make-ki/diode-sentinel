// All visible copy and measured values are centralized and traced in CLAIMS-TRACE.md.
export const film = {
  fps: 30, width: 1920, height: 1080, duration: 1800,
  brand: 'Diode Sentinel',
  hook: ['No replies.', 'No handshakes.', 'No decryption.'],
  direction: 'One direction only.',
  positioning: ['PS-26145 · NTRO', 'Inside a room', 'with no door.'],
  diagram: {source:'Gateway link', diode:'Hardware data diode', sensor:'Monitoring enclave', return:'No path back'},
  contract: {eyebrow:'The one-way observability contract', headline:['Five requested features.', 'Impossible by the first constraint.'], rows:['JA3S / JA4S','Negotiated cipher / server certificate','Round-trip time','NXDOMAIN ratio','Outbound-to-inbound byte ratio'], total:'21 feature rows', qualifiers:'5 impossible rows cover 6 named features', stats:[{label:'Observable',value:15},{label:'Impossible',value:5},{label:'Substituted',value:1}], gate:['Response-side field: rcode','CI gate fails the build']},
  substitution: {eyebrow:'Substitution, done honestly', headline:['The closest', 'observable signal.'], rows:[{label:'Out / in byte ratio',signal:'Bytes to a first-seen destination',detail:"Compared with the host’s own median baseline"},{label:'JA3S',signal:'JA4 from the ClientHello',detail:'QUIC Initial keys are public by design'}], footer:'The arithmetic belongs on the alert.'},
  clock:{eyebrow:'Streaming with bounded latency',headline:['The clock closes', 'the windows.'], labels:['Traffic falls silent','Monotonic clock','Scored window'], qualifier:'Bounded by design: ≤ 2 s flow-idle + ≤ 10 s window'},
  cnn:{eyebrow:'A numpy-only character CNN',headline:['Hand-written.', 'Gradient-checked.'],stats:[{label:'Parameters',value:4930,prefix:'~'},{label:'Analytic / finite-difference match',text:'7e-09'}],qualifier:'Gradient-test threshold: < 1e-4'},
  replay:{eyebrow:'Replay reproducibility',headline:['Byte-identical', 'alerts.'],stats:[{label:'Rules-only',value:46},{label:'With --ml',value:68}],qualifier:'Replayed capture vs committed .regression/ fixtures'},
  models:{eyebrow:'models-567 evaluation',headline:['Four that work.', 'Two honest failures.'],rows:[{name:'4 working models',signal:'Recall 1.000 · 0 benign FP',detail:'models-567 evaluation'},{name:'2 IsolationForests',signal:'0.000',detail:'Documented negative result · triage corroboration'}]},
  honesty:{eyebrow:'Measured on CTU IoT-23 · no retuning',headline:['Show the misses.'], rows:[{name:'Hakai',result:'Recall 1.000',kind:'normal'},{name:'HideNSeek',result:'Recall 1.000',kind:'normal'},{name:'Trojan',result:'Recall 0.000 · miss',kind:'critical'},{name:'Philips HUE',result:'Structural false positive',kind:'amber'}],qualifier:'Historical measurements. NOT currently repo-reproducible.',remedy:'Re-runnable once the dataset is re-mounted.'},
  messy:{eyebrow:'Our own FP-pressure variant',headline:['A false positive.', 'A stated remedy.'],badge:'Critical',signal:'Benign backup host',detail:'One critical false positive',remedy:'Operator-curated authorised-destination registry',outcome:'Demotes to medium. Does not suppress.'},
  closing:{line:'Exactly why. What we did instead.', attribution:'SIH 2026 · PS-26145 · NTRO'},
  production:{team:'TEAM NAMES NOT SUPPLIED',url:'PROJECT URL NOT SUPPLIED'},
} as const;
// Ordered narrative follows VIDEO-BRIEF §3, compressed to a 60-second cut.
export const cuts = [
  {id:'constraint',start:0,end:180}, {id:'positioning',start:180,end:300},
  {id:'contract',start:300,end:660}, {id:'substitution',start:660,end:840},
  {id:'clock',start:840,end:1020}, {id:'cnn',start:1020,end:1110},
  {id:'replay',start:1110,end:1200}, {id:'models',start:1200,end:1350},
  {id:'honesty',start:1350,end:1530}, {id:'messy',start:1530,end:1680},
  {id:'closing',start:1680,end:1800},
] as const;
