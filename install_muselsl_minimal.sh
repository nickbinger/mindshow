#!/bin/bash

# Minimal MuseLSL install for Pi Zero
# Skips optional dependencies

echo "Minimal MuseLSL Install"
echo "======================="

# Just the essentials
pip3 install --no-cache-dir --no-deps muselsl
pip3 install --no-cache-dir pylsl
pip3 install --no-cache-dir bleak

# Test
echo ""
echo "Testing..."
python3 -c "import muselsl; print('✓ MuseLSL works')" || echo "✗ Failed"

echo ""
echo "Try: muselsl list"