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
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pkgs.uv ];
        shellHook = ''
          echo
          echo "one-way-ids dev shell -- uv + libstdc++ ready"
          echo "  uv sync                     # reproduce the exact Python env (uv.lock)"
          echo "  uv run python tests/test_dga_cnn.py"
          echo "  uv run python training/bench_dga.py  # full external-corpus benchmark"
          echo
          # numpy/scipy/lightgbm need libstdc++.so.6, which Nix keeps off the
          # default loader path. Referencing the store path here (rather than
          # hardcoding a gcc hash) survives nixos-rebuild.
          export LD_LIBRARY_PATH="${pkgs.gcc.cc.lib}/lib:${pkgs.zlib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
        '';
      };
    };
}
