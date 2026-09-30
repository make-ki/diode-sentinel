# demo_video

Two ways to put Diode Sentinel on screen. Both render the real code paths —
nothing here is a mockup of the dashboard.

| Artefact | Source | What it is |
|---|---|---|
| `out/dashboard_tour.mp4` | `record_dashboard.py` | The live dashboard **being operated**: a synthetic cursor travels, filters are clicked, an alert row opens its evidence. |
| `out/diode-sentinel-demo.mp4` | `build_demo_video.py` | The assembled cut: title card → dashboard → terminal contract gate → proof → end card. |

## Recording the dashboard tour

```sh
demo_video/record_dashboard.sh                  # -> out/dashboard_tour.{webm,mp4}
demo_video/record_dashboard.sh --no-mp4
demo_video/record_dashboard.sh --alerts .regression/alerts_rules.reference.jsonl
```

The script starts `dashboard.py` on an unused port (default 8701, deliberately
not 8600), waits for the first `/api/alerts` response so the recording never
captures an empty queue, then drives the page with Playwright's screencast API.

### Where the mouse comes from

There is no mouse. The browser is headless, so there is no pointer to capture.
Playwright's `show_actions(cursor="pointer")` injects an overlay (`<x-pw-glass>`)
and draws a pointer that animates from one action point to the next — the same
mechanism behind the "AI agent uses a browser" videos. Verified two ways:
the decoration node exists in the DOM, and diffing a recording made with
`cursor="pointer"` against one made with `cursor="none"` shows a small glyph
appearing at the click coordinates.

`glide()` in the recorder adds an explicit stepped `mouse.move` to each target
first. That is what gives the pointer readable travel between action points
instead of it teleporting.

### Toolchain and the NixOS traps

Everything lives in the dev shell (`flake.nix`), not in `pyproject.toml`, so
the sensor's dependency contract stays pure Python:

- `demo-python` — an interpreter with `playwright` importable. The PyPI wheel is
  **not** used: it ships a prebuilt node driver that NixOS's non-FHS loader
  cannot exec, and nixpkgs patches its build onto nix's node.
- `demo-python`/`demo-playwright` exist so `playwrightEnv` never lands on `PATH`
  directly — that would shadow `python` with an interpreter that has playwright
  but no numpy/scapy.
- `PLAYWRIGHT_BROWSERS_PATH` points at a derivation containing one file, a
  symlink from playwright's expected `ffmpeg-1011/ffmpeg-linux` to the nixpkgs
  ffmpeg. Downloading playwright's own prebuilt ffmpeg is the fragile step on
  NixOS, so we don't. If a Playwright bump makes recording complain about a
  missing ffmpeg, read the expected directory name out of the error and update
  `playwrightRuntime` in `flake.nix`.
- `PW_CHROMIUM` pins the browser so the recording doesn't depend on whichever
  chromium the host prefers.
- `demo-playwright codegen http://127.0.0.1:8701` opens the point-and-click
  selector picker if the dashboard's markup changes.

## Honesty constraints (AGENTS.md / HANDOFF.md)

The dashboard itself carries the disclaimer, and the tour must not contradict
it. Specifically, do not add a chapter or caption that:

- claims **zero false positives** — the MESSY variant emits a critical
  `data_exfiltration` false positive on a benign host;
- presents the `--ml` tier as a robust primary detector — it is quorum-gated
  because it does not generalise to benign traffic shapes it wasn't trained on;
- promises **MITRE technique IDs** — the alert schema has no such field;
- implies the one-way feed can confirm delivery, server response or outcome;
- presents the ~2,000× real-time figure as a headline — the capture is sparse.

Chapter text should restate wording the dashboard already uses. Counts are
alert records, not incidents, and the capture is a synthetic replay.
