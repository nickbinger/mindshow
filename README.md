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
- [ ] Pair Muse via BLE
- [ ] Connect to Muse via BrainFlow
- [ ] Add basic GUI/visualization
- [ ] Commit and push to GitHub

### Phase 2: Raspberry Pi Setup (Future)
- [ ] Set up Pi Zero 2 W with BrainFlow
- [ ] Test BLE connection on Pi
- [ ] Implement data processing pipeline

### Phase 3: LED Integration (Future)
- [ ] Connect to Pixelblaze via WebSocket
- [ ] Design LED patterns for different brain states
- [ ] Test LED control

### Phase 4: Wearable Integration (Future)
- [ ] Combine EEG + motion + optional sensors
- [ ] Optimize for battery life
- [ ] Heat management

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Muse S Gen 2 EEG headband
- Bluetooth-enabled computer

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

## 📁 Project Structure

```
mindshow/
├── config.py              # Configuration settings
├── muse_connection.py     # Initial Muse connection test
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

Edit `config.py` to customize:
- Muse MAC address
- Sample rate
- Buffer sizes
- Logging levels

## 📊 Expected Output

When running `muse_connection.py` successfully, you should see:
```
INFO - Data shape: (5, 1280)
INFO - Number of channels: 5
INFO - Number of samples: 1280
INFO - Sample data from first channel:
INFO - First 10 samples: [123.45, 124.67, ...]
INFO - Data range: -500.00 to 500.00
```

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to connect to Muse"**
   - Ensure Muse is turned on and in pairing mode
   - Verify MAC address in `config.py`
   - Check Bluetooth is enabled
   - Try using nRF Connect to verify Muse is advertising

2. **"Permission denied" errors**
   - On macOS, grant Bluetooth permissions to Terminal/VS Code
   - On Linux, ensure user is in `bluetooth` group

3. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## 🤝 Contributing

This is a personal project for Burning Man 2024. Feel free to fork and adapt for your own projects!

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- BrainFlow team for the excellent EEG library
- Muse team for the accessible EEG hardware
- Burning Man community for inspiration 