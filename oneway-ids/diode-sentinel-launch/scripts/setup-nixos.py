#!/usr/bin/env python3
"""Retarget Remotion's npm video binaries to this NixOS host's ELF loader."""
from pathlib import Path
import glob, re, shutil, subprocess
root=Path(__file__).resolve().parents[1]
if not Path('/etc/NIXOS').exists():
    print('Non-NixOS host: no binary patch needed.')
    raise SystemExit(0)
patch=shutil.which('patchelf') or sorted(glob.glob('/nix/store/*-patchelf-*/bin/patchelf'))[0]
node=shutil.which('node')
elf=subprocess.check_output(['readelf','-l',node],text=True)
loader=re.search(r'interpreter: (.*?)\]',elf).group(1)
runtime=[str(Path(loader).parent),*glob.glob('/nix/store/*-gcc-*-libgcc/lib'),*glob.glob('/nix/store/*-gcc-*-lib/lib'),*glob.glob('/nix/store/*-zlib-*/lib')]
rpath='$ORIGIN:'+':'.join(runtime)
folder=root/'node_modules/@remotion/compositor-linux-x64-gnu'
for file in folder.iterdir():
    if file.name in ('ffmpeg','ffprobe','remotion'):
        subprocess.run([patch,'--set-interpreter',loader,str(file)],check=True)
    elif file.suffix!='.so':
        continue
    subprocess.run([patch,'--force-rpath','--set-rpath',rpath,str(file)],check=True)
print('Patched Remotion compositor / FFmpeg for NixOS.')
