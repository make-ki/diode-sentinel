{
  description = "One-way NIDS (SIH 2026 PS-26145) - reproducible environment";

  # The flake registry's nixpkgs (the same source `nix shell nixpkgs#...`
  # resolves to); flake.lock freezes the exact commit, so `nix develop`
  # reproduces the OS-side dependencies (uv + libstdc++) bit-for-bit.
  inputs.nixpkgs.url = "nixpkgs";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      # Playwright for browser-driven demo recordings: the screencast API
      # (1.59+) records a scripted session and can draw a *synthetic* mouse
      # pointer that animates between action points (show_actions(cursor=
      # "pointer"), 1.61+). The nixpkgs build is used instead of the PyPI
      # wheel because the wheel ships a prebuilt node driver that the NixOS
      # non-FHS loader cannot exec; nixpkgs patches it onto nix's node.
      # Verified on this host: recorded a vp8 1280x720 WebM end to end.
      playwrightEnv = pkgs.python3.withPackages (ps: [ ps.playwright ]);

      # Playwright's screencast muxer looks for its own ffmpeg at
      # $PLAYWRIGHT_BROWSERS_PATH/ffmpeg-<n>/ffmpeg-linux, and downloading
      # that prebuilt binary is the fragile step on NixOS. Point it at the
      # nixpkgs ffmpeg instead. `ffmpeg-1011` is the directory name pinned by
      # Playwright 1.61; after a Playwright bump, if recording reports a
      # missing ffmpeg, read the expected path out of the error and update it.
      playwrightRuntime = pkgs.runCommand "playwright-runtime" { } ''
        mkdir -p $out/ffmpeg-1011
        ln -s ${pkgs.ffmpeg.bin}/bin/ffmpeg $out/ffmpeg-1011/ffmpeg-linux
      '';

      # Do NOT put playwrightEnv on PATH directly: it ships bin/python, which
      # would shadow the interpreter the repo's own scripts expect, and that
      # interpreter has numpy/scapy but no playwright. These wrappers expose
      # it under explicit names instead, so `demo-python` means "the one with
      # playwright" and nothing else changes.
      demoPython = pkgs.writeShellScriptBin "demo-python" ''
        exec ${playwrightEnv}/bin/python "$@"
      '';
      demoPlaywright = pkgs.writeShellScriptBin "demo-playwright" ''
        exec ${playwrightEnv}/bin/playwright "$@"
      '';
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.uv
          # Demo-video tooling only. None of this is a runtime dependency of
          # the sensor: the shipped system is pure Python and must stay that
          # way (AGENTS.md). These are here so a demonstration video can be
          # captured and encoded from the same reproducible shell.
          pkgs.ffmpeg      # frames -> MP4/H.264; without it only GIF/WebP is possible
          pkgs.asciinema   # terminal casts for the pipeline/demo segments
          pkgs.asciinema-agg  # asciicast -> GIF (lightweight alternative to vhs)
                              # NB: pkgs.agg is Anti-Grain Geometry, a C++ renderer,
                              # NOT asciinema's agg. Do not "simplify" this attr.
          # VHS is kept but is NOT currently usable on this host: vhs-0.12.0
          # exits 0 while writing no output, for a stock `vhs new` tape as
          # well as a hand-written one. It does spawn ttyd + chromium, then
          # stops before the ffmpeg encode, so the failure is silent.
          # Verified working instead: asciinema rec -> agg -> ffmpeg (mp4).
          # Re-test with `vhs new t.tape && vhs t.tape` after any nixpkgs bump.
          pkgs.vhs         # terminal-as-code recorder: .tape -> mp4/webm/gif
          pkgs.ttyd        # VHS's virtual-terminal backend (required by vhs)
          pkgs.gifsicle    # optimise the fallback animated GIF path
          pkgs.piper-tts   # offline neural narration (no network; fits the enclave)
          pkgs.socat       # talk to FIFO/socket sources when scripting a capture
          pkgs.xdotool     # scripted keystroke/mouse input on the live display
          pkgs.xvfb        # headless X server (Xvfb), for deterministic capture
          pkgs.xvfb-run    # the xvfb-run wrapper; pkgs.xvfb ships only `Xvfb`
          # Fonts for VHS renders and ffmpeg drawtext. makeFontsConf pins them
          # via FONTCONFIG_FILE below, so a render cannot silently pick up
          # whatever font the host happens to have (or fail to find one).
          pkgs.nerd-fonts.jetbrains-mono
          pkgs.dejavu_fonts
          # Browser-driven demo recording. chromium is the browser Playwright
          # drives (so no CDN browser download); demo-python is an interpreter
          # with playwright importable, demo-playwright its CLI.
          #   nix develop --command demo-python demo_video/record_dashboard.py
          #   nix develop --command demo-playwright codegen http://127.0.0.1:8600
          pkgs.chromium
          demoPython
          demoPlaywright
        ];
        shellHook = ''
          echo
          echo "one-way-ids dev shell -- uv + libstdc++ ready"
          echo "  uv sync                     # reproduce the exact Python env (uv.lock)"
          echo "  uv run python tests/test_dga_cnn.py"
          echo "  uv run python training/bench_dga.py  # full external-corpus benchmark"
          echo "  vhs demo.tape               # demo video: terminal segment -> mp4/webm/gif"
          echo "  piper                       # demo video: offline TTS narration"
          echo "  ffmpeg -version             # demo video: encoder + assembler (dev-only)"
          echo "  demo-python                 # demo video: interpreter with playwright importable"
          echo "  demo-playwright codegen URL # demo video: point-and-click selector picker"
          echo
          # numpy/scipy/lightgbm need libstdc++.so.6, which Nix keeps off the
          # default loader path. Referencing the store path here (rather than
          # hardcoding a gcc hash) survives nixos-rebuild.
          export LD_LIBRARY_PATH="${pkgs.gcc.cc.lib}/lib:${pkgs.zlib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
          # Fontconfig for the demo-video tools. Without this, vhs and
          # `ffmpeg drawtext` cannot resolve a font in the dev shell.
          export FONTCONFIG_FILE="${pkgs.makeFontsConf { fontDirectories = [ pkgs.nerd-fonts.jetbrains-mono pkgs.dejavu_fonts ]; }}"
          # Playwright runtime for browser-driven demo recordings. Pointing
          # the browsers path at our own derivation keeps the ffmpeg shim
          # above in place and stops Playwright from trying to fetch a
          # prebuilt ffmpeg/browser it cannot exec on NixOS.
          export PLAYWRIGHT_BROWSERS_PATH="${playwrightRuntime}"
          export PW_CHROMIUM="${pkgs.chromium}/bin/chromium"
        '';
      };
    };
}
