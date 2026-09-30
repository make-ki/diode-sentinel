"""Detect spectral-onset accents in the user-supplied track, not an assumed BPM."""
from pathlib import Path
import json, wave
import numpy as np
root=Path(__file__).resolve().parents[1]
with wave.open(str(root/'public/music.wav')) as w:
    sr=w.getframerate();audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,w.getnchannels()).mean(axis=1)/32768
# Downsample for timing analysis only. Original stereo track remains intact.
audio=audio[::4];sr=sr/4
n=1024;hop=256
frames=np.lib.stride_tricks.sliding_window_view(audio,n)[::hop]
spec=np.abs(np.fft.rfft(frames*np.hanning(n),axis=1))
flux=np.maximum(0,np.diff(np.log1p(spec),axis=0)).sum(axis=1)
flux=np.convolve(flux,np.ones(3)/3,mode='same')
times=(np.arange(len(flux))*hop+n/2)/sr
peaks=[i for i in range(2,len(flux)-2) if flux[i]>=max(flux[i-2:i+3])]
# Choose substantial accents with a refractory interval; this is an onset map,
# not a claim that every peak is a beat or that the track has constant tempo.
rank=sorted(peaks,key=lambda i:flux[i],reverse=True);chosen=[]
for i in rank:
    if all(abs(times[i]-times[j])>.38 for j in chosen):chosen.append(i)
    if len(chosen)>=90:break
onsets=sorted([{'seconds':round(float(times[i]),4),'strength':round(float(flux[i]/max(flux)),4)} for i in chosen],key=lambda p:p['seconds'])
targets=[0,4,12,20,27,30.75,34.5,38.25,42,47,52]
cuts=[]
for target in targets:
    nearby=[p for p in onsets if abs(p['seconds']-target)<=.65]
    peak=min(nearby,key=lambda p:abs(p['seconds']-target)/(.2+p['strength'])) if nearby else {'seconds':target,'strength':0}
    sec=target if target in (0,52) else peak['seconds'];frame=round(sec*30)
    cuts.append({'target':target,'seconds':round(frame/30,4),'frame':frame,'accentStrength':peak['strength']})
data={'source':'First Light - naneki.mp4','method':'Positive log spectral flux with local peak selection; cut points snapped to nearby measured accents.','durationSeconds':round(len(audio)/sr,5),'fps':30,'onsets':onsets,'cuts':cuts}
(root/'beats.json').write_text(json.dumps(data,indent=2)+'\n')
print('Music-aligned cut frames:',[p['frame'] for p in cuts],flush=True)
