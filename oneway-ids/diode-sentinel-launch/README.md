# Diode Sentinel — inside the engine

**7:33.6 · 1920×1080 · 30 fps · H.264/AAC MP4**

Final film: `out/diode-sentinel-explainer.mp4`.
Composition: **DiodeSentinelExplainer**. Team: **samarags**.

This film combines the C architecture walkthrough with B packet experiments:
observations arriving → flows and windows → timing, scan and source-history
experiments → DNS/encrypted models → source correlation → evidence export.
The dashboard demonstrations are actual cursor-operated recordings of the
software. They run at their recorded speed and include complete workflows.
Animations teach the inputs; they do not simulate model verdicts.

Copy and verified product claims: `../VIDEO-BRIEF.md` §§9–11.
Every spoken line, authored diagram label and selected UI record is traced in
[EXPLAINER-CLAIMS-TRACE.md](EXPLAINER-CLAIMS-TRACE.md). The capture is synthetic:
14,171 packets and 108 emitted records with the enabled demonstration options.
These are demo counts, not production accuracy or throughput figures.

## Preview and render

```sh
# Start in the sensor repository. NixOS requires its existing loader-path shim.
source .env-ml
cd diode-sentinel-launch
npm ci
npm run prepare:explainer
npx remotion studio src/index.ts

# Generic render, using Remotion's browser on other platforms:
npx remotion render src/index.ts DiodeSentinelExplainer out/diode-sentinel-explainer.mp4 --concurrency=2 --crf=18 --offthreadvideo-cache-size-in-bytes=268435456
```

On this NixOS machine, run `python3 scripts/setup-nixos.py` once after `npm ci`,
then `npm run render:explainer`. It uses installed Chromium at
`$CHROMIUM_PATH`, `$CHROME_BIN`, or Chromium on `PATH` when available. The
render script falls back to Remotion's browser selection when none is set.
Google Fonts supply Inter and JetBrains Mono through `@remotion/google-fonts`.
The first font load requires network access.

`prepare:explainer` strictly checks every voice/capture hash, narration text,
Indian locale, and the selected records used by the illustrations. It then
builds the timeline and music bed. Missing music is allowed; missing speech
or required dashboard footage fails the production check.

## Narration and synchronized soundtrack

The narrator is the **Indian English synthetic voice `en-IN-PrabhatNeural`**
from Microsoft Edge TTS, with its `en-IN` catalog locale verified and the
provider rate set to −10%. Speech is normalized to −16 LUFS at 48 kHz mono.
No speech is accelerated, compressed in time or stretched. Exact text, voice
settings and WAV hashes are in `explainer-voice.json`.
[Microsoft documents its Indian English voice locale](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts).

The supplied `First Light - naneki.mp4` provides the soundtrack. The original
track is excluded from Git; the completed film contains the soundtrack. To
rebuild with that track, place a licensed copy beside `package.json`. Its extracted
`public/music.wav` is extended using 2.4-second equal-power crossfades in the
musical body, preserving the source tempo. The bed is normalized to −22 LUFS,
then ducked beneath narration, with a one-second fade-in and two-second
fade-out. `explainer-beats.json` records actual measured accents, cuts, reveals,
loop joins and exact durations. Cuts/reveals snap to nearby measured accents;
the longer film does not assume a fixed 100 BPM grid.

Music preparation also accepts `public/music-master.wav` or
`public/music.mp3`. If none exists, music is omitted successfully and narration
still renders. To replace the track, add the replacement at `public/music.mp3`,
remove or rename the previous WAV music sources, then run preparation again.
Narration WAV files live in `public/explainer-narration/`. Regenerate with
`scripts/prepare-explainer-voice.py`; see its CLI for the external TTS step.
The actual voice identity is synthetic; no human narrator identity is claimed.

## Actual working software

`scripts/capture-explainer.py` records the real dashboard at 1600×1000 using
Playwright and a visible cursor overlay. It generates a seeded capture plus
focused rolling/source-history fixtures. The FIFO pipeline replays at 25×
simulated packet time, while cursor interaction and film playback remain
1× wall-clock speed. It reaches its real completed state at EOF.

The demo enables rules, character CNN, LightGBM, the model bundle, rolling scan
and source context. It never opens a production interface. Captures, selected
records, action timestamps, hashes and the downloaded matching JSON bundle
are preserved in `public/explainer-captures/capture-manifest.json`.

```sh
# Run from the sensor repository on this NixOS machine:
nix develop path:. --command demo-python diode-sentinel-launch/scripts/capture-explainer.py
```

The encrypted metadata scene shows the actual XGBoost vector with ten named
inputs; the scan scene opens `scan_rf`; the DNS scene opens a DNS shape rule.
Model scores are not calibrated probabilities. Correlation keeps its actual
contributors attached. The exported hash covers the original alert record;
unavailable capture/packet/model provenance remains explicit in the bundle.

## Chapters

| Start | Scene |
|---|---|
| 00:00 | Small observations. A larger picture. |
| 00:24 | Watch the observations arrive. |
| 01:02 | Put the observations together. |
| 01:40 | Listen to the rhythm. |
| 02:16 | Keep both windows in view. |
| 02:58 | Remember whose history it is. |
| 03:40 | Read the shape of a name. |
| 04:19 | Two branches. Different observations. |
| 05:10 | The right inputs. The right branch. |
| 05:50 | Follow the source. Connect the signals. |
| 06:27 | Carry the evidence forward. |
| 07:12 | See everything. Touch nothing. |

## Source files and review

- `explainer-script.json`: scene order, headlines, spoken copy and clip mapping.
- `src/explainer/ExplainerFilm.tsx`: scenes, deliberate cameras, transitions and mix.
- `src/explainer/Graphics.tsx`: animated teaching diagrams and original diode mark.
- `src/theme.ts`: Inter, JetBrains Mono, colors and spring configuration.
- `scripts/prepare-explainer-media.py`: speech-led timeline and measured music cues.
- `explainer-beats.json`: exact cuts/reveals and soundtrack edit provenance.
- `explainer-voice.json`: Indian voice identity, text, timings and source hashes.

```sh
npm run typecheck
npm run claims:explainer
npm run review:explainer
# With the sensor's numpy/scipy environment and loader shim already active:
../.venv/bin/python scripts/verify-explainer.py --align
python3 scripts/inspect-explainer.py
```

The review renders a diagram frame, a software frame and a completion frame
for every applicable scene. They are saved in `out/explainer-review/`. Final
export audio is cross-correlated against all twelve exact voice WAV files;
only a consistent codec-padding timestamp offset can be corrected, using
stream copy. No re-encode or time stretching is used. Results are saved in
`out/explainer-audio-sync.json`; production checks are in
[EXPLAINER-VALIDATION.md](EXPLAINER-VALIDATION.md).
Thirty-two frames extracted from the final MP4 were also visually reviewed;
their report and contact sheets are in `out/explainer-review/export/`.

No logo/URL/event details are missing from the current approved script: it uses
the original code-drawn diode mark and **Built by samarags**. A custom approved
logo can later be added at `public/logo.svg` and substituted for `DiodeMark`.
No invented team names or URLs are displayed.

The previous film remains at `out/diode-sentinel-product-demo.mp4` with its
`DiodeSentinelProductDemo` composition and separate assets. Its historical
commands and narration are in [ARCHIVE-PRODUCT-DEMO.md](ARCHIVE-PRODUCT-DEMO.md).
