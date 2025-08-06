# Pixelblaze-Async Research Documentation

*Based on analysis of [NickWaterton/Pixelblaze-Async](https://github.com/NickWaterton/Pixelblaze-Async) repository*

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Async Programming Approach](#async-programming-approach)
3. [MQTT Integration](#mqtt-integration)
4. [Key Differences from pixelblaze-client](#key-differences-from-pixelblaze-client)
5. [Advanced Features](#advanced-features)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)
8. [Integration Patterns](#integration-patterns)
9. [Troubleshooting](#troubleshooting)
10. [Comparison Analysis](#comparison-analysis)

---

## Repository Overview

The [Pixelblaze-Async](https://github.com/NickWaterton/Pixelblaze-Async) library provides an **asynchronous interface** for controlling Pixelblaze LED controllers, with built-in MQTT support. It's designed for Python 3.6-3.8 and requires familiarity with `asyncio`.

### Key Features
- **Async/await interface** - Modern asynchronous programming
- **MQTT integration** - Built-in MQTT broker support
- **Multiple device support** - Control multiple Pixelblazes simultaneously
- **Pattern sequencer support** - Control Pixelblaze's internal sequencer
- **Flash memory management** - Safe flash memory operations
- **Standalone MQTT interface** - Can be used without async programming

### Requirements
```bash
# Python 3.6-3.8 (tested on 3.6.9 and 3.8.5)
pip install aiohttp paho-mqtt
```

---

## Async Programming Approach

### Basic Async Connection

```python
import asyncio
from pixelblaze_async.PixelblazeClient import PixelblazeClient

async def main():
    # Create async client
    pb = PixelblazeClient("192.168.0.241")
    
    # Connect asynchronously
    await pb.connect()
    
    # Async operations
    patterns = await pb.getPatterns()
    await pb.setActivePattern("sparkfire")
    await pb.setVars({"brightness": 0.8, "hue": 0.3})
    
    # Clean disconnect
    await pb.disconnect()

# Run async function
asyncio.run(main())
```

### Multiple Device Management

```python
async def control_multiple_devices():
    devices = [
        PixelblazeClient("192.168.0.241"),
        PixelblazeClient("192.168.0.242"),
        PixelblazeClient("192.168.0.243")
    ]
    
    # Connect to all devices
    for device in devices:
        await device.connect()
    
    # Synchronized operations
    await asyncio.gather(*[
        device.setActivePattern("sparkfire") 
        for device in devices
    ])
    
    # Cleanup
    for device in devices:
        await device.disconnect()
```

---

## MQTT Integration

### MQTT Interface Setup

```python
from pixelblaze_async.PixelblazeClient import PixelblazeClient

# MQTT-enabled client
pb = PixelblazeClient(
    "192.168.0.241",
    mqtt_broker="localhost",
    mqtt_port=1883,
    mqtt_topic="pixelblaze/device1"
)

# Start MQTT interface
await pb.start_mqtt_interface()
```

### MQTT Message Examples

```bash
# Set pattern via MQTT
mosquitto_pub -h localhost -t "pixelblaze/device1/pattern" -m "sparkfire"

# Set variables via MQTT
mosquitto_pub -h localhost -t "pixelblaze/device1/vars" -m '{"brightness": 0.8, "hue": 0.3}'

# Set brightness via MQTT
mosquitto_pub -h localhost -t "pixelblaze/device1/brightness" -m "80"

# Get status via MQTT
mosquitto_sub -h localhost -t "pixelblaze/device1/status"
```

### MQTT Topics Structure

```
pixelblaze/device1/
├── pattern          # Set active pattern
├── pattern_id       # Set pattern by ID
├── vars             # Set variables (JSON)
├── brightness       # Set global brightness (0-100)
├── max_brightness   # Set max brightness (0-1)
├── controls         # Set UI controls (JSON)
├── sequencer        # Control sequencer
├── status           # Device status
└── patterns         # Available patterns
```

---

## Key Differences from pixelblaze-client

### 1. Async vs Sync

**Pixelblaze-Async (Async):**
```python
# Async operations
await pb.connect()
patterns = await pb.getPatterns()
await pb.setActivePattern("sparkfire")
await pb.disconnect()
```

**pixelblaze-client (Sync):**
```python
# Synchronous operations
pb.connect()
patterns = pb.getPatterns()
pb.setActivePattern("sparkfire")
pb.disconnect()
```

### 2. MQTT Integration

**Pixelblaze-Async:**
- Built-in MQTT support
- Can be used as standalone MQTT interface
- Remote control via MQTT messages

**pixelblaze-client:**
- WebSocket only
- Direct Python API
- No MQTT support

### 3. Pattern Sequencer Support

**Pixelblaze-Async:**
```python
# Control internal sequencer
await pb.startSequencer(mode=1)  # Shuffle mode
await pb.startSequencer(mode=2)  # Playlist mode
await pb.pauseSequencer()
await pb.playSequencer()
await pb.stopSequencer()
```

**pixelblaze-client:**
- No sequencer control
- Manual pattern switching only

---

## Advanced Features

### 1. Flash Memory Management

```python
# Enable flash save (IMPORTANT for persistent settings)
await pb._enable_flash_save(True)

# Set controls with flash save
await pb.setControls({"brightness": 0.8}, saveFlash=True)

# Disable flash save to preserve memory
await pb._enable_flash_save(False)
```

### 2. Pattern Sequencer Control

```python
# Start sequencer in shuffle mode
await pb.startSequencer(mode=1)

# Start sequencer in playlist mode
await pb.startSequencer(mode=2)

# Pause/play sequencer
await pb.pauseSequencer()
await pb.playSequencer()

# Stop sequencer
await pb.stopSequencer()

# Set sequence timer (milliseconds per pattern)
await pb.setSequenceTimer(5000)  # 5 seconds per pattern
```

### 3. Hardware Configuration

```python
# Get hardware configuration
config = await pb._get_hardware_config()
print(f"Pixel count: {config['pixelCount']}")
print(f"Color order: {config['colorOrder']}")
print(f"Data speed: {config['dataSpeed']}")

# Set hardware configuration
await pb.setpixelCount(60)
await pb.setcolorOrder("RGB")
await pb.setDataspeed(800000)  # Advanced users only
```

### 4. Advanced Control Methods

```python
# Set color control (HSV/RGB picker)
await pb.setColorControl("hue_picker", [0.5, 1.0, 1.0])  # HSV
await pb.setColorControl("rgb_picker", [1.0, 0.0, 0.0])  # RGB

# Set UI controls
await pb.setControl("brightness", 0.8)
await pb.setControls({"brightness": 0.8, "speed": 0.5})

# Check if variable exists
if await pb.variableExists("brightness"):
    await pb.setVariable("brightness", 0.8)
```

---

## Code Examples

### 1. Async Biometric Controller

```python
import asyncio
from pixelblaze_async.PixelblazeClient import PixelblazeClient

class AsyncBiometricController:
    def __init__(self, address: str):
        self.pb = PixelblazeClient(address)
        self.mood_mapping = {
            'engaged': {'hue': 0.0, 'brightness': 0.8},
            'neutral': {'hue': 0.33, 'brightness': 0.6},
            'relaxed': {'hue': 0.66, 'brightness': 0.4}
        }
    
    async def connect(self):
        await self.pb.connect()
    
    async def update_from_biometric(self, attention_score: float, relaxation_score: float):
        """Update pattern based on biometric data"""
        if attention_score > 0.7:
            mood = 'engaged'
        elif relaxation_score > 0.6:
            mood = 'relaxed'
        else:
            mood = 'neutral'
        
        variables = self.mood_mapping[mood]
        await self.pb.setVars(variables)
        return mood
    
    async def smooth_transition(self, target_vars: dict, duration: float = 1.0):
        """Smooth transition to target variables"""
        current_vars = await self.pb.getVars()
        steps = int(duration * 10)
        
        for step in range(steps + 1):
            progress = step / steps
            interpolated = {}
            
            for var_name in target_vars:
                if var_name in current_vars:
                    current = current_vars[var_name]
                    target = target_vars[var_name]
                    interpolated[var_name] = current + (target - current) * progress
            
            await self.pb.setVars(interpolated)
            await asyncio.sleep(duration / steps)
    
    async def disconnect(self):
        await self.pb.disconnect()

# Usage
async def main():
    controller = AsyncBiometricController("192.168.0.241")
    await controller.connect()
    
    # Test mood updates
    await controller.update_from_biometric(0.8, 0.2)  # Engaged
    await asyncio.sleep(2)
    
    await controller.update_from_biometric(0.2, 0.8)  # Relaxed
    await asyncio.sleep(2)
    
    await controller.disconnect()

asyncio.run(main())
```

### 2. MQTT-Enabled Controller

```python
import asyncio
from pixelblaze_async.PixelblazeClient import PixelblazeClient

class MQTTBiometricController:
    def __init__(self, address: str, mqtt_broker: str = "localhost"):
        self.pb = PixelblazeClient(
            address,
            mqtt_broker=mqtt_broker,
            mqtt_topic=f"pixelblaze/{address}"
        )
    
    async def start(self):
        """Start MQTT interface"""
        await self.pb.connect()
        await self.pb.start_mqtt_interface()
        print("MQTT interface started")
        print("Send commands to MQTT topics:")
        print(f"  - pixelblaze/{self.pb.ip}/pattern")
        print(f"  - pixelblaze/{self.pb.ip}/vars")
        print(f"  - pixelblaze/{self.pb.ip}/brightness")
    
    async def stop(self):
        """Stop MQTT interface"""
        await self.pb.disconnect()

# Usage
async def main():
    controller = MQTTBiometricController("192.168.0.241")
    await controller.start()
    
    # Keep running for MQTT commands
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await controller.stop()

asyncio.run(main())
```

### 3. Multi-Device Synchronization

```python
import asyncio
from pixelblaze_async.PixelblazeClient import PixelblazeClient

class MultiDeviceController:
    def __init__(self, addresses: list):
        self.devices = [PixelblazeClient(addr) for addr in addresses]
    
    async def connect_all(self):
        """Connect to all devices"""
        await asyncio.gather(*[device.connect() for device in self.devices])
    
    async def synchronized_set_pattern(self, pattern_name: str):
        """Set pattern on all devices simultaneously"""
        await asyncio.gather(*[
            device.setActivePattern(pattern_name) 
            for device in self.devices
        ])
    
    async def synchronized_set_vars(self, variables: dict):
        """Set variables on all devices simultaneously"""
        await asyncio.gather(*[
            device.setVars(variables) 
            for device in self.devices
        ])
    
    async def wave_effect(self, base_vars: dict, wave_function):
        """Create wave effect across multiple devices"""
        tasks = []
        for i, device in enumerate(self.devices):
            wave_offset = i / len(self.devices)
            wave_vars = wave_function(base_vars, wave_offset)
            tasks.append(device.setVars(wave_vars))
        
        await asyncio.gather(*tasks)
    
    async def disconnect_all(self):
        """Disconnect from all devices"""
        await asyncio.gather(*[device.disconnect() for device in self.devices])

# Usage
async def main():
    addresses = ["192.168.0.241", "192.168.0.242", "192.168.0.243"]
    controller = MultiDeviceController(addresses)
    
    await controller.connect_all()
    
    # Synchronized operations
    await controller.synchronized_set_pattern("sparkfire")
    await controller.synchronized_set_vars({"brightness": 0.8})
    
    # Wave effect
    def wave_func(base_vars, offset):
        return {**base_vars, "hue": (base_vars.get("hue", 0) + offset) % 1.0}
    
    await controller.wave_effect({"brightness": 0.8}, wave_func)
    
    await controller.disconnect_all()

asyncio.run(main())
```

---

## Best Practices

### 1. Async Context Managers

```python
class AsyncPixelblazeContext:
    def __init__(self, address: str):
        self.pb = PixelblazeClient(address)
    
    async def __aenter__(self):
        await self.pb.connect()
        return self.pb
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pb.disconnect()

# Usage
async def main():
    async with AsyncPixelblazeContext("192.168.0.241") as pb:
        await pb.setActivePattern("sparkfire")
        await pb.setVars({"brightness": 0.8})
```

### 2. Error Handling

```python
async def safe_operation(operation_func, *args, **kwargs):
    """Safely execute async operation with error handling"""
    try:
        return await operation_func(*args, **kwargs)
    except Exception as e:
        print(f"Operation failed: {e}")
        return None

# Usage
result = await safe_operation(pb.setActivePattern, "sparkfire")
```

### 3. Connection Management

```python
class RobustAsyncController:
    def __init__(self, address: str, max_retries: int = 3):
        self.pb = PixelblazeClient(address)
        self.max_retries = max_retries
    
    async def connect_with_retry(self):
        """Connect with retry logic"""
        for attempt in range(self.max_retries):
            try:
                await self.pb.connect()
                return True
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise e
        return False
    
    async def ensure_connected(self):
        """Ensure connection is active"""
        if not self.pb.connected:
            return await self.connect_with_retry()
        return True
```

### 4. Flash Memory Safety

```python
async def safe_flash_operations(pb):
    """Safely perform flash memory operations"""
    # Enable flash save temporarily
    await pb._enable_flash_save(True)
    
    try:
        # Perform operations that need to be saved
        await pb.setControls({"brightness": 0.8}, saveFlash=True)
        await pb.setActivePattern("sparkfire")
    finally:
        # Always disable flash save to preserve memory
        await pb._enable_flash_save(False)
```

---

## Integration Patterns

### 1. WebSocket Server Integration

```python
import asyncio
import websockets
import json
from pixelblaze_async.PixelblazeClient import PixelblazeClient

class AsyncPixelblazeWebSocketServer:
    def __init__(self, pixelblaze_address: str):
        self.pb = PixelblazeClient(pixelblaze_address)
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        await self.pb.connect()
        
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket, path):
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')
                params = data.get('params', {})
                
                if command == 'set_pattern':
                    await self.pb.setActivePattern(params['pattern'])
                    await websocket.send(json.dumps({'status': 'success'}))
                
                elif command == 'set_vars':
                    await self.pb.setVars(params)
                    await websocket.send(json.dumps({'status': 'success'}))
                
                elif command == 'get_vars':
                    vars = await self.pb.getVars()
                    await websocket.send(json.dumps({'vars': vars}))
        
        except websockets.exceptions.ConnectionClosed:
            pass

# Usage
async def main():
    server = AsyncPixelblazeWebSocketServer("192.168.0.241")
    await server.start_server()

asyncio.run(main())
```

### 2. REST API Integration

```python
from fastapi import FastAPI, HTTPException
from pixelblaze_async.PixelblazeClient import PixelblazeClient
import asyncio

app = FastAPI()
pb = None

@app.on_event("startup")
async def startup_event():
    global pb
    pb = PixelblazeClient("192.168.0.241")
    await pb.connect()

@app.on_event("shutdown")
async def shutdown_event():
    if pb:
        await pb.disconnect()

@app.get("/api/variables")
async def get_variables():
    try:
        vars = await pb.getVars()
        return {"variables": vars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/variables")
async def set_variables(variables: dict):
    try:
        await pb.setVars(variables)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pattern")
async def set_pattern(pattern: str):
    try:
        await pb.setActivePattern(pattern)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Async/Await Errors

**Problem**: `SyntaxError: 'await' outside async function`

**Solution**:
```python
# Wrap in async function
async def main():
    pb = PixelblazeClient("192.168.0.241")
    await pb.connect()

# Run with asyncio
asyncio.run(main())
```

#### 2. MQTT Connection Issues

**Problem**: MQTT broker connection fails

**Solution**:
```python
# Check MQTT broker status
await pb._waitForMQTT()

# Verify MQTT connection
if pb._MQTT_connected:
    print("MQTT connected")
else:
    print("MQTT not connected")
```

#### 3. WebSocket Conflicts

**Problem**: WebSocket connection conflicts with web interface

**Solution**:
```python
# Close web interface before connecting
print("⚠️  Close Pixelblaze web interface before running")

# Wait for WebSocket connection
await pb._waitForWS()
```

#### 4. Flash Memory Warnings

**Problem**: Flash memory wear warnings

**Solution**:
```python
# Always disable flash save by default
await pb._enable_flash_save(False)

# Only enable when needed
await pb._enable_flash_save(True)
await pb.setControls(vars, saveFlash=True)
await pb._enable_flash_save(False)
```

---

## Comparison Analysis

### Pixelblaze-Async vs pixelblaze-client

| Feature | Pixelblaze-Async | pixelblaze-client |
|---------|------------------|-------------------|
| **Programming Model** | Async/await | Synchronous |
| **Python Version** | 3.6-3.8 | 3.9+ |
| **MQTT Support** | ✅ Built-in | ❌ None |
| **Sequencer Control** | ✅ Full support | ❌ None |
| **Flash Memory** | ✅ Safe management | ⚠️ Basic |
| **Multiple Devices** | ✅ Async parallel | ✅ Sync sequential |
| **WebSocket Only** | ✅ Yes | ✅ Yes |
| **Learning Curve** | ⚠️ Requires async knowledge | ✅ Simple sync API |

### When to Use Each

**Use Pixelblaze-Async when:**
- You need MQTT integration
- You want to control pattern sequencer
- You're comfortable with async programming
- You need to control multiple devices simultaneously
- You want advanced features

**Use pixelblaze-client when:**
- You prefer synchronous programming
- You want a simpler API
- You don't need MQTT
- You're using Python 3.9+
- You want a more mature library

---

## Conclusion

The [Pixelblaze-Async](https://github.com/NickWaterton/Pixelblaze-Async) library provides a powerful alternative to the pixelblaze-client with:

1. **Modern async programming** - Better for concurrent operations
2. **MQTT integration** - Remote control capabilities
3. **Advanced features** - Sequencer control, flash memory management
4. **Multiple device support** - Parallel control of multiple Pixelblazes

### Key Takeaways for Our Project:

1. **Async approach** - Better for real-time biometric data processing
2. **MQTT integration** - Could enable remote control of MindShow
3. **Sequencer control** - Could automate pattern transitions
4. **Flash memory safety** - Important for production deployments
5. **Multiple device support** - Could control multiple LED installations

### Integration Recommendations:

1. **Consider async approach** for real-time brainwave processing
2. **Evaluate MQTT integration** for remote control capabilities
3. **Implement flash memory safety** in production code
4. **Use sequencer control** for automated pattern management
5. **Plan for multiple devices** in large installations

---

*Document generated from analysis of [NickWaterton/Pixelblaze-Async](https://github.com/NickWaterton/Pixelblaze-Async) repository* 