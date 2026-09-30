#!/usr/bin/env python3
"""Build a slower, speech-led timeline and a crossfaded First Light music bed."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import shutil
import wave

import numpy as np
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = shutil.which('ffmpeg') or '/nix/store/nm4ih3jrw0zma6qxhk5s2ks2r0gppzfl-ffmpeg-9.0.1-bin/bin/ffmpeg'
FPS = 30


def validate(script, voices, capture):
    """Fail a production build on stale speech, missing clips or changed records."""
    for scene in script:
        voice = voices.get(scene['id'])
        if not voice or voice['text'] != scene['text'] or voice.get('locale') != 'en-IN':
            raise ValueError(f"Missing, stale or non-Indian narration: {scene['id']}")
        audio = ROOT / 'public' / voice['file']
        if not audio.exists() or hashlib.sha256(audio.read_bytes()).hexdigest() != voice['audioSha256']:
            raise ValueError(f"Narration asset hash mismatch: {scene['id']}")
        if scene['clip']:
            name = scene['clip']
            if name not in capture['clips'] or not (ROOT / 'public/explainer-captures' / f'{name}.mp4').exists():
                raise ValueError(f'Missing recorded software: {name}')
    for name, artifact in capture['artifact_hashes'].items():
        path = ROOT / 'public/explainer-captures' / name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
            raise ValueError(f'Capture provenance mismatch: {name}')
    records = capture['selected_records']
    rolling = records['rolling-scan']['record']['evidence']
    if rolling['rolling_distinct_dst_port_pairs'] != 20 or rolling['rolling_window_s'] != 60:
        raise ValueError('Rolling illustration disagrees with selected record')
    history = records['source-context']['record']['evidence']
    if not history['source_novel_within_lookback'] or history['fleet_destination_novel']:
        raise ValueError('Source-relative illustration disagrees with selected record')
    if history['source_history_coverage_now'] != 'complete_within_lookback':
        raise ValueError('Selected history record does not have the illustrated coverage')
    encrypted = records['encrypted-metadata']['record']['evidence']
    if encrypted['model'] != 'xgboost' or len(encrypted['metadata_features']) != 10:
        raise ValueError('Selected encrypted-model record is not the named metadata vector')
    print('Verified all Indian voice hashes, fresh capture hashes and illustration/record matches.')


def read_wave(path):
    with wave.open(str(path), 'rb') as stream:
        rate, channels = stream.getframerate(), stream.getnchannels()
        if stream.getsampwidth() != 2:
            raise ValueError('Expected 16-bit PCM for soundtrack editing')
        data = np.frombuffer(stream.readframes(stream.getnframes()), '<i2')
    return data.reshape(-1, channels).astype(np.float32) / 32768, rate


def write_wave(path, data, rate):
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(data.shape[1])
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes((np.clip(data, -.999, .999) * 32767).astype('<i2').tobytes())


def accents(data, rate):
    # Analyze the actual edited bed, rather than assuming a BPM grid.
    mono = data.mean(axis=1)[::4]
    reduced_rate = rate / 4
    size, hop = 1024, 256
    blocks = np.lib.stride_tricks.sliding_window_view(mono, size)[::hop]
    spectra = np.log1p(np.abs(np.fft.rfft(blocks * np.hanning(size), axis=1)))
    flux = np.maximum(0, np.diff(spectra, axis=0)).sum(axis=1)
    flux /= max(float(flux.max()), 1e-9)
    peaks, _ = find_peaks(flux, distance=round(.32 * reduced_rate / hop),
                          prominence=.04, height=.075)
    return [{'seconds': round(float((n + 1) * hop / reduced_rate), 4),
             'strength': round(float(flux[n]), 4)} for n in peaks]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true', help='Validate all production assets before preparation')
    args = parser.parse_args()
    script = json.loads((ROOT / 'explainer-script.json').read_text())
    voice_path = ROOT / 'explainer-voice.json'
    if voice_path.exists():
        voice_source = json.loads(voice_path.read_text())
        voice_source = voice_source.get('segments', []) if isinstance(voice_source, dict) else voice_source
    else:
        voice_source = []
    voices = {entry['id']: entry for entry in voice_source}
    capture_path = ROOT / 'public/explainer-captures/capture-manifest.json'
    capture = json.loads(capture_path.read_text()) if capture_path.exists() else {'clips': {}, 'viewport': {'width': 1600, 'height': 1000}}
    if args.strict:
        validate(script, voices, capture)
    # Allow each mouse workflow to finish at its recorded speed, including the
    # download and the retained-history fields near the end of those recordings.
    expected = sum(max(s['minSeconds'], voices.get(s['id'], {}).get('speechSeconds', 0) + 4)
                   + capture['clips'].get(s.get('clip'), {}).get('recordedSeconds', 0) * .43
                   for s in script) + 25
    source = next((ROOT / 'public' / name for name in ('music.wav', 'music-master.wav') if (ROOT / 'public' / name).exists()), None)
    source_name = 'First Light - naneki.mp4'
    if source is None and (ROOT / 'public/music.mp3').exists():
        source = ROOT / '.media-cache/explainer-music-input.wav'
        source.parent.mkdir(exist_ok=True)
        subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y',
                        '-i', str(ROOT / 'public/music.mp3'), '-ar', '48000', '-ac', '2',
                        '-c:a', 'pcm_s16le', str(source)], check=True)
        source_name = 'public/music.mp3'
    onsets, music, music_edit = [], None, None
    if source:
        original, rate = read_wave(source)
        # Preserve the opening once, then repeat a musical body. Equal-power
        # overlap preserves tempo and avoids an abrupt restart or silence.
        old_beats = json.loads((ROOT / 'beats.json').read_text()) if (ROOT / 'beats.json').exists() else {}
        original_onsets = old_beats.get('onsets', []) if source_name != 'public/music.mp3' else accents(original, rate)
        track_seconds = len(original) / rate
        body_start = min(original_onsets, key=lambda p: abs(p['seconds'] - 12.1))['seconds'] if original_onsets else min(12.1, track_seconds * .2)
        body_end = min(original_onsets, key=lambda p: abs(p['seconds'] - 46.9))['seconds'] if original_onsets else min(46.9, track_seconds)
        if body_end <= body_start + 1:
            body_start, body_end = 0, track_seconds
        overlap_seconds = min(2.4, (body_end - body_start) / 4)
        overlap = round(overlap_seconds * rate)
        bed = original[:round(body_end * rate)].copy()
        body = original[round(body_start * rate):round(body_end * rate)]
        phase = np.linspace(0, np.pi / 2, overlap, dtype=np.float32)[:, None]
        joins = []
        while len(bed) / rate < expected:
            join = len(bed) - overlap
            joins.append(round(join / rate, 4))
            blended = bed[-overlap:] * np.cos(phase) + body[:overlap] * np.sin(phase)
            bed = np.concatenate((bed[:-overlap], blended, body[overlap:]))
        bed = bed[:math.ceil(expected * rate)]
        # Overlap can add energy even with equal-power weights. Lower the
        # whole bed before PCM conversion, preserving dynamics without clipping.
        bed_peak = float(np.abs(bed).max())
        pre_pcm_gain = min(1.0, .95 / max(bed_peak, 1e-9))
        bed *= pre_pcm_gain
        onsets = accents(bed, rate)
        raw = ROOT / '.media-cache/explainer-music-bed.wav'
        raw.parent.mkdir(exist_ok=True)
        write_wave(raw, bed, rate)
        music_edit = {'source': source_name, 'sourceWavSha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'tempoChanged': False,
                      'bodyStartSeconds': body_start, 'bodyEndSeconds': body_end,
                      'crossfadeSeconds': overlap_seconds, 'joinsSeconds': joins,
                      'prePCMLinearGain': pre_pcm_gain,
                      'method': 'Equal-power crossfades, followed by measured spectral-flux accents'}
        music = 'explainer-music.wav'

    def next_accent(frame):
        suitable = [o for o in onsets if frame / FPS <= o['seconds'] <= frame / FPS + .8]
        return round(max(suitable, key=lambda o: o['strength'])['seconds'] * FPS) if suitable else frame

    scenes, narration, cuts = [], [], []
    start = 0
    for entry in script:
        segment = voices.get(entry['id'])
        speech = segment.get('speechSeconds', segment.get('durationSeconds', 0)) if segment else 0
        length = math.ceil(max(entry['minSeconds'], speech + 4) * FPS)
        graphic_reveal = next_accent(start + 25) - start
        ui_reveal = next_accent(start + math.floor(length * .43)) - start
        clip = entry.get('clip')
        file_exists = clip and (ROOT / 'public/explainer-captures' / f'{clip}.mp4').exists()
        if file_exists:
            recorded_frames = math.ceil(capture['clips'][clip]['recordedSeconds'] * FPS)
            length = max(length, ui_reveal + recorded_frames + 24)
        end = next_accent(start + length)
        scenes.append({**entry, 'start': start, 'end': end,
                       'graphicReveal': graphic_reveal, 'uiReveal': ui_reveal,
                       'clipAvailable': bool(file_exists)})
        cuts.append({'id': entry['id'], 'seconds': round(start / FPS, 4), 'frame': start,
                     'graphicRevealFrame': start + graphic_reveal, 'uiRevealFrame': start + ui_reveal})
        if segment:
            narration.append({**segment, 'startFrame': start + 60,
                              'durationFrames': math.ceil(speech * FPS) + 1})
        start = end
    if music:
        subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(raw),
                        '-t', f'{start / FPS:.6f}', '-af', 'loudnorm=I=-22:TP=-2:LRA=9,aresample=48000',
                        '-ar', '48000', '-ac', '2', str(ROOT / 'public' / music)], check=True)
    beats = {'fps': FPS, 'durationFrames': start, 'durationSeconds': round(start / FPS, 4),
             'source': music_edit, 'onsets': onsets, 'cuts': cuts,
             'pacing': 'Speech remains at provider rate; at least two seconds before and after speech; UI footage at 1x.'}
    (ROOT / 'explainer-beats.json').write_text(json.dumps(beats, indent=2) + '\n')
    data = {'fps': FPS, 'width': 1920, 'height': 1080, 'duration': start, 'scenes': scenes,
            'narration': narration, 'music': music, 'capture': capture,
            'team': 'samarags', 'brand': 'Diode Sentinel',
            'scriptSha256': hashlib.sha256((ROOT / 'explainer-script.json').read_bytes()).hexdigest()}
    (ROOT / 'src/explainer/data.generated.ts').write_text('export const explainer = ' + json.dumps(data, indent=2) + ' as const;\n')
    print(f'Prepared {len(scenes)} scenes, {len(narration)} Indian voice segments, {start / FPS:.2f} seconds.')


if __name__ == '__main__':
    main()
