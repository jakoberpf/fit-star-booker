#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)
cd $GIT_ROOT

which pyenv > /dev/null 2>&1
if [ "$?" -ne "0" ]; then
  echo "ERROR: Please install pyenv - https://github.com/pyenv/pyenv"
  exit 1
fi

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source $GIT_ROOT/.venv/bin/activate

# Install requirements
pip3 install -r requirements.txt