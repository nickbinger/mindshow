#!/bin/bash

# Install MuseLSL and dependencies on Pi Zero

echo "Installing MuseLSL on Pi Zero"
echo "=============================="

# 1. System dependencies
echo "1. Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
    libbluetooth-dev \
    libatlas-base-dev \
    python3-dev \
    python3-pip \
    libglib2.0-dev

# 2. Python bluetooth packages
echo ""
echo "2. Installing Python Bluetooth packages..."
pip3 install --no-cache-dir pybluez2
pip3 install --no-cache-dir bleak

# 3. Install pylsl (lightweight version)
echo ""
echo "3. Installing PyLSL..."
pip3 install --no-cache-dir pylsl

# 4. Install muselsl
echo ""
echo "4. Installing MuseLSL..."
pip3 install --no-cache-dir muselsl

# 5. Test imports
echo ""
echo "5. Testing installation..."
python3 -c "import muselsl; print('✓ MuseLSL imported')"
python3 -c "import pylsl; print('✓ PyLSL imported')"
python3 -c "from muselsl import list_muses; print('✓ Can list Muses')"

echo ""
echo "Installation complete!"
echo ""
echo "Test with:"
echo "  muselsl list"
echo "  python3 test_muselsl_simple.py"