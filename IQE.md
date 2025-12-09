# IQE Integration Guide

## Overview

**IQE** (In Queso Emergency) is the LX Studio/Chromatik LED control system located at `~/src/iqe`.
**MindShow** sends brainwave data to IQE via OSC (Open Sound Control) on port **3232**.

### The Connection:
```
MindShow (brainwaves) → OSC port 3232 → LX Studio → MindshowEffect → LEDs
```

MindShow calculates brain states and sends:
- `colorBlend` - Brain state color (0.0=relaxed/blue → 1.0=engaged/red)
- `speed` - Animation speed based on engagement level

IQE's `MindshowEffect.java` receives these OSC messages and colors the LEDs accordingly.

---

## IQE Components

### 1. **LX/Chromatik** (Core - Java)
- LED pattern engine
- Listens for OSC on port 3232
- Sends OSC responses on port 3333
- Location: `~/src/iqe`

### 2. **Control UI** (Optional - TypeScript/Web)
- Web interface for LX parameter control
- Runs on http://localhost:8282
- OSC bridge on port 8080

### 3. **Flamecaster** (Optional - Python)
- ArtNet router for PixelBlaze devices
- Routes LED data from LX to PixelBlaze controllers
- Location: `~/src/Flamecaster`

### 4. **NodeJS OSC Bridge** (Legacy)
- Older OSC bridge system
- Mostly replaced by Control UI

---

## Prerequisites (One-time Setup)

```bash
# Install Node dependencies for IQE workspaces
cd ~/src/iqe
npm install  # Root dependencies
cd src/control-ui && npm install
cd ../nodejs && npm install
cd ../..

# Build Java project
./mvnw clean package -DskipTests

# Download Chromatik if needed
./src/scripts/download_chromatik.sh
```

---

## Manual Startup Instructions

### Component 1: Flamecaster (Optional - for PixelBlaze ArtNet routing)

**Terminal 1:**
```bash
cd ~/src/Flamecaster
python -m Flamecaster --file ../iqe/src/main/resources/flamecaster-config.conf
```

**What it does:** Routes ArtNet packets from LX to PixelBlaze controllers over WiFi
**Skip if:** You're not using PixelBlaze devices

---

### Component 2: Control UI (Web Interface)

**Terminal 2:**
```bash
cd ~/src/iqe/src/control-ui

# Option A: Development mode (auto-reload)
npm run start:dev
# Web UI at http://localhost:8282

# Option B: Production mode
npm run build && npm run start
```

**What it does:**
- Web UI for controlling LX parameters via OSC
- TypeScript server bridges web UI to OSC
- Access at: http://localhost:8282

**Ports:**
- Web server: 8282
- OSC bridge: 8080

---

### Component 3: NodeJS OSC Bridge (Alternative/Legacy)

**Terminal 3 (if NOT using Control UI):**
```bash
cd ~/src/iqe/src/nodejs

# Set environment variables
export IQE_WEB_PORT=80
export IQE_APP_OSC_TO_PORT=3232    # Send to LX
export IQE_APP_OSC_FROM_PORT=3333  # Receive from LX

node scripts.js bridge
```

**What it does:** Older OSC bridge system (Control UI is preferred)

---

### Component 4: LX/Chromatik (Core LED System)

**Terminal 4:**
```bash
cd ~/src/iqe

# Build if needed
./mvnw clean package -DskipTests

# Run LX/Chromatik
java $( [[ $(uname) == 'Darwin' ]] && echo "-XstartOnFirstThread" ) \
    -cp ./target/iqe-1.0-SNAPSHOT-jar-with-dependencies.jar:./vendor/glxstudio.jar \
    heronarts.lx.studio.ChromatikIQE iqe.lxp
```

**What it does:**
- Launches Chromatik/LX Studio GUI
- Loads project file `iqe.lxp`
- Listens for OSC on port 3232
- Sends OSC responses on port 3333

---

## Recommended Startup Sequences

### Minimal Setup (MindShow → LX Only)

**Terminal 1: Start LX**
```bash
cd ~/src/iqe
java $( [[ $(uname) == 'Darwin' ]] && echo "-XstartOnFirstThread" ) \
    -cp ./target/iqe-1.0-SNAPSHOT-jar-with-dependencies.jar:./vendor/glxstudio.jar \
    heronarts.lx.studio.ChromatikIQE iqe.lxp
```

**Wait for LX GUI to fully load**, then:

**Terminal 2: Start MindShow**
```bash
cd ~/src/mindshow
source .venv/bin/activate
export DYLD_LIBRARY_PATH=/opt/homebrew/lib
python integrated_mindshow_system.py
```

**Requirements:**
- Muse S Gen 2 headband powered on and in pairing mode (LED blinking)
- Bluetooth enabled on laptop

---

### Full Setup (All Components)

**Terminal 1: Flamecaster (if using PixelBlaze)**
```bash
cd ~/src/Flamecaster
python -m Flamecaster --file ../iqe/src/main/resources/flamecaster-config.conf
```

**Terminal 2: Control UI**
```bash
cd ~/src/iqe/src/control-ui
npm run start:dev
```

**Terminal 3: LX/Chromatik**
```bash
cd ~/src/iqe
java $( [[ $(uname) == 'Darwin' ]] && echo "-XstartOnFirstThread" ) \
    -cp ./target/iqe-1.0-SNAPSHOT-jar-with-dependencies.jar:./vendor/glxstudio.jar \
    heronarts.lx.studio.ChromatikIQE iqe.lxp
```

**Terminal 4: MindShow**
```bash
cd ~/src/mindshow
source .venv/bin/activate
export DYLD_LIBRARY_PATH=/opt/homebrew/lib
python integrated_mindshow_system.py
```

---

## Using the Automatic Startup Script

**Quick Start (all-in-one):**
```bash
cd ~/src/iqe
./RUN.sh
```

This automatically starts:
1. Flamecaster (if configured)
2. Control UI
3. LX/Chromatik

Then manually start MindShow in a separate terminal.

---

## Useful npm Scripts

From `~/src/iqe` directory:

```bash
# Control UI shortcuts
npm run control         # Build + start control UI
npm run control:dev     # Dev mode with hot reload

# OSC Bridge (legacy)
npm run bridge          # Start nodejs OSC bridge

# Other tools
npm run midi            # Start MIDI bridge
npm run render          # Start ArtNet visualization
npm run lxp             # Rebuild LX project fixtures

# Java
npm run build:java      # Build Java project
npm run run:lx          # Run LX (same as ./RUN.sh)

# Setup
npm run install:all     # Install all workspace dependencies
npm run clean           # Remove all node_modules
```

---

## What You'll See When Running

### MindShow Dashboard (http://localhost:8000)
- Real-time brainwave visualization (Alpha, Beta, Theta, Delta, Gamma bands)
- Attention/relaxation scores
- Color mood indicator
- Interactive manual controls

### Control UI (http://localhost:8282)
- LX parameter sliders
- Channel controls
- Pattern selection
- Effect controls

### LX Studio GUI
- Pattern visualization
- Add/enable `MindshowEffect` in the effects chain
- Watch LEDs respond to brain state:
  - **Relaxed** → Blue tones, slower pulse
  - **Focused** → Red tones, faster pulse
  - **Neutral** → Purple/magenta blend

### Monitor OSC Communication

**MindShow logs:**
```bash
tail -f /tmp/mindshow.log | grep "OSC"

# You'll see messages like:
# "🎵 OSC auto-sent to LX: colorBlend=0.452, speed=0.510"
```

**Check MindShow is sending OSC:**
```bash
# In MindShow output, look for:
# "🎵 OSC client initialized for LX communication on port 3232"
```

---

## Network Configuration

### Ports Used:
- **3232**: OSC from MindShow → LX (incoming to LX)
- **3333**: OSC from LX → clients (outgoing from LX)
- **8000**: MindShow web dashboard
- **8080**: Control UI OSC bridge
- **8282**: Control UI web interface

### OSC Messages Sent by MindShow:
- `/lx/mixer/master/effect/.../colorBlend` - Brain state color (0.0-1.0)
- `/lx/mixer/master/effect/.../speed` - Animation speed (0.0-1.0)

---

## Enabling MindshowEffect in LX

1. Open LX/Chromatik GUI
2. Go to **Mixer** → **Master Effects**
3. Add effect: **MindshowEffect** (under COLOR category)
4. Enable the effect
5. Adjust parameters:
   - **Color**: Manual override (usually leave at 0.5 for OSC control)
   - **Speed**: Manual override (usually leave at 0.5 for OSC control)
   - **Sensitivity**: How much the effect influences the output (0-1)

**Note:** When MindShow is running, it will automatically control the Color and Speed parameters via OSC.

---

## Demo Mode (No Muse Headband)

If MindShow can't connect to the Muse headband, it runs in demo mode:
- Sends oscillating demo values to LX
- You'll see the LEDs pulse through colors automatically
- Useful for testing the OSC connection

---

## Troubleshooting

### MindShow Not Connecting to Muse
```bash
# Check Bluetooth is enabled
# Ensure Muse is on and LED is blinking
# Check logs:
tail -f /tmp/mindshow.log
```

### OSC Not Working
```bash
# Verify ports aren't blocked
lsof -i :3232  # Should show LX listening
lsof -i :8000  # Should show MindShow

# Check MindShow logs for OSC initialization
grep "OSC" /tmp/mindshow.log

# In LX, check OSC settings:
# Window → OSC → Verify receive port is 3232
```

### LX Won't Start
```bash
# Rebuild Java project
cd ~/src/iqe
./mvnw clean package -DskipTests

# Check Java version (needs Java 17 Temurin)
java -version

# Download Chromatik if missing
./src/scripts/download_chromatik.sh
```

### Control UI Port Conflicts
```bash
# Kill processes on conflicting ports
lsof -ti:8282 | xargs kill -9  # Control UI
lsof -ti:8080 | xargs kill -9  # OSC bridge

# Then restart Control UI
cd ~/src/iqe/src/control-ui
npm run start:dev
```

---

## Shutdown

### Stop Individual Components:
```bash
# Ctrl+C in each terminal

# Or kill specific ports:
lsof -ti:8282 | xargs kill -9  # Control UI
lsof -ti:8080 | xargs kill -9  # OSC bridge
lsof -ti:8000 | xargs kill -9  # MindShow

# Kill all Java processes (LX)
pkill -f ChromatikIQE

# Kill Flamecaster
pkill -f Flamecaster
```

### Stop MindShow:
```bash
# If running in foreground: Ctrl+C

# If running in background:
cd ~/src/mindshow
./stop_mindshow.sh
```

---

## Quick Reference URLs

- **MindShow Dashboard**: http://localhost:8000
- **Control UI**: http://localhost:8282
- **LX GUI**: Native window (no URL)
- **NodeJS Bridge** (if used): http://localhost:80

---

## System Architecture Diagram

```
┌─────────────────────┐
│  Muse S Gen 2 EEG   │
│     Headband        │
└──────────┬──────────┘
           │ Bluetooth
           ▼
┌─────────────────────┐
│     MindShow        │
│  (Python System)    │
│  Port 8000          │
└──────────┬──────────┘
           │ OSC (port 3232)
           │ colorBlend, speed
           ▼
┌─────────────────────┐
│    LX/Chromatik     │
│   (Java System)     │
│  MindshowEffect     │
└──────────┬──────────┘
           │ ArtNet
           ▼
┌─────────────────────┐
│   LED Hardware      │
│  (Pixelblaze, etc)  │
└─────────────────────┘

Optional:
┌─────────────────────┐
│   Control UI        │
│  (TypeScript Web)   │
│  Port 8282          │
└──────────┬──────────┘
           │ OSC (3232/3333)
           └──────────→ LX
```

---

## Additional Resources

- IQE Main README: `~/src/iqe/README.md`
- IQE Claude Guide: `~/src/iqe/CLAUDE.md`
- PixelBlaze Fleet: `~/src/iqe/PIXELBLAZE_FLEET.md`
- MindShow README: `~/src/mindshow/README.md`
- MindShow Claude Guide: `~/src/mindshow/CLAUDE.md`

---

*Last updated: December 2025*
