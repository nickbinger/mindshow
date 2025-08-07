#!/bin/bash

# MindShow Status Script
# Shows the current state of all MindShow components

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

# Function to check if a process is running
process_running() {
    pgrep -f "$1" >/dev/null 2>&1
}

# Function to check if Muse LSL stream is running
check_muse_stream() {
    python3 -c "import pylsl; streams = pylsl.resolve_streams(); print(len([s for s in streams if 'Muse' in s.name()]))" 2>/dev/null || echo "0"
}

# Function to get process info
get_process_info() {
    local pattern=$1
    if process_running "$pattern"; then
        local pids=$(pgrep -f "$pattern")
        echo "Running (PIDs: $pids)"
    else
        echo "Not running"
    fi
}

# Function to get port info
get_port_info() {
    local port=$1
    if port_in_use $port; then
        local process=$(lsof -i :$port | grep LISTEN | head -1 | awk '{print $1}')
        echo "In use by: $process"
    else
        echo "Available"
    fi
}

# Function to check dashboard accessibility
check_dashboard() {
    if port_in_use 8000; then
        if curl -s http://localhost:8000 >/dev/null 2>&1; then
            echo "Accessible"
        else
            echo "Port in use but not responding"
        fi
    else
        echo "Not running"
    fi
}

# Main execution
main() {
    echo "📊 MindShow Status Report"
    echo "========================="
    echo ""
    
    # Check main system
    print_status "Main System:"
    if [ -f /tmp/mindshow_system.pid ]; then
        local pid=$(cat /tmp/mindshow_system.pid)
        if kill -0 $pid 2>/dev/null; then
            print_success "Running (PID: $pid)"
        else
            print_error "PID file exists but process is dead"
            rm -f /tmp/mindshow_system.pid
        fi
    else
        print_warning "No PID file found"
    fi
    
    # Check Python process
    print_status "Python Process:"
    local python_status=$(get_process_info "integrated_mindshow_system.py")
    if [[ $python_status == *"Running"* ]]; then
        print_success "$python_status"
    else
        print_warning "$python_status"
    fi
    
    # Check Muse LSL stream
    print_status "Muse LSL Stream:"
    local muse_status=$(get_process_info "muselsl stream")
    if [[ $muse_status == *"Running"* ]]; then
        print_success "$muse_status"
    else
        print_warning "$muse_status"
    fi
    
    # Check if Muse stream is available
    print_status "Muse Stream Available:"
    local stream_count=$(check_muse_stream)
    if [ "$stream_count" -gt 0 ]; then
        print_success "Yes ($stream_count stream(s))"
    else
        print_warning "No streams detected"
    fi
    
    # Check web server
    print_status "Web Server (Port 8000):"
    local port_status=$(get_port_info 8000)
    if [[ $port_status == *"Available"* ]]; then
        print_warning "$port_status"
    else
        print_success "$port_status"
    fi
    
    # Check dashboard accessibility
    print_status "Dashboard Accessibility:"
    local dashboard_status=$(check_dashboard)
    if [[ $dashboard_status == "Accessible" ]]; then
        print_success "$dashboard_status"
    else
        print_warning "$dashboard_status"
    fi
    
    echo ""
    print_status "Quick Commands:"
    echo "  Start:   ./start_mindshow.sh"
    echo "  Stop:    ./stop_mindshow.sh"
    echo "  Status:  ./status_mindshow.sh"
    echo "  Dashboard: http://localhost:8000"
}

# Run main function
main "$@"
