#!/usr/bin/env python3
"""
End-to-end runner: one-way feed -> flows -> features -> detectors -> fusion
-> standardized alerts.

Two ingest modes share ONE detection path (pipeline.StreamProcessor), so live
and replay cannot drift apart:

  offline (default)   read a pcap file. The stream clock advances with packet
                      timestamps, so output is deterministic and byte-identical
                      to the original prototype's.
  --live IFACE        capture from an interface through an AF_PACKET raw
                      socket (live_source.AfPacketSource). The stream clock
                      follows the wall clock, so a link that goes silent still
                      closes idle flows and completes windows on schedule.

Offline reading is backend-agnostic (dpkt preferred, scapy fallback for the
--parity assertion). Live dissection uses the same dpkt calls as the offline
dpkt backend, so the two share one parser.

Examples:
  python run.py                          # replay traffic.pcap
  python run.py --parity                 # dpkt vs scapy parity assertion
  python run.py --ml                     # replay + ML tier
  sudo python run.py --live eth0         # live capture
  sudo python run.py --live eth0 --sample 4 --duration 300
"""
import argparse
import json
import os
import sys
import time
from collections import Counter

import config
from config import (PCAP_PATH, ALERTS_PATH, DURATION, CAPTURE_BATCH,
                    CAPTURE_TIMEOUT, LINE_RATE_SAMPLE, STATE_PATH,
                    STATE_SAVE_EVERY)
from pipeline import StreamProcessor
from detectors import AlertSink
from pcap_reader import best_reader, iter_scapy, iter_dpkt
from live_source import (AfPacketSource, CaptureConfigError,
                         CapturePermissionError, PcapStreamSource,
                         list_interfaces)


# --------------------------------------------------------------------------
# driver (shared by offline replay and live capture)
# --------------------------------------------------------------------------

def _batched(it, n=CAPTURE_BATCH):
    """Adapt a packet iterator to the read_batch() callable the driver wants.

    Returns a partial final batch, then None once the iterator is exhausted
    (None means 'stop'; [] means 'nothing right now').
    """
    def read_batch():
        out = []
        for _ in range(n):
            try:
                out.append(next(it))
            except StopIteration:
                return out if out else None
        return out
    return read_batch


def run_stream(read_batch, sink, clock=None, ml_scorer=None,
               tls_state_path=None, live=False, processor=None,
               on_tick=None, idle_limit=None, dga_cnn=None, models567=None):
    """Drive a StreamProcessor over batches of packet tuples.

    clock:        callable -> stream-relative seconds. None means "use packet
                  timestamps", which reproduces the original single-loop
                  behaviour exactly (offline). Live passes a wall-clock reader
                  so idle gaps still advance the clock.
    on_tick:      callback(proc) after each batch, for checkpointing.
    idle_limit:   stop after N consecutive empty batches (harness use).
    """
    proc = processor or StreamProcessor(sink, ml_scorer,
                                        tls_state_path=tls_state_path,
                                        dga_cnn=dga_cnn,
                                        models567=models567)
    wall0 = time.perf_counter()
    idle = 0
    last_t = 0.0
    while True:
        batch = read_batch()
        if batch is None:
            break
        if not batch:
            if not live:
                break
            idle += 1
            if idle_limit is not None and idle >= idle_limit:
                break
            # idle: wall clock closes the window if we have one, otherwise
            # hold at the last packet's time (packet-time mode)
            proc.tick(clock() if clock is not None else last_t)
            if on_tick:
                on_tick(proc)
            continue
        idle = 0
        for pkt in batch:
            proc.feed(pkt)
            last_t = pkt[0]
            proc.tick(pkt[0] if clock is None else max(pkt[0], clock()))
        if on_tick:
            on_tick(proc)
    stats = proc.finish()
    stats["wall"] = time.perf_counter() - wall0
    return stats


def run_pipeline(packets, sink, ml_scorer=None, tls_state_path=None,
                 dga_cnn=None, models567=None):
    """Offline replay of a packet iterable (named entry point for parity).

    Passing tls_state_path opts into a warm replay: the stored JA4 inventory
    is loaded, so the baseline gate is skipped. Without it the run is cold and
    byte-identical to the original prototype.
    """
    proc = StreamProcessor(sink, ml_scorer, tls_state_path=tls_state_path,
                           dga_cnn=dga_cnn, models567=models567)
    if tls_state_path:
        proc.tls.load_state(tls_state_path)
    stats = run_stream(_batched(packets), sink, processor=proc)
    if tls_state_path:
        # symmetric with live: --state loads on entry and checkpoints on exit,
        # which makes "learn the baseline from a recorded window, then deploy
        # warm" a supported workflow instead of a manual file edit.
        proc.tls.save_state(tls_state_path)
    return stats


def run_live(iface, sink, ml_scorer=None, state_path=STATE_PATH,
             sample=LINE_RATE_SAMPLE, duration=None, source=None, clock=None,
             batch=CAPTURE_BATCH, idle_limit=None, verbose=True, on_tick=None,
             dga_cnn=None, models567=None):
    """Live capture driver.

    source and clock are injectable so the live code path can be exercised and
    parity-tested without CAP_NET_RAW -- see test_live.py.
    on_tick(proc) observes the pipeline after each batch (tests use it to prove
    an alert fired during the capture rather than only at finish).
    """
    if source is None:
        source = AfPacketSource(iface, sample=sample, batch=batch)
        source.open()

    anchor = source.anchor
    config.set_time_anchor(anchor)      # alerts now carry real wall-clock time

    # Which clock drives the stream: an injected one (tests), the source's own
    # (socket = wall clock; pcap stream = wall clock if live, else the stream's
    # own record timestamps so archive replay stays deterministic).
    if clock is not None:
        stream_clock = lambda: clock() - anchor
    else:
        stream_clock = (source.default_clock()
                        if hasattr(source, "default_clock")
                        else lambda: time.time() - anchor)
    # A None stream_clock means "advance with packet timestamps" (archive
    # replay): there is no wall clock to consult, and packet time cannot run
    # ahead of the packets being processed.

    state_path = state_path or None
    proc = StreamProcessor(sink, ml_scorer, tls_state_path=state_path,
                           dga_cnn=dga_cnn, models567=models567)
    warmed = proc.tls.load_state(state_path) if state_path else False
    if verbose:
        if warmed:
            print(f"warm start: {len(proc.tls.inv_global)} JA4 fingerprints "
                  f"restored from {state_path}")
        elif state_path:
            print(f"cold start: no inventory at {state_path} -- learning a "
                  f"baseline for the first {config.BASELINE_SECONDS:.0f}s")
        print(f"capturing on {iface} (sample 1-in-{sample}) -- Ctrl-C to stop")
        if hasattr(source, "is_live"):
            print("stream clock: " + ("record timestamps (archive replay)"
                                      if stream_clock is None
                                      else "wall clock (live feed)"))

    next_save = [STATE_SAVE_EVERY]

    def elapsed():
        """Stream seconds covered so far -- wall clock on a live feed, newest
        record timestamp in packet-time (archive) mode."""
        if stream_clock is not None:
            return stream_clock()
        return getattr(source, "_last_ts", anchor) - anchor

    def read_batch():
        if duration is not None and elapsed() >= duration:
            return None
        return source.drain(batch)

    def _tick(proc):
        if on_tick:
            on_tick(proc)
        if not state_path or proc.last_flush_t < next_save[0]:
            return
        next_save[0] = proc.last_flush_t + STATE_SAVE_EVERY
        proc.tls.save_state(state_path)
        _write_sidecar("live", _stats_view(proc, time.perf_counter() - t0[0]))

    t0 = [time.perf_counter()]
    interrupted = False
    try:
        stats = run_stream(read_batch, sink, clock=stream_clock,
                           live=True, processor=proc, on_tick=_tick,
                           idle_limit=idle_limit)
    except KeyboardInterrupt:
        interrupted = True
        stats = proc.finish()
        stats["wall"] = time.perf_counter() - t0[0]

    if state_path:
        proc.tls.save_state(state_path)
    _write_sidecar("live", stats)

    snap = source.snapshot() if hasattr(source, "snapshot") else {}
    close = getattr(source, "close", None)
    if close is not None:
        close()
    _print_live_report(sink, stats, snap, warmed, state_path, interrupted)
    return stats


def _stats_view(proc, wall):
    """Live view of counters partway through a capture (no finish())."""
    return dict(npkt=proc.npkt, flows=proc.assembler.closed_count,
                windows=proc.agg.flushed, ndns=proc.ndns, ntls=proc.ntls,
                by_class=Counter(a["threat_class"] for a in proc.sink.alerts),
                by_sev=Counter(a["severity"] for a in proc.sink.alerts),
                n_alerts=len(proc.sink.alerts),
                suppressed=proc.sink.suppressed, wall=max(wall, 1e-9))


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def _print_report(parser_name, s):
    print("=" * 64)
    print("ONE-WAY NIDS PROTOTYPE -- FEASIBILITY REPORT")
    print("=" * 64)
    print(f"parser backend             : {parser_name}")
    print(f"packets processed          : {s['npkt']:,}")
    print(f"flows closed               : {s['flows']:,}")
    print(f"windows flushed            : {s['windows']}")
    print(f"DNS queries inspected      : {s['ndns']:,}")
    print(f"TLS ClientHellos parsed    : {s['ntls']:,}")
    print(f"wall time                  : {s['wall']:.2f}s")
    print(f"processing rate            : {s['npkt'] / s['wall']:,.0f} pkt/s | "
          f"{s['flows'] / s['wall']:,.0f} flow/s")
    print(f"simulated traffic duration : {DURATION:.0f}s  ->  "
          f"{DURATION / s['wall']:.1f}x real-time")
    print(f"alerts emitted             : {s['n_alerts']} "
          f"(+{s['suppressed']} suppressed by allowlist)")
    print(f"by class                   : {dict(s['by_class'])}")
    print(f"by severity                : {dict(s['by_sev'])}")


def _print_live_report(sink, s, snap, warmed, state_path, interrupted):
    print()
    print("=" * 64)
    print("LIVE CAPTURE REPORT" + ("  (interrupted)" if interrupted else ""))
    print("=" * 64)
    print(f"interface                  : {snap.get('iface', 'injected source')}")
    if snap.get("eof"):
        print("feed                       : ended (writer closed the stream)")
    print(f"stream duration            : {s['wall']:.2f}s wall")
    print(f"frames received            : {snap.get('seen', 0):,}")
    print(f"frames analysed            : {snap.get('analysed', s['npkt']):,}")
    if snap.get("sampled_out"):
        print(f"skipped by sampler         : {snap['sampled_out']:,} "
              f"(1-in-{snap['sample']})")
    print(f"non-IPv4 frames            : {snap.get('non_ipv4', 0):,}"
          f"  (ARP/LLDP/IPv6 -- not parsed)")
    print(f"non-TCP/UDP IPv4 frames    : {snap.get('other_ip', 0):,}"
          f"  (ICMP/GRE/ESP -- no detector consumes these)")
    print(f"malformed frames           : {snap.get('malformed', 0):,}")
    print(f"kernel socket drops        : {snap.get('kernel_dropped', 0):,}")
    if snap.get("kernel_dropped"):
        print("                             ^ traffic LOST before analysis -- "
              "raise SO_RCVBUF or increase --sample")
    print(f"packets processed          : {s['npkt']:,}")
    print(f"flows closed               : {s['flows']:,}")
    print(f"windows flushed            : {s['windows']}")
    print(f"DNS queries inspected      : {s['ndns']:,}")
    print(f"TLS ClientHellos parsed    : {s['ntls']:,}")
    print(f"alerts emitted             : {s['n_alerts']} "
          f"(+{s['suppressed']} suppressed by allowlist)")
    print(f"by class                   : {dict(s['by_class'])}")
    print(f"by severity                : {dict(s['by_sev'])}")
    if state_path:
        print(f"inventory state            : {state_path} "
              f"(warm start: {'yes' if warmed else 'no'})")


def _write_sidecar(parser_name, s):
    """Dashboard sidecar: the suppressed count is not in alerts.jsonl."""
    try:
        with open(os.path.join(os.path.dirname(ALERTS_PATH) or ".",
                               "run_stats.json"), "w") as fh:
            json.dump({"suppressed": s["suppressed"],
                       "parser": parser_name,
                       "pkt_per_s": round(s["npkt"] / s["wall"]),
                       "alerts": s["n_alerts"],
                       "mode": "live" if parser_name == "live" else "replay"},
                      fh)
    except OSError:
        pass


# --------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------

def load_scorer(sink, ml_model):
    """Build the Tier-2 scorer, degrading to rules-only if unavailable."""
    if not ml_model:
        return None
    from ml_tier import MLScorer
    try:
        return MLScorer.from_file(sink, ml_model)
    except FileNotFoundError:
        print(f"[warn] ML model '{ml_model}' not found -- run train_ml.py "
              f"first; continuing rules-only")
    except Exception as e:
        print(f"[warn] ML model '{ml_model}' could not be loaded "
              f"({type(e).__name__}: {e}); continuing rules-only")
    return None


def load_dga_cnn(model_path):
    """Build the Tier-2 DGA character CNN, degrading to rules-only if absent."""
    if not model_path:
        return None
    from dga_cnn import DgaCnnScorer
    try:
        return DgaCnnScorer.from_file(model_path)
    except FileNotFoundError:
        print(f"[warn] DGA CNN model '{model_path}' not found -- run "
              f"train_dga_cnn.py first; continuing rules-only")
    except Exception as e:
        print(f"[warn] DGA CNN model '{model_path}' could not be loaded "
              f"({type(e).__name__}: {e}); continuing rules-only")
    return None


def load_models567(manifest_path):
    """Load category 5-7 models from a JSON manifest, or stay disabled."""
    if not manifest_path:
        return None
    from models_567 import Models567
    try:
        with open(manifest_path) as fh:
            manifest = json.load(fh)
        return Models567(manifest["models"])
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"[warn] category 5-7 manifest '{manifest_path}' could not be "
              f"loaded ({type(exc).__name__}: {exc}); continuing rules-only")
    except Exception as exc:
        print(f"[warn] category 5-7 models unavailable ({type(exc).__name__}: "
              f"{exc}); continuing rules-only")
    return None


def main(pcap_path=PCAP_PATH, parity=False, ml_model=None, live=None,
         pipe=None, state_path=None, sample=LINE_RATE_SAMPLE, duration=None,
         no_state=False, dga_model=None, models567_manifest=None):
    dga_cnn = load_dga_cnn(dga_model)
    models567 = load_models567(models567_manifest)
    if live or pipe:
        sink = AlertSink(truncate=False)       # live: append, dashboard tails
        scorer = load_scorer(sink, ml_model)
        target = pipe or live
        try:
            source = PcapStreamSource(pipe, sample=sample,
                                      timeout=CAPTURE_TIMEOUT).open() \
                if pipe else None
            run_live(target, sink, ml_scorer=scorer, source=source,
                     state_path=None if no_state else (state_path or STATE_PATH),
                     sample=sample, duration=duration, dga_cnn=dga_cnn,
                     models567=models567)
        except (CaptureConfigError, CapturePermissionError) as e:
            print(f"[error] {e}", file=sys.stderr)
            return 2
        return 0

    backends = [("dpkt", iter_dpkt), ("scapy", iter_scapy)] if parity \
        else [best_reader()]
    reports = {}
    for name, reader in backends:
        sink = AlertSink()
        scorer = load_scorer(sink, ml_model)
        try:
            reports[name] = run_pipeline(reader(pcap_path), sink, scorer,
                                         tls_state_path=state_path,
                                         dga_cnn=dga_cnn,
                                         models567=models567)
        except ImportError:
            print(f"[skip] {name} not installed")
            continue
        _print_report(name, reports[name])
        print(f"full alert log: {ALERTS_PATH}")
        _write_sidecar(name, reports[name])
    if len(reports) == 2:
        a, b = reports["dpkt"]["by_class"], reports["scapy"]["by_class"]
        print("-" * 64)
        print("PARITY CHECK:", "IDENTICAL" if a == b else f"DIVERGED\n {a}\n {b}")
        if a != b:
            raise SystemExit(1)
    return 0


def _cli(argv=None):
    p = argparse.ArgumentParser(
        description="One-way NIDS prototype (offline replay or live capture)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pcap", nargs="?", default=PCAP_PATH,
                   help="pcap file to replay (default: traffic.pcap)")
    p.add_argument("--live", metavar="IFACE",
                   help="capture live from this interface (needs CAP_NET_RAW)")
    p.add_argument("--pipe", metavar="PATH",
                   help="read a pcap stream from a FIFO (or growing file) that "
                        "a capture tool is writing -- needs no privileges")
    p.add_argument("--list-interfaces", action="store_true",
                   help="print the interface names available to capture and exit")
    p.add_argument("--state", metavar="PATH",
                   help=f"JA4 inventory checkpoint file (default live: "
                        f"{os.path.basename(STATE_PATH)})")
    p.add_argument("--no-state", action="store_true",
                   help="disable inventory persistence (cold start every run)")
    p.add_argument("--sample", type=int, default=LINE_RATE_SAMPLE, metavar="N",
                   help="analyse 1 packet in N on live capture (default: 1)")
    p.add_argument("--duration", type=float, metavar="SECS",
                   help="stop live capture after SECS of stream time")
    p.add_argument("--parity", action="store_true",
                   help="assert dpkt and scapy readers agree (offline only)")
    p.add_argument("--ml", action="store_true",
                   help="enable the Tier-2 LightGBM flow scorer")
    p.add_argument("--dga-cnn", action="store_true", dest="dga_cnn",
                   help="enable the Tier-2 DGA character CNN confirmer "
                        "(needs model_dga_cnn.npz from train_dga_cnn.py)")
    p.add_argument("--models-567", metavar="MANIFEST",
                   help="enable category 5-7 XGBoost/forest/CNN models from "
                        "a JSON manifest")
    return p


def _run_cli(argv=None):
    args = _cli(argv).parse_args(argv)
    if args.list_interfaces:
        names = list_interfaces()
        print("\n".join(names) if names else "(no interfaces found)")
        return 0
    if args.sample < 1:
        print("[error] --sample must be >= 1", file=sys.stderr)
        return 2
    if args.live and args.pipe:
        print("[error] --live and --pipe are mutually exclusive",
              file=sys.stderr)
        return 2
    return main(args.pcap, parity=args.parity,
                ml_model="model_ml.txt" if args.ml else None,
                live=args.live, pipe=args.pipe, state_path=args.state,
                sample=args.sample, duration=args.duration,
                no_state=args.no_state,
                dga_model="model_dga_cnn.npz" if args.dga_cnn else None,
                models567_manifest=args.models_567)


if __name__ == "__main__":
    raise SystemExit(_run_cli())
