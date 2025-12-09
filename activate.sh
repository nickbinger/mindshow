#!/bin/bash
# Quick activation script for MindShow virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "MindShow environment activated"
    echo "Python: $(which python)"
    echo "To deactivate, type: deactivate"
else
    echo "Virtual environment not found. Run ./setup.sh first"
fi
