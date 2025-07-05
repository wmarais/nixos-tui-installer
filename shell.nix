{ pkgs ? import <nixpkgs> {} }:
let
  pythonEnv =  pkgs.python313.withPackages (ps: with ps; [
    pip
    virtualenv
    pyyaml
    psutil
    debugpy
  ]);

  #vscodeEnv = with pkgs; pkgs.vscode-with-extensions.override {
  #    vscodeExtensions = with vscode-extensions; [
  #      redhat.vscode-yaml
  #      shd101wyy.markdown-preview-enhanced
  #
  #      mkhl.direnv
  #      arrterian.nix-env-selector

  #      ms-python.vscode-pylance
  #      ms-python.python
  #      ms-python.pylint
  #      ms-python.flake8
  #      charliermarsh.ruff

  #      #ms-python.mypy-type-checker
  #      ms-python.debugpy
  #    ];
  #  };

in

pkgs.mkShell {
  name = "python-vscode-env";

  buildInputs = [
    pkgs.direnv
    pkgs.which
    pkgs.vivid
    pkgs.bash
    pythonEnv
    #vscodeEnv
  ];

  shellHook = ''
    #echo "nix-shell ready with Python: $(which python)"
    #virtualenv .venv
    #source venv/bin/activate
  '';
}

