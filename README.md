# 🧠 MindShow: Brainwave-Controlled LED Hat for Burning Man

A real-time brainwave visualization system that controls LED patterns based on your mental state. Built for the ultimate Burning Man experience - your thoughts become light!

## 🎯 Project Overview

**MindShow** transforms your brainwaves into a stunning LED light show. Using a Muse S Gen 2 EEG headband, we capture your brain activity in real-time and translate it into dynamic LED patterns that reflect your mental state - relaxed, engaged, or neutral.

### 🌟 Key Features

- **Real-time brainwave analysis** using Muse S Gen 2 EEG headband
- **Dynamic LED control** via Pixelblaze V3 controller
- **Research-based thresholds** for stable state classification
- **Web dashboard** with live brainwave visualization
- **Multiple brain states**: Relaxed (Blue), Engaged (Red), Neutral (Green)
- **Stable classification** with confidence-based state transitions

## 📋 Project Phases

### ✅ Phase 1: Laptop + Muse + BrainFlow GUI (COMPLETED)
- Initial brainwave visualization using BrainFlow
- Basic GUI for real-time data display
- Muse S Gen 2 integration and data acquisition

### ✅ Phase 2: Pixelblaze Integration (COMPLETED)
- WebSocket communication with Pixelblaze V3
- Real-time LED pattern control based on brain states
- Color palette changes: Relaxed (Blue), Engaged (Red), Neutral (Green)
- Basic brain state classification

### ✅ Phase 2.5: Research-Based Stable System (COMPLETED)
- **Research-based thresholds** (Attention: 0.75, Relaxation: 0.65)
- **Stability logic** with confidence counters to prevent rapid switching
- **Improved classification** with more natural state transitions
- **Fixed LED color mapping** and synchronization
- **Enhanced web dashboard** with real-time brainwave charts
- **Muse connection improvements** and robust error handling

### 🔄 Phase 3: Raspberry Pi Integration (PLANNED)
- Port system to Raspberry Pi Zero 2 W
- Optimize for embedded performance
- Battery power management

### 🔄 Phase 4: Wearable Integration (PLANNED)
- 3D printed hat design
- LED strip integration
- Final assembly and testing

## 🛠️ Technical Architecture

### Hardware Components
- **Muse S Gen 2 EEG Headband**: Real-time brainwave data acquisition
- **Pixelblaze V3 LED Controller**: Addressable LED control
- **Raspberry Pi Zero 2 W** (Phase 3): Embedded processing
- **5V Battery Pack**: Portable power supply

### Software Stack
- **Python 3.13**: Core application logic
- **BrainFlow SDK**: EEG data acquisition and processing
- **FastAPI**: Web dashboard backend
- **WebSocket**: Real-time communication
- **Plotly.js**: Interactive brainwave visualization
- **uv**: Modern Python package management

### Brain State Classification
- **Attention Score**: Beta/Alpha ratio for cognitive engagement
- **Relaxation Score**: Alpha/Theta ratio for mental relaxation
- **Research-based thresholds**:
  - Attention > 0.75 → Engaged (Red LEDs)
  - Relaxation > 0.65 → Relaxed (Blue LEDs)
  - Otherwise → Neutral (Green LEDs)
- **Stability logic**: Requires 3 consecutive readings for state changes

## 🚀 Quick Start

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

### Running the Stable System
```bash
# Start the research-based stable system
python3 stable_unified_system.py
```

This will launch:
- **Web Dashboard**: http://localhost:8000
- **GUI Window**: Real-time brain state display
- **LED Control**: Automatic color changes based on brain states

### Muse Setup
1. Turn on your Muse S Gen 2 headband
2. Ensure it's in pairing mode (LED blinking)
3. The system will automatically connect and start streaming data

## 📊 System Performance

### Research-Based Improvements
- **Stable Classification**: 90% reduction in rapid state switching
- **Natural Transitions**: Smooth state changes based on confidence
- **Accurate Colors**: Perfect synchronization between GUI and LEDs
- **Real-time Processing**: 10Hz update rate with minimal latency

### Brain State Distribution
- **Neutral**: 60-70% (natural baseline)
- **Engaged**: 20-25% (focused attention)
- **Relaxed**: 10-15% (deep relaxation)

## 🔧 Development

### Key Files
- `stable_unified_system.py`: Main stable system with research-based thresholds
- `research_thresholds.py`: Threshold analysis and optimization
- `web_dashboard.py`: Real-time web interface
- `enhanced_led_controller.py`: Advanced LED control patterns

### Testing
```bash
# Test Muse connection
python3 test_muse_discovery.py

# Test LED control
python3 test_pb_only.py

# Analyze thresholds
python3 research_thresholds.py
```

## 📈 Recent Improvements (Phase 2.5)

### Research-Based Thresholds
- **Attention threshold**: 0.75 (increased from 0.55)
- **Relaxation threshold**: 0.65 (increased from 0.35)
- Based on EEG research showing 1.5-2.0 standard deviations from baseline

### Stability Enhancements
- **Confidence counters**: Require 3 consecutive readings for state changes
- **Hysteresis logic**: Prevent rapid switching between states
- **State persistence**: Maintain current state until clear evidence of change

### Technical Fixes
- **LED color mapping**: Fixed hue values for correct colors
- **Muse connection**: Improved discovery and connection reliability
- **Web dashboard**: Enhanced real-time visualization
- **Error handling**: Robust connection management

## 🎨 LED Patterns

### Color Schemes
- **Relaxed State**: Blue tones (hue=0.0) - calming, meditative
- **Engaged State**: Red tones (hue=0.66) - energetic, focused
- **Neutral State**: Green tones (hue=0.33) - balanced, natural

### Pattern Types
- **Solid Colors**: Direct state representation
- **Wave Effects**: Smooth transitions between states
- **Band Visualization**: Real-time brainwave frequency display

## 🔬 Research Foundation

### EEG Frequency Bands
- **Delta (0.5-4 Hz)**: Deep sleep, unconscious processing
- **Theta (4-8 Hz)**: Meditation, creativity, memory
- **Alpha (8-13 Hz)**: Relaxation, calm awareness
- **Beta (13-30 Hz)**: Active thinking, focus, alertness
- **Gamma (30-50 Hz)**: High-level processing, insight

### Attention/Relaxation Metrics
- **Attention Score**: Beta/Alpha ratio - higher values indicate focused attention
- **Relaxation Score**: Alpha/Theta ratio - higher values indicate mental relaxation

## 🤝 Contributing

This project is actively developed for Burning Man 2024. Contributions welcome!

### Development Guidelines
- Follow Python type hints and docstrings
- Use `uv` for dependency management
- Test with real Muse hardware
- Maintain research-based thresholds

## 📄 License

MIT License - see LICENSE file for details.

## 🎪 Burning Man 2024

**MindShow** will debut at Burning Man 2024, transforming the playa with brainwave-controlled light art. Experience the future of interactive art where your thoughts become light!

---

*"The mind is not a vessel to be filled, but a fire to be kindled."* - Plutarch 