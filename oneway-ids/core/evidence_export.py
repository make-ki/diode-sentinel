"""Small offline alert-evidence export helpers (stdlib only)."""
import hashlib
import json
from datetime import datetime, timezone


SCHEMA_VERSION = "diode-sentinel-alert-evidence/v1"


def canonical_record_bytes(record):
    """Stable UTF-8 serialization used only to fingerprint the alert record."""
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def record_sha256(record):
    return hashlib.sha256(canonical_record_bytes(record)).hexdigest()


def make_alert_bundle(record, triage, filters, *, matched_alerts,
                      page_limit, page_truncated, generated_at=None):
    """Build a review bundle without inventing packet or model provenance."""
    stamp = generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": stamp,
        "filter_context": {
            "filters": filters,
            "matched_alerts": matched_alerts,
            "page_limit": page_limit,
            "page_truncated": bool(page_truncated),
            "selection": "one alert selected from the matching visible page",
        },
        "alert": {
            "record": record,
            "record_sha256": record_sha256(record),
            "triage": triage,
        },
        "provenance_availability": {
            "capture_identity": "not recorded in alert",
            "packet_references": "not recorded in alert",
            "model_artifact_identity": "not recorded in alert",
            "note": "Unavailable provenance is not inferred from the alert fields.",
        },
        "integrity": {
            "algorithm": "SHA-256",
            "canonicalization": "UTF-8 JSON with sorted keys and compact separators",
            "scope": "alert.record only",
            "purpose": "content integrity check",
            "legal_custody_claim": False,
        },
    }
