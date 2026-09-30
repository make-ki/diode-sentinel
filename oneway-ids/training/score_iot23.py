#!/usr/bin/env python3
"""Replay a local IoT-23 capture and score host-level alerts against Zeek labels.

Only packets matching the conn.log originator -> responder 5-tuple are fed to
the detector. This makes directionality explicit even when the supplied pcap
contains both sides of a connection. No data is downloaded or mounted.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict

# Direct invocation sets sys.path[0] to training/, not the repository root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detectors import AlertSink
from core.pcap_reader import best_reader
from core.pipeline import StreamProcessor


def read_conn_log(path):
    """Return directional conn tuples and per-host ground truth.

    IoT-23 Zeek conn logs commonly append ``label`` and ``detailed-label``.
    Rows without a recognized label still constrain packet direction, but do
    not create host ground truth. Any host with a malicious-labeled row is
    positive; hosts seen only in benign-labeled rows are negative.
    """
    fields = None
    separator = "\t"
    directions = set()
    labels = defaultdict(set)
    label_rows = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#separator"):
                encoded = line.split(None, 1)[1].strip()
                separator = bytes(encoded, "ascii").decode("unicode_escape")
                continue
            if line.startswith("#fields"):
                raw_fields = line[len("#fields"):].lstrip().rstrip("\n").split(separator)
                if raw_fields and re.fullmatch(r"label\s{2,}detailed-label", raw_fields[-1]):
                    raw_fields[-1:] = ["label", "detailed-label"]
                fields = raw_fields
                continue
            if line.startswith("#") or not line.strip():
                continue
            if fields is None:
                raise ValueError("conn.log is missing its #fields header")
            values = line.rstrip("\n").split(separator)
            # Some IoT-23 exports store the final two label columns in one
            # tab-delimited cell, separated by the Zeek multi-space suffix.
            if len(values) == len(fields) - 1 and fields[-2:] == ["label", "detailed-label"]:
                suffix = re.split(r"\s{2,}", values[-1], maxsplit=1)
                if len(suffix) == 2:
                    values[-1:] = suffix
            if len(values) != len(fields):
                continue
            row = dict(zip(fields, values))
            try:
                src, dst = row["id.orig_h"], row["id.resp_h"]
                sport, dport = int(row["id.orig_p"]), int(row["id.resp_p"])
                proto = row["proto"].lower()
            except (KeyError, ValueError):
                continue
            if proto not in {"tcp", "udp"}:
                continue
            directions.add((src, sport, dst, dport, proto))
            primary_label = row.get("label", "").strip().casefold()
            if primary_label in {"malicious", "attack", "infected"}:
                labels[src].add("malicious")
                label_rows += 1
            elif primary_label in {"benign", "normal", "clean"}:
                labels[src].add("benign")
                label_rows += 1
    if not directions:
        raise ValueError("conn.log contained no usable TCP/UDP connection tuples")
    if not label_rows:
        raise ValueError("conn.log contains no recognized primary labels; expected label values such as Benign or Malicious")
    return directions, labels


def one_way_packets(packet_iter, directions):
    """Yield packets with an unambiguous conn.log originator direction only."""
    for packet in packet_iter:
        _, src, dst, proto, sport, dport = packet[:6]
        forward = (src, sport, dst, dport, proto)
        reverse = (dst, dport, src, sport, proto)
        if forward in directions and reverse not in directions:
            yield packet


def require_packets(packet_count):
    if packet_count == 0:
        raise ValueError("no pcap packets matched the unambiguous conn.log originator tuples; verify capture and conn.log belong together")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def score_hosts(alerts, labels):
    """Compute host-level metrics, counting a host alert once regardless of volume."""
    truth = {host: "malicious" if "malicious" in kinds else "benign"
             for host, kinds in labels.items() if kinds}
    alerted = {a["src"] for a in alerts}
    positive = {h for h, label in truth.items() if label == "malicious"}
    negative = {h for h, label in truth.items() if label == "benign"}
    tp = positive & alerted
    fn = positive - alerted
    fp = negative & alerted
    tn = negative - alerted
    precision = len(tp) / (len(tp) + len(fp)) if tp or fp else 0.0
    recall = len(tp) / len(positive) if positive else 0.0
    return {
        "hosts": {h: {"label": truth[h], "alerted": h in alerted}
                  for h in sorted(truth)},
        "counts": {"tp": len(tp), "fp": len(fp), "fn": len(fn), "tn": len(tn),
                   "malicious_hosts": len(positive), "benign_hosts": len(negative),
                   "alerted_hosts": len(alerted)},
        "precision": precision,
        "recall": recall,
        "alert_classes": dict(sorted(Counter(a["threat_class"] for a in alerts).items())),
    }


def run(pcap_path, conn_path):
    directions, labels = read_conn_log(conn_path)
    reader_name, reader = best_reader()
    # AlertSink writes each alert; keep that output isolated and disposable.
    with tempfile.TemporaryDirectory(prefix="iot23-score-") as tempdir:
        sink = AlertSink(path=f"{tempdir}/alerts.jsonl")
        proc = StreamProcessor(sink)
        packet_count = 0
        for packet in one_way_packets(reader(pcap_path), directions):
            packet_count += 1
            proc.feed(packet)
            proc.tick(packet[0])
        require_packets(packet_count)
        stats = proc.finish()
        result = score_hosts(sink.alerts, labels)
    result["input"] = {"pcap": pcap_path, "conn_log": conn_path,
                       "pcap_sha256": sha256_file(pcap_path),
                       "conn_log_sha256": sha256_file(conn_path),
                       "reader": reader_name, "direction_filter": "conn.log originator -> responder",
                       "direction_tuples": len(directions), "packets_scored": packet_count,
                       "ambiguous_reverse_tuples_dropped": sum(
                           1 for item in directions
                           if (item[2], item[3], item[0], item[1], item[4]) in directions) // 2,
                       "pipeline_flows": stats["flows"], "pipeline_windows": stats["windows"],
                       "alert_count": stats["n_alerts"]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap", help="local pcap/pcapng readable by the configured packet reader")
    parser.add_argument("conn_log", help="local Zeek conn.log with label fields")
    parser.add_argument("-o", "--output", help="write JSON result here (stdout by default)")
    args = parser.parse_args()
    result = run(args.pcap, args.conn_log)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
