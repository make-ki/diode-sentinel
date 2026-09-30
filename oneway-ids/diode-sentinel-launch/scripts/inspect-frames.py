#!/usr/bin/env python3
"""Extract representative product-demo frames and a contact sheet."""
from pathlib import Path
import argparse, subprocess, shutil, glob, math
ap=argparse.ArgumentParser();ap.add_argument('video',nargs='?',default='out/product-draft.mp4');ap.add_argument('--ffmpeg',default=shutil.which('ffmpeg') or next(iter(glob.glob('/nix/store/*-ffmpeg-*-bin/bin/ffmpeg')), 'ffmpeg'));args=ap.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'out/review';out.mkdir(parents=True,exist_ok=True)
frames=[('intro',2),('live',8),('alert-opening',14.4),('evidence',17),('source-filter',21.8),('correlation',25.7),('dga-model',28.8),('encrypted-model',32.6),('scan-model',36.6),('exfil-model',40),('passive',44.8),('closing',50.2)]
for label,sec in frames:
    subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-ss',str(sec),'-i',str(root/args.video),'-frames:v','1',str(out/f'{label}.png')],check=True)
print(f'Extracted {len(frames)} review frames from {args.video}.')
try:
    from PIL import Image,ImageDraw
    sheet=Image.new('RGB',(1600,math.ceil(len(frames)/2)*480),'#101014');draw=ImageDraw.Draw(sheet)
    for i,(label,sec) in enumerate(frames):
        im=Image.open(out/f'{label}.png').convert('RGB');im.thumbnail((800,450));x=(i%2)*800;y=(i//2)*480;sheet.paste(im,(x,y+30));draw.text((x+12,y+8),f'{label} / {sec:.1f}s',fill='white')
    sheet.save(out/'contact-sheet.jpg',quality=94)
except ImportError:
    print('Pillow absent: individual review frames are available.')
