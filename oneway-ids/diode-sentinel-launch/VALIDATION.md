# Final product-demo validation

Validated 30 September 2026. Deliverable:
`out/diode-sentinel-product-demo.mp4`.

- Video: H.264, 1920×1080, 30 fps, 1,560 frames, exactly 52.000 s.
- Audio: AAC stereo, 48 kHz; MP4 duration 52.010 s including codec tail.
- File size: 14,675,886 bytes (about 14.7 MB).
- TypeScript: `npm run typecheck` passes.
- Claims: `node scripts/claims-trace.mjs` passes; selected records are matched
  to the captured API snapshot, including the actual 0.783 beacon rule score.

The half-resolution draft was rendered and reviewed. Corrections included
restoring the correlation shot, including the soundtrack and narration,
holding the alert-title framing before panning to measurements, retaining the
source-filter label, and enlarging the sensor's Seen/Analyzed counters.
The final film was rendered at full resolution and representative frames
from all scenes inspected in `out/review/`. Headlines and model labels fit;
the recorded software remains genuine footage with visible cursor movement.

All ten narration segments finish before their next scene cut. Each was
matched against decoded audio from the final MP4 using waveform correlation:
match coefficients 0.9735–0.9895, timing residuals at most 0.67 ms. Results are
in `out/narration-sync-check.json`. A consistent 43 ms encoder-padding offset
was measured and corrected by copying audio/video packets with adjusted audio
timestamps; there was no re-encoding or tempo change. The same check and
optional correction are available in `scripts/verify-narration.py --align`.

Music comes from the user-supplied First Light MP4. Cut boundaries were
snapped to measured spectral-flux accents and rounded to 30 fps in
`beats.json`. The soundtrack has a 1 s entrance, 2 s exit and narration ducking.
The decoded mix measured approximately -17.27 LUFS integrated, -3.08 dBTP and
5 LU loudness range, with no peak clipping. Loudness figures are QC results
for the film audio, not product measurements.

Missing-audio preparation was checked in an isolated temporary directory:
absent music/narration generates safe disabled flags; an optional music.mp3
selects the fallback. Remotion's `Config.setMuted()` takes no argument and
always enables muting; it is called only when all audio is absent.

The software footage was recorded freshly from the current dashboard and
its seeded synthetic replay, with rules, DGA CNN, LightGBM and models-567
loaded. No production interface or private persisted state was used.
The selected DNS alert is a rules alert; the film describes the character
CNN's role without claiming that it produced that record. Detector scores
are not presented as probabilities or accuracy benchmarks.
