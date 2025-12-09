# Firestorm - Pixelblaze Centralized Control Console

**Source**: [https://github.com/simap/Firestorm](https://github.com/simap/Firestorm)  
**License**: See original repository  
**Status**: External reference code - Under evaluation for integration

## Overview

Firestorm is a centralized control console for Pixelblaze WiFi LED controllers. It provides:

- **Automatic Device Discovery**: Uses UDP broadcast packets (firmware v2.10+) to automatically detect all Pixelblaze controllers on a network
- **Time Synchronization**: NTP-like algorithm for synchronized animations across multiple devices
- **Pattern Management**: Network-wide pattern switching and sequence creation
- **HTTP API**: RESTful API for automation and integration
- **Web UI**: React-based interface for pattern control

## Key Features

### 1. UDP Discovery System (`app/discovery.js`)
- Listens on UDP port 1889 for Pixelblaze beacon packets
- Automatically detects devices without manual IP configuration
- Implements time synchronization protocol
- Maintains device registry with last-seen tracking

### 2. WebSocket Controller (`app/controller.js`)
- Manages WebSocket connections to individual Pixelblaze devices
- Handles pattern list retrieval and parsing
- Implements command queuing and retry logic
- Supports program cloning and management

### 3. HTTP API (`app/api.js`)
- `/discover` (GET): Returns all known Pixelblaze controllers
- `/command` (POST/GET): Sets command states for specified devices
- `/reload` (POST): Triggers config/pattern reload from all controllers
- `/clonePrograms` (POST): Clones programs from one controller to others
- `/controllers/:sourceId/dump` (GET): Exports all patterns as ZIP file

### 4. React Web UI (`src/`)
- Pattern discovery and grouping across network
- Playlist creation and management
- Pattern cloning interface
- Real-time device status

## Technical Architecture

```
┌─────────────────┐
│  UDP Discovery  │───▶ Listens on port 1889 for beacon packets
│  (discovery.js)  │    Responds with time sync packets
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Controller    │───▶ WebSocket connection per device (port 81)
│ (controller.js) │    Pattern list, config, command management
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   HTTP API      │───▶ Express server (port 80/3000)
│    (api.js)     │    REST endpoints for automation
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   React UI      │───▶ Browser-based control interface
│   (src/App.js)  │    Pattern selection and playlist management
└─────────────────┘
```

## Comparison with MindShow

| Feature | Firestorm | MindShow (Current) |
|---------|-----------|-------------------|
| **Device Discovery** | ✅ Automatic UDP broadcast | ✅ Manual IP configuration |
| **Multi-Device Control** | ✅ Centralized console | ✅ MultiPixelblazeController class |
| **Pattern Switching** | ✅ Network-wide sync | ✅ Per-device WebSocket control |
| **Time Sync** | ✅ NTP-like algorithm | ❌ Not implemented |
| **Brainwave Integration** | ❌ Not applicable | ✅ Real-time EEG control |
| **Color Mood System** | ❌ Not applicable | ✅ Perceptual color biasing |
| **Web Dashboard** | ✅ Pattern management UI | ✅ Brainwave visualization + controls |
| **API** | ✅ HTTP REST API | ✅ FastAPI with WebSocket |

## Potential Integration Opportunities

### 1. **Device Discovery Enhancement** (High Priority)
- Replace manual IP configuration with Firestorm's UDP discovery
- Auto-detect Pixelblaze devices on startup
- Reduce configuration overhead for Burning Man deployment

**Implementation Approach**:
- Port UDP discovery logic to Python (using `socket` module)
- Integrate into `MultiPixelblazeController` initialization
- Maintain backward compatibility with manual IP configuration

### 2. **Time Synchronization** (Medium Priority)
- Add pattern timer sync across multiple devices
- Useful for coordinated light shows with multiple Pixelblaze units
- Implement NTP-like algorithm in Python

**Implementation Approach**:
- Port time sync protocol from `discovery.js`
- Add sync endpoint to MindShow API
- Optional feature for multi-device setups

### 3. **Pattern Management** (Low Priority)
- Use Firestorm's pattern cloning for deployment
- Leverage pattern discovery across network
- Could be useful for managing patterns across multiple devices

**Implementation Approach**:
- Evaluate if needed for Burning Man deployment
- May be overkill for single-device or small setups

### 4. **Hybrid Approach** (Recommended)
- Keep MindShow's brainwave control and color mood system
- Integrate Firestorm's discovery mechanism
- Use Firestorm's time sync for multi-device coordination
- Best of both worlds: automatic discovery + brainwave control

## Code Structure

```
external/firestorm/
├── app/                    # Server-side code
│   ├── discovery.js        # UDP discovery and time sync
│   ├── controller.js       # WebSocket controller per device
│   ├── api.js              # HTTP API endpoints
│   └── README.md           # Server app documentation
├── src/                    # React web app
│   ├── App.js              # Main React component
│   ├── PatternView.js      # Pattern display component
│   ├── index.js            # React entry point
│   └── README.md           # Web app documentation
├── public/                 # Static web assets
├── assets/                 # Images and resources
├── server.js               # Express server entry point
├── package.json            # Node.js dependencies
└── README.md               # This file
```

## Key Implementation Details

### UDP Discovery Protocol
- **Port**: 1889 (UDP)
- **Packet Types**: 
  - `BEACONPACKET` (42): Device discovery
  - `TIMESYNC` (43): Time synchronization
- **Packet Format**: 12+ bytes
  - Bytes 0-3: Packet type (UInt32LE)
  - Bytes 4-7: Sender ID (UInt32LE)
  - Bytes 8-11: Sender time (UInt32LE)

### WebSocket Protocol
- **Port**: 81 (WebSocket)
- **Message Types**: JSON commands and binary data
- **Key Commands**:
  - `{getConfig: true, listPrograms: true}`: Get device info
  - `{activeProgramId: "..."}`: Switch pattern
  - `{brightness: 0.5}`: Set brightness

### HTTP API Endpoints
- **Base URL**: `http://localhost:80` (or custom port)
- **Discovery**: `GET /discover` - Returns all devices
- **Command**: `POST /command` - Send commands to devices
- **Reload**: `POST /reload` - Refresh all device configs
- **Clone**: `POST /clonePrograms` - Copy patterns between devices

## Evaluation Checklist

### Phase 1: Code Review ✅
- [x] Clone Firestorm repository
- [x] Review discovery mechanism
- [x] Review WebSocket controller implementation
- [x] Review HTTP API design
- [x] Document key features and architecture

### Phase 2: Integration Planning (Next)
- [ ] Evaluate UDP discovery porting to Python
- [ ] Design integration with `MultiPixelblazeController`
- [ ] Plan time sync implementation (if needed)
- [ ] Assess impact on existing MindShow architecture
- [ ] Create integration roadmap

### Phase 3: Implementation (Future)
- [ ] Port UDP discovery to Python
- [ ] Integrate with MindShow startup
- [ ] Test automatic device detection
- [ ] Implement time sync (optional)
- [ ] Update documentation

## Dependencies

**Node.js Stack** (Firestorm original):
- Node.js (LTS version)
- Yarn package manager
- Express.js
- React
- WebSocket (ws)

**Python Stack** (MindShow):
- Python 3.13
- FastAPI
- WebSocket support (websockets)
- Socket programming (socket)

## Notes

- This is **reference code** for evaluation purposes
- Firestorm is written in **Node.js/JavaScript**
- MindShow is written in **Python**
- Integration will require **porting key features** to Python
- Focus on **discovery mechanism** as primary integration target
- Time sync may be useful for multi-device Burning Man setup

## References

- **Original Repository**: https://github.com/simap/Firestorm
- **Pixelblaze Documentation**: https://www.bhencke.com/pixelblaze
- **MindShow Integration**: See `PROJECT_OVERVIEW.md` for integration roadmap

---

*Last Updated: August 13, 2025 - Code pulled for evaluation*
