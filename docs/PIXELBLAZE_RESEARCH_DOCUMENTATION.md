# Pixelblaze Development Research Documentation

*Based on analysis of [zranger1/pixelblaze-client](https://github.com/zranger1/pixelblaze-client) repository*

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Core Architecture](#core-architecture)
3. [API Patterns and Best Practices](#api-patterns-and-best-practices)
4. [Pattern Management](#pattern-management)
5. [Variable Control](#variable-control)
6. [Connection Management](#connection-management)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Real-world Examples](#real-world-examples)
10. [Integration Patterns](#integration-patterns)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Development Tips](#development-tips)

---

## Repository Overview

The [pixelblaze-client](https://github.com/zranger1/pixelblaze-client) is a Python library that provides a **synchronous interface** for controlling Pixelblaze LED controllers. It's designed to be simple, reliable, and production-ready.

### Key Features
- **Synchronous API** - No async/await complexity
- **Multiple Pixelblaze Support** - Control multiple devices simultaneously
- **Pattern Management** - Upload, download, and manage patterns
- **Variable Control** - Real-time parameter adjustment
- **Error Recovery** - Robust connection handling
- **Production Ready** - Used in real installations

### Requirements
```bash
pip install pixelblaze-client
# Dependencies:
# - websocket-client
# - requests
# - pytz
# - py-mini-racer
```

---

## Core Architecture

### Basic Connection Pattern

```python
from pixelblaze import *

# Simple connection
pb = Pixelblaze("192.168.0.241")
pb.connect()

# Multiple devices
pixelblazes = [
    Pixelblaze("192.168.0.241"),
    Pixelblaze("192.168.0.242"),
    Pixelblaze("192.168.0.243")
]

for pb in pixelblazes:
    pb.connect()
```

### Connection States

The library manages connection states internally:
- **Disconnected** - No active connection
- **Connecting** - Establishing WebSocket connection
- **Connected** - Ready for commands
- **Error** - Connection failed or lost

---

## API Patterns and Best Practices

### 1. Context Manager Pattern

```python
# Recommended: Use context manager for automatic cleanup
with Pixelblaze("192.168.0.241") as pb:
    pb.setActivePattern("sparkfire")
    pb.setVariable("brightness", 0.8)
    # Connection automatically closed when exiting context
```

### 2. Connection Pool Pattern

```python
# For multiple devices
class PixelblazeManager:
    def __init__(self, addresses):
        self.pixelblazes = [Pixelblaze(addr) for addr in addresses]
    
    def __enter__(self):
        for pb in self.pixelblazes:
            pb.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for pb in self.pixelblazes:
            pb.disconnect()
    
    def broadcast_command(self, command, *args, **kwargs):
        """Send command to all connected Pixelblazes"""
        results = []
        for pb in self.pixelblazes:
            try:
                result = getattr(pb, command)(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Error on {pb.address}: {e}")
        return results
```

### 3. Command Chaining

```python
# Chain commands for efficiency
pb = Pixelblaze("192.168.0.241")
pb.connect()
pb.setActivePattern("sparkfire").setVariable("brightness", 0.8).setVariable("speed", 0.5)
```

---

## Pattern Management

### Getting Pattern List

```python
# Get all available patterns
patterns = pb.getPatternList()
for pattern_id, pattern_name in patterns.items():
    print(f"{pattern_id}: {pattern_name}")

# Get current active pattern
current = pb.getActivePattern()
print(f"Currently running: {current}")
```

### Pattern Switching

```python
# Switch by pattern ID (recommended)
pb.setActivePattern("43MSBYij")  # sparkfire pattern

# Switch by pattern name
pb.setActivePattern("sparkfire")

# Verify pattern switched
current = pb.getActivePattern()
assert current == "sparkfire"
```

### Pattern Upload/Download

```python
# Download existing pattern
pattern_code = pb.getPattern("sparkfire")
print(pattern_code)

# Upload new pattern
new_pattern = """
export function beforeRender(delta) {
    t1 = time(0.1)
    t2 = time(0.2)
}

export function render(index) {
    h = (index / pixelCount + t1) % 1
    v = wave(t2 + index * 0.1)
    hsv(h, 1, v)
}
"""

pb.setPattern("my_custom_pattern", new_pattern)
pb.setActivePattern("my_custom_pattern")
```

---

## Variable Control

### Setting Variables

```python
# Single variable
pb.setVariable("brightness", 0.8)

# Multiple variables at once
pb.setVariables({
    "brightness": 0.8,
    "speed": 0.5,
    "hue": 0.3
})

# Get current variables
vars = pb.getVariables()
print(f"Current brightness: {vars.get('brightness', 0)}")
```

### Variable Types and Ranges

```python
# Common variable types
variables = {
    "brightness": 0.0,    # 0.0 to 1.0
    "speed": 0.5,         # 0.0 to 1.0 (pattern dependent)
    "hue": 0.3,           # 0.0 to 1.0 (color wheel)
    "saturation": 1.0,    # 0.0 to 1.0
    "value": 1.0,         # 0.0 to 1.0
    "temperature": 0.7,    # Pattern-specific
    "intensity": 0.8,     # Pattern-specific
}
```

### Real-time Variable Updates

```python
import time

# Smooth brightness transition
for brightness in range(0, 101, 5):
    pb.setVariable("brightness", brightness / 100.0)
    time.sleep(0.1)

# Color cycling
for hue in range(0, 101, 2):
    pb.setVariable("hue", hue / 100.0)
    time.sleep(0.05)
```

---

## Connection Management

### Robust Connection Handling

```python
class RobustPixelblaze:
    def __init__(self, address, max_retries=3):
        self.address = address
        self.max_retries = max_retries
        self.pb = Pixelblaze(address)
    
    def connect_with_retry(self):
        """Connect with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                self.pb.connect()
                return True
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Connection failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        return False
    
    def ensure_connected(self):
        """Ensure connection is active, reconnect if needed"""
        if not self.pb.isConnected():
            return self.connect_with_retry()
        return True
```

### Connection Pooling

```python
class PixelblazePool:
    def __init__(self, addresses):
        self.pixelblazes = {}
        for addr in addresses:
            self.pixelblazes[addr] = Pixelblaze(addr)
    
    def connect_all(self):
        """Connect to all Pixelblazes"""
        results = {}
        for addr, pb in self.pixelblazes.items():
            try:
                pb.connect()
                results[addr] = True
            except Exception as e:
                results[addr] = False
                print(f"Failed to connect to {addr}: {e}")
        return results
    
    def broadcast(self, command, *args, **kwargs):
        """Send command to all connected Pixelblazes"""
        results = {}
        for addr, pb in self.pixelblazes.items():
            if pb.isConnected():
                try:
                    result = getattr(pb, command)(*args, **kwargs)
                    results[addr] = result
                except Exception as e:
                    results[addr] = f"Error: {e}"
        return results
```

---

## Error Handling

### Exception Types

```python
try:
    pb = Pixelblaze("192.168.0.241")
    pb.connect()
    pb.setActivePattern("sparkfire")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Graceful Degradation

```python
class FaultTolerantPixelblaze:
    def __init__(self, address):
        self.address = address
        self.pb = Pixelblaze(address)
        self.last_known_state = {}
    
    def safe_set_variable(self, name, value):
        """Safely set variable with fallback"""
        try:
            self.pb.setVariable(name, value)
            self.last_known_state[name] = value
            return True
        except Exception as e:
            print(f"Failed to set {name}={value}: {e}")
            return False
    
    def restore_last_state(self):
        """Restore last known good state"""
        for name, value in self.last_known_state.items():
            self.safe_set_variable(name, value)
```

---

## Performance Optimization

### Batch Operations

```python
# Efficient: Batch multiple operations
pb.setVariables({
    "brightness": 0.8,
    "speed": 0.5,
    "hue": 0.3,
    "saturation": 1.0
})

# Less efficient: Individual operations
pb.setVariable("brightness", 0.8)
pb.setVariable("speed", 0.5)
pb.setVariable("hue", 0.3)
pb.setVariable("saturation", 1.0)
```

### Rate Limiting

```python
import time
from threading import Lock

class RateLimitedPixelblaze:
    def __init__(self, address, max_rate=10):  # 10 commands per second
        self.pb = Pixelblaze(address)
        self.max_rate = max_rate
        self.last_command_time = 0
        self.lock = Lock()
    
    def rate_limited_command(self, command, *args, **kwargs):
        """Execute command with rate limiting"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_command_time
            min_interval = 1.0 / self.max_rate
            
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
            
            result = getattr(self.pb, command)(*args, **kwargs)
            self.last_command_time = time.time()
            return result
```

### Connection Reuse

```python
# Good: Reuse connection
with Pixelblaze("192.168.0.241") as pb:
    for i in range(100):
        pb.setVariable("brightness", i / 100.0)
        time.sleep(0.1)

# Bad: Create new connection each time
for i in range(100):
    with Pixelblaze("192.168.0.241") as pb:
        pb.setVariable("brightness", i / 100.0)
    time.sleep(0.1)
```

---

## Real-world Examples

### Biometric Data Integration

```python
class BiometricPixelblazeController:
    def __init__(self, address):
        self.pb = Pixelblaze(address)
        self.pb.connect()
        self.mood_mapping = {
            'engaged': {'hue': 0.0, 'brightness': 0.8},    # Red
            'neutral': {'hue': 0.33, 'brightness': 0.6},   # Green
            'relaxed': {'hue': 0.66, 'brightness': 0.4}    # Blue
        }
    
    def update_from_biometric(self, attention_score, relaxation_score):
        """Update pattern based on biometric data"""
        if attention_score > 0.7:
            mood = 'engaged'
        elif relaxation_score > 0.6:
            mood = 'relaxed'
        else:
            mood = 'neutral'
        
        variables = self.mood_mapping[mood]
        self.pb.setVariables(variables)
        return mood
    
    def smooth_transition(self, target_vars, duration=1.0):
        """Smoothly transition to target variables"""
        current_vars = self.pb.getVariables()
        steps = int(duration * 10)  # 10 updates per second
        
        for step in range(steps + 1):
            progress = step / steps
            interpolated = {}
            
            for var_name in target_vars:
                current = current_vars.get(var_name, 0)
                target = target_vars[var_name]
                interpolated[var_name] = current + (target - current) * progress
            
            self.pb.setVariables(interpolated)
            time.sleep(duration / steps)
```

### Pattern Sequencing

```python
class PatternSequencer:
    def __init__(self, address):
        self.pb = Pixelblaze(address)
        self.pb.connect()
        self.patterns = [
            "sparkfire",
            "rainbow fonts", 
            "color twinkles",
            "fireflies"
        ]
        self.current_index = 0
    
    def next_pattern(self):
        """Switch to next pattern in sequence"""
        self.current_index = (self.current_index + 1) % len(self.patterns)
        pattern = self.patterns[self.current_index]
        self.pb.setActivePattern(pattern)
        return pattern
    
    def previous_pattern(self):
        """Switch to previous pattern in sequence"""
        self.current_index = (self.current_index - 1) % len(self.patterns)
        pattern = self.patterns[self.current_index]
        self.pb.setActivePattern(pattern)
        return pattern
    
    def set_pattern_by_index(self, index):
        """Set pattern by index"""
        if 0 <= index < len(self.patterns):
            self.current_index = index
            pattern = self.patterns[index]
            self.pb.setActivePattern(pattern)
            return pattern
        return None
```

### Multi-Device Synchronization

```python
class SynchronizedPixelblazeGroup:
    def __init__(self, addresses):
        self.pixelblazes = [Pixelblaze(addr) for addr in addresses]
        self.connect_all()
    
    def connect_all(self):
        """Connect to all Pixelblazes"""
        for pb in self.pixelblazes:
            try:
                pb.connect()
            except Exception as e:
                print(f"Failed to connect to {pb.address}: {e}")
    
    def synchronized_set_variables(self, variables):
        """Set variables on all devices simultaneously"""
        for pb in self.pixelblazes:
            if pb.isConnected():
                try:
                    pb.setVariables(variables)
                except Exception as e:
                    print(f"Failed to set variables on {pb.address}: {e}")
    
    def synchronized_pattern_switch(self, pattern_name):
        """Switch pattern on all devices simultaneously"""
        for pb in self.pixelblazes:
            if pb.isConnected():
                try:
                    pb.setActivePattern(pattern_name)
                except Exception as e:
                    print(f"Failed to switch pattern on {pb.address}: {e}")
    
    def wave_effect(self, base_variables, wave_function):
        """Create wave effect across multiple devices"""
        for i, pb in enumerate(self.pixelblazes):
            if pb.isConnected():
                # Calculate wave offset for this device
                wave_offset = i / len(self.pixelblazes)
                wave_variables = wave_function(base_variables, wave_offset)
                try:
                    pb.setVariables(wave_variables)
                except Exception as e:
                    print(f"Failed to set wave variables on {pb.address}: {e}")
```

---

## Integration Patterns

### WebSocket Server Integration

```python
import asyncio
import websockets
import json
from pixelblaze import Pixelblaze

class PixelblazeWebSocketServer:
    def __init__(self, pixelblaze_address):
        self.pb = Pixelblaze(pixelblaze_address)
        self.pb.connect()
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')
                params = data.get('params', {})
                
                if command == 'set_variables':
                    self.pb.setVariables(params)
                    await websocket.send(json.dumps({'status': 'success'}))
                
                elif command == 'set_pattern':
                    pattern = params.get('pattern')
                    self.pb.setActivePattern(pattern)
                    await websocket.send(json.dumps({'status': 'success'}))
                
                elif command == 'get_variables':
                    variables = self.pb.getVariables()
                    await websocket.send(json.dumps({'variables': variables}))
                
                else:
                    await websocket.send(json.dumps({'error': 'Unknown command'}))
        
        except websockets.exceptions.ConnectionClosed:
            pass

# Usage
server = PixelblazeWebSocketServer("192.168.0.241")
start_server = websockets.serve(server.handle_client, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

### REST API Integration

```python
from flask import Flask, request, jsonify
from pixelblaze import Pixelblaze

app = Flask(__name__)
pb = Pixelblaze("192.168.0.241")
pb.connect()

@app.route('/api/variables', methods=['GET'])
def get_variables():
    """Get current variables"""
    try:
        variables = pb.getVariables()
        return jsonify({'variables': variables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/variables', methods=['POST'])
def set_variables():
    """Set variables"""
    try:
        variables = request.json.get('variables', {})
        pb.setVariables(variables)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pattern', methods=['POST'])
def set_pattern():
    """Set active pattern"""
    try:
        pattern = request.json.get('pattern')
        pb.setActivePattern(pattern)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Connection Failures

**Problem**: `ConnectionError: Failed to connect to Pixelblaze`

**Solutions**:
```python
# Check network connectivity
import socket
try:
    socket.create_connection(("192.168.0.241", 81), timeout=5)
    print("Network connectivity OK")
except:
    print("Network connectivity failed")

# Try with retry logic
def connect_with_retry(address, max_retries=3):
    for attempt in range(max_retries):
        try:
            pb = Pixelblaze(address)
            pb.connect()
            return pb
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e
```

#### 2. Pattern Switching Not Working

**Problem**: Pattern doesn't change when using `setActivePattern()`

**Solutions**:
```python
# Verify pattern exists
patterns = pb.getPatternList()
if "sparkfire" not in patterns.values():
    print("Pattern not found")

# Try by ID instead of name
pattern_id = "43MSBYij"
pb.setActivePattern(pattern_id)

# Check current pattern
current = pb.getActivePattern()
print(f"Current pattern: {current}")
```

#### 3. Variable Changes Not Visible

**Problem**: Setting variables doesn't change the LED appearance

**Solutions**:
```python
# Check if pattern supports the variable
variables = pb.getVariables()
print(f"Available variables: {variables}")

# Try different variable names
pb.setVariable("brightness", 0.5)
pb.setVariable("bri", 0.5)  # Alternative name
pb.setVariable("value", 0.5)  # Alternative name

# Check pattern code for exported variables
pattern_code = pb.getPattern(pb.getActivePattern())
print(pattern_code)
```

#### 4. Performance Issues

**Problem**: Slow response or laggy updates

**Solutions**:
```python
# Use batch operations
pb.setVariables({
    "brightness": 0.8,
    "speed": 0.5,
    "hue": 0.3
})

# Implement rate limiting
import time
last_update = 0
min_interval = 0.1  # 100ms between updates

def rate_limited_update(variables):
    global last_update
    current_time = time.time()
    if current_time - last_update >= min_interval:
        pb.setVariables(variables)
        last_update = current_time
```

#### 5. WebSocket Conflicts

**Problem**: Connection conflicts with web interface

**Solutions**:
```python
# Close web interface before connecting
print("⚠️  Close Pixelblaze web interface before running this script")

# Use connection pooling
class PixelblazePool:
    def __init__(self):
        self.connections = {}
    
    def get_connection(self, address):
        if address not in self.connections:
            self.connections[address] = Pixelblaze(address)
            self.connections[address].connect()
        return self.connections[address]
    
    def close_all(self):
        for pb in self.connections.values():
            pb.disconnect()
```

---

## Development Tips

### 1. Use Context Managers

```python
# Always use context managers for automatic cleanup
with Pixelblaze("192.168.0.241") as pb:
    pb.setActivePattern("sparkfire")
    pb.setVariables({"brightness": 0.8, "speed": 0.5})
```

### 2. Implement Proper Error Handling

```python
def safe_pixelblaze_operation(func):
    """Decorator for safe Pixelblaze operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return None
        except TimeoutError as e:
            print(f"Timeout error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    return wrapper

@safe_pixelblaze_operation
def set_pattern_safely(pb, pattern_name):
    return pb.setActivePattern(pattern_name)
```

### 3. Use Configuration Files

```python
import yaml

# config.yaml
pixelblazes:
  - address: "192.168.0.241"
    name: "main_display"
  - address: "192.168.0.242"
    name: "side_display"

patterns:
  sparkfire:
    variables:
      brightness: 0.8
      speed: 0.5
  rainbow:
    variables:
      brightness: 0.6
      speed: 0.3

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Apply configuration
for pb_config in config['pixelblazes']:
    pb = Pixelblaze(pb_config['address'])
    pb.connect()
    pb.setActivePattern("sparkfire")
    pb.setVariables(config['patterns']['sparkfire']['variables'])
```

### 4. Implement Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggedPixelblaze:
    def __init__(self, address):
        self.pb = Pixelblaze(address)
        self.logger = logging.getLogger(f"Pixelblaze-{address}")
    
    def set_variables_logged(self, variables):
        """Set variables with logging"""
        self.logger.info(f"Setting variables: {variables}")
        try:
            self.pb.setVariables(variables)
            self.logger.info("Variables set successfully")
        except Exception as e:
            self.logger.error(f"Failed to set variables: {e}")
            raise
```

### 5. Use Type Hints

```python
from typing import Dict, Optional, List
from pixelblaze import Pixelblaze

class TypedPixelblazeController:
    def __init__(self, address: str) -> None:
        self.pb: Pixelblaze = Pixelblaze(address)
    
    def set_variables(self, variables: Dict[str, float]) -> bool:
        """Set variables with type checking"""
        try:
            self.pb.setVariables(variables)
            return True
        except Exception:
            return False
    
    def get_variables(self) -> Dict[str, float]:
        """Get current variables"""
        return self.pb.getVariables()
    
    def set_pattern(self, pattern_name: str) -> bool:
        """Set active pattern"""
        try:
            self.pb.setActivePattern(pattern_name)
            return True
        except Exception:
            return False
```

### 6. Implement Health Checks

```python
class PixelblazeHealthMonitor:
    def __init__(self, address: str):
        self.pb = Pixelblaze(address)
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
    
    def health_check(self) -> Dict[str, any]:
        """Perform health check"""
        try:
            # Test connection
            if not self.pb.isConnected():
                self.pb.connect()
            
            # Test basic operations
            variables = self.pb.getVariables()
            current_pattern = self.pb.getActivePattern()
            
            return {
                'status': 'healthy',
                'connected': True,
                'variables': variables,
                'current_pattern': current_pattern,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def monitor_continuously(self):
        """Continuous health monitoring"""
        while True:
            health = self.health_check()
            if health['status'] == 'unhealthy':
                print(f"Health check failed: {health['error']}")
                # Attempt reconnection
                try:
                    self.pb.connect()
                except Exception as e:
                    print(f"Reconnection failed: {e}")
            
            time.sleep(self.health_check_interval)
```

---

## Conclusion

The [pixelblaze-client library](https://github.com/zranger1/pixelblaze-client) provides a robust, production-ready interface for controlling Pixelblaze LED controllers. Key takeaways:

1. **Use synchronous API** - Simpler than async/await for most use cases
2. **Implement proper error handling** - Connection failures are common
3. **Use context managers** - Automatic cleanup prevents resource leaks
4. **Batch operations** - More efficient than individual commands
5. **Monitor connection health** - Implement reconnection logic
6. **Rate limit commands** - Avoid overwhelming the device
7. **Use configuration files** - Separate configuration from code
8. **Implement logging** - Essential for debugging and monitoring

This research provides a solid foundation for building reliable Pixelblaze applications, especially for biometric data integration and real-time control systems.

---

*Document generated from analysis of [zranger1/pixelblaze-client](https://github.com/zranger1/pixelblaze-client) repository* 