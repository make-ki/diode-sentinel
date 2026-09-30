#!/usr/bin/env python3
"""Render explainer narration with a verified Microsoft en-IN voice.

Audio is synthesized at its natural provider rate (rate=-10%) and normalized
to 48 kHz mono. No time-stretching is applied, so the spoken pacing and pauses
remain those of the provider. Run with --sample to render the approved sample
line before explainer-script.json is ready.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = "en-IN-PrabhatNeural"
RATE = "-10%"
PROVIDER = "Microsoft Edge TTS"
FFMPEG = "/nix/store/nm4ih3jrw0zma6qxhk5s2ks2r0gppzfl-ffmpeg-9.0.1-bin/bin/ffmpeg"
SAMPLE_TEXT = "A packet is a small observation. Put those observations together, and a pattern begins to appear."


def ensure_verified_voice() -> None:
    """Fail closed unless provider catalog confirms this exact Indian voice."""
    import edge_tts

    voices = asyncio.run(edge_tts.list_voices())
    match = next((v for v in voices if v.get("ShortName") == VOICE), None)
    if not match or match.get("Locale") != "en-IN":
        raise RuntimeError(f"Microsoft voice catalog did not verify {VOICE} as en-IN")


def duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        if wav.getframerate() != 48000 or wav.getnchannels() != 1:
            raise RuntimeError(f"Unexpected normalized audio format in {path}")
        return wav.getnframes() / wav.getframerate()


async def synthesize(text: str, mp3_path: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(mp3_path))


def render_segment(segment: dict, out_dir: Path, cache_root: Path) -> dict:
    sid = str(segment["id"])
    text = str(segment["text"])
    min_seconds = float(segment.get("minSeconds", 0))
    digest = hashlib.sha256(f"{PROVIDER}\0{VOICE}\0{RATE}\0{text}".encode()).hexdigest()
    cache_dir = cache_root / digest
    cache_dir.mkdir(parents=True, exist_ok=True)
    raw_mp3 = cache_dir / "source.mp3"
    natural_wav = cache_dir / "natural.wav"
    output_wav = out_dir / f"{sid}.wav"
    metadata_path = cache_dir / "explainer-voice.json"

    if not raw_mp3.exists() or raw_mp3.stat().st_size == 0:
        asyncio.run(synthesize(text, raw_mp3))
    if not natural_wav.exists() or natural_wav.stat().st_mtime < raw_mp3.stat().st_mtime:
        subprocess.run([
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw_mp3),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,afade=t=in:d=0.025",
            "-ar", "48000", "-ac", "1", str(natural_wav),
        ], check=True)

    speech_seconds = duration_seconds(natural_wav)
    target_seconds = max(speech_seconds, min_seconds)
    if (not output_wav.exists() or output_wav.stat().st_mtime < natural_wav.stat().st_mtime
            or output_wav.stat().st_size == 0):
        if target_seconds > speech_seconds:
            subprocess.run([
                FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(natural_wav),
                "-af", "apad", "-t", f"{target_seconds:.4f}", "-ar", "48000", "-ac", "1", str(output_wav),
            ], check=True)
        else:
            output_wav.write_bytes(natural_wav.read_bytes())

    actual_seconds = duration_seconds(output_wav)
    record = {
        "id": sid,
        "text": text,
        "provider": PROVIDER,
        "locale": "en-IN",
        "voice": VOICE,
        "rate": RATE,
        "speechSeconds": round(speech_seconds, 4),
        "durationSeconds": round(actual_seconds, 4),
        "minSeconds": min_seconds,
        "file": f"explainer-narration/{sid}.wav",
        "audioSha256": hashlib.sha256(output_wav.read_bytes()).hexdigest(),
    }
    metadata_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{sid}: {actual_seconds:.2f}s | {VOICE} | {RATE}", flush=True)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="render the sample line only")
    args = parser.parse_args()
    if not FFMPEG or not Path(FFMPEG).is_file():
        raise RuntimeError(f"Required ffmpeg was not found at {FFMPEG}")
    if args.sample:
        segments = [{"id": "sample", "text": SAMPLE_TEXT, "minSeconds": 0}]
    else:
        script_path = ROOT / "explainer-script.json"
        if not script_path.is_file():
            raise FileNotFoundError(f"Expected narration segments in {script_path}")
        source = json.loads(script_path.read_text())
        segments = source["segments"] if isinstance(source, dict) else source
        if not isinstance(segments, list) or not segments:
            raise ValueError("explainer-script.json must contain a non-empty segments list")
    ensure_verified_voice()
    output_dir = ROOT / "public" / "explainer-narration"
    cache_root = ROOT / ".media-cache" / "explainer-voice"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_root.mkdir(parents=True, exist_ok=True)
    records = []
    for segment in segments:
        records.append(render_segment(segment, output_dir, cache_root))
    if not args.sample:
        manifest = {
            "provider": PROVIDER,
            "catalogVerified": True,
            "locale": "en-IN",
            "voice": VOICE,
            "rate": RATE,
            "processing": "48 kHz mono loudness normalization; natural speech retained; trailing silence pads to minSeconds; no time stretching",
            "segments": records,
        }
        (cache_root / "explainer-voice.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (ROOT / "explainer-voice.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    # uv's temporary target is supplied by the caller; no project dependency
    # or environment file is changed by this script.
    temporary_tts = Path("/tmp/diode-explainer-tts")
    if temporary_tts.is_dir():
        sys.path.insert(0, str(temporary_tts))
    main()
