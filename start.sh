#!/bin/bash

# MindShow Start Script
# Uses BrainFlow for Muse connection (more reliable than LSL)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_FILE="/tmp/mindshow.log"

# Check virtual environment
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Clear log
> "$LOG_FILE"

echo -e "${BLUE}🧠 Starting MindShow${NC}"
echo "===================="

# Check for command line options
if [[ "$1" == "--brainflow" ]] || [[ "$1" == "-b" ]]; then
    echo "Using BrainFlow only (skipping LSL)"
    export SKIP_LSL=1
elif [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo "  --brainflow, -b    Use BrainFlow only (skip LSL check)"
    echo "  --help, -h         Show this help"
    exit 0
fi

# Kill any existing processes
pkill -f "integrated_mindshow_system.py" 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sleep 1

# Start the system
cd "$SCRIPT_DIR"
echo "Starting system..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
    export PYLSL_LIB=/opt/homebrew/lib/liblsl.dylib
fi

python integrated_mindshow_system.py >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > /tmp/mindshow_system.pid

# Wait for startup
for i in {1..10}; do
    if lsof -i :8000 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ System running!${NC}"
        echo -e "${GREEN}Dashboard: http://localhost:8000${NC}"
        echo ""
        echo "Muse: Will connect if headband is on and Bluetooth enabled"
        echo "LEDs: Connected to Pixelblaze controllers"
        echo ""
        echo "Log: tail -f $LOG_FILE"
        echo "Stop: ./stop_mindshow.sh"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "System starting slowly. Check log:"
tail -20 "$LOG_FILE"