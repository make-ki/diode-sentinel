# Explainer production validation

Status: complete. Final 1080p export, audio alignment and scene-frame review
passed on 1 October 2026.

Final artifact: `out/diode-sentinel-explainer.mp4`, 97,960,990 bytes,
453.6 seconds, 1920×1080 at 30 fps, H.264 video / 48 kHz stereo AAC audio.
The video contains exactly 13,608 picture frames. SHA-256:
`8baa950cdc3499b6c4f5a6cfcb30a6a9bf1cef6e23ff06932313be9ee09bf5c2`.

The complete first draft rendered successfully at 960×540, 30 fps, 376.8 s
(`out/diode-sentinel-explainer-draft.mp4`, 33,080,910 bytes). Frame review then
corrected headline overlap, diagram labels/paths, camera framing and workflow
lengths. The revised final timeline is 453.6 s / 13,608 frames.

Verified before final render:

- TypeScript type check passes.
- All twelve narration texts, Indian locale/settings and exact WAV SHA-256
  hashes match the script and provider manifest.
- All fresh recording/artifact hashes match capture provenance.
- Thirty-two scene samples rendered without browser errors. Each scene has a
  diagram frame; each software scene also has a working and completion frame.
- The nine original recordings are shown completely at playbackRate 1. The
  overview recording is reused to explain packet organization.
- The rolling and source-history illustrations agree with actual selected
  records. The encrypted XGBoost record contains its ten observed inputs.
- The downloaded JSON's original record equals the selected rolling alert;
  its canonical SHA-256 matches the UI selection and downloaded record hash.
- The 14,171-packet / 108-record demonstration is labeled Synthetic replay.
- Music has 15 equal-power joins at unchanged tempo. The edited bed has 853
  measured accents; cut/reveal timestamps are recorded in explainer-beats.json.
- EXPLAINER-CLAIMS-TRACE.md traces all twelve spoken/visible scenes, 121 diagram
  literals, captured software text, selected records and the full replay stream.

Final gates (completed after render):

```sh
../.venv/bin/python scripts/verify-explainer.py --align
python3 scripts/inspect-explainer.py
```

The audio check measures exact source matches in the actual export and
corrects only a consistent mux/codec timestamp offset with stream copy. It
checks both narration and soundtrack, then reports peaks and clipping. The
frame check validates 1920×1080, 30 fps and exactly 13,608 picture frames,
then extracts samples from every scene for actual-export review.

All twelve narration segments matched their exact source WAV files in the
export: minimum correlation 0.962333, maximum residual offset 0.6667 ms.
Twelve music-only windows also matched: minimum correlation 0.996751,
maximum residual offset 0 ms. Decoding the mix to mono measured a peak of
−3.225 dBFS and zero samples at or above the check's 0.999 clipping threshold.
These are numerical alignment checks, not a claim of a human listening review.
The full report is `out/explainer-audio-sync.json`.

Thirty-two frames extracted from the actual final MP4 were visually inspected
across diagram, working-software and workflow-completion samples. Headlines,
diagram labels and selected evidence remain readable; the mouse actions and
completed workflows are preserved. The extraction report and contact sheets
are in `out/explainer-review/export/`. Its `frames.json` records the final
video hash and stream metadata. Source-frame review also reported no browser
errors.

This film is a synthetic product demonstration. It introduces no new model
training, independent dataset evaluation, accuracy or production-throughput
result. The preserved earlier product movie and regression references are
separate artifacts.
