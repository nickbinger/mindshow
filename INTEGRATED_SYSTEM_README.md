# 🧠 MindShow Integrated System - Phase 2+3

**Lightweight, Pi-ready system with multi-Pixelblaze support**

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run the System
```bash
python integrated_mindshow_system.py
```

The system will:
1. **Auto-discover** Pixelblaze controllers on your network
2. **Connect to Muse S Gen 2** via MuseLSL (primary) or BrainFlow (fallback)
3. **Start web dashboard** at http://localhost:8000
4. **Begin real-time processing** of brain states → LED control

## 🎯 Key Features

### **Phase 2: Areas Lacking Context - ADDRESSED**
- ✅ **EEG Source Selection**: MuseLSL primary with BrainFlow fallback
- ✅ **Device Discovery**: Auto-discovery of Muse and Pixelblaze devices
- ✅ **Pi-Ready Architecture**: Lightweight, optimized for headless operation
- ✅ **Comprehensive Error Handling**: Robust reconnection and recovery

### **Phase 3: Pixelblaze WebSocket Control - IMPLEMENTED**
- ✅ **Pattern Management**: Full `listPrograms` and `activeProgramId` support
- ✅ **Multi-Device Support**: Control up to 4 Pixelblaze V3 controllers
- ✅ **Research-Based Protocol**: Text-based pattern lists, proper frame handling
- ✅ **Variable Synchronization**: Real-time variable control across devices

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MindShow Integrated System                   │
├─────────────────────────────────────────────────────────────────┤
│  EEG Processing          │  Multi-Pixelblaze Control             │
│  • MuseLSL (Primary)     │  • Auto-Discovery                     │
│  • BrainFlow (Fallback)  │  • 4x Device Support                  │
│  • Research Thresholds   │  • Pattern Management                 │
│  • State Stability       │  • Variable Sync                      │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard           │  Pi Deployment Ready                  │
│  • Real-time Monitoring  │  • Lightweight Dependencies           │
│  • Device Status         │  • Headless Operation                 │
│  • Brainwave Charts      │  • Network-First Design               │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Brain State Classification

**Research-Based Thresholds (Phase 2)**:
- **Attention**: 0.75 (Beta/Alpha ratio)
- **Relaxation**: 0.65 (Alpha/Theta ratio) 
- **Stability**: 3 consecutive readings + 2s minimum duration

**LED Mappings**:
- **Engaged** → Red, high brightness, fast patterns
- **Relaxed** → Blue, low brightness, slow patterns  
- **Neutral** → Green, medium brightness, balanced patterns

## 🎆 Multi-Pixelblaze Support

**Auto-Discovery**: Scans network (192.168.x.x) for Pixelblaze devices
**Pattern Control**: Uses Phase 3 research protocol:
```
{"listPrograms": true}        → Get pattern list
{"activeProgramId": "ID"}     → Switch pattern
{"setVars": {"hue": 0.5}}    → Control variables
```

**Synchronized Control**: All 4 devices receive coordinated updates

## 🍓 Raspberry Pi Deployment

### Pi Setup
1. **Install Raspberry Pi OS Lite** (64-bit recommended)
2. **Enable SSH and WiFi**
3. **Install Python 3.11+**
4. **Clone repository**
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Run system**: `python integrated_mindshow_system.py`

### Pi Optimizations (Auto-detected)
- **Lightweight processing**: Reduced buffer sizes
- **Network-first**: Minimal local compute
- **Error recovery**: Robust reconnection logic

## 📊 Web Dashboard

Visit **http://localhost:8000** for:
- **Real-time brain state** monitoring
- **Pixelblaze device status** (connected/patterns/variables)
- **Brainwave activity charts** (Delta, Theta, Alpha, Beta, Gamma)
- **System statistics** and health monitoring

## 🔧 Configuration

Edit `MindShowConfig` in `integrated_mindshow_system.py`:

```python
@dataclass
class MindShowConfig:
    # EEG Settings
    muse_mac_address: str = "YOUR-MUSE-MAC-HERE"
    eeg_source: str = "muselsl"  # "muselsl", "brainflow", or "auto"
    
    # Brain State Thresholds
    attention_threshold: float = 0.75
    relaxation_threshold: float = 0.65
    
    # Pixelblaze Settings
    max_controllers: int = 4
    discovery_timeout: float = 5.0
    
    # System Settings
    update_rate: float = 10.0  # Hz
    web_port: int = 8000
    pi_mode: bool = False  # Auto-detected
```

## 🚨 Troubleshooting

### EEG Connection Issues
1. **MuseLSL**: Ensure `muselsl stream` is running
2. **BrainFlow**: Check MAC address in config
3. **Permissions**: May need `sudo` for Bluetooth access

### Pixelblaze Connection Issues  
1. **Network**: Ensure devices on same WiFi network
2. **Discovery**: Check IP range in `PixelblazeDiscovery.discover_devices()`
3. **WebSocket**: Close Pixelblaze web UI to avoid conflicts

### Pi Deployment Issues
1. **Dependencies**: Use `pip install --user` if permission issues
2. **Bluetooth**: Enable with `sudo systemctl enable bluetooth`
3. **WiFi**: Configure in `/etc/wpa_supplicant/wpa_supplicant.conf`

## 📁 Project Structure

```
mindshow/
├── integrated_mindshow_system.py    # 🎯 MAIN INTEGRATED SYSTEM
├── requirements.txt                 # Dependencies
├── config/                         # Configuration files
├── deep_research/                  # Phase research docs
├── Old/                           # Archived previous implementation
│   ├── src/                      # Previous modular code
│   ├── tests/                    # Previous test files  
│   └── *.py                      # Previous individual scripts
├── README.md                      # Original project README
├── PROJECT_OVERVIEW.md            # Updated project phases
├── CURRENT_STATUS.md              # Updated status
└── INTEGRATED_SYSTEM_README.md    # 📖 This file
```

## 🎉 Success Metrics

The integrated system successfully addresses **Phase 2** and **Phase 3** requirements:

### Phase 2 ✅
- **Context provided** for EEG setup, Pixelblaze configuration, Pi deployment
- **MuseLSL integration** with BrainFlow fallback
- **Auto-discovery** for seamless device setup
- **Pi optimization** for production deployment

### Phase 3 ✅  
- **WebSocket pattern control** using research-based protocol
- **Multi-device support** for 4 Pixelblaze controllers
- **Pattern list management** with text-based parsing
- **Variable synchronization** across all devices

**Ready for Phase 4**: Raspberry Pi Integration and Phase 5: Multi-device coordination!

