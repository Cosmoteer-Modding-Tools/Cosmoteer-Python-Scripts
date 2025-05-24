#!/usr/bin/env bash
set -e

echo "Checking Python..."
command -v python3 >/dev/null || { echo "ERROR: python3 not found."; exit 1; }

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! Run './run.sh' to start."
