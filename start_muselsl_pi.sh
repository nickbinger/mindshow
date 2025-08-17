#!/bin/bash

# Start MuseLSL streaming on Pi Zero
# This is lighter weight than BrainFlow

echo "MuseLSL Streamer for Pi Zero"
echo "============================="

# 1. Find Muse
echo "Finding Muse..."
MUSE_LIST=$(python3 -c "from muselsl import list_muses; muses = list_muses(); print(muses[0]['address'] if muses else '')" 2>/dev/null)

if [ -z "$MUSE_LIST" ]; then
    echo "✗ No Muse found"
    echo ""
    echo "Trying muselsl list directly:"
    muselsl list
    exit 1
fi

echo "✓ Found Muse: $MUSE_LIST"

# 2. Start streaming
echo ""
echo "Starting stream..."
echo "Press Ctrl+C to stop"
echo ""

# Use --backend bgapi for better Pi compatibility
muselsl stream --address "$MUSE_LIST" --backend bgapi

# Alternative if bgapi doesn't work:
# muselsl stream --address "$MUSE_LIST"