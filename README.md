# MindShow - EEG LED Hat for Burning Man

A real-time brainwave visualization system that connects a Muse S Gen 2 EEG headband to LED patterns on a wearable hat.

## 🎯 Project Overview

This project creates an LED hat that changes colors and patterns based on brainwave activity detected by a Muse S Gen 2 EEG headband. The system uses a Raspberry Pi Zero 2 W to process EEG data and control LED patterns via a Pixelblaze controller.

## 🏗️ Architecture

```
Muse S Gen 2 (EEG) → BLE → Raspberry Pi Zero 2 W → WebSocket → Pixelblaze → LEDs
```

## 📋 Development Phases

### Phase 1: Laptop + Muse + BrainFlow GUI ✅
- [x] Set up Python environment
- [x] Install dependencies
- [x] Pair Muse via BLE
- [x] Connect to Muse via BrainFlow
- [x] Add basic GUI/visualization
- [x] Commit and push to GitHub

### Phase 2: Pixelblaze Integration + Brainwave Analysis ✅
- [x] Install Pixelblaze WebSocket client
- [x] Implement BrainFlow attention/relaxation detection
- [x] Create real-time brainwave state classification
- [x] Connect to Pixelblaze via WebSocket
- [x] Implement color palette changes (relaxed=blue, engaged=red)
- [x] Test real-time LED pattern modification
- [x] **FIXED: Color mapping issues** (red/blue hue values swapped)
- [x] **FIXED: GUI/LED synchronization** (real-time updates)
- [x] **ENHANCED: Muse keep-alive mechanism** (prevents sleep)
- [x] **ADDED: Robust connection verification** and error handling

### Phase 2.5: Enhanced Features (Research Integration) ✅
- [x] **Modern Python Development**: Migrated to `pyproject.toml` with uv package manager
- [x] **Enhanced LED Controller**: Smooth transitions, wave effects, performance optimization
- [x] **Web Dashboard**: FastAPI + WebSocket real-time visualization
- [x] **Advanced Color Mapping**: HSV color space, easing functions, band-specific visualization
- [x] **Simulation Mode**: Development without hardware dependencies

### Phase 3: Raspberry Pi Setup (Future)
- [ ] Set up Pi Zero 2 W with BrainFlow
- [ ] Test BLE connection on Pi
- [ ] Implement data processing pipeline
- [ ] Port Pixelblaze integration to Pi

### Phase 4: Wearable Integration (Future)
- [ ] Combine EEG + motion + optional sensors
- [ ] Optimize for battery life
- [ ] Heat management
- [ ] Final LED hat assembly

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Muse S Gen 2 EEG headband
- Bluetooth-enabled computer
- Pixelblaze V3 controller (for Phase 2+)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nickbinger/mindshow.git
   cd mindshow
   ```

2. **Set up virtual environment (Modern approach)**
   ```bash
   # Install uv (modern Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Initialize project with uv
   uv sync
   ```

3. **Configure your Muse**
   - Edit `config.py` and replace `MUSE_MAC_ADDRESS` with your Muse's MAC address
   - Find your Muse's MAC address using:
     - macOS: System Preferences → Bluetooth → Muse → Advanced → MAC Address
     - Or use nRF Connect app to scan for BLE devices

4. **Test the connection**
   ```bash
   uv run python muse_connection.py
   ```

5. **Run the full system (Phase 2)**
   ```bash
   uv run python pixelblaze_integration_simple_gui.py
   ```

6. **Launch the web dashboard (Phase 2.5)**
   ```bash
   uv run python web_dashboard.py
   ```
   Then open http://localhost:8000 in your browser

## 📁 Project Structure

```
mindshow/
├── config.py                    # Configuration settings
├── pyproject.toml              # Modern Python project configuration
├── muse_connection.py           # Initial Muse connection test
├── data_monitor.py              # Text-based EEG data verification
├── eeg_visualizer.py            # Real-time EEG visualization with brainwave analysis
├── pixelblaze_integration_simple_gui.py  # ✅ WORKING: Full EEG-to-LED system
├── enhanced_led_controller.py   # 🆕 Enhanced LED animations and effects
├── web_dashboard.py             # 🆕 FastAPI web dashboard with real-time charts
├── test_colors.py               # Color mapping verification
├── test_muse_connection.py      # Muse connection testing
├── test_single_color.py         # Individual color testing
├── requirements.txt             # Legacy dependencies (being replaced)
└── README.md                   # This file
```

## 🔧 Configuration

Edit `config.py` to customize:
- Muse MAC address
- Sample rate
- Buffer sizes
- Pixelblaze IP address

## 🎨 Current Features (Phase 2.5 Complete)

### Real-time Brainwave Analysis
- **Attention Detection**: Beta wave analysis for focus/engagement
- **Relaxation Detection**: Alpha wave analysis for calm states
- **State Classification**: Automatic brain state classification
- **10Hz Update Rate**: Real-time processing and display
- **Enhanced Processing**: Logarithmic scaling and advanced filtering

### LED Control (Enhanced)
- **Advanced Color Mapping**: 
  - 🔴 **Engaged/Focused** → RED LEDs (intensity based on attention)
  - 🔵 **Relaxed/Calm** → BLUE LEDs (intensity based on relaxation)
  - 🟢 **Neutral** → GREEN LEDs
- **Smooth Transitions**: Easing functions for color changes
- **Wave Effects**: Expanding pulses and moving waves
- **Band-specific Visualization**: Different LED sections for EEG bands
- **Performance Optimization**: Manual write control and pre-allocated buffers

### Web Dashboard (New!)
- **Real-time Charts**: Plotly.js for live EEG and brain state visualization
- **Modern UI**: Responsive design with dark theme
- **Remote Monitoring**: Accessible from any device on the network
- **Interactive Controls**: Brightness and animation controls
- **WebSocket Communication**: Real-time data streaming

### GUI Interface (Legacy)
- **Real-time Display**: Live brain state, attention, and relaxation scores
- **Color-coded States**: Visual indicators for each brain state
- **Synchronized Updates**: GUI and LED changes happen together

### System Reliability
- **Enhanced Keep-alive**: Prevents Muse from sleeping
- **Connection Verification**: Robust error handling and reconnection
- **Stable Operation**: Long-running sessions without disconnections
- **Simulation Mode**: Development without hardware dependencies

## 🆕 Research Integration

This project now incorporates best practices from comprehensive development research:

### Modern Python Development
- **uv Package Manager**: Faster dependency resolution and installation
- **pyproject.toml**: Modern project configuration
- **Type Hints**: Comprehensive type annotations
- **Structured Logging**: Environment-aware logging with Loguru

### Enhanced Hardware Integration
- **Robust BLE Management**: Automatic reconnection with exponential backoff
- **Performance Optimization**: Manual LED control and pre-allocated buffers
- **Error Handling**: Graceful degradation when hardware unavailable

### Advanced Visualization
- **Web Dashboard**: FastAPI + WebSocket real-time interface
- **Interactive Charts**: Plotly.js for live data visualization
- **Responsive Design**: Works on desktop and mobile devices

### Development Tools
- **Testing Framework**: Comprehensive test suite with hardware mocking
- **Code Quality**: Ruff linting and MyPy type checking
- **CI/CD Ready**: GitHub Actions configuration

## 🐛 Troubleshooting

### Color Issues
If colors appear swapped, run the color test:
```bash
uv run python test_colors.py
```

### Connection Issues
Test Muse connection:
```bash
uv run python test_muse_connection.py
```

### Web Dashboard Issues
Check if the dashboard is running:
```bash
curl http://localhost:8000/health
```

### GUI Issues
The system uses Tkinter which may have threading issues. The core functionality works even if the GUI crashes. Consider using the web dashboard instead.

### Modern Development
To use the new uv package manager:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run with uv
uv run python your_script.py
```

## 🔬 Testing

Run the comprehensive test suite:
```bash
uv run pytest -v
```

For hardware-dependent tests:
```bash
uv run pytest -v -m "hardware"
```

## 📊 Performance

- **Real-time Processing**: 10Hz brainwave analysis
- **LED Updates**: 60 FPS smooth transitions
- **Web Dashboard**: Real-time WebSocket communication
- **Memory Usage**: Optimized with pre-allocated buffers
- **CPU Usage**: Efficient numpy-based processing

## 🤝 Contributing

This project follows modern Python development practices:
- Use `uv` for dependency management
- Follow PEP 8 with 88-character line limit
- Include type hints for all functions
- Write tests for both mocked and real hardware
- Use structured logging with Loguru

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- BrainFlow team for the excellent EEG library
- Muse team for the accessible EEG hardware
- Burning Man community for inspiration
- Research contributors for comprehensive development documentation 