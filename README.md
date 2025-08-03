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

2. **Set up virtual environment**
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Muse**
   - Edit `config.py` and replace `MUSE_MAC_ADDRESS` with your Muse's MAC address
   - Find your Muse's MAC address using:
     - macOS: System Preferences → Bluetooth → Muse → Advanced → MAC Address
     - Or use nRF Connect app to scan for BLE devices

5. **Test the connection**
   ```bash
   python muse_connection.py
   ```

6. **Run the full system (Phase 2)**
   ```bash
   python pixelblaze_integration_simple_gui.py
   ```

## 📁 Project Structure

```
mindshow/
├── config.py                    # Configuration settings
├── muse_connection.py           # Initial Muse connection test
├── data_monitor.py              # Text-based EEG data verification
├── eeg_visualizer.py            # Real-time EEG visualization with brainwave analysis
├── pixelblaze_integration_simple_gui.py  # ✅ WORKING: Full EEG-to-LED system
├── test_colors.py               # Color mapping verification
├── test_muse_connection.py      # Muse connection testing
├── test_single_color.py         # Individual color testing
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

Edit `config.py` to customize:
- Muse MAC address
- Sample rate
- Buffer sizes
- Pixelblaze IP address

## 🎨 Current Features (Phase 2 Complete)

### Real-time Brainwave Analysis
- **Attention Detection**: Beta wave analysis for focus/engagement
- **Relaxation Detection**: Alpha wave analysis for calm states
- **State Classification**: Automatic brain state classification
- **10Hz Update Rate**: Real-time processing and display

### LED Control
- **Color Mapping**: 
  - 🔴 **Engaged/Focused** → RED LEDs
  - 🔵 **Relaxed/Calm** → BLUE LEDs  
  - 🟢 **Neutral** → GREEN LEDs
- **Brightness Control**: Dynamic brightness based on brainwave intensity
- **Real-time Updates**: Synchronized GUI and LED updates

### GUI Interface
- **Real-time Display**: Live brain state, attention, and relaxation scores
- **Color-coded States**: Visual indicators for each brain state
- **Synchronized Updates**: GUI and LED changes happen together

### System Reliability
- **Enhanced Keep-alive**: Prevents Muse from sleeping
- **Connection Verification**: Robust error handling and reconnection
- **Stable Operation**: Long-running sessions without disconnections

## 🐛 Troubleshooting

### Color Issues
If colors appear swapped, run the color test:
```bash
python test_colors.py
```

### Connection Issues
Test Muse connection:
```bash
python test_muse_connection.py
```

### GUI Issues
The system uses Tkinter which may have threading issues. The core functionality works even if the GUI crashes. 