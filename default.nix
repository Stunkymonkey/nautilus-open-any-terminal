{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    mypy
    pylint
    python3
    ruff
    shellcheck
  ];
}
