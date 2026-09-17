"""
Streaming pipeline primitives: flow assembly and time-window aggregation.

Both are one-way-native: they consume only (timestamp, src, dst, dport,
size, is_syn) tuples extracted from a single direction of traffic. No TCP
state assumptions, no response-side features.
"""
from collections import Counter, defaultdict

from config import WINDOW, IDLE_TIMEOUT, TICK_INTERVAL, TLS_PORTS
from detectors import (DDosDetector, ScanDetector, ExfilDetector,
                       BeaconDetector, DGADetector, TlsDetector, FusionEngine)
from tls_meta import TlsRecordReassembler, SeqTracker, parse_client_hello
from quic_meta import is_quic_initial, extract_quic_client_hello


class FlowAssembler:
    """Groups packets into flows by 5-tuple; closes flows after idle timeout.

    Closed flows are dicts with: key, t0, t1, npkt, nbytes, nsyn.
    """

    def __init__(self, idle_timeout=IDLE_TIMEOUT):
        self.timeout = idle_timeout
        self.active = {}
        self.closed_count = 0

    def feed(self, t, src, sport, dst, dport, proto, size, is_syn):
        key = (src, sport, dst, dport, proto)
        f = self.active.get(key)
        if f is None:
            self.active[key] = dict(key=key, t0=t, t1=t, npkt=1,
                                    nbytes=size, nsyn=int(is_syn),
                                    packet_sizes=[size], packet_times=[t],
                                    packet_directions=[1])
        else:
            f["npkt"] += 1
            f["nbytes"] += size
            f["t1"] = t
            f["nsyn"] += int(is_syn)
            if len(f["packet_sizes"]) < 128:
                f["packet_sizes"].append(size)
                f["packet_times"].append(t)
                f["packet_directions"].append(1)

    def emit_ready(self, t):
        """Yield flows idle for longer than the timeout."""
        out = []
        for key in list(self.active):
            f = self.active[key]
            if t - f["t1"] > self.timeout:
                out.append(f)
                del self.active[key]
        self.closed_count += len(out)
        return out

    def finish(self):
        out = list(self.active.values())
        self.closed_count += len(out)
        self.active.clear()
        return out


class WindowAggregator:
    """Fixed tumbling windows of traffic statistics.

    Per window tracks:
      npkt, nbytes, nsyn            -- volumetric counters
      srcs (Counter)                -- for source-IP entropy
      pairs {src: set((dst,dport))} -- for fan-out / scan detection
      src_bytes {src: bytes}        -- per-source volume (exfil baseline)
      novel_dsts / novel_bytes      -- destinations never seen before
    Calls each on_flush(window) callback when a window completes.
    """

    def __init__(self, window=WINDOW):
        self.window = window
        self.callbacks = []
        self.cur = None
        self.cur_idx = None
        self.seen_dsts = set()
        self.flushed = 0

    def register(self, fn):
        self.callbacks.append(fn)

    def _new_window(self, idx):
        return dict(idx=idx, t0=idx * self.window, t1=(idx + 1) * self.window,
                    npkt=0, nbytes=0, nsyn=0,
                    srcs=Counter(), pairs=defaultdict(set),
                    src_bytes=defaultdict(float),
                    pair_bytes=defaultdict(float),
                    novel_dsts=set(), novel_bytes=defaultdict(float))

    def feed(self, t, src, dst, dport, size, is_syn):
        idx = int(t // self.window)
        if self.cur is not None and idx > self.cur["idx"]:
            self._flush(self.cur)
            self.cur = None
        if self.cur is None:
            self.cur = self._new_window(idx)

        w = self.cur
        w["npkt"] += 1
        w["nbytes"] += size
        w["nsyn"] += int(is_syn)
        w["srcs"][src] += 1
        w["pairs"][src].add((dst, dport))
        w["src_bytes"][src] += size
        w["pair_bytes"][(src, dst)] += size
        if dst not in self.seen_dsts:
            self.seen_dsts.add(dst)
            w["novel_dsts"].add(dst)
        if dst in w["novel_dsts"]:
            w["novel_bytes"][src] += size

    def _flush(self, w):
        self.flushed += 1
        for fn in self.callbacks:
            fn(w)

    def flush_current(self):
        """Flush the trailing (incomplete) window -- call at end of capture."""
        if self.cur is not None:
            self._flush(self.cur)
            self.cur = None

    def tick(self, t):
        """Close the current window if the stream clock has moved past it.

        feed() alone suffices offline: packets keep arriving, so the window
        index advances by itself. A live link can go quiet, and without this
        a window that saw a flood followed by silence would never be scored
        (the flood verdict would sit unscored until the next packet arrived).
        Windows with no traffic are never created -- an empty window has zero
        counters and fires nothing.
        """
        if self.cur is not None and int(t // self.window) > self.cur["idx"]:
            self._flush(self.cur)
            self.cur = None


class StreamProcessor:
    """The single streaming pipeline, shared by offline replay and live
    capture so detection behaviour cannot drift between the two.

        feed(pkt)  one packet tuple (identical schema to pcap_reader)
        tick(t)    advance the stream clock: close idle flows, flush the ML
                   micro-batch, close completed windows
        finish()   drain everything and return the stats dict

    Offline drives tick() with packet time (so replay stays bit-identical to
    the original batch-free loop). Live drives it with max(packet time, wall
    clock) so a silent link still closes windows on schedule.
    """

    def __init__(self, sink, ml_scorer=None, tick_interval=TICK_INTERVAL,
                 tls_state_path=None, dga_cnn=None, models567=None):
        self.sink = sink
        self.ml_scorer = ml_scorer
        self.dga_cnn = dga_cnn
        self.models567 = models567
        self.tick_interval = tick_interval

        self.assembler = FlowAssembler()
        self.agg = WindowAggregator()

        self.ddos = DDosDetector(sink)
        self.scan = ScanDetector(sink)
        self.exfil = ExfilDetector(sink)
        self.beacon = BeaconDetector(sink)
        self.dga = DGADetector(sink, cnn=dga_cnn)
        self.tls = TlsDetector(sink, state_path=tls_state_path)
        self.fusion = FusionEngine(sink)
        sink.subscribe(self.fusion.on_alert)
        self.agg.register(self.ddos.on_window)
        self.agg.register(self.scan.on_window)
        self.agg.register(self.exfil.on_window)
        if self.models567:
            self.agg.register(self._score_model_window)

        self.npkt = self.ndns = self.ntls = 0
        self.last_flush_t = -1.0
        self.tls_states = {}
        self.quic_seen = set()

    def feed(self, pkt):
        """Process one packet tuple:
        (t, src, dst, proto, sport, dport, size, is_syn, payload, qname, seq)
        """
        (t, src, dst, proto, sport, dport, size, is_syn, payload, qname,
         seq) = pkt
        self.npkt += 1
        self.assembler.feed(t, src, sport, dst, dport, proto, size, is_syn)
        self.agg.feed(t, src, dst, dport, size, is_syn)

        if proto == "tcp":
            # ---- TLS metadata hook (one-way, ClientHello only) ----
            if dport in TLS_PORTS and payload and not is_syn:
                key = (src, sport, dst, dport)
                state = self.tls_states.get(key)
                if state is None:
                    state = self.tls_states[key] = {
                        "rt": TlsRecordReassembler(),
                        "seq": SeqTracker(),
                        "seen": False}
                st, seqt = state["rt"], state["seq"]
                if not st.dead and not state["seen"]:
                    verdict = seqt.update(seq, len(payload))
                    if verdict == "duplicate":
                        pass                       # retransmit: drop
                    elif verdict == "gap":
                        st.dead = True             # hole: do not guess
                    else:
                        for rec in st.feed(payload):
                            meta = parse_client_hello(rec)
                            if meta is not None:
                                state["seen"] = True
                                self.ntls += 1
                                self.assembler.active[key]["tls_meta"] = meta
                                self.tls.on_hello(t, src, dst, dport, meta)
                                break
        elif proto == "udp":
            if dport == 53 and qname:
                self.dga.on_dns(t, src, qname)
                self.ndns += 1
            # ---- QUIC Initial hook: JA4 from the QUIC crypto stream ----
            if dport in TLS_PORTS and payload and is_quic_initial(payload):
                qkey = (src, sport, dst, dport)
                if qkey not in self.quic_seen:
                    self.quic_seen.add(qkey)
                    qmeta = extract_quic_client_hello(payload)
                    if qmeta is not None:
                        self.ntls += 1
                        flow = self.assembler.active.get(
                            (src, sport, dst, dport, "udp"))
                        if flow is not None:
                            flow["tls_meta"] = qmeta
                        self.tls.on_hello(t, src, dst, dport, qmeta)

    def _score_model_flow(self, flow):
        if not self.models567:
            return
        for threat, confidence, evidence in self.models567.score_flow(flow):
            src, _, dst, dport, proto = flow["key"]
            self.sink.emit(flow["t1"], src, dst, dport, proto,
                           threat, confidence, evidence)

    def _score_model_window(self, window):
        if not self.models567:
            return
        for src in window["pairs"]:
            for threat, confidence, evidence in self.models567.score_scan(
                    window, src):
                self.sink.emit(window["t1"] - 1, src, "*", 0, "*",
                               threat, confidence, evidence)
        for (src, dst), total in window["pair_bytes"].items():
            for threat, confidence, evidence in self.models567.score_exfil(
                    window, src, dst, total):
                self.sink.emit(window["t1"] - 1, src, dst, 0, "*",
                               threat, confidence, evidence)

    def tick(self, t):
        if t - self.last_flush_t < self.tick_interval:
            return
        for f in self.assembler.emit_ready(t):
            self.beacon.on_flow(f)
            self._score_model_flow(f)
            if self.ml_scorer:
                self.ml_scorer.on_flow(f)
            k = f["key"]
            self.tls_states.pop((k[0], k[1], k[2], k[3]), None)
        if self.ml_scorer:
            self.ml_scorer.flush()
        self.agg.tick(t)
        self.last_flush_t = t

    def finish(self):
        for f in self.assembler.finish():
            self.beacon.on_flow(f)
            self._score_model_flow(f)
            if self.ml_scorer:
                self.ml_scorer.on_flow(f)
            k = f["key"]
            self.tls_states.pop((k[0], k[1], k[2], k[3]), None)
        if self.ml_scorer:
            self.ml_scorer.flush()
        self.agg.flush_current()
        return dict(npkt=self.npkt,
                    flows=self.assembler.closed_count,
                    windows=self.agg.flushed,
                    ndns=self.ndns,
                    ntls=self.ntls,
                    by_class=Counter(a["threat_class"]
                                     for a in self.sink.alerts),
                    by_sev=Counter(a["severity"]
                                   for a in self.sink.alerts),
                    n_alerts=len(self.sink.alerts),
                    suppressed=self.sink.suppressed)
