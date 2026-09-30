#!/usr/bin/env python3
"""Measure narration alignment in the exported film, not just source timings.

Requires numpy/scipy from the sensor's existing virtual environment. Video
production only: these imports add nothing to the sensor runtime. Use --align
to compensate a consistent encoder-padding offset without re-encoding.
"""
import argparse,json,wave,subprocess,shutil,tempfile,glob
from pathlib import Path
import numpy as np
from scipy.signal import correlate
p=argparse.ArgumentParser();p.add_argument('video',nargs='?',default='out/diode-sentinel-product-demo.mp4');p.add_argument('--align',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parents[1];video=(root/args.video).resolve()
ffmpeg=shutil.which('ffmpeg') or next(iter(glob.glob('/nix/store/*-ffmpeg-*-bin/bin/ffmpeg')),'ffmpeg')
def samples(path):
    with wave.open(str(path)) as w:
        if w.getsampwidth()!=2:raise ValueError('Expected PCM16 input')
        x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768
        return x.reshape(-1,w.getnchannels()).mean(axis=1),w.getframerate()
def measure():
    with tempfile.TemporaryDirectory(prefix='diode-audio-qc-') as temp:
        decoded=Path(temp)/'mix.wav'
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(video),'-vn','-ac','1','-ar','48000',str(decoded)],check=True)
        mix,rate=samples(decoded);rows=[]
        for n in json.loads((root/'narration.json').read_text()):
            voice,sr=samples(root/'public'/n['file']);assert sr==rate
            expected=round(n['startFrame']/30*rate);left=max(0,expected-8000)
            window=mix[left:expected+len(voice)+8000]
            dots=correlate(window,voice,mode='valid',method='fft');best=int(np.argmax(dots))
            v=window[best:best+len(voice)]
            match=float(np.dot(voice,v)/(np.linalg.norm(voice)*np.linalg.norm(v)))
            rows.append({'scene':n['id'],'plannedStartSeconds':round(expected/rate,3),'alignmentOffsetMs':round((left+best-expected)/rate*1000,2),'correlationWithRenderedAudio':round(match,4)})
    return rows
rows=measure()
if args.align:
    offsets=[r['alignmentOffsetMs'] for r in rows]
    offset=float(np.median(offsets))
    if min(r['correlationWithRenderedAudio'] for r in rows)<.9 or max(offsets)-min(offsets)>2:
        raise RuntimeError('Audio offset is not consistent enough for an automatic correction')
    if abs(offset)>1:
        aligned=video.with_name(video.stem+'-aligned.mp4')
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-itsoffset',str(-offset/1000),'-i',str(video),'-i',str(video),'-map','1:v:0','-map','0:a:0','-c','copy','-movflags','+faststart',str(aligned)],check=True)
        aligned.replace(video);print(f'Corrected {offset:.2f}ms audio offset without re-encoding.')
        rows=measure()
for r in rows:
    if r['correlationWithRenderedAudio']<.9 or abs(r['alignmentOffsetMs'])>2:
        raise RuntimeError(f'Exported narration failed timing/match check: {r}')
(root/'out/narration-sync-check.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
