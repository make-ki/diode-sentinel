# Benign replay training experiment

`training/train_ml.py` can append explicitly selected benign-source flows from
a second pcap while preserving the original pcap's generator labels. Replay
traffic is never assumed wholly benign: only flows whose source address was
named with `--benign-source-ip` are admitted, and a flow that the existing
ground-truth labeler recognizes as an attack remains malicious. The replay
capture must use the same relative event-time convention as the training
capture; training uses flows before 420 seconds and reports flows at or after
420 seconds as the temporal holdout.

Example for a MESSY capture, where `10.0.0.6` is the designated benign backup
host:

```sh
source .env-ml
.venv/bin/python training/train_ml.py \
  --pcap traffic.pcap \
  --benign-replay-pcap traffic-messy.pcap \
  --benign-source-ip 10.0.0.6 \
  --output training/model_ml_messy_experiment.txt
```

The option is deliberately explicit: selecting a source IP asserts that its
otherwise-unlabelled replay flows are benign. Do not select an attack source
or a host whose replay contains unrepresented attacks. Known attacks identified
by the current generator labeler retain their malicious label. The CLI refuses
to accept source IPs without a replay pcap and refuses a replay pcap without
at least one selected source IP.

The default output is `training/model_ml_experiment.txt`, so an experiment
cannot replace the shipped `model_ml.txt` by default. Each run writes a JSON
sidecar at `<model path>.report.json`, including held-out benign false-positive
count/rate and malicious detections at the deployed probability threshold
0.95. This measures the specific temporal holdout; it is not a generalization
claim. Replay flows with times at or after the split are held out, while early
replay flows may train the model. No improvement is claimed until a run's JSON
report demonstrates it.

## Measured experiment (29 September 2026)

`ml-replay-evaluation.json` records the comparison at threshold 0.95. On the
same evaluation rows at t >= 420 s (default capture plus selected MESSY source
flows), the shipped model flags **35/541** benign flows, while the experiment
flags **2/541**. Both detect **60/75** generator-labelled malicious flows.
These rows are held out of the new experiment's fit; the old model's training
provenance does not establish that the same rows were unseen by it.

On the **entire** MESSY replay through the real pipeline, shipped vs experiment
emits 79 vs 25 `ml_flow_suspicious` alerts, of which 59 vs 4 are on designated
benign hosts. This full-capture comparison includes the experiment's training
times and is not an independent holdout result. It supersedes the handoff's
approximate 74-alert count for this freshly generated capture. Neither result
supports deployment generalisation. The shipped model remains unchanged.

Reproduce without overwriting the default capture or shipped model:

```sh
source .env-ml
.venv/bin/python - <<'PY'
import os, runpy
from core import config
config.PCAP_PATH = '/tmp/diode-messy-fixes.pcap'
os.environ['MESSY'] = '1'
runpy.run_path('gen_traffic.py', run_name='__main__')
PY
.venv/bin/python training/train_ml.py --pcap traffic.pcap \
  --benign-replay-pcap /tmp/diode-messy-fixes.pcap \
  --benign-source-ip 10.0.0.6 --benign-source-ip 10.0.0.17 \
  --benign-source-ip 10.0.0.18 --benign-source-ip 10.0.0.21 \
  --output /tmp/diode-ml-replay.txt
```

The backup event occurs before the split, so this experiment does not validate
an unseen later backup transfer. Add an independent backup scenario before
promoting this model. Keep the residual errors and the one-way limitations in
view when comparing the aggregate false-positive rates.
