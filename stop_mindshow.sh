#!/bin/bash

# MindShow Stop Script
# Cleanly shuts down all MindShow processes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        print_status "Killing processes on port $port..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to check if a process is running
process_running() {
    pgrep -f "$1" >/dev/null 2>&1
}

# Function to kill processes by pattern
kill_processes() {
    local pattern=$1
    local name=$2
    
    if process_running "$pattern"; then
        print_status "Stopping $name..."
        pkill -f "$pattern" 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if process_running "$pattern"; then
            print_warning "Force killing $name..."
            pkill -9 -f "$pattern" 2>/dev/null || true
        fi
    else
        print_status "$name is not running"
    fi
}

# Main execution
main() {
    echo "🛑 MindShow Stop Script"
    echo "======================="
    
    # Kill main system if PID file exists
    if [ -f /tmp/mindshow_system.pid ]; then
        local pid=$(cat /tmp/mindshow_system.pid)
        print_status "Stopping MindShow system (PID: $pid)..."
        kill $pid 2>/dev/null || true
        rm -f /tmp/mindshow_system.pid
        sleep 2
    fi
    
    # Kill any remaining processes on port 8000
    kill_port 8000
    
    # Kill muselsl processes
    kill_processes "muselsl stream" "Muse LSL Stream"
    
    # Kill any Python processes running the main script
    kill_processes "integrated_mindshow_system.py" "MindShow Python Process"
    
    # Kill any uvicorn processes
    kill_processes "uvicorn" "Uvicorn Server"
    
    # Final cleanup - kill any remaining processes on port 8000
    if port_in_use 8000; then
        print_warning "Port 8000 is still in use, force killing..."
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    fi
    
    print_success "🎉 MindShow system stopped successfully"
}

# Run main function
main "$@"
