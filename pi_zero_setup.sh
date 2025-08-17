#!/bin/bash

# MindShow Setup for Raspberry Pi Zero
# Optimized for limited resources (512MB RAM, single core)

set -e

echo "🥧 MindShow Pi Zero Setup"
echo "========================"

# Check if running on Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages (this may take a while on Pi Zero)..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Install Bluetooth dependencies
echo "Installing Bluetooth support..."
sudo apt-get install -y bluetooth bluez libbluetooth-dev python3-dev
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER
echo "Added $USER to bluetooth group (may need to logout/login)"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install requirements one by one to avoid memory issues
echo "Installing Python packages (one at a time for Pi Zero)..."

# Core packages
pip install --no-cache-dir fastapi==0.104.1
pip install --no-cache-dir uvicorn==0.24.0
pip install --no-cache-dir websockets==12.0
pip install --no-cache-dir websocket-client==1.6.4
pip install --no-cache-dir loguru==0.7.2

# NumPy might need special handling on Pi Zero
echo "Installing NumPy (this will take several minutes)..."
pip install --no-cache-dir --no-binary :all: numpy==1.24.0 || \
    pip install --no-cache-dir numpy==1.24.0

# BrainFlow
echo "Installing BrainFlow..."
pip install --no-cache-dir brainflow==5.11.0

# Try to install pylsl (might fail on Pi Zero)
echo "Attempting pylsl install (optional)..."
pip install --no-cache-dir pylsl || echo "pylsl installation failed (using BrainFlow instead)"

# Create Pi Zero specific start script
cat > start_pi_zero.sh << 'EOF'
#!/bin/bash

# Start MindShow on Pi Zero (BrainFlow mode)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"

# Set environment to use BrainFlow
export MINDSHOW_USE_BRAINFLOW=1
export MINDSHOW_SKIP_LSL=1

# Clear log
> /tmp/mindshow.log

echo "Starting MindShow (Pi Zero Mode)..."

# Start with reduced resources
python integrated_mindshow_system.py >> /tmp/mindshow.log 2>&1 &
PID=$!
echo $PID > /tmp/mindshow_system.pid

sleep 5

if lsof -i :8000 >/dev/null 2>&1; then
    echo "✓ System running!"
    echo "Dashboard: http://$(hostname -I | cut -d' ' -f1):8000"
    echo "Log: tail -f /tmp/mindshow.log"
else
    echo "Failed to start. Check /tmp/mindshow.log"
fi
EOF

chmod +x start_pi_zero.sh

echo ""
echo "✅ Pi Zero setup complete!"
echo ""
echo "To start MindShow on Pi Zero:"
echo "  ./start_pi_zero.sh"
echo ""
echo "Note: This uses BrainFlow instead of LSL for better Pi Zero performance"