#!/usr/bin/env python3
"""Verify en-IN narration identity, timing, and peaks in the explainer export.

The audio stream is decoded only for measurement. Optional --align handles a
single consistent mux/codec offset by shifting timestamps and stream-copying;
it never re-encodes, time-stretches, or otherwise changes audio samples.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_MANIFEST = ROOT / "explainer-voice.json"
DATA_TS = ROOT / "src/explainer/data.generated.ts"
OUTPUT_REPORT = ROOT / "out/explainer-audio-sync.json"
EXPECTED_PROVIDER = "Microsoft Edge TTS"
EXPECTED_LOCALE = "en-IN"
EXPECTED_VOICE = "en-IN-PrabhatNeural"
EXPECTED_RATE = "-10%"
SEARCH_RADIUS_MS = 170
MIN_CORRELATION = 0.90
MAX_OFFSET_MS = 2.0
MUSIC_MIN_CORRELATION = 0.95
MUSIC_WINDOW_SECONDS = 1.0
MIN_MUSIC_GAP_SECONDS = 0.7


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    package = "ffmpeg" if name == "ffprobe" else name
    matches = sorted(Path("/nix/store").glob(f"*-{package}-*-bin/bin/{name}"))
    if matches:
        return str(matches[-1])
    raise FileNotFoundError(f"Could not find {name} on PATH or in /nix/store")


def load_timeline() -> dict:
    source = DATA_TS.read_text()
    marker = "export const explainer ="
    if marker not in source:
        raise ValueError(f"{DATA_TS} does not contain {marker!r}")
    payload = source.split(marker, 1)[1].strip()
    suffix = "as const;"
    if not payload.endswith(suffix):
        raise ValueError("Generated explainer data does not end with `as const;`")
    return json.loads(payload[:-len(suffix)].strip())


def load_wav(path: Path, start_seconds: float = 0.0, duration_seconds: float | None = None) -> tuple[np.ndarray, int]:
    import numpy as np

    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2:
            raise ValueError(f"Expected signed PCM16 audio: {path}")
        channels = wav.getnchannels()
        rate = wav.getframerate()
        first = max(0, round(start_seconds * rate))
        wav.setpos(min(first, wav.getnframes()))
        frames = wav.getnframes() - min(first, wav.getnframes())
        if duration_seconds is not None:
            frames = min(frames, max(0, round(duration_seconds * rate)))
        samples = np.frombuffer(wav.readframes(frames), dtype="<i2")
    values = samples.astype(np.float64) / 32768.0
    return values.reshape(-1, channels).mean(axis=1), rate


def verify_voice_assets(timeline: dict, manifest: dict) -> list[dict]:
    for key, wanted in (("provider", EXPECTED_PROVIDER), ("locale", EXPECTED_LOCALE),
                        ("voice", EXPECTED_VOICE), ("rate", EXPECTED_RATE)):
        if manifest.get(key) != wanted:
            raise ValueError(f"Voice manifest {key}={manifest.get(key)!r}; expected {wanted!r}")
    if manifest.get("catalogVerified") is not True:
        raise ValueError("Voice manifest does not record provider-catalog verification")

    tracks = manifest.get("segments")
    narration = timeline.get("narration")
    if not isinstance(tracks, list) or not isinstance(narration, list) or not narration:
        raise ValueError("Voice manifest and generated timeline must contain narration segments")
    by_id = {segment.get("id"): segment for segment in tracks}
    if len(by_id) != len(tracks) or set(by_id) != {segment.get("id") for segment in narration}:
        raise ValueError("Voice manifest segment IDs do not match generated narration IDs")

    checked = []
    for item in narration:
        voice = by_id[item["id"]]
        for field in ("text", "provider", "locale", "voice", "rate", "audioSha256"):
            if item.get(field) != voice.get(field):
                raise ValueError(f"{item['id']}: timeline and voice manifest disagree on {field}")
        audio_path = ROOT / "public" / voice["file"]
        digest = hashlib.sha256(audio_path.read_bytes()).hexdigest()
        if digest != voice.get("audioSha256"):
            raise ValueError(f"{item['id']}: source WAV SHA-256 does not match voice manifest")
        if voice.get("provider") != EXPECTED_PROVIDER or voice.get("locale") != EXPECTED_LOCALE:
            raise ValueError(f"{item['id']}: unexpected provider or locale")
        if voice.get("voice") != EXPECTED_VOICE or voice.get("rate") != EXPECTED_RATE:
            raise ValueError(f"{item['id']}: unexpected voice or rate")
        checked.append({"timeline": item, "voice": voice, "path": audio_path})
    return checked


def probe(video: Path, ffprobe: str) -> dict:
    result = subprocess.run([
        ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def decode_mix(video: Path, ffmpeg: str) -> tuple[np.ndarray, int]:
    with tempfile.TemporaryDirectory(prefix="diode-explainer-audio-qc-") as temp:
        decoded = Path(temp) / "mix.wav"
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
            "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(decoded),
        ], check=True)
        return load_wav(decoded)


def music_checkpoints(timeline: dict) -> list[tuple[str, float, float]]:
    """Choose short track excerpts away from narration and its ducking ramps."""
    narration = sorted(timeline.get("narration", []), key=lambda n: n["startFrame"])
    fps = timeline["fps"]
    windows = [("opening-bed", 1.1, 0.7)]  # full music level after fade-in, before first narration
    for current, following in zip(narration, narration[1:]):
        gap_start = (current["startFrame"] + current["durationFrames"]) / fps + 1.0
        gap_end = following["startFrame"] / fps - 0.2
        available = gap_end - gap_start
        if available >= MIN_MUSIC_GAP_SECONDS:
            windows.append((f"gap-after-{current['id']}", gap_start, min(MUSIC_WINDOW_SECONDS, available)))
    return windows


def measure_music(mix: np.ndarray, sample_rate: int, timeline: dict) -> tuple[list[dict], str | None]:
    import numpy as np
    from scipy.signal import correlate

    music_name = timeline.get("music")
    if not music_name:
        return [], "No soundtrack is configured in generated explainer data."
    source_path = ROOT / "public" / music_name
    if not source_path.is_file():
        return [], f"Configured soundtrack is missing: {music_name}"
    with wave.open(str(source_path), "rb") as wav:
        source_rate = wav.getframerate()
        if source_rate != sample_rate or source_rate != 48000:
            raise ValueError(f"Soundtrack sample rate {source_rate} does not match export {sample_rate}")
        total_source_frames = wav.getnframes()

    radius = round(SEARCH_RADIUS_MS / 1000 * sample_rate)
    results = []
    for name, start_seconds, requested_seconds in music_checkpoints(timeline):
        start_sample = round(start_seconds * sample_rate)
        duration = min(requested_seconds, max(0.0, (total_source_frames - start_sample) / sample_rate))
        segment, _ = load_wav(source_path, start_seconds, duration)
        if len(segment) < round(MIN_MUSIC_GAP_SECONDS * sample_rate):
            continue
        left = max(0, start_sample - radius)
        right = min(len(mix), start_sample + len(segment) + radius)
        window = mix[left:right]
        if len(window) < len(segment):
            continue
        scores = correlate(window, segment, mode="valid", method="fft")
        best = int(np.argmax(scores))
        candidate = window[best:best + len(segment)]
        denom = np.linalg.norm(segment) * np.linalg.norm(candidate)
        similarity = float(np.dot(segment, candidate) / denom) if denom else 0.0
        measured = left + best
        results.append({
            "id": name,
            "plannedStartSeconds": round(start_sample / sample_rate, 6),
            "measuredStartSeconds": round(measured / sample_rate, 6),
            "alignmentOffsetMs": round((measured - start_sample) * 1000 / sample_rate, 4),
            "correlation": round(similarity, 6),
            "windowSeconds": round(len(segment) / sample_rate, 4),
            "source": f"public/{music_name}",
        })
    return results, None


def measure(video: Path, timeline: dict, assets: list[dict], ffmpeg: str, ffprobe: str) -> tuple[list[dict], list[dict], str | None, dict]:
    import numpy as np
    from scipy.signal import correlate

    mix, sample_rate = decode_mix(video, ffmpeg)
    rows = []
    for asset in assets:
        item, voice, path = asset["timeline"], asset["voice"], asset["path"]
        source, source_rate = load_wav(path)
        if source_rate != sample_rate or source_rate != 48000:
            raise ValueError(f"{item['id']}: narration and export sample rates differ")
        expected_start = round(item["startFrame"] / timeline["fps"] * sample_rate)
        radius = round(SEARCH_RADIUS_MS / 1000 * sample_rate)
        left = max(0, expected_start - radius)
        right = min(len(mix), expected_start + len(source) + radius)
        window = mix[left:right]
        if len(window) < len(source):
            raise ValueError(f"{item['id']}: export is too short to contain the complete narration")
        scores = correlate(window, source, mode="valid", method="fft")
        best = int(np.argmax(scores))
        actual_start = left + best
        candidate = window[best:best + len(source)]
        denom = np.linalg.norm(source) * np.linalg.norm(candidate)
        similarity = float(np.dot(source, candidate) / denom) if denom else 0.0
        offset_ms = (actual_start - expected_start) * 1000 / sample_rate
        src_peak = float(np.max(np.abs(source))) if len(source) else 0.0
        rows.append({
            "id": item["id"],
            "text": voice["text"],
            "file": voice["file"],
            "audioSha256": voice["audioSha256"],
            "plannedStartSeconds": round(expected_start / sample_rate, 6),
            "measuredStartSeconds": round(actual_start / sample_rate, 6),
            "alignmentOffsetMs": round(offset_ms, 4),
            "correlation": round(similarity, 6),
            "speechSeconds": voice["speechSeconds"],
            "sourcePeak": round(src_peak, 7),
            "sourceClippedSamples": int(np.count_nonzero(np.abs(source) >= 0.999)),
        })

    peak = float(np.max(np.abs(mix))) if len(mix) else 0.0
    peak_report = {
        "decodedSampleRate": sample_rate,
        "decodedChannels": 1,
        "peakLinear": round(peak, 7),
        "peakDbfs": round(20 * np.log10(max(peak, 1e-12)), 3),
        "clippedSamplesAtOrAbove0_999": int(np.count_nonzero(np.abs(mix) >= 0.999)),
        "decodedSampleCount": len(mix),
    }
    music_rows, music_skip_reason = measure_music(mix, sample_rate, timeline)
    return rows, music_rows, music_skip_reason, peak_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", nargs="?", default="out/diode-sentinel-explainer.mp4")
    parser.add_argument("--align", action="store_true", help="stream-copy shift consistent audio offset and recheck")
    args = parser.parse_args()
    import numpy as np

    video = (ROOT / args.video).resolve()
    if not video.is_file():
        raise FileNotFoundError(f"Export does not exist: {video}")
    timeline = load_timeline()
    manifest = json.loads(VOICE_MANIFEST.read_text())
    assets = verify_voice_assets(timeline, manifest)
    ffmpeg, ffprobe = executable("ffmpeg"), executable("ffprobe")
    stream_metadata = probe(video, ffprobe)
    audio_streams = [s for s in stream_metadata.get("streams", []) if s.get("codec_type") == "audio"]
    if len(audio_streams) != 1:
        raise ValueError(f"Expected exactly one exported audio stream; found {len(audio_streams)}")

    rows, music_rows, music_skip_reason, peak_report = measure(video, timeline, assets, ffmpeg, ffprobe)
    offsets = [row["alignmentOffsetMs"] for row in rows]
    matches = [row["correlation"] for row in rows]
    if args.align:
        if min(matches) < MIN_CORRELATION:
            raise RuntimeError("Audio match is too weak to apply a safe stream-copy offset correction")
        if music_rows and min(row["correlation"] for row in music_rows) < MUSIC_MIN_CORRELATION:
            raise RuntimeError("Soundtrack match is too weak to apply a safe stream-copy offset correction")
        all_offsets = offsets + [row["alignmentOffsetMs"] for row in music_rows]
        if max(all_offsets) - min(all_offsets) > MAX_OFFSET_MS:
            raise RuntimeError("Narration offsets are not consistent enough for a global stream-copy correction")
        correction_ms = float(np.median(all_offsets))
        if abs(correction_ms) > MAX_OFFSET_MS:
            corrected = video.with_name(video.stem + "-aligned" + video.suffix)
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-itsoffset", f"{-correction_ms / 1000:.6f}", "-i", str(video),
                "-i", str(video), "-map", "1:v:0", "-map", "0:a:0",
                "-c", "copy", "-movflags", "+faststart", str(corrected),
            ], check=True)
            corrected.replace(video)
            rows, music_rows, music_skip_reason, peak_report = measure(video, timeline, assets, ffmpeg, ffprobe)
            stream_metadata = probe(video, ffprobe)

    failed = [row for row in rows if row["correlation"] <= MIN_CORRELATION or abs(row["alignmentOffsetMs"]) >= MAX_OFFSET_MS]
    if failed:
        raise RuntimeError("Exported narration alignment failed: " + json.dumps(failed, ensure_ascii=False))
    music_failed = [row for row in music_rows if row["correlation"] <= MUSIC_MIN_CORRELATION or abs(row["alignmentOffsetMs"]) >= MAX_OFFSET_MS]
    if music_failed:
        raise RuntimeError("Exported soundtrack alignment failed: " + json.dumps(music_failed, ensure_ascii=False))
    if peak_report['clippedSamplesAtOrAbove0_999']:
        raise RuntimeError('The decoded soundtrack contains clipped samples')
    report = {
        "video": str(video.relative_to(ROOT)) if video.is_relative_to(ROOT) else str(video),
        "voice": {key: manifest.get(key) for key in ("provider", "locale", "voice", "rate", "catalogVerified")},
        "alignmentLimits": {"searchRadiusMs": SEARCH_RADIUS_MS, "minimumVoiceCorrelationExclusive": MIN_CORRELATION, "minimumMusicCorrelationExclusive": MUSIC_MIN_CORRELATION, "maximumAbsoluteOffsetMsExclusive": MAX_OFFSET_MS},
        "streamMetadata": stream_metadata,
        "audioPeakAndClipping": peak_report,
        "narration": rows,
        "music": {
            "source": timeline.get("music"),
            "sourceSha256": hashlib.sha256((ROOT / "public" / timeline["music"]).read_bytes()).hexdigest()
            if timeline.get("music") and (ROOT / "public" / timeline["music"]).is_file() else None,
            "skippedReason": music_skip_reason,
            "measurements": music_rows,
        },
    }
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
