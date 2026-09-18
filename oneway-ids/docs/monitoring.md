# Prometheus + Grafana monitoring for the one-way NIDS

The sensor can expose its live internals as Prometheus metrics; the stack in
`monitoring/` scrapes them and ships a pre-built Grafana dashboard plus a set
of alert rules. Everything about the *sensor* stays stdlib-only: the exporter
(`metrics.py`) hand-renders the Prometheus text exposition format rather than
adding `prometheus_client` to the pinned environment, for the same reason the
SOC dashboard has no Flask.

```
run.py --metrics-port 9100  ──►  Prometheus (:9090)  ──►  Grafana (:3000)
        /metrics                        15s scrapes        provisioned
      (stdlib HTTP)                   alert rules        "NIDS Overview"
```

## Quick start

```bash
# 1. the stack (from monitoring/)
docker compose up -d
#    Grafana  http://localhost:3000   admin / admin   (dashboard auto-loaded)
#    Prom     http://localhost:9090

# 2. the sensor, with metrics on (project root)
.venv/bin/python run.py --metrics-port 9100            # replay
sudo .venv/bin/python run.py --live eth0 --metrics-port 9100
.venv/bin/python run.py --pipe /run/nids/feed.pcap --metrics-port 9100

# 3. check the exporter directly
curl -s localhost:9100/metrics | grep nids_alerts_total
```

All three can start in any order; Prometheus retries scrapes until the sensor
is up (the dashboard's "Sensor" tile goes green).

## Exported metrics

All under the `nids_` prefix, labelled with `sensor_pid` (so several sensors
on one host stay distinguishable).

| Metric | Type | Meaning |
|---|---|---|
| `nids_packets_processed_total` | counter | packets fed into the pipeline |
| `nids_flows_closed_total` | counter | idle-closed flows handed to scoring |
| `nids_flows_active{kind}` | gauge | open flows per protocol (tcp/udp) |
| `nids_windows_flushed_total` | counter | 10 s detection windows flushed |
| `nids_dns_queries_total` | counter | DNS qnames dissected |
| `nids_clienthellos_parsed_total` | counter | TLS/QUIC ClientHellos parsed |
| `nids_alerts_total{threat_class,severity}` | counter | alerts emitted, by class AND severity |
| `nids_alerts_suppressed_total` | counter | squashed by the Tier-0 allowlist |
| `nids_ml_alerts_total` | counter | Tier-2 LightGBM verdicts |
| `nids_cnn_alerts_total` | counter | Tier-2 DGA character-CNN confirmations |
| `nids_frames_seen_total` | counter | frames pulled off the socket (live) |
| `nids_frames_analysed_total` | counter | frames that survived the sampler |
| `nids_frames_sampled_out_total` | counter | frames skipped by the 1-in-N guard |
| `nids_frames_non_ipv4_total` | counter | ARP/IPv6/etc -- not parsed |
| `nids_frames_other_ip_total` | counter | ICMP/GRE/ESP -- no detector consumes |
| `nids_frames_malformed_total` | counter | failed dissection |
| `nids_kernel_dropped_total` | counter | **kernel ring-buffer drops: lost traffic** |
| `nids_process_cpu_seconds_total` | counter | sensor CPU time (from /proc) |
| `nids_process_resident_memory_bytes` | gauge | sensor RSS |
| `nids_process_start_time_seconds` | gauge | restart detection |

Alert counters are bumped eagerly via `AlertSink.subscribe` (an alert is too
rare an event to reconstruct by diffing at scrape time); everything else is
sampled from the live objects at each scrape, so nothing can drift from what
the sensor is actually doing. Severity is *derived* from confidence exactly
as `detectors._severity` does, so `nids_alerts_total{severity=...}` always
agrees with the SOC dashboard.

## Alert rules (`monitoring/prometheus/rules/`)

| Alert | Fires when | Why |
|---|---|---|
| `NidsSensorDown` | scrape fails for 2 m | an unmonitored diode receive side is a blind sensor |
| `NidsSensorRestarted` | process start-time changed | warm-start / capture-death visibility |
| `NidsKernelPacketDrops` | any `kernel_dropped` increase | one-way loss is invisible by definition -- page on it |
| `NidsSamplingHeavily` | sampler skips > half of frames | coverage trade-off became the dominant mode |
| `NidsCriticalAlert` | any critical alert in 5 m | detection, at sensor severity |
| `NidsHighAlert` | any high alert in 5 m | detection |
| `NidsAlertBurst` | > 25 alerts in 10 m | incident or new host entering the stream |
| `NidsDgaCnnConfirmations` | CNN confirmations firing | lexical gate passed what the CNN caught |

## The Grafana dashboard

`monitoring/grafana/dashboards/nids-overview.json` is provisioned
automatically (folder **NIDS**, uid `nids-overview`) and contains:

- **KPI row** -- Sensor up/down, alerts (5m), critical, high, kernel drops
  (red > 0; on a one-way feed any drop is an incident).
- **Detection mix** -- stacked alert rate by threat class and by severity
  (the Prometheus-side version of the SOC dashboard's timeline/ring).
- **Ingest health** -- packets/s, flows closed/s, sampled-out/s, active flows
  per protocol, windows flushed/s.
- **Deep inspection** -- DNS qnames/s and ClientHellos/s (TCP + QUIC).
- **Tier-2 attribution** -- LightGBM verdicts/s, DGA CNN confirmations/s,
  allowlisted/s.

Links at the top jump to the stdlib SOC dashboard (`:8600`) and the Prometheus
UI. The dashboard is read-only-provisioned; clone it in the UI to customise.

## Multiple sensors / remote sensors

`prometheus.yml` scrapes `host.docker.internal:9100` by default. For a remote
sensor (or several), add targets -- static:

```yaml
scrape_configs:
  - job_name: nids
    static_configs:
      - targets: ["sensor-a.lab:9100"]
        labels: { sensor: a }
      - targets: ["sensor-b.lab:9100"]
        labels: { sensor: b }
```

or file-based service discovery:

```yaml
    file_sd_configs:
      - files: ["/etc/prometheus/targets/*.yml"]
```

Every dashboard panel and alert rule is label-agnostic (`job="nids"` plus
whatever labels you add), so extra sensors appear per-instance without
changes.

## Replay as a batch job

Replay (`run.py traffic.pcap --metrics-port 9100`) serves metrics too, but the
process is short-lived and the counters are process-lifetime (they reset with
each run). Two consequences, both already handled:

- `honor_timestamps: false` is set in `prometheus.yml` -- replayed stream time
  is not wall time, and stale samples must still be ingested.
- `NidsSensorRestarted` fires on every replay restart; that is the intended
  semantics (counters really did reset).

For continuous replay loops, wrap the run:

```bash
while true; do .venv/bin/python run.py traffic.pcap --metrics-port 9100; done
```

## Standalone Prometheus/Grafana (no Docker)

Point your existing Prometheus at the sensor and include the rules:

```yaml
scrape_configs:
  - job_name: nids
    honor_timestamps: false
    static_configs:
      - targets: ["sensor-host:9100"]
rule_files:
  - /path/to/oneway-ids/monitoring/prometheus/rules/alert_rules.yml
```

In Grafana: add a Prometheus datasource, then import
`monitoring/grafana/dashboards/nids-overview.json` (dashboards → import).

## Files

```
monitoring/
  docker-compose.yml                    the stack (Prometheus v3.13.1 LTS, Grafana 12.4.11)
  prometheus/prometheus.yml             scrape config (honor_timestamps: false for replay)
  prometheus/rules/alert_rules.yml      8 alert rules (availability, ingest, detections)
  grafana/provisioning/datasources/     Prometheus datasource (auto)
  grafana/provisioning/dashboards/      dashboard provider (auto)
  grafana/dashboards/nids-overview.json the NIDS Overview dashboard
```

Sensor side: `metrics.py` (exporter), `run.py --metrics-port PORT`,
`test_metrics.py` (19 unit tests).
