"""Cautious presentation helpers for the dashboard alert stream.

This module adapts recorded evidence only. It does not score, enrich, mutate,
or infer detector output.
"""
from collections import Counter


_FUSED = {
    "confirmed_exfiltration", "confirmed_c2_implant",
    "botnet_c2_with_dga", "multi_signal_fusion",
}
_MODELS = {"ml_flow_suspicious", "recon_model_scan", "data_exfiltration_model",
           "encrypted_session_malware"}
_LABELS = {
    "udp_burst_fanout": "UDP burst across destination endpoints",
    "udp_target_burst": "Many-source UDP burst at one endpoint",
    "c2_beaconing": "Periodic flow pattern",
    "data_exfiltration": "Large transfer to a new destination",
    "data_exfiltration_model": "Model-flagged transfer pattern",
    "tls_known_malware": "TLS fingerprint on local known list",
    "tls_novel_fingerprint": "New TLS fingerprint",
    "dga_domain": "Suspicious DNS label pattern",
    "dns_tunneling": "Repeated bulky or overlong DNS queries",
    "recon_vertical_scan": "Port scan against one destination",
    "recon_horizontal_scan": "Port scan across destinations",
    "recon_rolling_vertical_scan": "Rolling-window port scan against one destination",
    "recon_rolling_horizontal_scan": "Rolling-window scan across destinations",
    "recon_model_scan": "Model-flagged scan pattern",
    "ddos_syn_flood": "SYN-heavy traffic window",
    "ddos_volumetric_spoofed": "High-volume traffic with many sources",
    "encrypted_session_malware": "Encrypted-session model match",
    "ml_flow_suspicious": "Model-flagged flow pattern",
    "confirmed_exfiltration": "Correlated transfer signals",
    "confirmed_c2_implant": "Correlated TLS and periodicity signals",
    "botnet_c2_with_dga": "Correlated periodicity and DNS signals",
    "multi_signal_fusion": "Multiple correlated detector signals",
}

# Ordered serving vectors from core/models_567.py. Keep these presentation
# schemas beside the adapter: alerts store only positional values, so changing
# this order without changing the model evidence format would mislabel data.
# The schemas describe the exact vectors emitted by those model call sites.
_VECTOR_SCHEMAS = {
    "encrypted_xgb": (
        ("ClientHello cipher-suite count", "count"),
        ("ClientHello extension count", "count"),
        ("ClientHello offered TLS version", "code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown"),
        ("Transport code", "0 = TLS, 1 = QUIC"),
        ("SNI-present flag", "0/1"),
        ("Signature-algorithm count", "count"),
        ("Flow packet count", "packets"),
        ("Flow bytes", "bytes"),
        ("Flow duration", "seconds"),
        ("Packet-size coefficient of variation", "unitless"),
    ),
    "scan_rf": (
        ("Distinct destination/port pairs", "pairs"),
        ("Distinct destination IPs", "IPs"),
        ("Maximum ports on one destination", "ports"),
        ("Maximum per-destination share of pairs", "unitless ratio"),
        ("Source bytes in window", "bytes"),
    ),
    "exfil_xgb": (
        ("Pair bytes in current window", "bytes"),
        ("Source bytes in current window", "bytes"),
        ("Pair/source byte ratio", "unitless ratio"),
        ("Window index", "index"),
        ("Destination novel to stream", "0/1"),
    ),
}


def _model_vector_schema(threat, evidence):
    """Return the vector schema only when the recorded model identifies it."""
    model = evidence.get("model")
    if threat == "encrypted_session_malware" and "metadata_features" in evidence:
        return "encrypted_xgb", _VECTOR_SCHEMAS["encrypted_xgb"]
    if model in _VECTOR_SCHEMAS:
        return model, _VECTOR_SCHEMAS[model]
    return None, None


def _named_vector_facts(vector, schema):
    """Name positional values only for a full, known vector of exact length."""
    if not isinstance(vector, (list, tuple)):
        return None
    # Some serializers may preserve a one-row matrix. Flatten only that known
    # wrapper; never guess at arbitrary nesting or partial vectors.
    if len(vector) == 1 and isinstance(vector[0], (list, tuple)):
        vector = vector[0]
    if len(vector) != len(schema):
        return None
    return [{"label": f"{label} ({unit})", "value": value}
            for (label, unit), value in zip(schema, vector)]


def _facts(evidence, fields):
    """Select present values; zero and False are recorded observations."""
    out = []
    for key, label in fields:
        value = evidence.get(key)
        if value is not None and value != "":
            out.append({"label": label, "value": value})
    return out


def _value(evidence, key):
    value = evidence.get(key)
    return value if value is not None and value != "" else None


def _summary(threat, evidence, kind):
    def clip(text, limit=160):
        if len(text) <= limit:
            return text
        head = text[:limit - 4].rsplit(" ", 1)[0]
        return head + " ..."

    def compact(parts, limit=160):
        text = "; ".join(f"{label} {value}" for label, value in parts
                          if value is not None and value != "")
        return clip(text, limit) if text else "Measurements not recorded"

    if threat == "c2_beaconing":
        n, interval, cv, gate = (_value(evidence, k) for k in
                                 ("flows_in_series", "mean_interval_s", "iat_cv", "cv_gate"))
        result = compact((("flows", n), ("mean interval (s)", interval), ("CV", cv), ("gate", gate)))
        if result != "Measurements not recorded":
            return result
    elif threat == "data_exfiltration":
        size, baseline, ratio, age = (_value(evidence, k) for k in
                                      ("bytes_to_new_dst", "src_baseline_bytes_median", "ratio_vs_baseline", "pair_age_windows"))
        if any(x is not None for x in (size, baseline, ratio, age)):
            text = compact((("bytes to new destination", size), ("baseline bytes", baseline),
                            ("guarded ratio" if baseline == 0 else "ratio",
                             f"{ratio}x" if ratio is not None else None), ("age windows", age)))
            if evidence.get("authorised_destination"):
                entries = evidence.get("registry_entries") or []
                text += "; operator registry match" + (f" {', '.join(map(str, entries))}" if entries else "")
            return clip(text)
    elif threat.startswith("tls_"):
        ja4, sni, scope = (_value(evidence, k) for k in ("ja4", "sni", "novelty_scope"))
        match = evidence.get("match_source")
        if threat == "tls_known_malware" and match:
            return compact((("JA4", ja4), ("matched local configured list", "not externally validated")))
        if any(x is not None for x in (ja4, sni, scope)):
            return compact((("JA4", ja4), ("SNI", sni), ("scope", scope)))
    elif threat == "dga_domain":
        label = _value(evidence, "qname_label")
        length = _value(evidence, "label_length")
        if evidence.get("detector_tier") == "tier2_cnn_only":
            probability = _value(evidence, "dga_cnn_prob")
            if label is not None or probability is not None:
                return compact((("CNN-only label", label), ("length", length),
                                ("model score (uncalibrated)", probability)))
        entropy = _value(evidence, "char_entropy_bits")
        if any(x is not None for x in (label, length, entropy)):
            return compact((("label", label), ("length", length), ("lexical entropy (bits)", entropy)))
    elif threat == "dns_tunneling":
        qlen, qtype, queries, total = (_value(evidence, k) for k in
                                      ("query_bytes", "qtype", "tunnel_queries_from_src", "cumulative_tunnel_bytes"))
        if any(x is not None for x in (qlen, qtype, queries, total)):
            return compact((("query bytes", qlen), ("qtype", qtype), ("queries", queries),
                            ("cumulative query bytes", total),
                            ("limitation", "not verified exfil volume")))
    elif threat.startswith("recon_") and kind != "model":
        rolling = threat.startswith("recon_rolling_")
        pair_key = "rolling_distinct_dst_port_pairs" if rolling else "distinct_dst_port_pairs"
        pairs, ips, top = (_value(evidence, k) for k in
                           (pair_key, "distinct_dst_ips", "pairs_on_top_dst"))
        window = _value(evidence, "window")
        if any(x is not None for x in (pairs, ips, top, window)):
            parts = [("destination/port pairs", pairs), ("destinations", ips),
                     ("top-destination pairs", top), ("window", window)]
            if rolling:
                parts.extend((
                    ("rolling horizon (s)", evidence.get("rolling_window_s")),
                    ("current-window pairs", evidence.get("current_window_distinct_pairs")),
                    ("observed window-end times (stream seconds)",
                     f"{evidence.get('oldest_observed_window_end_s')}–{evidence.get('newest_observed_window_end_s')}"
                     if evidence.get("oldest_observed_window_end_s") is not None
                     and evidence.get("newest_observed_window_end_s") is not None else None),
                ))
            return compact(parts)
    elif threat.startswith("udp_"):
        return compact((("UDP packets", _value(evidence, "udp_packets")),
                        ("pkt/s", _value(evidence, "udp_packet_rate_per_s")),
                        ("destination endpoints", _value(evidence, "distinct_destination_endpoints")),
                        ("source IPs", _value(evidence, "distinct_source_ips")),
                        ("window (s)", _value(evidence, "window_s"))))
    elif threat.startswith("ddos_"):
        pkts, rate, sources, syn = (_value(evidence, k) for k in
                                    ("window_pkts", "pkt_rate_per_s", "distinct_src_ips", "syn_ratio"))
        if any(x is not None for x in (pkts, rate, sources, syn)):
            return compact((("packets", pkts), ("pkt/s", rate), ("source IPs", sources),
                            ("SYN ratio", syn)))
    elif threat in _FUSED:
        signals = evidence.get("contributing_signals")
        if isinstance(signals, list) and signals:
            names = [str(item.get("threat_class")) for item in signals
                     if isinstance(item, dict) and item.get("threat_class")]
            combo = _value(evidence, "combination")
            if isinstance(combo, str) and "half-life=" in combo:
                combo = "noisy-OR; " + combo.split("half-life=", 1)[1].rstrip(")") + "s half-life"
            text = compact((("signals", ", ".join(names) if names else None),
                            ("window (s)", _value(evidence, "window_s")),
                            ("method", combo), ("limitation", "not confirmation")))
            return text
    elif kind == "model":
        vector = evidence.get("flow_features")
        if vector is None:
            vector = evidence.get("features")
        if vector is None:
            vector = evidence.get("metadata_features")
        if isinstance(vector, dict) and vector:
            names = {"npkt": "packets", "nbytes": "bytes", "duration": "duration_s",
                     "nsyn": "SYNs", "bytes_per_pkt": "mean_bytes_per_packet",
                     "pkts_per_sec": "packets_per_second", "dport": "destination_port"}
            observed = [(names.get(k, k), v) for k, v in vector.items()
                        if k in names and v is not None]
            if observed:
                return compact((("observed flow", ", ".join(f"{k}={v}" for k, v in observed)),))
            return "Raw model feature values recorded"
        if isinstance(vector, (list, tuple)):
            _, schema = _model_vector_schema(threat, evidence)
            named = _named_vector_facts(vector, schema) if schema else None
            if named:
                shown = ", ".join(
                    f"{fact['label'].split(' (', 1)[0]}={fact['value']}"
                    for fact in named[:3])
                return compact((("named model inputs", shown),))
            return f"Raw numeric model vector recorded ({len(vector)} values)"[:160]
        if evidence.get("model"):
            score = evidence.get("malicious_probability")
            if score is None:
                score = evidence.get("sequence_score")
            return compact((("model", evidence.get("model")),
                            ("uncalibrated model score", score)))
    return "Measurements not recorded"


def _caveat(threat, evidence, kind):
    if threat.startswith("udp_"):
        return "Only emitted UDP datagrams are observed. This burst does not establish reflection or amplification; legitimate discovery or scanning can look similar."
    if threat in _FUSED:
        return "Correlation combines detector outputs from one-way observations; signals may share causes and do not confirm compromise."
    if threat == "data_exfiltration" or threat == "data_exfiltration_model":
        if evidence.get("authorised_destination"):
            return "One-way byte volume cannot establish intent; this destination matched an operator-maintained registry entry."
        if threat == "data_exfiltration" and evidence.get("src_baseline_bytes_median") == 0:
            return "One-way bytes show volume, not authorization; benign backups can look similar. Ratio uses a 1-byte floor when baseline is zero."
        return "One-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar."
    if threat.startswith("tls_"):
        if threat == "tls_known_malware":
            return "ClientHello is one-way observable; bundled known-JA4 indicator is a simulated profile, not validated external threat intelligence."
        return "Only client-side TLS metadata is visible; novelty or a local known-list match can also reflect legitimate software changes."
    if threat == "encrypted_session_malware" and "metadata_features" in evidence:
        return ("The named vector contains client-side metadata and flow measurements. "
                "This alert has no metadata-availability flags, so a recorded zero "
                "does not establish whether a field was absent, empty, or defaulted.")
    if threat in ("dga_domain", "dns_tunneling"):
        return "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use."
    if threat.startswith("recon_") or threat.startswith("ddos_"):
        if threat.startswith("recon_rolling_"):
            return ("This rolling fan-out pattern uses one-way packet metadata. "
                    "Bounded history evictions can make the retained pair count "
                    "lower than the full observed history; authorized scanners "
                    "can produce similar patterns.")
        return "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements."
    if kind == "model":
        return "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training."
    if threat == "c2_beaconing":
        return "Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern."
    return "One-way traffic evidence is incomplete and may have benign explanations."


def _next_step(threat, evidence, kind):
    if threat.startswith("udp_"):
        return "Check the source owners, destination services and observed rate against authorized discovery, scanning or load tests."
    if threat in _FUSED:
        return "Review each listed source alert and its packet-time window before escalating."
    if threat.startswith("tls_"):
        return "Compare the observed JA4 and SNI with the host's approved software inventory."
    if threat == "data_exfiltration" or threat == "data_exfiltration_model":
        if evidence.get("authorised_destination"):
            return "Review the matched operator authorization, volume cap, and observed destination before accepting the transfer."
        return "Compare the observed destination and transfer volume with this source's prior byte baseline and backup schedule."
    if threat in ("dga_domain", "dns_tunneling"):
        return "Review the captured DNS query names and qtypes for this source and time window."
    if threat.startswith("recon_"):
        return "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule."
    if threat.startswith("ddos_"):
        return "Inspect the packet sample and source distribution for the recorded window."
    if threat == "c2_beaconing":
        return "Compare the recorded flow times with the source's expected scheduled connections."
    if kind == "model":
        return "Review the raw recorded model features alongside the source's deterministic alerts."
    return "Review the original alert record and its recorded evidence."


def describe_alert(alert):
    """Return a display adapter with facts drawn only from recorded evidence."""
    threat = alert.get("threat_class") if isinstance(alert, dict) else None
    threat = threat or "unknown"
    evidence = alert.get("evidence") if isinstance(alert.get("evidence"), dict) else {}
    if threat in _FUSED:
        kind, score_label = "correlation", "Correlation score"
    elif threat == "dga_domain" and evidence.get("detector_tier") == "tier2_cnn_only":
        kind, score_label = "model", "Model score"
    elif threat in _MODELS:
        kind, score_label = "model", "Model score"
    elif threat in _LABELS:
        kind, score_label = "rule", "Rule score"
    else:
        kind, score_label = "unknown", "Detector score"

    fields = {
        "udp_burst_fanout": (("protocol", "Protocol"), ("udp_packets", "UDP packets"), ("udp_bytes", "Observed bytes"), ("udp_packet_rate_per_s", "UDP packets per second"), ("distinct_destination_ips", "Destination IPs"), ("distinct_destination_ports", "Destination ports"), ("distinct_destination_endpoints", "Destination endpoints"), ("window_s", "Window (s)")),
        "udp_target_burst": (("protocol", "Protocol"), ("udp_packets", "UDP packets"), ("udp_packet_rate_per_s", "UDP packets per second"), ("distinct_source_ips", "Source IPs"), ("destination_ip", "Destination IP"), ("destination_port", "Destination port"), ("window_s", "Window (s)")),
        "c2_beaconing": (("flows_in_series", "Flows in series"), ("mean_interval_s", "Mean interval (s)"), ("iat_cv", "Interval CV"), ("cv_gate", "CV gate")),
        "data_exfiltration": (("bytes_to_new_dst", "Observed bytes to new destination"), ("src_baseline_bytes_median", "Source median baseline bytes"), ("ratio_vs_baseline", "Ratio vs baseline"), ("pair_age_windows", "Pair age (windows)"), ("authorised_destination", "Operator registry match"), ("registry_entries", "Registry entries"), ("volume_classes", "Registry volume classes")),
        "tls_known_malware": (("ja4", "JA4"), ("sni", "SNI"), ("match_source", "Detector-reported match source"), ("transport", "Transport")),
        "tls_novel_fingerprint": (("ja4", "JA4"), ("sni", "SNI"), ("novelty_scope", "Novelty scope"), ("transport", "Transport")),
        "dga_domain": (("qname_label", "DNS label"), ("label_length", "Label length"), ("char_entropy_bits", "Lexical entropy (bits)"), ("high_entropy_query_streak", "High-entropy streak"), ("cnn_positive_streak", "CNN positive streak")),
        "dns_tunneling": (("query_bytes", "Query bytes"), ("qtype", "Query type"), ("max_label_length", "Maximum label length"), ("tunnel_queries_from_src", "Tunnel-like queries"), ("cumulative_tunnel_bytes", "Cumulative query bytes")),
        "recon_vertical_scan": (("distinct_dst_port_pairs", "Destination/port pairs"), ("distinct_dst_ips", "Destination IPs"), ("pairs_on_top_dst", "Pairs on top destination"), ("window", "Window")),
        "recon_horizontal_scan": (("distinct_dst_port_pairs", "Destination/port pairs"), ("distinct_dst_ips", "Destination IPs"), ("pairs_on_top_dst", "Pairs on top destination"), ("window", "Window")),
        "recon_rolling_vertical_scan": (("rolling_distinct_dst_port_pairs", "Distinct destination/port pairs in rolling history"), ("current_window_distinct_pairs", "Pairs in current window"), ("distinct_dst_ips", "Distinct destination IPs"), ("pairs_on_top_dst", "Pairs on top destination"), ("rolling_window_s", "Rolling horizon (s)"), ("oldest_observed_window_end_s", "Oldest observed window end (stream seconds)"), ("newest_observed_window_end_s", "Newest observed window end (stream seconds)"), ("observed_endpoints_sample", "Observed endpoint sample"), ("observed_endpoints_truncated", "Endpoint sample truncated"), ("history_evictions", "History evictions")),
        "recon_rolling_horizontal_scan": (("rolling_distinct_dst_port_pairs", "Distinct destination/port pairs in rolling history"), ("current_window_distinct_pairs", "Pairs in current window"), ("distinct_dst_ips", "Distinct destination IPs"), ("pairs_on_top_dst", "Pairs on top destination"), ("rolling_window_s", "Rolling horizon (s)"), ("oldest_observed_window_end_s", "Oldest observed window end (stream seconds)"), ("newest_observed_window_end_s", "Newest observed window end (stream seconds)"), ("observed_endpoints_sample", "Observed endpoint sample"), ("observed_endpoints_truncated", "Endpoint sample truncated"), ("history_evictions", "History evictions")),
        "ddos_syn_flood": (("window_pkts", "Window packets"), ("pkt_rate_per_s", "Packet rate (per second)"), ("distinct_src_ips", "Source IPs"), ("syn_ratio", "SYN ratio"), ("src_syn_share", "Top source SYN share")),
        "ddos_volumetric_spoofed": (("window_pkts", "Window packets"), ("pkt_rate_per_s", "Packet rate (per second)"), ("distinct_src_ips", "Source IPs"), ("src_ip_entropy_bits", "Source IP entropy (bits)"), ("syn_ratio", "SYN ratio")),
    }
    facts = _facts(evidence, fields.get(threat, ()))
    if threat.startswith("udp_"):
        facts.extend(_facts(evidence, (("threshold_min_udp_packets", "Packet threshold"),
                                      ("threshold_min_destination_endpoints", "Endpoint threshold"),
                                      ("threshold_min_source_ips", "Source threshold"))))
    if threat in _FUSED:
        facts.extend(_facts(evidence, (("window_s", "Correlation window (s)"),
                                      ("combination", "Combination method"))))
    if kind == "model":
        vector = evidence.get("flow_features")
        if vector is None:
            vector = evidence.get("features")
        if vector is None:
            vector = evidence.get("metadata_features")
        model_facts = []
        if evidence.get("model") is not None:
            model_facts.append({"label": "Model", "value": evidence["model"]})
        if isinstance(vector, dict):
            names = {"npkt": "Observed packets", "nbytes": "Observed bytes",
                     "duration": "Flow duration (s)", "nsyn": "Observed SYNs",
                     "bytes_per_pkt": "Mean bytes per packet", "pkts_per_sec": "Packets per second",
                     "dport": "Destination port"}
            model_facts.extend({"label": names.get(key, f"Raw feature {key}"), "value": value}
                               for key, value in vector.items()
                               if value is not None and value != "")
        elif isinstance(vector, (list, tuple)):
            _, schema = _model_vector_schema(threat, evidence)
            named = _named_vector_facts(vector, schema) if schema else None
            if named:
                model_facts.extend(named)
            else:
                model_facts.append({"label": "Unmapped numeric feature vector", "value": list(vector)})
        score = evidence.get("malicious_probability")
        if score is None:
            score = evidence.get("sequence_score")
        if score is None and threat == "dga_domain":
            score = evidence.get("dga_cnn_prob")
        if score is not None:
            model_facts.append({"label": "Model score (uncalibrated)", "value": score})
        if isinstance(evidence.get("iforest_corroboration"), dict):
            for key in ("anomaly_score", "score_kind", "more_anomalous_when"):
                value = evidence["iforest_corroboration"].get(key)
                if value is not None:
                    model_facts.append({"label": f"IsolationForest {key.replace('_', ' ')}", "value": value})
        facts.extend(model_facts)

    related = []
    signals = evidence.get("contributing_signals")
    if isinstance(signals, list):
        for item in signals:
            if not isinstance(item, dict):
                continue
            related.append({
                "label": item.get("threat_class", "unknown"),
                "age_seconds": item.get("age_s"),
                "effective_score": item.get("effective_confidence"),
                "destination": item.get("dst") if item.get("dst") not in (None, "*") else None,
            })

    return {
        "kind": kind,
        "label": _LABELS.get(threat, threat.replace("_", " ").capitalize()),
        "summary": _summary(threat, evidence, kind),
        "facts": facts,
        "caveat": _caveat(threat, evidence, kind),
        "next_step": _next_step(threat, evidence, kind) if kind != "unknown" else None,
        "score_label": score_label,
        "related": related,
    }


def summarize_alerts(alerts):
    """Return presentation counters, partitioned by alert kind."""
    counts = Counter()
    sources = set()
    for alert in alerts:
        counts["raw_records"] += 1
        description = describe_alert(alert)
        counts[description["kind"] + "_records"] += 1
        if description["kind"] == "rule" and alert.get("severity") == "critical":
            counts["critical_rule_records"] += 1
        evidence = alert.get("evidence") if isinstance(alert.get("evidence"), dict) else {}
        if evidence.get("authorised_destination"):
            counts["authorised_records"] += 1
        src = alert.get("src")
        if src not in (None, "", "*"):
            sources.add(src)
    counts["source_count"] = len(sources)
    return {key: counts[key] for key in (
        "raw_records", "rule_records", "model_records", "correlation_records",
        "unknown_records", "critical_rule_records", "authorised_records",
        "source_count")}
