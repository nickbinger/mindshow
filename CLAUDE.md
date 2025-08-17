# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### System Control
```bash
# Start the complete MindShow system (daemon mode)
./start_mindshow.sh

# Stop all MindShow processes
./stop_mindshow.sh

# Check system status
./status_mindshow.sh

# Monitor logs
tail -f /tmp/mindshow.log
```

### Development & Testing
```bash
# Test Muse connection
python3 test_muse_discovery.py

# Test LED control
python3 test_pb_only.py

# Analyze brainwave thresholds
python3 research_thresholds.py

# Test the stable unified system
python3 stable_unified_system.py

# Test dashboard data
python3 test_dashboard_data.py

# Install dependencies with uv
uv sync
```

### Dependency Management
```bash
# Install Python packages (if uv not available)
pip3 install pylsl fastapi uvicorn websocket-client loguru numpy

# Check for required packages
python3 -c "import pylsl, fastapi, uvicorn, websocket, loguru, numpy"
```

## Architecture

### Core System Design
The MindShow system transforms brainwaves into LED patterns through a multi-component architecture:

1. **EEG Data Acquisition**: Muse S Gen 2 headband → MuseLSL stream → Python processing
2. **Brain State Classification**: Real-time analysis of Alpha/Beta/Theta waves to determine mental states
3. **LED Control**: WebSocket connection to Pixelblaze V3 controller for pattern manipulation
4. **Web Dashboard**: FastAPI server providing real-time visualization at http://localhost:8000

### Key Components

**integrated_mindshow_system.py**: Main system orchestrator
- Manages EEG streaming (MuseLSL primary, BrainFlow fallback)
- Handles Pixelblaze WebSocket connections
- Implements Phase 4b color mood slider with anti-flicker protection
- Automatic pattern selection on startup

**Brain State Processing**:
- **Attention Score**: Beta/Alpha ratio (threshold: 0.75)
- **Relaxation Score**: Alpha/Theta ratio (threshold: 0.65)
- **Stability Logic**: 3 consecutive readings required for state changes
- **Smoothing**: Exponential moving average (factor: 0.1) for smooth transitions

**Pixelblaze Integration**:
- WebSocket protocol for real-time control
- Automatic discovery of controllers on network
- Pattern switching with "Phase 4b Color Mood Plasma" as default
- Variable update throttling (2% change threshold, 0.5s minimum interval)

### System States
- **Relaxed**: Blue tones (colorMoodBias towards 0.0)
- **Engaged**: Red tones (colorMoodBias towards 1.0)  
- **Neutral**: Green tones (colorMoodBias around 0.5)

### Critical Files
- **Configuration**: `config/config.py` - System parameters and thresholds
- **Startup/Shutdown**: `start_mindshow.sh`, `stop_mindshow.sh` - Process management
- **Pattern Files**: `pixelblaze_patterns/` - JavaScript patterns for Pixelblaze
- **Research Docs**: `deep_research/` - Implementation guides and phase documentation

## Important Context

### Current Phase Status
- **Phase 1**: ✅ Foundation System (Complete)
- **Phase 2**: ✅ Documentation (Complete)
- **Phase 3**: ✅ WebSocket Connection (Complete with anti-flicker)
- **Phase 4b**: ✅ Color Mood Slider (Implemented)
- **Phase 5-7**: 🔄 Multiple controllers, advanced EEG, headless deployment (Planned)

### Network Configuration
- **Pixelblaze IP**: 192.168.0.241 (hardcoded in current implementation)
- **Dashboard Port**: 8000
- **WebSocket Port**: 81 (Pixelblaze)

### Known Issues & Solutions
- **Pattern Flickering**: Resolved with variable update throttling
- **Muse Connection**: Requires DYLD_LIBRARY_PATH=/opt/homebrew/lib on macOS
- **High Relaxation Values**: Scaled to 500,000 max for proper normalization

### Testing Priority
1. Verify Muse headband connection and data stream
2. Confirm Pixelblaze WebSocket connection
3. Test pattern switching and color mood updates
4. Monitor for flickering or instability
5. Check dashboard real-time updates

## Development Notes

### State Management
The system uses confidence counters and duration tracking to prevent rapid state switching. Each state change requires 3 consecutive readings above threshold and minimum 2 seconds duration.

### Color Mood Implementation
The colorMoodBias variable (0.0-1.0) controls perceptual color shifting:
- Smooth transitions via exponential moving average
- Anti-flicker protection through update throttling
- Mapped to brain state with weighted averaging

### Process Management
The startup script handles:
- Cleanup of existing processes
- Dependency checking
- Muse LSL stream initialization
- Main system launch in daemon mode
- PID tracking for clean shutdown

### Performance Optimization
- 10Hz update rate for real-time responsiveness
- Throttled WebSocket updates to prevent overload
- Efficient numpy operations for signal processing
- Minimal logging in production mode