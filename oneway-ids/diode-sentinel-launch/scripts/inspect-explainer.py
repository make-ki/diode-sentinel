#!/usr/bin/env python3
"""Inspect scene samples from the actual exported MP4, with stream checks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def executable(name):
    package = 'ffmpeg' if name == 'ffprobe' else name
    return shutil.which(name) or str(next(Path('/nix/store').glob(f'*-{package}-*-bin/bin/{name}')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', nargs='?', default='out/diode-sentinel-explainer.mp4')
    args = parser.parse_args()
    video = (ROOT / args.video).resolve()
    beats = json.loads((ROOT / 'explainer-beats.json').read_text())
    metadata = json.loads(subprocess.check_output([
        executable('ffprobe'), '-v', 'error', '-show_format', '-show_streams',
        '-of', 'json', str(video),
    ]))
    picture = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    if (picture['width'], picture['height'], picture['avg_frame_rate']) != (1920, 1080, '30/1'):
        raise ValueError('The final export is not 1920×1080 at 30 fps')
    if int(picture['nb_frames']) != beats['durationFrames']:
        raise ValueError('Exported picture length differs from the approved timeline')
    output = ROOT / 'out/explainer-review/export'
    output.mkdir(parents=True, exist_ok=True)
    shots = []
    for index, cut in enumerate(beats['cuts']):
        end = beats['cuts'][index + 1]['frame'] if index + 1 < len(beats['cuts']) else beats['durationFrames']
        frames = [('graphic', min(end - 1, cut['graphicRevealFrame'] + 110))]
        if cut['id'] not in ('intro', 'closing'):
            frames += [('software', min(end - 1, cut['uiRevealFrame'] + 250)), ('completion', end - 50)]
        for kind, frame in frames:
            path = output / f'{cut["id"]}-{kind}.png'
            subprocess.run([
                executable('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y',
                '-ss', f'{frame / beats["fps"]:.9f}', '-i', str(video),
                '-frames:v', '1', str(path),
            ], check=True)
            shots.append({'scene': cut['id'], 'kind': kind, 'frame': frame, 'file': str(path.relative_to(ROOT))})
    report = {'video': str(video.relative_to(ROOT)), 'videoSha256': hashlib.sha256(video.read_bytes()).hexdigest(),
              'streamMetadata': metadata, 'shots': shots}
    (output / 'frames.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Checked 1080p/30, {beats["durationFrames"]} frames; extracted {len(shots)} actual export frames.')


if __name__ == '__main__':
    main()
