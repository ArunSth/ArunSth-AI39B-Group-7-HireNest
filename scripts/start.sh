#!/usr/bin/env bash
# Creates venv if missing, installs requirements once, activates and runs the app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  venv/bin/python -m pip install --upgrade pip
  if [ -f requirements.txt ]; then
    venv/bin/python -m pip install -r requirements.txt
  fi
fi
source venv/bin/activate
python run.py