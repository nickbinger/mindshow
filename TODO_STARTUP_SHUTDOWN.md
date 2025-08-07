# TODO: Startup and Shutdown Issues

## 🚨 Critical Issues to Fix

### 1. **Complex Startup Process**
**Problem**: Takes multiple commands and attempts to get the system running
- Need to manually start `muselsl stream` first
- Need to ensure correct working directory (`/Users/nicholasbinger/mindshow`)
- Need to set `DYLD_LIBRARY_PATH=/opt/homebrew/lib`
- Multiple failed attempts before success

**Solutions Needed**:
- [ ] Create a single startup script that handles all dependencies
- [ ] Auto-detect and start Muse LSL stream if not running
- [ ] Proper environment variable setup
- [ ] Better error handling and retry logic
- [ ] Clear status indicators for each startup step

### 2. **Unclean Shutdown**
**Problem**: System doesn't shut down cleanly when hanging
- Background processes remain running
- Web dashboard becomes unreachable
- Port conflicts on restart
- Zombie processes

**Solutions Needed**:
- [ ] Implement proper signal handling (SIGINT, SIGTERM)
- [ ] Clean shutdown of all components (Muse, Pixelblaze, Dashboard)
- [ ] Process cleanup on exit
- [ ] Port release and cleanup
- [ ] Graceful WebSocket disconnection

### 3. **Dashboard Unreachable After Hanging**
**Problem**: After system hangs, dashboard shows "site can't be reached"
- Web server process may be stuck
- Port 8000 may be in use by zombie process
- No automatic recovery

**Solutions Needed**:
- [ ] Health check for web server
- [ ] Automatic restart of dashboard if unreachable
- [ ] Port conflict detection and resolution
- [ ] Better error reporting for web server issues

## 🔧 Technical Improvements Needed

### 4. **Process Management**
- [ ] Use proper process management (systemd, supervisor, or custom)
- [ ] Implement process monitoring and auto-restart
- [ ] Better logging of process states
- [ ] Resource cleanup on abnormal exit

### 5. **Error Recovery**
- [ ] Automatic retry for failed connections
- [ ] Fallback modes when components fail
- [ ] Better error messages and debugging info
- [ ] Graceful degradation when Muse unavailable

### 6. **User Experience**
- [ ] Single command startup: `./start_mindshow.sh`
- [ ] Single command shutdown: `./stop_mindshow.sh`
- [ ] Status command: `./status_mindshow.sh`
- [ ] Clear progress indicators during startup

## 📋 Implementation Plan

### Phase 1: Quick Fixes
1. Create startup script that handles all dependencies
2. Add proper signal handling for clean shutdown
3. Implement process cleanup on exit

### Phase 2: Robustness
1. Add health checks for all components
2. Implement automatic recovery
3. Better error handling and logging

### Phase 3: User Experience
1. Single command interface
2. Status monitoring
3. Clear progress indicators

## 🎯 Success Criteria
- [ ] System starts with single command
- [ ] System shuts down cleanly with Ctrl+C
- [ ] No zombie processes left behind
- [ ] Dashboard always accessible when system is running
- [ ] Clear error messages when something goes wrong

## 📝 Notes
- Current system works well when running, but startup/shutdown is problematic
- Relaxation fix is working (no longer stuck at 0.000)
- Real-time sliders and debug features are functional
- Need to focus on operational reliability next
