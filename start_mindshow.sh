#!/bin/bash

# MindShow Startup Script - Daemon Mode
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
PID_FILE="/tmp/mindshow_system.pid"
MUSE_PID_FILE="/tmp/mindshow_muse.pid"
LOG_FILE="/tmp/mindshow.log"
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
        return 1
    fi
    
    # Check if Muse is available
    print_status "Checking for Muse devices..."
    local muse_list_output=$(DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl list 2>&1)
    if echo "$muse_list_output" | grep -q "No Muses found"; then
        print_warning "No Muse devices found. Starting in demo mode."
        return 1
    fi
    
    # Start muselsl stream in background with proper logging
    print_status "Starting Muse LSL stream..."
    DYLD_LIBRARY_PATH=/opt/homebrew/lib muselsl stream >> "$LOG_FILE" 2>&1 &
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
    
    # Start the main system in background with proper logging
    cd "$SCRIPT_DIR"
    DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
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

# Main execution
main() {
    echo "🧠 MindShow Startup Script (Daemon Mode)"
    echo "========================================="
    
    # Check if we're in the right directory
    if [ ! -f "$SCRIPT_DIR/$PYTHON_SCRIPT" ]; then
        print_error "Please run this script from the mindshow directory"
        exit 1
    fi
    
    # Cleanup any existing processes
    cleanup_on_startup
    
    # Check Python dependencies
    check_python_deps
    
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
