# Codex video MCP

The project-scoped `.codex/config.toml` registers `diode_demo_video`. Restart
Codex (or reload MCP servers) from this trusted project to expose two tools:

- `record_dashboard_tour` records the actual dashboard using the ML or rules
  regression fixture, with an animated cursor and alert inspection.
- `render_full_demo` builds the edited title/dashboard/terminal/proof/end-card
  video.

Both commands enter the repository's Nix development shell for its pinned
Chromium, Playwright and FFmpeg tools. Outputs go under `demo_video/out/`.
The MCP uses synthetic fixtures and does not capture a live network interface.
Runway can provide optional generated establishing shots, motion graphics or
voiceover after connecting its Codex/ChatGPT integration; keep product claims
grounded in the repository's measured evidence.
