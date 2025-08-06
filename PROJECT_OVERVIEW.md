# MindShow Project Overview

*Brainwave-controlled LED art installation for Burning Man 2025*

## 🎯 Project Vision

**MindShow** is an interactive art installation that transforms brainwave data into real-time LED animations. Users wear a Muse EEG headband, and their mental state (attention, relaxation) controls the speed, color, and patterns of LED displays.

### **Core Concept**
- **Input**: Muse S Gen 2 EEG headband (brainwave data)
- **Processing**: Real-time brainwave analysis (attention/relaxation scores)
- **Output**: Pixelblaze LED controller with dynamic patterns
- **Experience**: Your thoughts become light art

## 🎪 Burning Man 2025

**MindShow** will debut at Burning Man 2025, creating an immersive experience where participants can see their mental states visualized in real-time through beautiful LED animations.

## 🧠 Technical Architecture

### **Data Flow**
```
Muse EEG → Brainwave Processing → Mood Index → LED Control → Visual Art
```

### **Key Components**

#### **1. EEG Data Acquisition**
- **Device**: Muse S Gen 2 EEG headband
- **Channels**: TP9, AF7, AF8, TP10 (4 EEG channels)
- **Sampling Rate**: 256 Hz
- **Data**: Raw EEG + band powers (Delta, Theta, Alpha, Beta, Gamma)

#### **2. Brainwave Processing**
- **Attention Score**: Beta/Alpha ratio (engagement level)
- **Relaxation Score**: Alpha/Theta ratio (calmness level)
- **Thresholds**: Attention > 0.75, Relaxation > 0.65
- **Stability**: 3 consecutive readings for state changes

#### **3. LED Control**
- **Device**: Pixelblaze V3 LED controller
- **Connection**: WebSocket (ws://192.168.0.241:81)
- **Control Axes**:
  - **Speed**: 80%-120% range based on attention
  - **Color**: ROYGBIV spectrum based on mood
  - **Brightness**: Based on relaxation level

#### **4. Pattern Library**
- **139+ patterns** from ZRanger1's collection
- **Categories**: 1D, 2D/3D, Experimental, Multisegment
- **Biometric integration**: Speed, color, complexity control

## 🔬 Research Foundation

### **EEG Processing Libraries**
1. **BrainFlow** (1.5k stars) - Industry-standard EEG processing
   - Advanced signal filtering and feature extraction
   - Multi-device support and production-ready
   - Professional-grade artifact removal

2. **MuseLSL2** (9 stars) - Lightweight Muse integration
   - Fixed timestamp accuracy issues
   - Complete channel streaming (EEG, PPG, motion)
   - Simple installation and reliable streaming

### **LED Control Libraries**
1. **pixelblaze-client** - Synchronous LED control
2. **Pixelblaze-Async** - Async control with MQTT
3. **PixelblazePatterns** - 139+ production-ready patterns

## 🚀 Development Phases

### **✅ Phase 1: Muse Integration (COMPLETED)**
- Muse S Gen 2 connection established
- Real-time brainwave data acquisition
- Basic attention/relaxation calculation

### **✅ Phase 2: LED Control (COMPLETED)**
- Pixelblaze WebSocket connection
- Variable control (hue, brightness, speed)
- Pattern switching and management

### **✅ Phase 3: Custom Pixelblaze Pattern Coding (COMPLETED)**
- Universal pattern control system
- Speed control (80%-120% range)
- Color palette control (ROYGBIV spectrum)
- Enhanced mood index with multi-source data
- Real-time responsiveness (<100ms latency)

### **🔄 Phase 4: Raspberry Pi Integration (PLANNED)**
- Port system to Raspberry Pi Zero 2 W
- Optimize for embedded performance
- Production deployment preparation

### **🔄 Phase 5: Production Deployment (PLANNED)**
- Burning Man 2025 installation
- Multi-device synchronization
- Environmental robustness

## 🎯 Current Capabilities

### **✅ Working Components**
- **Muse connection**: Real-time brainwave data
- **Brainwave processing**: Attention/relaxation calculation
- **LED control**: Pixelblaze variable manipulation
- **Pattern library**: 139+ patterns available
- **Research foundation**: Comprehensive library analysis

### **🔄 In Progress**
- **Pixelblaze testing**: Device currently offline
- **BrainFlow integration**: Professional EEG processing
- **Production deployment**: System optimization

### **📋 Next Steps**
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
- **Scalable**: Can control multiple LED installations
- **Accessible**: Easy for participants to understand and use

## 🔬 Scientific Foundation

### **Brainwave Analysis**
- **Attention**: Beta/Alpha ratio (13-30Hz / 8-13Hz)
- **Relaxation**: Alpha/Theta ratio (8-13Hz / 4-8Hz)
- **Thresholds**: Research-based values for reliable detection
- **Stability**: Prevents rapid state switching

### **LED Control Mapping**
- **Speed**: 80%-120% range based on attention level
- **Color**: ROYGBIV spectrum based on mood state
- **Brightness**: Based on relaxation level
- **Patterns**: Dynamic selection based on mental state

## 🚀 Production Goals

### **Burning Man 2025**
- **Installation**: Interactive LED art piece
- **Experience**: Brainwave-controlled light show
- **Impact**: Memorable and engaging participant experience

### **Technical Requirements**
- **Reliability**: Robust operation in harsh environment
- **Performance**: Real-time responsiveness (<100ms)
- **Scalability**: Support multiple users and installations
- **Maintainability**: Easy troubleshooting and updates

## 📚 Documentation Strategy

### **Self-Documenting Repository**
- **Navigation guide**: Quick access to all information
- **Research summaries**: Consolidated findings
- **Status tracking**: Current working components
- **Deployment guides**: Production-ready instructions

### **Context Recovery**
- **Project overview**: Complete context in one place
- **Current status**: What's working and what needs attention
- **Architecture guide**: System design and components
- **Research summary**: All findings consolidated

---

*This document provides complete context for the MindShow project. Update as the project evolves.* 