# Cross-dataset DGA benchmark — SUPERSEDED

**Status: superseded. This note describes the pre-full-run state of play; every
number in it came from the 20,000-label `--quick` subsample and is not the
record. Read [`BENCH-DGA.md`](BENCH-DGA.md) instead — it is written from the
complete corpus, and `dga_bench.json` is the machine-readable original.**

This file is kept as the record of how the full run was scoped: what the quick
run estimated, what the full corpus confirmed, and what it revised. The
estimates below are deliberately **not** corrected in place — the deltas are
the point.

## What the full run changed

| Quantity | `--quick` estimate (20k) | Full corpus (record) |
|---|---|---|
| benign per-string FP @0.5 | 0.163 | **0.165** |
| benign per-string FP @0.9 | — | 0.117 |
| rule FP (benign) | 0.018 | **0.0169** |
| conficker — rule → CNN TPR | 0.023 → 0.886 | **0.019 → 0.886** |
| pushdo — rule → CNN TPR | 0.000 → 0.451 | **0.000 → 0.446** |
| benign alerts/h at shipped k | 16.9 (k=2) | **17.33 (k=2) → 0.46 (k=4, shipped)** |
| families still hit at k=4 | 6/8 | **7/8** |
| pushdo, queries to 1st alert at k=4 | 321 | **164** |
| mixed-host precision (5% DGA) | 0.162 | **0.171** |
| benign host, 1 qps | 20,000 queries / 5.6 h | **1,000,000 queries / 277.8 h** |

The shapes survived; the digits did not, and two of them moved a conclusion:
the quick run's 6/8 at k=4 became 7/8 at scale, and pushdo's cost at k=4 fell
from 321 queries to 164. Both made the shipped quorum *safer*, not riskier —
but a 20k-sample guess would have understated it in both directions. That is
the argument for running the whole corpus rather than shipping the subsample.

The full run also surfaced a bug the quick run structurally could not (see
`BENCH-DGA.md` §Result 4): feeding the detector a *sorted* benign stream fired
**9.92 alerts/h** from the same corpus, quorum and detector that report
**0.432/h** when shuffled — order is load-bearing for any quorum counter, and
`--quick` had been shuffling all along, hiding it.

## What was still open here, and its status

Everything in the original "Remaining work" list is done:

- [x] Full benchmark run, `dga_bench.json` saved (336 s wall, deterministic given
      the recorded corpus digests)
- [x] Quorum decision re-confirmed at full scale — `DGA_CNN_MIN_STREAK = 4`
      stands, sweep recorded in the `config.py` comment
- [x] `test_bench_dga.py` written — 31 checks, fixture corpus offline (network
      access asserted away), family attribution, uniform-vs-prefix sampling,
      the ordering-artifact regression, quorum-sweep math
- [x] README / PRESENTATION.md / DECK-VS-CODE.md updated to the external-corpus
      numbers

Still open, and honestly so (carried forward into `BENCH-DGA.md`):
stream scenarios are driven through the detector at 1 qps rather than replayed
through pcap ingest, and the benign corpus is Alexa-2017, which under-
represents auto-generated CDN hostnames — real-world FP pressure is likely
**higher** than measured, not lower.

## Reproducing it

```bash
nix develop                       # NixOS: uv + libstdc++ (flake.lock pins nixpkgs)
uv sync                           # exact pinned interpreter deps from uv.lock
uv run python bench_dga.py        # full corpus, ~6 min -> dga_bench.json
uv run python bench_dga.py --quick    # 20k uniform subsample, ~40 s
uv run python test_bench_dga.py   # 31 offline harness checks
```
