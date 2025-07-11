{ pkgs ? import <nixpkgs> {} }:
let
  pythonEnv =  pkgs.python313.withPackages (ps: with ps; [
    pip
    virtualenv
    pyyaml
    #dataclass-wizard
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
    pkgs.python313
    pkgs.python313Packages.pip
    pkgs.python313Packages.setuptools
    pkgs.python313Packages.wheel
    pkgs.python313Packages.pyyaml

    #pkgs.python313Packages.pyjson5
    #pkgs.python313Packages.pyyaml
    #pkgs.python313Packages.dataclass-wizard
    #vscodeEnv
  ];

  shellHook = ''
    echo "nix-shell ready with Python: $(which python)"
    if [ ! -d .venv ]; then
      virtualenv .venv
    fi
    source .venv/bin/activate
    pip install "dataclass-wizard[yaml]"
  '';
}

