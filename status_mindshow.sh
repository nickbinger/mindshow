#!/bin/bash

# MindShow Status Script
# Shows the current status of all MindShow processes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PID_FILE="/tmp/mindshow_system.pid"
MUSE_PID_FILE="/tmp/mindshow_muse.pid"
LOG_FILE="/tmp/mindshow.log"

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

# Function to check if a process is running
process_running() {
    pgrep -f "$1" >/dev/null 2>&1
}

# Function to check process by PID file
check_pid_file() {
    local pid_file=$1
    local name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            print_success "$name is running (PID: $pid)"
            return 0
        else
            print_error "$name PID file exists but process is not running (PID: $pid)"
            return 1
        fi
    else
        print_warning "$name is not running (no PID file)"
        return 1
    fi
}

# Function to check Muse LSL stream
check_muse_stream() {
    local stream_count=$(python3 -c "import pylsl; streams = pylsl.resolve_streams(); print(len([s for s in streams if 'Muse' in s.name()]))" 2>/dev/null || echo "0")
    if [ "$stream_count" -gt 0 ]; then
        print_success "Muse LSL stream is available ($stream_count stream(s))"
        return 0
    else
        print_warning "No Muse LSL streams found"
        return 1
    fi
}

# Function to show log tail
show_log_tail() {
    if [ -f "$LOG_FILE" ]; then
        echo ""
        print_status "Recent log entries:"
        echo "===================="
        tail -10 "$LOG_FILE" 2>/dev/null || print_warning "Could not read log file"
    else
        print_warning "No log file found"
    fi
}

# Main execution
main() {
    echo "📊 MindShow Status Report"
    echo "========================="
    
    # Check main system
    echo ""
    print_status "Checking MindShow System..."
    if check_pid_file "$PID_FILE" "MindShow System"; then
        SYSTEM_RUNNING=true
    else
        SYSTEM_RUNNING=false
    fi
    
    # Check Muse stream
    echo ""
    print_status "Checking Muse LSL Stream..."
    if check_pid_file "$MUSE_PID_FILE" "Muse LSL Stream"; then
        MUSE_RUNNING=true
    else
        MUSE_RUNNING=false
    fi
    
    # Check for any Muse streams
    echo ""
    print_status "Checking for Muse LSL streams..."
    check_muse_stream
    
    # Check port 8000
    echo ""
    print_status "Checking Dashboard Port..."
    if port_in_use 8000; then
        print_success "Dashboard is accessible on port 8000"
        print_status "URL: http://localhost:8000"
    else
        print_error "Dashboard is not accessible on port 8000"
    fi
    
    # Check for any remaining processes
    echo ""
    print_status "Checking for any remaining MindShow processes..."
    
    local found_processes=false
    
    if process_running "integrated_mindshow_system.py"; then
        print_warning "Found Python process running integrated_mindshow_system.py"
        found_processes=true
    fi
    
    if process_running "muselsl stream"; then
        print_warning "Found muselsl stream process"
        found_processes=true
    fi
    
    if process_running "uvicorn"; then
        print_warning "Found uvicorn server process"
        found_processes=true
    fi
    
    if [ "$found_processes" = false ]; then
        print_success "No orphaned MindShow processes found"
    fi
    
    # Show log tail
    show_log_tail
    
    # Summary
    echo ""
    echo "📋 Summary:"
    echo "==========="
    if [ "$SYSTEM_RUNNING" = true ] && [ "$MUSE_RUNNING" = true ]; then
        print_success "✅ MindShow system is fully operational"
    elif [ "$SYSTEM_RUNNING" = true ]; then
        print_warning "⚠️ MindShow system is running in demo mode (no Muse)"
    else
        print_error "❌ MindShow system is not running"
    fi
    
    echo ""
    print_status "Commands:"
    print_status "  Start:   ./start_mindshow.sh"
    print_status "  Stop:    ./stop_mindshow.sh"
    print_status "  Status:  ./status_mindshow.sh"
    print_status "  Logs:    tail -f $LOG_FILE"
}

# Run main function
main "$@"
