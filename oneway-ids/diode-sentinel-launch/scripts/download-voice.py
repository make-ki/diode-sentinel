from pathlib import Path
from urllib.request import urlretrieve
root=Path(__file__).resolve().parents[1]/'.media-cache/voice'
root.mkdir(parents=True,exist_ok=True)
base='https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/'
for name in ['en_US-ryan-high.onnx','en_US-ryan-high.onnx.json','MODEL_CARD']:
    dest=root/name
    if not dest.exists():
        print('Downloading '+name,flush=True)
        urlretrieve(base+name,dest)
print('Narration voice available.',flush=True)
