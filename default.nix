{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    black
    isort
    mypy
    pylint
    python3
    shellcheck
  ];
}
