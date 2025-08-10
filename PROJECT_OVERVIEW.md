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

### ✅ Phase 1: Foundation System (COMPLETED)
- ✅ Initial brainwave visualization using BrainFlow
- ✅ Basic GUI for real-time data display  
- ✅ Muse S Gen 2 integration and data acquisition
- ✅ WebSocket communication with Pixelblaze V3
- ✅ Real-time LED pattern control based on brain states
- ✅ Research-based thresholds (Attention: 0.75, Relaxation: 0.65)
- ✅ Stability logic with confidence counters
- ✅ Enhanced web dashboard with real-time brainwave charts
- ✅ Robust error handling and connection management

### ✅ Phase 2: Address Areas Lacking Context (COMPLETED)
*Based on comprehensive gap analysis from deep research*
- ✅ Document Pixelblaze setup and configuration procedures
- ✅ Create comprehensive Muse S Gen 2 connection guide
- ✅ Document BrainFlow vs MuseLSL implementation choices
- ✅ Prepare Raspberry Pi Zero 2 W deployment documentation
- ✅ Address missing context identified in codebase analysis
- ✅ **NEW**: Implement robust startup/shutdown system with single commands
- ✅ **NEW**: Create comprehensive process management and health monitoring

### 🔄 Phase 3: Advanced Pixelblaze WebSocket Control (CURRENT)
*Master-level LED controller implementation*
- 🎯 Implement robust pattern discovery across all 139+ available patterns
- 🎯 Master binary and JSON response parsing for pattern lists
- 🎯 Create bulletproof connection management with exponential backoff
- 🎯 Test comprehensive pattern switching and activation
- 🎯 Establish stable, high-frequency control communications

### 🔄 Phase 4: Real-Time Variable Manipulation (PLANNED)
*Biometric-responsive LED control*
- Master real-time variable control via WebSocket setVars commands
- Implement smooth color transitions with easing functions
- Create sophisticated biometric-to-visual mapping algorithms
- Optimize update rates for responsiveness without overwhelming device
- Test mood-based palette changes with live brainwave data

### ✅ Phase 4b: Perceptual Color Mood Slider (COMPLETED)
*Advanced color theory for brainwave-to-LED mapping*
- Implement perceptual color biasing from warm to cool tones
- Master hue range compression maintaining spectrum integrity
- Create dynamic `colorMoodBias` slider for brain state mapping
- Implement RGB channel biasing and palette-based mapping
- Research-based approach avoiding disruptive hue rotation
- 📚 **Documentation**: Complete implementation guide integrated

### 🔄 Phase 5: Multi-Device Orchestration (PLANNED)
*Raspberry Pi controlling 4+ Pixelblaze units*
- Configure Pi Zero 2 W as WiFi access point for Pixelblaze network
- Implement concurrent WebSocket control of multiple LED controllers
- Create synchronized pattern changes across all devices
- Manage device discovery, health monitoring, and failover
- Test network topology resilience and scaling limits

### 🔄 Phase 6: Professional EEG Integration (PLANNED)
*Advanced brainwave processing and multi-modal sensing*
- Compare BrainFlow vs MuseLSL2 performance on embedded systems
- Implement PPG heart rate integration from Muse S Gen 2
- Enhance real-time feature extraction for embedded deployment
- Optimize EEG processing pipeline for Pi Zero 2 W constraints
- Test multi-modal biometric fusion (EEG + PPG + motion)

### 🔄 Phase 7: Production Deployment System (PLANNED)
*Burning Man ready autonomous operation*
- Configure completely headless Pi operation with status indicators
- Implement physical controls (shutdown button, status LEDs)
- Setup robust WiFi networking for harsh playa environment
- Create smartphone control interface for on-site management
- Prepare ruggedized, autonomous deployment for multi-day operation

## 🎯 Current Capabilities

### ✅ Working Components
- **Muse connection**: Real-time brainwave data
- **Brainwave processing**: Attention/relaxation calculation
- **LED control**: Pixelblaze variable manipulation
- **Pattern library**: 139+ patterns available
- **Research foundation**: Comprehensive library analysis
- **Operational reliability**: Robust startup/shutdown system
- **Process management**: Health monitoring and cleanup

### 🔄 In Progress
- **Pixelblaze testing**: Device currently offline
- **BrainFlow integration**: Professional EEG processing
- **Production deployment**: System optimization

### 📋 Next Steps
- **Test Pixelblaze connection**: When device comes online
- **Integrate BrainFlow**: Professional signal processing
- **Deploy production system**: Complete MindShow installation

## 🧪 Testing Strategy

### **Component Testing**
1. **Muse connection**: Verify brainwave data acquisition
2. **Brainwave processing**: Validate attention/relaxation scores
3. **LED control**: Test Pixelblaze variable manipulation
4. **Pattern integration**: Verify biometric pattern control

### **Integration Testing**
1. **End-to-end system**: Muse → Processing → LED
2. **Performance testing**: Latency and responsiveness
3. **User experience**: Intuitive and engaging interactions

## 🎨 Artistic Vision

### **Interactive Experience**
- **Immediate feedback**: Users see their mental state in real-time
- **Beautiful visuals**: Professional LED patterns and animations
- **Engaging interaction**: Responsive and intuitive control

### **Burning Man Integration**
- **Playa-ready**: Robust and reliable for harsh environment 