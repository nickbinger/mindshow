#!/bin/bash

# Fix BrainFlow installation on Raspberry Pi Zero
# The issue is missing shared libraries

echo "Fixing BrainFlow on Pi Zero..."
echo "=============================="

# 1. First uninstall broken BrainFlow
echo "1. Removing broken BrainFlow..."
pip3 uninstall -y brainflow

# 2. Install system dependencies
echo "2. Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    libbluetooth-dev \
    libglib2.0-dev \
    build-essential \
    cmake \
    git

# 3. Try installing pre-built wheel first (fastest)
echo "3. Attempting wheel install..."
pip3 install --no-cache-dir brainflow

# 4. Test if it worked
echo "4. Testing installation..."
python3 -c "from brainflow.board_shim import BoardShim; print('✓ BrainFlow imported successfully')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Wheel install failed, trying alternative..."
    
    # 5. Alternative: Install older stable version
    echo "5. Installing older stable version..."
    pip3 install --no-cache-dir brainflow==5.6.0
    
    # Test again
    python3 -c "from brainflow.board_shim import BoardShim; print('✓ BrainFlow imported')" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "Still failed. Trying manual fix..."
        
        # 6. Manual library fix
        echo "6. Checking for library files..."
        VENV_LIB=$(python3 -c "import site; print(site.getsitepackages()[0])")
        BRAINFLOW_DIR="$VENV_LIB/brainflow/lib"
        
        echo "Looking in: $BRAINFLOW_DIR"
        ls -la "$BRAINFLOW_DIR" 2>/dev/null || echo "Directory not found"
        
        # Try to find the library
        find "$VENV_LIB/brainflow" -name "*.so" 2>/dev/null
    fi
fi

echo ""
echo "Done. Now test with:"
echo "  python3 test_pi_simple.py"