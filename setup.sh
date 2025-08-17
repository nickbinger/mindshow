#!/bin/bash

# MindShow Setup Script
# Creates a reliable Python virtual environment and installs dependencies
# Works on macOS (laptop) and Raspberry Pi Zero

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect OS and architecture
detect_platform() {
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    if [ "$OS" = "Darwin" ]; then
        PLATFORM="macos"
        print_status "Detected macOS on $ARCH"
    elif [ "$OS" = "Linux" ]; then
        if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
            PLATFORM="pi"
            print_status "Detected Raspberry Pi"
        else
            PLATFORM="linux"
            print_status "Detected Linux on $ARCH"
        fi
    else
        print_error "Unsupported platform: $OS"
        exit 1
    fi
}

# Function to check Python availability
check_python() {
    # Try to find Python 3.8+
    for PYTHON_CMD in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command -v $PYTHON_CMD >/dev/null 2>&1; then
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
            PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
            PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
            
            if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
                PYTHON=$PYTHON_CMD
                print_success "Found Python $PYTHON_VERSION at $(which $PYTHON_CMD)"
                return 0
            fi
        fi
    done
    
    print_error "Python 3.8+ is required but not found"
    if [ "$PLATFORM" = "macos" ]; then
        print_status "Install Python with: brew install python@3.11"
    elif [ "$PLATFORM" = "pi" ] || [ "$PLATFORM" = "linux" ]; then
        print_status "Install Python with: sudo apt-get install python3 python3-pip python3-venv"
    fi
    exit 1
}

# Function to create virtual environment
create_venv() {
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_status "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment created at $VENV_DIR"
}

# Function to activate venv and upgrade pip
activate_and_upgrade() {
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies from requirements.txt..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "requirements.txt not found at $REQUIREMENTS_FILE"
        exit 1
    fi
    
    # Platform-specific installations
    if [ "$PLATFORM" = "macos" ]; then
        # On macOS, we may need special handling for pylsl
        print_status "Installing macOS-specific dependencies..."
        pip install pylsl --no-cache-dir
    elif [ "$PLATFORM" = "pi" ]; then
        # On Pi, we may need system packages first
        print_status "Checking for required system packages on Pi..."
        if ! dpkg -l | grep -q libbluetooth-dev; then
            print_warning "Installing required system packages..."
            sudo apt-get update
            sudo apt-get install -y libbluetooth-dev python3-dev
        fi
    fi
    
    # Install all requirements
    pip install -r "$REQUIREMENTS_FILE"
    
    # Install muselsl separately as it's not in requirements.txt but needed
    print_status "Installing muselsl for Muse headband support..."
    pip install muselsl
    
    print_success "All dependencies installed successfully"
}

# Function to create activation scripts
create_activation_scripts() {
    print_status "Creating activation helper scripts..."
    
    # Create activate.sh
    cat > "$SCRIPT_DIR/activate.sh" << 'EOF'
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
EOF
    chmod +x "$SCRIPT_DIR/activate.sh"
    
    # Update start_mindshow.sh to use venv
    print_status "Updating start_mindshow.sh to use virtual environment..."
    
    # Create new start script that uses venv
    cat > "$SCRIPT_DIR/start_mindshow_venv.sh" << 'EOF'
#!/bin/bash

# MindShow Startup Script - Virtual Environment Version
# Uses the local virtual environment for all Python commands

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_SCRIPT="integrated_mindshow_system.py"
PID_FILE="/tmp/mindshow_system.pid"
MUSE_PID_FILE="/tmp/mindshow_muse.pid"
LOG_FILE="/tmp/mindshow.log"
MUSE_STREAM_TIMEOUT=30
SYSTEM_STARTUP_TIMEOUT=60

# Check if venv exists
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Use venv Python for all commands
PYTHON_CMD="$VENV_DIR/bin/python"
PIP_CMD="$VENV_DIR/bin/pip"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    if port_in_use $port; then
        print_warning "Port $port is in use. Killing existing processes..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check if Muse LSL stream is running
check_muse_stream() {
    $PYTHON_CMD -c "import pylsl; streams = pylsl.resolve_streams(); print(len([s for s in streams if 'Muse' in s.name()]))" 2>/dev/null || echo "0"
}

# Function to start Muse LSL stream
start_muse_stream() {
    print_status "Starting Muse LSL stream..."
    
    # Check if muselsl is available in venv
    if ! $VENV_DIR/bin/muselsl --help >/dev/null 2>&1; then
        print_warning "muselsl not found in virtual environment. Installing..."
        $PIP_CMD install muselsl
    fi
    
    # Check for Muse devices
    print_status "Checking for Muse devices..."
    local muse_list_output
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS specific
        muse_list_output=$(DYLD_LIBRARY_PATH=/opt/homebrew/lib $VENV_DIR/bin/muselsl list 2>&1)
    else
        muse_list_output=$($VENV_DIR/bin/muselsl list 2>&1)
    fi
    
    if echo "$muse_list_output" | grep -q "No Muses found"; then
        print_warning "No Muse devices found. Starting in demo mode."
        return 1
    fi
    
    # Start muselsl stream in background
    print_status "Starting Muse LSL stream..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        DYLD_LIBRARY_PATH=/opt/homebrew/lib $VENV_DIR/bin/muselsl stream >> "$LOG_FILE" 2>&1 &
    else
        $VENV_DIR/bin/muselsl stream >> "$LOG_FILE" 2>&1 &
    fi
    local muse_pid=$!
    echo $muse_pid > "$MUSE_PID_FILE"
    
    # Wait for stream to be available
    print_status "Waiting for Muse stream to be available..."
    local attempts=0
    while [ $attempts -lt $MUSE_STREAM_TIMEOUT ]; do
        if [ "$(check_muse_stream)" -gt 0 ]; then
            print_success "Muse LSL stream is now available (PID: $muse_pid)"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # If we get here, stream didn't start
    kill $muse_pid 2>/dev/null || true
    rm -f "$MUSE_PID_FILE"
    print_warning "Muse LSL stream failed to start within $MUSE_STREAM_TIMEOUT seconds"
    print_status "Starting in demo mode without Muse..."
    return 1
}

# Function to cleanup on startup
cleanup_on_startup() {
    print_status "Cleaning up any existing processes..."
    
    # Kill any existing processes
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        kill $pid 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
    
    if [ -f "$MUSE_PID_FILE" ]; then
        local muse_pid=$(cat "$MUSE_PID_FILE")
        kill $muse_pid 2>/dev/null || true
        rm -f "$MUSE_PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "integrated_mindshow_system.py" 2>/dev/null || true
    pkill -f "muselsl stream" 2>/dev/null || true
    kill_port 8000
    
    # Clear log file
    > "$LOG_FILE"
}

# Function to start the main system
start_main_system() {
    print_status "Starting MindShow Integrated System..."
    
    # Kill any existing processes on port 8000
    kill_port 8000
    
    # Start the main system in background
    cd "$SCRIPT_DIR"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        DYLD_LIBRARY_PATH=/opt/homebrew/lib $PYTHON_CMD "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    else
        $PYTHON_CMD "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    fi
    local system_pid=$!
    echo $system_pid > "$PID_FILE"
    
    # Wait for system to start
    print_status "Waiting for system to start..."
    local attempts=0
    while [ $attempts -lt $SYSTEM_STARTUP_TIMEOUT ]; do
        if port_in_use 8000; then
            print_success "MindShow system is now running (PID: $system_pid)"
            print_success "Dashboard: http://localhost:8000"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # If we get here, system didn't start
    kill $system_pid 2>/dev/null || true
    rm -f "$PID_FILE"
    print_error "MindShow system failed to start within $SYSTEM_STARTUP_TIMEOUT seconds"
    return 1
}

# Main execution
main() {
    echo "🧠 MindShow Startup Script (Virtual Environment)"
    echo "================================================"
    
    print_status "Using Python from: $(which python)"
    print_status "Python version: $(python --version)"
    
    # Cleanup any existing processes
    cleanup_on_startup
    
    # Check if Muse stream is already running
    if [ "$(check_muse_stream)" -gt 0 ]; then
        print_success "Muse LSL stream is already running"
    else
        # Start Muse stream
        start_muse_stream
    fi
    
    # Start main system
    start_main_system || exit 1
    
    echo ""
    print_success "🎉 MindShow system is ready and running in background!"
    print_status "Dashboard: http://localhost:8000"
    print_status "Log file: $LOG_FILE"
    print_status "Use './status_mindshow.sh' to check status"
    print_status "Use './stop_mindshow.sh' to stop the system"
    echo ""
}

# Run main function
main "$@"
EOF
    chmod +x "$SCRIPT_DIR/start_mindshow_venv.sh"
    
    print_success "Created activation scripts"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    source "$VENV_DIR/bin/activate"
    
    # Check critical packages
    PYTHON_CMD="$VENV_DIR/bin/python"
    
    $PYTHON_CMD -c "import pylsl" 2>/dev/null && print_success "✓ pylsl" || print_error "✗ pylsl"
    $PYTHON_CMD -c "import fastapi" 2>/dev/null && print_success "✓ fastapi" || print_error "✗ fastapi"
    $PYTHON_CMD -c "import uvicorn" 2>/dev/null && print_success "✓ uvicorn" || print_error "✗ uvicorn"
    $PYTHON_CMD -c "import websocket" 2>/dev/null && print_success "✓ websocket-client" || print_error "✗ websocket-client"
    $PYTHON_CMD -c "import numpy" 2>/dev/null && print_success "✓ numpy" || print_error "✗ numpy"
    $PYTHON_CMD -c "import loguru" 2>/dev/null && print_success "✓ loguru" || print_error "✗ loguru"
    
    # Check if muselsl is available
    if $VENV_DIR/bin/muselsl --help >/dev/null 2>&1; then
        print_success "✓ muselsl command available"
    else
        print_warning "✗ muselsl command not found (optional for Muse support)"
    fi
}

# Main setup flow
main() {
    echo "🧠 MindShow Setup Script"
    echo "========================"
    echo ""
    
    detect_platform
    check_python
    create_venv
    activate_and_upgrade
    install_dependencies
    create_activation_scripts
    verify_installation
    
    echo ""
    print_success "🎉 Setup complete!"
    echo ""
    echo "To use MindShow:"
    echo "  1. Activate environment: source activate.sh"
    echo "  2. Start system: ./start_mindshow_venv.sh"
    echo ""
    echo "Or use the new venv-aware startup script directly:"
    echo "  ./start_mindshow_venv.sh"
    echo ""
}

# Run main function
main "$@"