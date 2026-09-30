#!/usr/bin/env python3
"""Generate timed offline narration segments, with room for music between lines."""
from pathlib import Path
import json, subprocess, wave
root=Path(__file__).resolve().parents[1]
PIPER='/nix/store/p90w17vwskwk4nv72bxphq6l8bimj57b-piper-tts-1.8.0/bin/piper'
FFMPEG='/nix/store/nm4ih3jrw0zma6qxhk5s2ks2r0gppzfl-ffmpeg-9.0.1-bin/bin/ffmpeg'
voice=root/'.media-cache/voice/en_US-ryan-high.onnx'
beats=json.loads((root/'beats.json').read_text());cutframes=[p['frame'] for p in beats['cuts']]
lines=[
('intro','Diode Sentinel. Traffic, turned into evidence.'),
('live','Watch packets arrive, counters update, and security alerts take shape. All in one operator view.'),
('evidence','Open an alert to see its severity, score, and the exact signal behind it.'),
('sources','Follow each source. Correlate signals across detectors. Light G B M and Isolation Forest add supporting evidence.'),
('dns','A character C N N examines domain names.'),
('encrypted','Sequence C N N and X G Boost examine encrypted sessions.'),
('scan','Random Forest identifies scanning patterns.'),
('exfil','X G Boost examines transfers and destination novelty.'),
('passive','Passive monitoring. Built for the receive side of a hardware data diode.'),
('closing','Diode Sentinel. Built by Sama rags.'),
]
manifest=[]
for i,(name,text) in enumerate(lines):
    raw=root/'.media-cache'/f'voice-{name}.wav';final=root/'public/narration'/f'{name}.wav'
    start=cutframes[i]+8;end=cutframes[i+1]-6;available=(end-start)/30
    subprocess.run([PIPER,'-m',str(voice),'-f',str(raw),'--length-scale','0.96','--noise-scale','0.35','--noise-w-scale','0.5','--sentence-silence','0.1'],input=text,text=True,check=True,stdout=subprocess.DEVNULL)
    with wave.open(str(raw)) as w:duration=w.getnframes()/w.getframerate()
    # A small time adjustment fits short model labels to their music-aligned
    # slots. Longer sentences retain their natural pauses; nothing is clipped.
    speed=max(1,duration/available)
    if speed>1.35:raise RuntimeError(f'{name}: narration would need excessive speed ({speed:.2f})')
    filt=f'atempo={speed:.5f},highpass=f=75,lowpass=f=14000,loudnorm=I=-16:TP=-1.5:LRA=7,afade=t=in:d=0.025,afade=t=out:st={max(0,duration/speed-.05):.4f}:d=0.05'
    subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(raw),'-af',filt,'-ar','48000','-ac','1',str(final)],check=True)
    with wave.open(str(final)) as w:actual=w.getnframes()/w.getframerate()
    manifest.append({'id':name,'text':text,'startFrame':start,'durationFrames':round(actual*30)+1,'seconds':round(actual,3),'speedAdjustment':round(speed,3),'file':f'narration/{name}.wav'})
    print(f'{name}: {actual:.2f}s / {available:.2f}s slot',flush=True)
(root/'narration.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'src/narration.generated.ts').write_text('export const narration = '+json.dumps(manifest,indent=2)+' as const;\n')
