#!/usr/bin/env python3
"""Capture fresh full-speed dashboard evidence for the B/C explainer."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import quote
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
for package_dir in (ROOT / ".venv/lib").glob("python*/site-packages"):
    sys.path.insert(0, str(package_dir))
import dpkt
from playwright.sync_api import sync_playwright
from core.config import SIM_START

OUT = ROOT / "diode-sentinel-launch/public/explainer-captures"
PORT = 18721
PYTHON = str(ROOT / ".venv/bin/python")
OUT.mkdir(parents=True, exist_ok=True)
FFMPEG = shutil.which("ffmpeg") or next(iter(Path("/nix/store").glob("*-ffmpeg-*-bin/bin/ffmpeg")), None)
if not FFMPEG:
    raise RuntimeError("ffmpeg executable not found")


def free_port(port: int) -> bool:
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


if not free_port(PORT):
    raise RuntimeError(f"port {PORT} is already in use")


def synthetic_packet(ts, src, dst, size=600, sport=40000, dport=443, proto="tcp", payload=b""):
    """Build one Ethernet packet in the same observable direction as the sensor."""
    eth = dpkt.ethernet.Ethernet()
    eth.src = b"\x02\x00\x00\x00\x00\x01"
    eth.dst = b"\x02\x00\x00\x00\x00\x02"
    ip = dpkt.ip.IP(src=socket.inet_aton(src), dst=socket.inet_aton(dst), ttl=64)
    ip.p = dpkt.ip.IP_PROTO_TCP if proto == "tcp" else dpkt.ip.IP_PROTO_UDP
    if not payload and size > 54:
        payload = b"A" * (size - 54)
    if proto == "tcp":
        transport = dpkt.tcp.TCP(sport=sport, dport=dport, seq=1000, ack=0,
                                  flags=dpkt.tcp.TH_ACK | dpkt.tcp.TH_PUSH, data=payload)
    else:
        transport = dpkt.udp.UDP(sport=sport, dport=dport, data=payload)
        transport.ulen = len(transport)
    ip.data = transport
    ip.len = len(ip)
    eth.data = ip
    return float(ts), bytes(eth)


def add_focused_scenarios(pcap_path: Path, destination: Path) -> dict:
    """Copy fresh generator frames and add test-shaped packets for opt-in paths."""
    with pcap_path.open("rb") as handle:
        reader = dpkt.pcap.Reader(handle)
        linktype = reader.datalink()
        packets = [(float(ts), frame) for ts, frame in reader]
    # Keep the complete seeded generator replay intact; put the focused fixtures
    # after its 600-second stream using the exact distinct-pair shapes exercised
    # by tests/test_hour_fixes.py.
    fixture = []
    for i in range(10):
        fixture.append(synthetic_packet(SIM_START + 605.1 + i / 100, "192.0.2.70", "198.51.100.70",
                                        sport=40000 + i, dport=1000 + i))
    for i in range(10):
        fixture.append(synthetic_packet(SIM_START + 615.1 + i / 100, "192.0.2.70", "198.51.100.70",
                                        sport=40010 + i, dport=1010 + i))
    # Host A sees the destination first. Host B sees another destination, then
    # transfers there: this is the source-history context case from the gate.
    fixture += [
        synthetic_packet(SIM_START + 625.0, "192.0.2.80", "198.51.100.80"),
        synthetic_packet(SIM_START + 625.1, "192.0.2.81", "198.51.100.81"),
    ]
    fixture += [synthetic_packet(SIM_START + 635.1 + i / 1000, "192.0.2.81", "198.51.100.80",
                                  size=6000, sport=41000, dport=443) for i in range(100)]
    packets.extend(fixture)
    packets.sort(key=lambda row: row[0])
    with destination.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle, linktype=linktype)
        for ts, frame in packets:
            writer.writepkt(frame, ts=ts)
        writer.close()
    return {"linktype": linktype, "generator_packets": len(packets) - len(fixture),
            "fixture_packets": len(fixture), "packets_total": len(packets),
            "fixture_timestamps": {"time_base": SIM_START,
                                   "rolling_scan_windows": [SIM_START + 605.1, SIM_START + 615.1],
                                   "source_history_seed": [SIM_START + 625.0, SIM_START + 625.1],
                                   "source_history_transfer": [SIM_START + 635.1, SIM_START + 635.199]}}


def api(path):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/{path}", timeout=5) as response:
        return json.load(response)


def alert_key(alert):
    def js_number(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    return "|".join(js_number(alert.get(key, "")) for key in
                     ("timestamp", "src", "threat_class", "confidence"))


def wait_ready():
    for _ in range(120):
        try:
            api("api/stats")
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("dashboard did not start")


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


manifest = {
    "source": "fresh seeded gen_traffic.py capture plus focused synthetic PCAP scenarios",
    "qualifier": "Synthetic replay; detector outputs are scenario evidence, not accuracy claims.",
    "replay": {"seed": "generator default", "mode": "--pipe pcap FIFO", "speed": 25,
               "pipeline_flags": ["--no-state", "--dga-cnn", "--ml", "--models-567 models567/manifest.json",
                                  "--source-context", "--rolling-scan"]},
    "viewport": {"width": 1600, "height": 1000},
    "clips": {}, "interactions": [], "selected_records": {}, "downloads": {},
}
children = []

with tempfile.TemporaryDirectory(prefix="diode-explainer-") as temp:
    work = Path(temp)
    capture = work / "fresh-seeded.pcap"
    combined = work / "explainer-replay.pcap"
    alerts = work / "alerts.jsonl"
    fifo = work / "feed.pcap"
    os.mkfifo(fifo)
    env = {**os.environ, "DIODESENTINEL_PCAP_PATH": str(capture),
           "DIODESENTINEL_ALERTS_PATH": str(alerts), "DIODESENTINEL_DEMO": "1"}
    env.pop("MESSY", None)
    subprocess.run([PYTHON, "gen_traffic.py"], cwd=ROOT, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    manifest["scenario"] = add_focused_scenarios(capture, combined)
    shutil.copy2(combined, OUT / "explainer-replay.pcap")
    log_path = OUT / "capture.log"
    log = log_path.open("w")
    try:
        server = subprocess.Popen([PYTHON, "dashboard.py", str(PORT)], cwd=ROOT,
                                  env=env, stdout=log, stderr=log)
        children.append(server)
        wait_ready()
        # Start the actual product pipeline with every requested optional tier.
        pipeline = subprocess.Popen([PYTHON, "run.py", "--pipe", str(fifo), "--no-state",
                                     "--dga-cnn", "--ml", "--models-567", "models567/manifest.json",
                                     "--source-context", "--rolling-scan"], cwd=ROOT, env=env,
                                    stdout=log, stderr=log)
        children.append(pipeline)
        replay = subprocess.Popen([PYTHON, "demo_replay.py", str(combined), str(fifo),
                                   "--speed", "25"], cwd=ROOT, env=env,
                                  stdout=log, stderr=log)
        children.append(replay)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM"), headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1,
                                    accept_downloads=True)
            page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            page.evaluate("document.documentElement.style.zoom='1'")
            # This overlay follows genuine Playwright mouse events and doesn't
            # modify dashboard values, controls, or layout.
            page.evaluate('''()=>{const c=document.createElement('div');c.id='demo-cursor';c.style.cssText='position:fixed;left:0;top:0;z-index:999999;pointer-events:none;filter:drop-shadow(0 2px 4px #000);transform:translate(-100px,-100px)';c.innerHTML='<svg width="28" height="36" viewBox="0 0 28 36"><path d="M3 2 L3 27 L10 21 L16 33 L21 30 L15 18 L25 17 Z" fill="white" stroke="#111" stroke-width="2"/></svg>';document.body.append(c);document.addEventListener('mousemove',e=>{c.style.transform=`translate(${e.clientX}px,${e.clientY}px)`});document.addEventListener('mousedown',()=>c.style.filter='drop-shadow(0 0 12px #ff8a1f)');document.addEventListener('mouseup',()=>c.style.filter='drop-shadow(0 2px 4px #000)');}''')
            current_clip = ""

            def move(selector, click=False, dwell=0):
                target = page.locator(selector).first
                target.wait_for(state="visible", timeout=15000)
                target.scroll_into_view_if_needed()
                box = target.bounding_box()
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2,
                                steps=60)
                page.wait_for_timeout(1100)
                if click:
                    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    page.wait_for_timeout(650)
                if dwell:
                    page.wait_for_timeout(dwell)
                manifest["interactions"].append({"clip": current_clip, "selector": selector,
                                                  "click": click, "steps": 60, "move_seconds": 1.1,
                                                  "timestamp_monotonic": round(time.monotonic(), 3),
                                                  "dwell_ms": dwell})
                return box

            def select_alert(term, predicate=None):
                move("#search", True)
                page.locator("#search").fill(term)
                page.wait_for_timeout(850)
                page.wait_for_selector("#alert-rows tr[data-key]", timeout=15000)
                result = api("api/alerts?limit=400&q=" + quote(term))
                candidates = result.get("alerts", [])
                selected = next((item for item in candidates
                                 if predicate is None or predicate(item)), None)
                if selected is None:
                    raise RuntimeError(f"no actual alert record matches {term!r} and its evidence predicate")
                raw = {key: value for key, value in selected.items() if key != "triage"}
                manifest["selected_records"][current_clip] = {
                    "record": raw, "triage": selected.get("triage"),
                    "record_key": selected.get("triage", {}).get("export_key"),
                    "ui_row_key": alert_key(raw)}
                # Use the alert's stable visible row key to avoid selecting a
                # newer but different model branch with the same class.
                row = page.locator(f'#alert-rows tr[data-key="{alert_key(raw)}"]')
                if row.count() == 0:
                    visible_keys = page.locator("#alert-rows tr[data-key]").evaluate_all(
                        "rows => rows.map(row => row.dataset.key)")
                    raise RuntimeError(f"selected alert row is not visible: {alert_key(raw)!r}; "
                                       f"visible keys={visible_keys[:6]!r}")
                move_locator(row, click=True)
                return raw

            def move_locator(target, click=False, dwell=0):
                target = target.first
                target.wait_for(state="visible", timeout=15000)
                target.scroll_into_view_if_needed()
                box = target.bounding_box()
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2,
                                steps=60)
                page.wait_for_timeout(1100)
                if click:
                    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    page.wait_for_timeout(650)
                if dwell:
                    page.wait_for_timeout(dwell)
                manifest["interactions"].append({"clip": current_clip,
                                                  "selector": "#alert-rows tr[data-key]",
                                                  "click": click, "steps": 60,
                                                  "move_seconds": 1.1,
                                                  "timestamp_monotonic": round(time.monotonic(), 3),
                                                  "dwell_ms": dwell})
                return box

            def record(name, action, focus, seconds=16):
                global current_clip
                current_clip = name
                video = OUT / f"{name}.webm"
                poster = OUT / f"{name}.png"
                page.screencast.start(path=str(video), size={"width": 1600, "height": 1000})
                started = time.monotonic()
                started_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                action()
                page.wait_for_timeout(max(0, int(seconds * 1000 - (time.monotonic() - started) * 1000)))
                ended = time.monotonic()
                ended_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                bounds = page.locator(focus).first.bounding_box()
                try:
                    visible_text = page.locator(focus).first.inner_text(timeout=2500)
                except Exception:
                    visible_text = ""
                page.screencast.stop()
                page.screenshot(path=str(poster), full_page=False)
                manifest["clips"][name] = {"focusSelector": focus, "focusBounds": bounds,
                                           "recordedSeconds": round(ended - started, 3),
                                           "visibleText": visible_text,
                                           "video": video.name, "poster": poster.name,
                                           "timestamps": {"start_utc": started_at, "end_utc": ended_at,
                                                          "start_monotonic": round(started, 3),
                                                          "end_monotonic": round(ended, 3)}}
                print(f"Captured {name} ({ended - started:.1f}s)", flush=True)

            # Let data move across the dashboard while the live counters settle.
            page.wait_for_timeout(5000)
            record("overview", lambda: (move("#sensor-strip", dwell=3500), move("#kpis", dwell=3500),
                                         move("#queue-count", dwell=1500)), "#sensor-strip", 24)
            page.wait_for_selector("#alert-rows tr[data-key]", timeout=25000)

            def beacon():
                select_alert("beacon")
                move("#detail-facts", dwell=4200)
            record("beacon", beacon, "#detail-modal .modal-box", 22)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def rolling():
                select_alert("recon_rolling")
                move("#detail-facts", dwell=4500)
            record("rolling-scan", rolling, "#detail-modal .modal-box", 26)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def source_history():
                select_alert("192.0.2.81", predicate=lambda row:
                    row.get("threat_class") == "data_exfiltration"
                    and row.get("evidence", {}).get("fleet_destination_novel") is False)
                move("#detail-facts", dwell=4500)
                move(".raw-evidence summary", click=True, dwell=1800)
                evidence = page.locator("#detail-evidence")
                evidence.scroll_into_view_if_needed()
                box = evidence.bounding_box()
                page.mouse.move(box["x"] + box["width"] / 2,
                                box["y"] + box["height"] / 2, steps=60)
                page.wait_for_timeout(1100)
                for _ in range(4):
                    page.mouse.wheel(0, 150)
                    page.wait_for_timeout(650)
                manifest["interactions"].append({"clip": current_clip,
                                                  "selector": "#detail-evidence",
                                                  "action": "gradual evidence scroll",
                                                  "scroll_steps": 4,
                                                  "timestamp_monotonic": round(time.monotonic(), 3)})
            record("source-context", source_history, "#detail-modal .modal-box", 26)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def dns_evidence():
                select_alert("dns")
                move("#detail-facts", dwell=4200)
            record("dns", dns_evidence, "#detail-modal .modal-box", 23)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def encrypted_evidence():
                select_alert("encrypted_session_malware", predicate=lambda row:
                    row.get("threat_class") == "encrypted_session_malware"
                    and row.get("evidence", {}).get("model") == "xgboost"
                    and len(row.get("evidence", {}).get("metadata_features", [])) == 10)
                move("#detail-facts", dwell=4500)
            record("encrypted-metadata", encrypted_evidence, "#detail-modal .modal-box", 32)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def scan_model():
                select_alert("recon_model_scan", predicate=lambda row:
                    row.get("threat_class") == "recon_model_scan"
                    and row.get("evidence", {}).get("model") == "scan_rf")
                move("#detail-facts", dwell=4200)
            record("scan-model", scan_model, "#detail-modal .modal-box", 22)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            def source_and_correlation():
                page.locator("#search").fill("confirmed_c2")
                page.wait_for_timeout(800)
                page.wait_for_selector("#alert-rows tr[data-key]", timeout=12000)
                row = page.locator("#alert-rows tr[data-key]").first
                route = row.locator(".cell-route").inner_text()
                source = route.split("→", 1)[0].strip()
                move(f'#top-sources [data-source="{source}"]', True, dwell=1500)
                move("#source-filter", dwell=1500)
                # Restore unfiltered records so the correlation can be selected.
                page.locator("#clear-source").click()
                page.locator("#search").fill("confirmed_c2")
                page.wait_for_timeout(800)
                select_alert("confirmed_c2", predicate=lambda row:
                    row.get("threat_class") == "confirmed_c2_implant")
                move("#detail-related", dwell=4500)
                return source
            record("source-correlation", source_and_correlation, "#detail-modal .modal-box", 22)
            page.keyboard.press("Escape")
            page.locator("#search").fill("")
            page.wait_for_timeout(700)

            # Capture a real selected-record JSON bundle from the UI.
            current_clip = "evidence-export"
            video = OUT / "evidence-export.webm"
            page.screencast.start(path=str(video), size={"width": 1600, "height": 1000})
            started = time.monotonic()
            started_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            select_alert("recon_rolling")
            move("#detail-facts", dwell=3000)
            move(".raw-evidence summary", click=True, dwell=3000)
            export_button = page.locator("#export-alert")
            export_button.scroll_into_view_if_needed()
            export_box = export_button.bounding_box()
            page.mouse.move(export_box["x"] + export_box["width"] / 2,
                            export_box["y"] + export_box["height"] / 2, steps=60)
            page.wait_for_timeout(1100)
            manifest["interactions"].append({"clip": current_clip, "selector": "#export-alert",
                                              "click": True, "steps": 60, "move_seconds": 1.1,
                                              "timestamp_monotonic": round(time.monotonic(), 3),
                                              "dwell_ms": 0})
            export_key = page.locator("#export-alert").get_attribute("data-record")
            with page.expect_download(timeout=15000) as download_info:
                page.mouse.click(export_box["x"] + export_box["width"] / 2,
                                 export_box["y"] + export_box["height"] / 2)
            download = download_info.value
            saved = OUT / "downloads" / (download.suggested_filename or "rolling-scan-evidence.json")
            saved.parent.mkdir(exist_ok=True)
            download.save_as(saved)
            page.wait_for_timeout(max(0, int(28000 - (time.monotonic() - started) * 1000)))
            ended = time.monotonic()
            ended_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            page.screencast.stop()
            page.screenshot(path=str(OUT / "evidence-export.png"), full_page=False)
            manifest["clips"]["evidence-export"] = {
                "focusSelector": "#export-alert", "recordedSeconds": round(ended - started, 3),
                "visibleText": page.locator("#detail-modal .modal-box").inner_text(),
                "selectedRecordKey": export_key,
                "video": video.name, "poster": "evidence-export.png",
                "timestamps": {"start_utc": started_at, "end_utc": ended_at,
                               "start_monotonic": round(started, 3),
                               "end_monotonic": round(ended, 3)}}
            manifest["downloads"][saved.name] = {"path": str(saved.relative_to(OUT)),
                                                  "sha256": sha256(saved), "bytes": saved.stat().st_size}
            browser.close()

        replay.wait(timeout=30)
        pipeline.wait(timeout=60)
        manifest["stats"] = api("api/stats")
        run_stats = alerts.parent / "run_stats.json"
        if run_stats.exists():
            shutil.copy2(run_stats, OUT / "run_stats.json")
        alert_summary = api("api/alerts?limit=400")
        manifest["api_alert_summary"] = {"matched": alert_summary.get("matched"),
                                          "stats": alert_summary.get("stats")}
        # Preserve the exact records shown, plus the complete pipeline output.
        if alerts.exists():
            shutil.copy2(alerts, OUT / "alerts.jsonl")
            all_alerts = [json.loads(line) for line in alerts.read_text().splitlines() if line.strip()]
            manifest["pipeline_alerts"] = {"count": len(all_alerts), "sha256": sha256(alerts),
                                            "path": "alerts.jsonl"}
            for name, predicate in {
                "rolling_scan": lambda row: row.get("threat_class", "").startswith("recon_rolling_"),
                "source_context": lambda row: row.get("src") == "192.0.2.81" and row.get("threat_class") == "data_exfiltration",
                "encrypted_metadata_xgb": lambda row: row.get("threat_class") == "encrypted_session_malware" and row.get("evidence", {}).get("model") == "xgboost" and len(row.get("evidence", {}).get("metadata_features", [])) == 10,
            }.items():
                match = next((row for row in all_alerts if predicate(row)), None)
                if match:
                    manifest["selected_records"][name] = match
        manifest["artifact_hashes"] = {}
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and path.name != "capture-manifest.json":
                manifest["artifact_hashes"][str(path.relative_to(OUT))] = {
                    "sha256": sha256(path), "bytes": path.stat().st_size}
        (OUT / "capture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        for name in manifest["clips"]:
            webm = OUT / f"{name}.webm"
            mp4 = OUT / f"{name}.mp4"
            subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-i", str(webm),
                            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)], check=True)
        manifest["artifact_hashes"] = {}
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and path.name != "capture-manifest.json":
                manifest["artifact_hashes"][str(path.relative_to(OUT))] = {
                    "sha256": sha256(path), "bytes": path.stat().st_size}
        (OUT / "capture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=6)
            except subprocess.TimeoutExpired:
                child.kill()
        log.close()
