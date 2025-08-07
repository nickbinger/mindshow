#!/bin/bash

# MindShow Startup Script
# Handles all dependencies and provides single-command startup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="integrated_mindshow_system.py"
MUSE_STREAM_TIMEOUT=30
SYSTEM_STARTUP_TIMEOUT=60

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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
    python3 -c "import pylsl; streams = pylsl.resolve_streams(); print(len([s for s in streams if 'Muse' in s.name()]))" 2>/dev/null || echo "0"
}

# Function to start Muse LSL stream
start_muse_stream() {
    print_status "Starting Muse LSL stream..."
    
    # Check if muselsl is available
    if ! command_exists muselsl; then
        print_error "muselsl command not found. Please install it first."
        exit 1
    fi
    
    # Check if Muse is available
    print_status "Checking for Muse devices..."
    local muse_list_output=$(DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl list 2>&1)
    if echo "$muse_list_output" | grep -q "No Muses found"; then
        print_error "No Muse devices found. Please ensure your Muse headband is connected and turned on."
        print_status "Available commands:"
        print_status "  - Check connection: DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl list"
        print_status "  - Start manually: DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl stream"
        return 1
    fi
    
    # Start muselsl stream in background
    print_status "Starting Muse LSL stream..."
    DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl stream > /dev/null 2>&1 &
    local muse_pid=$!
    
    # Wait for stream to be available
    print_status "Waiting for Muse stream to be available..."
    local attempts=0
    while [ $attempts -lt $MUSE_STREAM_TIMEOUT ]; do
        if [ "$(check_muse_stream)" -gt 0 ]; then
            print_success "Muse LSL stream is now available"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # If we get here, stream didn't start
    kill $muse_pid 2>/dev/null || true
    print_error "Muse LSL stream failed to start within $MUSE_STREAM_TIMEOUT seconds"
    print_status "This could be because:"
    print_status "  - Muse headband is not connected or turned on"
    print_status "  - Muse app is already streaming"
    print_status "  - Bluetooth connection issues"
    return 1
}

# Function to check Python dependencies
check_python_deps() {
    print_status "Checking Python dependencies..."
    
    local missing_deps=()
    
    # Check required packages
    python3 -c "import pylsl" 2>/dev/null || missing_deps+=("pylsl")
    python3 -c "import fastapi" 2>/dev/null || missing_deps+=("fastapi")
    python3 -c "import uvicorn" 2>/dev/null || missing_deps+=("uvicorn")
    python3 -c "import websocket" 2>/dev/null || missing_deps+=("websocket-client")
    python3 -c "import loguru" 2>/dev/null || missing_deps+=("loguru")
    python3 -c "import numpy" 2>/dev/null || missing_deps+=("numpy")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing Python dependencies: ${missing_deps[*]}"
        print_status "Installing missing dependencies..."
        pip3 install "${missing_deps[@]}"
    else
        print_success "All Python dependencies are available"
    fi
}

# Function to check if main script exists
check_main_script() {
    if [ ! -f "$SCRIPT_DIR/$PYTHON_SCRIPT" ]; then
        print_error "Main script $PYTHON_SCRIPT not found in $SCRIPT_DIR"
        exit 1
    fi
    print_success "Main script found: $PYTHON_SCRIPT"
}

# Function to start the main system
start_main_system() {
    print_status "Starting MindShow Integrated System..."
    
    # Kill any existing processes on port 8000
    kill_port 8000
    
    # Start the main system
    cd "$SCRIPT_DIR"
    DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 "$PYTHON_SCRIPT" &
    local system_pid=$!
    
    # Wait for system to start
    print_status "Waiting for system to start..."
    local attempts=0
    while [ $attempts -lt $SYSTEM_STARTUP_TIMEOUT ]; do
        if port_in_use 8000; then
            print_success "MindShow system is now running on http://localhost:8000"
            echo $system_pid > /tmp/mindshow_system.pid
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # If we get here, system didn't start
    kill $system_pid 2>/dev/null || true
    print_error "MindShow system failed to start within $SYSTEM_STARTUP_TIMEOUT seconds"
    return 1
}

# Main execution
main() {
    echo "🧠 MindShow Startup Script"
    echo "=========================="
    
    # Check if we're in the right directory
    if [ ! -f "$SCRIPT_DIR/$PYTHON_SCRIPT" ]; then
        print_error "Please run this script from the mindshow directory"
        exit 1
    fi
    
    # Check Python dependencies
    check_python_deps
    
    # Check if Muse stream is already running
    if [ "$(check_muse_stream)" -gt 0 ]; then
        print_success "Muse LSL stream is already running"
    else
        # Start Muse stream
        if ! start_muse_stream; then
            print_warning "Muse LSL stream could not be started"
            print_status "Starting system without Muse for testing..."
            print_status "You can connect Muse later and restart the system"
        fi
    fi
    
    # Start main system
    start_main_system || exit 1
    
    echo ""
    print_success "🎉 MindShow system is ready!"
    print_status "Dashboard: http://localhost:8000"
    print_status "Press Ctrl+C to stop the system"
    echo ""
    
    # Wait for user to stop
    wait
}

# Handle cleanup on exit
cleanup() {
    print_status "Shutting down MindShow system..."
    
    # Kill main system if PID file exists
    if [ -f /tmp/mindshow_system.pid ]; then
        local pid=$(cat /tmp/mindshow_system.pid)
        kill $pid 2>/dev/null || true
        rm -f /tmp/mindshow_system.pid
    fi
    
    # Kill any remaining processes on port 8000
    kill_port 8000
    
    # Kill muselsl processes
    pkill -f "muselsl stream" 2>/dev/null || true
    
    print_success "MindShow system stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
