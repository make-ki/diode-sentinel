#!/usr/bin/env python3
"""Project-local MCP tools for producing truthful Diode Sentinel demo video."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOOLS = [
    {
        "name": "record_dashboard_tour",
        "description": (
            "Record the real Diode Sentinel dashboard in a synthetic replay, "
            "with a visible cursor, live filtering, and an opened alert evidence panel. "
            "Writes demo_video/out/dashboard_tour.{webm,mp4}. Choose ml or rules fixtures."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"fixture": {"type": "string", "enum": ["ml", "rules"]}},
            "additionalProperties": False,
        },
    },
    {
        "name": "render_full_demo",
        "description": (
            "Render and assemble the polished Diode Sentinel demo (title, real dashboard, "
            "terminal proof, evidence cards, end card) to demo_video/out/diode-sentinel-demo.mp4. "
            "Uses only the committed synthetic alert fixture and local project assets."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def respond(message: dict) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def run_tool(name: str, args: dict) -> str:
    if name == "record_dashboard_tour":
        fixture = args.get("fixture", "ml")
        if fixture not in ("ml", "rules"):
            raise ValueError("fixture must be 'ml' or 'rules'")
        alerts = ROOT / ".regression" / f"alerts_{fixture}.reference.jsonl"
        cmd = ["nix", "develop", "--command", "demo-python", "demo_video/record_dashboard.py",
               "--alerts", str(alerts)]
        expected = [ROOT / "demo_video/out/dashboard_tour.webm", ROOT / "demo_video/out/dashboard_tour.mp4"]
    elif name == "render_full_demo":
        if args:
            raise ValueError("render_full_demo takes no arguments")
        cmd = ["nix", "develop", "--command", ".venv/bin/python", "demo_video/build_demo_video.py"]
        expected = [ROOT / "demo_video/out/diode-sentinel-demo.mp4"]
    else:
        raise ValueError(f"unknown tool: {name}")

    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1100)
    if proc.returncode:
        detail = (proc.stderr or proc.stdout)[-5000:]
        raise RuntimeError(f"Video render failed (exit {proc.returncode}):\n{detail}")
    outputs = [f"{p.relative_to(ROOT)} ({p.stat().st_size / 1_000_000:.1f} MB)"
               for p in expected if p.exists()]
    if not outputs:
        raise RuntimeError("Render finished but expected output files were not created")
    return "Created:\n" + "\n".join(outputs) + "\n\n" + (proc.stdout[-2500:] if proc.stdout else "")


def handle(message: dict) -> None:
    method = message.get("method")
    msg_id = message.get("id")
    if method == "notifications/initialized":
        return
    if method == "initialize":
        respond({"jsonrpc": "2.0", "id": msg_id, "result": {
            "protocolVersion": message.get("params", {}).get("protocolVersion", "2025-03-26"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "diode-demo-video", "version": "1.0.0"},
            "instructions": "Use record_dashboard_tour for an interactive product walkthrough or render_full_demo for the complete edited demo. Outputs are synthetic replay demonstrations; do not describe alert records as incidents or imply remote delivery was confirmed.",
        }})
    elif method == "ping":
        respond({"jsonrpc": "2.0", "id": msg_id, "result": {}})
    elif method == "tools/list":
        respond({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        params = message.get("params", {})
        try:
            result = run_tool(params.get("name", ""), params.get("arguments") or {})
            payload = {"content": [{"type": "text", "text": result}]}
        except Exception as exc:  # surfaced to Codex as an MCP tool error
            payload = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
        respond({"jsonrpc": "2.0", "id": msg_id, "result": payload})
    elif msg_id is not None:
        respond({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})


def main() -> None:
    os.chdir(ROOT)
    for line in sys.stdin:
        try:
            handle(json.loads(line))
        except Exception as exc:
            print(f"MCP protocol error: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
