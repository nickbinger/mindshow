#!/bin/bash

# MindShow Setup for Raspberry Pi Zero
# Uses BrainFlow instead of LSL for better performance on limited hardware

set -e

echo "🥧 MindShow Pi Zero Setup"
echo "========================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Install Bluetooth dependencies
echo "Installing Bluetooth support..."
sudo apt-get install -y bluetooth bluez libbluetooth-dev
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install lightweight requirements
echo "Installing Python packages..."
cat > requirements_pi_zero.txt << 'EOF'
# Lightweight requirements for Pi Zero
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
websocket-client==1.6.4
numpy==1.24.0
loguru==0.7.2

# BrainFlow instead of pylsl (lighter weight)
brainflow==5.11.0

# Skip heavy ML packages from muselsl
# No pandas, scikit-learn, matplotlib, seaborn
EOF

pip install --upgrade pip
pip install -r requirements_pi_zero.txt

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