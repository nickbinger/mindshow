# MindShow: Brainwave-Controlled LED Hat

A real-time brainwave visualization system that controls LED patterns based on your mental state, built for Burning Man.

## Project Overview

**MindShow** transforms brainwaves into LED light patterns. Using a Muse S Gen 2 EEG headband, it captures brain activity in real-time and translates it into dynamic LED patterns via Pixelblaze V3 controllers.

### Key Features

- **Real-time brainwave analysis** using Muse S Gen 2 EEG headband
- **Dynamic LED control** via Pixelblaze V3 controller
- **Continuous color mood mapping** (Phase 4b) - smooth warm/cool transitions
- **Web dashboard** with live brainwave visualization at http://localhost:8000
- **Multiple brain states**: Relaxed (Blue/cool), Engaged (Red/warm), Neutral (Green)
- **Stable classification** with confidence-based state transitions

## Quick Start

### Prerequisites
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/nickbinger/mindshow.git
cd mindshow

# Install dependencies
uv sync
```

### Running (Foreground - Recommended)
```bash
# 1. Turn on Muse S Gen 2 (LED blinking = pairing mode)
# 2. Run:
source .venv/bin/activate
export DYLD_LIBRARY_PATH=/opt/homebrew/lib
python integrated_mindshow_system.py

# Dashboard: http://localhost:8000
# Stop: Ctrl+C
```

### Alternative: Background/Daemon Mode
```bash
./start_mindshow.sh   # Start
./stop_mindshow.sh    # Stop
./status_mindshow.sh  # Check status
```

## Technical Architecture

### Hardware
- **Muse S Gen 2 EEG Headband**: Brainwave data acquisition
- **Pixelblaze V3 LED Controller**: Addressable LED control (default IP: 192.168.0.241)
- **Raspberry Pi Zero 2 W** (planned): Embedded deployment

### Software Stack
- **Python 3**: Core application
- **BrainFlow / MuseLSL**: EEG data acquisition (BrainFlow primary, LSL optional via `--lsl`)
- **FastAPI + uvicorn**: Web dashboard
- **websocket-client**: Pixelblaze communication
- **numpy**: Signal processing (FFT-based band power calculation)

### Brain State Classification
- **Attention Score**: Beta/Alpha power ratio
- **Relaxation Score**: Alpha/Theta power ratio (with multiple fallback methods)
- **Thresholds**: Attention > 0.75 = Engaged, Relaxation > 0.65 = Relaxed
- **Stability**: 3 consecutive readings + 2s minimum duration for state changes
- **Color Mood**: Continuous 0.0-1.0 mapping with S-curve easing and exponential smoothing

### Key Files
- `integrated_mindshow_system.py` - Main system (EEG, Pixelblaze, dashboard, all-in-one)
- `config/config.py` - Hardware configuration constants
- `Patterns/` - Pixelblaze JavaScript pattern files
- `start_mindshow.sh` / `stop_mindshow.sh` - Process management scripts

## Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation (BrainFlow, Pixelblaze, dashboard) | Done |
| 2 | Documentation & context gaps | Done |
| 3 | Pixelblaze WebSocket control | Done |
| 4b | Continuous color mood slider | Done |
| 5 | Multiple Pixelblaze controllers | Planned |
| 6 | Advanced EEG (PPG, BrainFlow vs LSL) | Planned |
| 7 | Headless Pi deployment | Planned |

## EEG Frequency Bands

| Band | Range | Associated State |
|------|-------|-----------------|
| Delta | 0.5-4 Hz | Deep sleep |
| Theta | 4-8 Hz | Meditation, creativity |
| Alpha | 8-13 Hz | Relaxation, calm awareness |
| Beta | 13-30 Hz | Active thinking, focus |
| Gamma | 30-50 Hz | High-level processing |

## Development

### Running Tests
```bash
pytest tests/
```

### Hardware Test Scripts
```bash
python3 test_phase4b_color_mood.py   # Test Pixelblaze color mood control
python3 test_dashboard_data.py       # Test dashboard WebSocket data
```

## License

MIT License
