"""Small, truthful sensor-health sidecar helpers.

Counts use ``None`` when the source cannot measure them. In particular, a
pcap stream has no kernel drop counter, which must not be reported as zero.
"""
from datetime import datetime, timezone
import json
import os
import tempfile
import time


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def health_snapshot(source, *, status, mode, started_at, updated_at=None,
                    error=None, idle_after=5.0, now=None):
    """Build the stable dashboard health object from a source snapshot."""
    now = now if now is not None else time.time()
    heartbeat_at = utc_now()
    snap = source.snapshot() if source is not None and hasattr(source, "snapshot") else {}
    last_packet = snap.get("last_packet_observed_at")
    effective_status = status
    if status == "active" and (last_packet is None or now - last_packet >= idle_after):
        effective_status = "idle"
    if status == "idle" and last_packet is not None and now - last_packet < idle_after:
        effective_status = "active"
    if mode == "interface":
        interface, path = getattr(source, "iface", None), None
    elif mode == "pcap_stream":
        interface, path = None, getattr(source, "path", None)
    else:
        interface, path = None, None
    return {
        "status": effective_status,
        "mode": mode,
        "interface": interface,
        "path": path,
        "started_at": started_at,
        "updated_at": updated_at or heartbeat_at,
        "heartbeat_at": updated_at or heartbeat_at,
        "last_packet_at": (datetime.fromtimestamp(last_packet, timezone.utc)
                           .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                           if last_packet else None),
        "counts": {
            "seen": snap.get("seen"),
            "analyzed": snap.get("analysed"),
            "sampled_out": snap.get("sampled_out"),
            "malformed": snap.get("malformed"),
            "kernel_drops": snap.get("kernel_dropped"),
        },
        "error": error,
    }


def atomic_write_json(path, value):
    """Replace a JSON sidecar atomically so readers never see partial data."""
    folder = os.path.dirname(os.path.abspath(path))
    fd, temp_path = tempfile.mkstemp(prefix=".run_stats-", suffix=".tmp",
                                     dir=folder, text=True)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    except BaseException:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def offline_health_snapshot(stats, path, started_at=None):
    """Completed replay status; the offline parser cannot measure raw frames."""
    stamp = utc_now()
    return {
        "status": "completed", "mode": "offline", "interface": None,
        "path": os.path.abspath(path), "started_at": started_at or stamp,
        "updated_at": stamp, "heartbeat_at": stamp, "last_packet_at": None,
        "counts": {"seen": None, "analyzed": stats.get("npkt"),
                   "sampled_out": None, "malformed": None,
                   "kernel_drops": None},
        "error": None,
    }
