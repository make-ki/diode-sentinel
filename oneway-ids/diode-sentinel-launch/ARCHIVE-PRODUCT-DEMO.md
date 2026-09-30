> Historical documentation for the earlier 52-second film. Current production: README.md.

# Diode Sentinel product demo

52 seconds · 1920×1080 · 30 fps · narrated H.264/AAC MP4.

Final film: `out/diode-sentinel-product-demo.mp4`. This revision follows the
approved product walkthrough in `../VIDEO-BRIEF.md` §9: actual software,
visible cursor movement, synthetic traffic arriving, an opened alert, source
filtering, correlation, named model roles, and passive monitoring. Team:
**samarags**. The original contract-first launch film remains in `out/`.

The next-film proposals were updated after the detector-quality pass:
[B — The packet laboratory, and C — Inside the engine](concepts/VIDEO-CONCEPTS.md).
They cover rolling scan context, source-relative history, model eligibility,
named inputs and evidence export. Open [the interactive storyboard](concepts/pipeline-lab.html)
locally to review the concepts. These are proposals; the rendered 52-second
film above has not been replaced. Their verified claims are in
`../VIDEO-BRIEF.md` §10, including the Indian English narration requirement.

## Preview and render

```sh
npm ci
npx remotion studio src/index.ts
npx remotion render src/index.ts DiodeSentinelProductDemo out/diode-sentinel-product-demo.mp4
```

The CLI refreshes the timeline, capture provenance and optional-audio manifest
automatically. Keep `beats.json`, `narration.json` and `public/captures/` with the
source. Google Fonts load Inter and JetBrains Mono through
`@remotion/google-fonts`; the first render requires network access.

On this NixOS machine:

```sh
python3 scripts/setup-nixos.py # once after npm ci, patches native tool loaders
npm run render
```

The render script uses installed Chromium at
`/home/stark/.nix-profile/bin/chromium` and concurrency 2. On other machines,
use the generic `npx remotion render` command above.

## Real software footage

`scripts/capture-product.py` generates a fresh seeded synthetic pcap and runs
the existing FIFO live pipeline with rules, DGA CNN, LightGBM and the
models-567 manifest. Playwright operates the real dashboard at 1600×1000;
only a cursor overlay is added to the recording. No production interface is
used. WebM recordings are converted to MP4 with three seconds of still tail.
The camera enlarges and pans across these recordings; displayed data is not
recreated or replaced. `public/captures/capture-manifest.json` preserves action
selectors, focus boxes, capture durations, final sensor statistics and alerts.

```sh
# From the sensor repository on this NixOS machine:
nix develop path:. --command demo-python diode-sentinel-launch/scripts/capture-product.py
```

Use `CLAIMS-TRACE.md` to review copy and the selected records. The DNS footage
opens a rules alert; the character-CNN explanation describes the enabled
model's role and does not attribute that alert to it. Model scores are not
calibrated probabilities. The persistent “Synthetic replay” caption qualifies
all displayed packet and alert counts.

## Soundtrack and narration

The supplied `First Light - naneki.mp4` is the music source. Its extracted
48 kHz stereo track is `public/music.wav`; the normalized version used by the
film is `public/music-master.wav`. Neither the tempo nor the original timing
is changed. `scripts/analyze-music.py` measures spectral-flux onsets;
`beats.json` stores those accents and the frame-aligned scene cuts. These are
measured track accents, not an assumed fixed BPM grid.

Music fades in for one second, fades out for two seconds and ducks around each
narration segment. `public/music.mp3` is an optional fallback if no master WAV
is available. Missing music renders successfully without a soundtrack.
Narration consists of timed offline Piper voice segments in `public/narration/`.
If those segments are absent, the render omits narration safely too.

To regenerate narration, download the voice with
`scripts/download-voice.py`, then run `scripts/prepare-narration.py`. The latter
currently names this machine's Piper and FFmpeg executables; adjust those
paths for another environment. Voice licensing is in
`.media-cache/voice/MODEL_CARD`. `narration.json` records every spoken line,
start frame, duration and any timing adjustment.

## Source structure and review

- `src/product-config.ts`: all authored visible copy and model descriptions.
- `src/theme.ts`: color palette, Google Fonts and spring configuration.
- `src/scenes/product/`: individual scene components and shared layout.
- `src/ui/ProductCamera.tsx`: enlarged recorded UI with deliberate camera motion.
- `src/ProductFilm.tsx`: transitions, narration and music envelopes.
- `beats.json`: measured accents and cuts; generated timeline follows it.

```sh
npm run typecheck
node scripts/claims-trace.mjs
python3 scripts/inspect-frames.py out/diode-sentinel-product-demo.mp4 --ffmpeg ffmpeg
```

Review frames are in `out/review/`; `VALIDATION.md` records final verification.

No logo file was supplied. The code-drawn diode mark is original production
artwork; an approved custom logo can be added at `public/logo.svg` and used in
`src/scenes/product/Shared.tsx`. No project URL was supplied, so none is
invented or displayed. The supplied music and team identity are already used;
there are no unresolved on-screen placeholders.

The final QC pass measures narration against decoded export audio. This host's
render had a consistent 43 ms codec-padding offset; the final MP4 has been
corrected without re-encoding. To repeat measurement and apply a correction
only when it is consistent across all narration segments:

```sh
# From the sensor repo, with its existing numpy/scipy virtual environment:
source .env-ml
.venv/bin/python diode-sentinel-launch/scripts/verify-narration.py --align
```

The check is idempotent: a film already aligned is left untouched. It writes
`out/narration-sync-check.json`. It requires the recorded narration segments.
