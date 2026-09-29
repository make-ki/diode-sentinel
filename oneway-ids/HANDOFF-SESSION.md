# Handoff — Diode Sentinel, session boundary

> **⚠ SUPERSEDED — this is a session log from the Zeek investigation, kept for
> the decision record. Almost everything in "Open work" below is DONE.**
> Read `AGENTS.md` for the current state instead. Status of the five items as
> of 29 Sep 2026:
> 1. Regression references — **done**, byte-identical (46 rules / 68 ML).
> 2. Observability contract — **done**, `core/observability.py` + an enforcing
>    `tests/test_contract.py`; it is the deck's headline.
> 3. qtype / DNS tunnelling — **done**, `_tunnel_check` fires 4 alerts on the
>    shipped capture.
> 4. Deck rewrite — **done**, `build_deck.py` emits 17 honest slides.
> 5. IoT-23 validation — **used**, slide 14 of the rebuilt deck.
>
> The one thing below that remains a live constraint is the last bullet:
> `dpkt.pcap.Writer` produces pcaps Zeek cannot parse.

Read `AGENTS.md` and `ZEEK-ONEWAY-FINDINGS.md` first. This file only carries
what changed this session and what is next.

## What was decided

The user's instruction was to **shift the entire architecture to Zeek and
Suricata** and to refactor the codebase. That decision is only partly
supported by measurement, and I want the next session to know exactly which
part is real:

- **Zeek as the Tier-1 protocol dissection layer: justified.** It parses TLS
  ClientHello and QUIC correctly on a strictly one-way feed, which removes
  the need for the hand-rolled `tls_meta.py` / `quic_meta.py`.
- **"We made Zeek work one-way where nobody else could": NOT justified.** My
  own repro disproved it. Vanilla Zeek works once the traffic is realistic.
  The failure was in `gen_traffic.py`. `ZEEK-ONEWAY-FINDINGS.md` has the
  ablation table proving `tcp_attempt_delay` is not load-bearing.
- **The defensible contribution is the observability contract**, not a Zeek
  config trick. That is what should be built next.

## What changed (committed as 912533b)

- `gen_traffic.py` — four TCP-realism fixes. This is the substantive change:
  it is why Zeek went from zero TLS analysis to 527 parsed records.
- `AGENTS.md` — new, follows the agents.md convention.
- `.gitignore` — was one line (`.bench/`); now covers outputs, venv, pycache,
  `.loop_*`, model artifacts.
- `.env.example` — new.
- `ZEEK-ONEWAY-FINDINGS.md` — new, records measurements and negative results.

## State on disk (not committed)

- `traffic.pcap` — regenerated, 12,295 packets. Untracked (gitignored).
- `.regression/alerts_rules.reference.jsonl` and `alerts_ml.reference.jsonl`
  — **STALE.** The generator change altered packet counts. `run.py` still
  emits 33 alerts, but the reference files must be regenerated before the
  byte-identical reproducibility claim is repeated.
- `alerts.jsonl` / `nids_state.json` / `run_stats.json` — gitignored outputs.

## Open work, priority order

1. **Regenerate the regression references** and confirm they are
   byte-identical. This is the project's reproducibility claim and it is
   currently unverified.
2. **Build the observability contract** as a real artifact: for each
   PS-requested feature, a row stating `observable | impossible | substituted`,
   with the substitute's formula. Mark JA3S, NXDOMAIN ratio and in/out byte
   ratio as unsatisfiable. Add a CI test that fails if any detector reads a
   bidirectional field. This is the novelty claim that survives scrutiny.
3. **Implement qtype parsing or remove the claim.** `PS-26145.md` asks for
   DNS tunnelling; `dashboard.py:42` labels the class as though it exists.
   There is no `qtype` parsing anywhere in the code.
4. **Rewrite the deck.** The deadline is 30 Sep 2026. The current deck
   describes Kafka/Flink/ClickHouse/React/ONNX — none of which exist. Lead
   with the observability contract and the IoT-23 validation instead.
5. **IoT-23 validation** (`HANDOFF.md` at the repo root) has real per-host
   numbers including an honest miss and a genuine one-way FP. Nothing in the
   deck uses it. It is the strongest unclaimed asset in the repo.

## Hard constraints for the next session

- Do not claim "zero false positives". The MESSY run emits a critical
  `data_exfiltration` FP at 0.95 on the benign cloud-backup host.
- Do not ship `--models-567` as a headline. `models567/eval.json` shows 2 of
  6 models at 0.000 recall and 2 never testable.
- Do not use `dpkt.pcap.Writer` to build pcaps for Zeek. A byte-identical
  round-trip through it produced zero flows in Zeek. Use `tshark`/`editcap`.
- Do not re-investigate the `tcp_attempt_delay` hypothesis. It is disproven
  and recorded.
