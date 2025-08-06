# MindShow Repository Navigation Guide

*Your expanded context and memory for the MindShow project*

## 🎯 Quick Start

**If you're new to this repository or returning after a break, start here:**

1. **Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Complete project context
2. **Check [CURRENT_STATUS.md](CURRENT_STATUS.md)** - What's working and what needs attention
3. **Review [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - System design and components
4. **Explore [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md)** - All research findings in one place

## 📁 Repository Structure

### **📚 Documentation (`docs/`)**
- **[RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md)** - All research findings consolidated
- **[BRAINFLOW_RESEARCH_DOCUMENTATION.md](docs/BRAINFLOW_RESEARCH_DOCUMENTATION.md)** - Industry-standard EEG processing
- **[MUSELSL2_RESEARCH_DOCUMENTATION.md](docs/MUSELSL2_RESEARCH_DOCUMENTATION.md)** - Lightweight Muse integration
- **[PIXELBLAZE_RESEARCH_DOCUMENTATION.md](docs/PIXELBLAZE_RESEARCH_DOCUMENTATION.md)** - LED control libraries
- **[PIXELBLAZE_ASYNC_RESEARCH.md](docs/PIXELBLAZE_ASYNC_RESEARCH.md)** - Async LED control
- **[PIXELBLAZE_PATTERNS_RESEARCH.md](docs/PIXELBLAZE_PATTERNS_RESEARCH.md)** - 139+ LED patterns

### **🔧 Source Code (`src/`)**
- **[eeg/](src/eeg/)** - EEG processing and brainwave analysis
- **[pixelblaze/](src/pixelblaze/)** - LED control and pattern management
- **[integration/](src/integration/)** - System integration components
- **[utils/](src/utils/)** - Utilities and helpers

### **🧪 Testing (`tests/`)**
- **[test_*.py](tests/)** - All test files organized by component
- **[examples/](examples/)** - Working example implementations

### **⚙️ Configuration (`config/`)**
- **[config.py](config/config.py)** - Main configuration
- **[requirements.txt](config/requirements.txt)** - Dependencies

## 🎯 Key Files by Purpose

### **🚀 Production-Ready Components**
- **[robust_websocket_controller.py](src/pixelblaze/robust_websocket_controller.py)** - Production LED controller
- **[stable_unified_system.py](src/integration/stable_unified_system.py)** - Complete working system
- **[enhanced_led_controller.py](src/pixelblaze/enhanced_led_controller.py)** - Advanced LED control

### **🔬 Research & Development**
- **[research_thresholds.py](src/eeg/research_thresholds.py)** - Brainwave threshold research
- **[debug_*.py](tests/debug_*.py)** - Debugging and testing tools
- **[test_*.py](tests/test_*.py)** - Component testing

### **📖 Guides & Documentation**
- **[PIXELBLAZE_CONTROL_GUIDE.md](docs/PIXELBLAZE_CONTROL_GUIDE.md)** - How to control Pixelblaze
- **[PIXELBLAZE_READY_TO_TEST.md](docs/PIXELBLAZE_READY_TO_TEST.md)** - Testing instructions
- **[PHASE_2_5_DOCUMENTATION.md](docs/PHASE_2_5_DOCUMENTATION.md)** - Phase completion docs

## 🔍 Finding Information Quickly

### **Need to understand the project?**
→ Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### **Want to see what's currently working?**
→ Check [CURRENT_STATUS.md](CURRENT_STATUS.md)

### **Looking for EEG processing options?**
→ Review [RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md) → BrainFlow or MuseLSL2 sections

### **Need LED control solutions?**
→ Review [RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md) → Pixelblaze sections

### **Want to test something?**
→ Check [CURRENT_STATUS.md](CURRENT_STATUS.md) → Testing section

### **Need to deploy?**
→ Read [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

## 🎯 Context Recovery Strategy

**If you're returning to this project after a break:**

1. **Start with [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Get the big picture
2. **Check [CURRENT_STATUS.md](CURRENT_STATUS.md)** - See what's working
3. **Review [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - Understand the system
4. **Scan [RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md)** - Find relevant research
5. **Look at [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - For production deployment

## 📋 Quick Reference

### **Current Working Components**
- ✅ **robust_websocket_controller.py** - Production LED controller
- ✅ **stable_unified_system.py** - Complete working system
- ✅ **BrainFlow integration** - Professional EEG processing
- ✅ **MuseLSL2 integration** - Lightweight Muse streaming
- ✅ **Pixelblaze patterns** - 139+ LED patterns available

### **Next Steps**
- 🔄 **Test Pixelblaze connection** - When device comes online
- 🔄 **Integrate BrainFlow** - Professional EEG processing
- 🔄 **Deploy production system** - Complete MindShow installation

### **Key Research Findings**
- **BrainFlow** - Industry-standard EEG processing (1.5k stars)
- **MuseLSL2** - Lightweight Muse integration (fixed timestamps)
- **Pixelblaze-Async** - Async LED control with MQTT
- **PixelblazePatterns** - 139+ production-ready patterns

## 🚀 Getting Started

### **For Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Test current system
python src/integration/stable_unified_system.py

# Test LED control (when Pixelblaze online)
python src/pixelblaze/robust_websocket_controller.py
```

### **For Research**
```bash
# Review research findings
open docs/RESEARCH_SUMMARY.md

# Check current status
open CURRENT_STATUS.md
```

### **For Deployment**
```bash
# Follow deployment guide
open docs/DEPLOYMENT_GUIDE.md
```

---

*This document serves as your expanded context and memory for the MindShow project. Update it as the project evolves.* 