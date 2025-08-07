#!/usr/bin/env python3
"""
MindShow Integrated System - Phases 2+3 Implementation
Lightweight, Pi-ready system with multi-Pixelblaze support

Based on deep research docs:
- Phase 2: Address Areas Lacking Context
- Phase 3: Pixelblaze WebSocket Pattern Control

Features:
- MuseLSL primary EEG streaming with BrainFlow fallback
- Support for 4 Pixelblaze V3 controllers per Pi
- Research-based WebSocket pattern control
- Auto-discovery and robust error handling
- PPG integration ready
- Web dashboard for monitoring and debugging
"""

import asyncio
import json
import logging
import time
import socket
import threading
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

import websocket
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger

# EEG Processing Imports
try:
    import pylsl  # MuseLSL primary
    MUSELSL_AVAILABLE = True
except ImportError:
    MUSELSL_AVAILABLE = False
    logger.warning("pylsl not available - MuseLSL disabled")

try:
    from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
    from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
    BRAINFLOW_AVAILABLE = True
except ImportError:
    BRAINFLOW_AVAILABLE = False
    logger.warning("BrainFlow not available - fallback disabled")

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MindShowConfig:
    """Configuration for integrated MindShow system"""
    
    # EEG Settings
    muse_mac_address: str = "78744271-945E-2227-B094-D15BC0F0FA0E"
    eeg_source: str = "muselsl"  # "muselsl" or "brainflow" 
    sample_rate: int = 256
    
    # Brain State Thresholds (research-based)
    attention_threshold: float = 0.75
    relaxation_threshold: float = 0.65
    state_confidence_required: int = 3
    min_state_duration: float = 2.0
    
    # Pixelblaze Settings  
    pixelblaze_port: int = 81
    discovery_timeout: float = 5.0
    max_controllers: int = 4
    connection_retry_attempts: int = 3
    connection_timeout: float = 10.0
    
    # System Settings
    update_rate: float = 10.0  # Hz
    web_port: int = 8000
    log_level: str = "INFO"
    pi_mode: bool = False  # Enable Pi optimizations
    
    # Phase 4b: Continuous Color Mood Configuration
    color_mood_smoothing: float = 0.3  # Exponential moving average factor (0-1)
    color_mood_intensity_scale: float = 0.5  # Base intensity for color shifts
    color_mood_attention_weight: float = 0.4  # How much attention affects warm shift
    color_mood_relaxation_weight: float = 0.4  # How much relaxation affects cool shift

# =============================================================================
# EEG PROCESSING
# =============================================================================

class MuseLSLProcessor:
    """Lightweight MuseLSL EEG processor for Pi deployment"""
    
    def __init__(self, config: MindShowConfig):
        self.config = config
        self.inlet = None
        self.connected = False
        self.buffer_size = 512
        self.data_buffer = []
        
    def connect(self) -> bool:
        """Connect to MuseLSL stream"""
        if not MUSELSL_AVAILABLE:
            logger.error("pylsl not available - cannot use MuseLSL")
            return False
            
        try:
            logger.info("Looking for Muse LSL streams...")
            streams = pylsl.resolve_streams()
            
            if not streams:
                logger.error("No Muse LSL streams found")
                return False
                
            logger.info(f"Found {len(streams)} EEG stream(s)")
            self.inlet = pylsl.StreamInlet(streams[0])
            self.connected = True
            logger.info("✅ Connected to Muse via LSL")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse LSL: {e}")
            return False
    
    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get latest EEG data from LSL stream"""
        if not self.connected or not self.inlet:
            return None
            
        try:
            # Get samples from stream
            samples, timestamps = self.inlet.pull_chunk(max_samples=64)
            if not samples:
                return None
            
            # Convert to numpy array
            data = np.array(samples).T  # Transpose to match BrainFlow format
            
            if data.shape[1] == 0:
                return None
            
            # Extract EEG channels (first 4 channels for Muse)
            eeg_data = data[:4, :]  # TP9, AF7, AF8, TP10
            
            # Calculate band powers using simple FFT approach
            sample_rate = self.config.sample_rate
            band_powers = self._calculate_band_powers(eeg_data, sample_rate)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'raw_data': data,
                'band_powers': band_powers,
                'sample_count': data.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Error getting LSL data: {e}")
            return None
    
    def _calculate_band_powers(self, eeg_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Calculate brainwave band powers"""
        try:
            # Average across channels
            avg_channel = np.mean(eeg_data, axis=0)
            
            # Apply FFT
            fft_vals = np.fft.rfft(avg_channel)
            fft_freqs = np.fft.rfftfreq(len(avg_channel), 1/sample_rate)
            psd = np.abs(fft_vals) ** 2
            
            # Define frequency bands
            bands = {
                'delta': (0.5, 4.0),
                'theta': (4.0, 8.0), 
                'alpha': (8.0, 13.0),
                'beta': (13.0, 30.0),
                'gamma': (30.0, 50.0)
            }
            
            # Calculate band powers
            band_powers = {}
            for band_name, (low_freq, high_freq) in bands.items():
                band_mask = (fft_freqs >= low_freq) & (fft_freqs <= high_freq)
                band_power = float(np.mean(psd[band_mask]))
                band_powers[band_name] = band_power
            
            return band_powers
            
        except Exception as e:
            logger.error(f"Error calculating band powers: {e}")
            return {'delta': 0, 'theta': 0, 'alpha': 0, 'beta': 0, 'gamma': 0}

class BrainFlowProcessor:
    """BrainFlow processor for advanced EEG features"""
    
    def __init__(self, config: MindShowConfig):
        self.config = config
        self.board = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to Muse via BrainFlow"""
        if not BRAINFLOW_AVAILABLE:
            logger.error("BrainFlow not available")
            return False
            
        try:
            logger.info("Connecting to Muse via BrainFlow...")
            
            # Configure BrainFlow parameters
            BoardShim.enable_dev_board_logger()
            params = BrainFlowInputParams()
            params.mac_address = self.config.muse_mac_address
            params.timeout = 15
            
            # Create and prepare board
            self.board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
            self.board.prepare_session()
            self.board.start_stream()
            
            # Wait for data to start flowing
            time.sleep(2)
            self.connected = True
            logger.info("✅ Connected to Muse via BrainFlow")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect via BrainFlow: {e}")
            return False
    
    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get EEG data from BrainFlow"""
        if not self.connected or not self.board:
            return None
            
        try:
            # Get raw EEG data
            data = self.board.get_board_data()
            if data.shape[1] == 0:
                return None
                
            # Get EEG channels and sampling rate
            eeg_channels = BoardShim.get_eeg_channels(BoardIds.MUSE_2_BOARD.value)
            sampling_rate = BoardShim.get_sampling_rate(BoardIds.MUSE_2_BOARD.value)
            
            # Calculate band powers using BrainFlow's method
            bands = [(0.5, 4.0), (4.0, 8.0), (8.0, 13.0), (13.0, 30.0), (30.0, 50.0)]
            avg_band_powers, _ = DataFilter.get_custom_band_powers(
                data, bands, eeg_channels, sampling_rate, apply_filter=True
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'raw_data': data,
                'band_powers': {
                    'delta': float(avg_band_powers[0]),
                    'theta': float(avg_band_powers[1]),
                    'alpha': float(avg_band_powers[2]),
                    'beta': float(avg_band_powers[3]),
                    'gamma': float(avg_band_powers[4])
                },
                'sample_count': data.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Error getting BrainFlow data: {e}")
            return None

class IntegratedEEGProcessor:
    """Integrated EEG processor with MuseLSL primary, BrainFlow fallback"""
    
    def __init__(self, config: MindShowConfig):
        self.config = config
        self.primary_processor = None
        self.fallback_processor = None
        self.connected = False
        self.current_source = None
        
        # Brain state tracking
        self.last_brain_state = "neutral"
        self.state_confidence = 0
        self.last_state_change = time.time()
        
    def connect(self) -> bool:
        """Connect to EEG source with primary/fallback logic"""
        logger.info("🧠 Connecting to EEG source...")
        
        # Try primary source (MuseLSL)
        if self.config.eeg_source == "muselsl" or self.config.eeg_source == "auto":
            self.primary_processor = MuseLSLProcessor(self.config)
            if self.primary_processor.connect():
                self.current_source = "muselsl"
                self.connected = True
                logger.info("✅ Connected via MuseLSL (primary)")
                return True
        
        # Fallback to BrainFlow
        if self.config.eeg_source == "brainflow" or self.config.eeg_source == "auto":
            self.fallback_processor = BrainFlowProcessor(self.config)
            if self.fallback_processor.connect():
                self.current_source = "brainflow"
                self.connected = True
                logger.info("✅ Connected via BrainFlow (fallback)")
                return True
        
        logger.error("❌ Failed to connect to any EEG source")
        return False
    
    def get_brain_state(self) -> Optional[Dict[str, Any]]:
        """Get current brain state with stability logic"""
        if not self.connected:
            return None
        
        # Get data from active processor
        processor = self.primary_processor if self.current_source == "muselsl" else self.fallback_processor
        raw_data = processor.get_data()
        
        if not raw_data:
            return None
        
        # Calculate attention and relaxation scores
        band_powers = raw_data['band_powers']
        attention_score = band_powers['beta'] / (band_powers['alpha'] + 1e-10)
        relaxation_score = band_powers['alpha'] / (band_powers['theta'] + 1e-10)
        
        # Normalize scores (0-1)
        attention_score = min(1.0, max(0.0, attention_score / 2.0))
        relaxation_score = min(1.0, max(0.0, relaxation_score / 2.0))
        
        # Classify brain state with stability
        brain_state = self._classify_stable_brain_state(attention_score, relaxation_score)
        
        return {
            'timestamp': raw_data['timestamp'],
            'source': self.current_source,
            'band_powers': band_powers,
            'attention': float(attention_score),
            'relaxation': float(relaxation_score),
            'brain_state': brain_state,
            'state_confidence': self.state_confidence,
            'sample_count': raw_data.get('sample_count', 0)
        }
    
    def _classify_stable_brain_state(self, attention: float, relaxation: float) -> str:
        """Classify brain state with research-based stability logic"""
        # Determine what the new state should be
        new_state = "neutral"
        if attention > self.config.attention_threshold:
            new_state = "engaged"
        elif relaxation > self.config.relaxation_threshold:
            new_state = "relaxed"
        
        # Apply stability logic
        if new_state != self.last_brain_state:
            self.state_confidence += 1
        else:
            self.state_confidence = max(0, self.state_confidence - 1)
        
        # Only change state if we have sufficient confidence and time
        current_time = time.time()
        time_since_change = current_time - self.last_state_change
        
        if (self.state_confidence >= self.config.state_confidence_required and 
            time_since_change >= self.config.min_state_duration):
            if new_state != self.last_brain_state:
                logger.info(f"🧠 Brain state changed: {self.last_brain_state} → {new_state}")
                self.last_brain_state = new_state
                self.last_state_change = current_time
            self.state_confidence = 0
        
        return self.last_brain_state
    
    def disconnect(self):
        """Disconnect from EEG source"""
        if self.fallback_processor and hasattr(self.fallback_processor, 'board') and self.fallback_processor.board:
            try:
                self.fallback_processor.board.stop_stream()
                self.fallback_processor.board.release_session()
            except:
                pass
        self.connected = False

# =============================================================================
# PIXELBLAZE CONTROLLER
# =============================================================================

@dataclass
class PixelblazeDevice:
    """Represents a single Pixelblaze V3 controller"""
    ip_address: str
    name: str = "Unknown"
    patterns: Dict[str, str] = field(default_factory=dict)  # ID -> Name mapping
    active_pattern: Optional[str] = None
    variables: Dict[str, float] = field(default_factory=dict)
    connected: bool = False
    last_seen: float = field(default_factory=time.time)
    websocket: Optional[Any] = None

class PixelblazeDiscovery:
    """Auto-discover Pixelblaze devices on network"""
    
    @staticmethod
    def discover_devices(timeout: float = 5.0) -> List[str]:
        """Discover Pixelblaze devices via network scanning"""
        logger.info("🔍 Discovering Pixelblaze devices...")
        
        # Get local network range
        local_ip = PixelblazeDiscovery._get_local_ip()
        if not local_ip:
            logger.error("Cannot determine local network")
            return []
        
        # Extract network base (e.g., 192.168.1.)
        network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
        logger.info(f"Scanning network: {network_base}0-255")
        
        # Scan for devices
        discovered = []
        threads = []
        results = []
        
        def check_device(ip: str):
            if PixelblazeDiscovery._is_pixelblaze(ip, timeout=1.0):
                results.append(ip)
        
        # Scan common IP ranges
        for i in range(1, 255):
            ip = f"{network_base}{i}"
            thread = threading.Thread(target=check_device, args=(ip,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads with timeout
        start_time = time.time()
        for thread in threads:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time > 0:
                thread.join(timeout=remaining_time)
        
        discovered = results
        logger.info(f"✅ Discovered {len(discovered)} Pixelblaze device(s): {discovered}")
        return discovered
    
    @staticmethod
    def _get_local_ip() -> Optional[str]:
        """Get local IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return None
    
    @staticmethod
    def _is_pixelblaze(ip: str, timeout: float = 1.0) -> bool:
        """Check if IP hosts a Pixelblaze device"""
        try:
            ws = websocket.create_connection(f"ws://{ip}:81", timeout=timeout)
            ws.send(json.dumps({"ping": True}))
            response = ws.recv()
            ws.close()
            
            # Check if response looks like Pixelblaze
            data = json.loads(response)
            return "ack" in data or "fps" in data
            
        except:
            return False

class MultiPixelblazeController:
    """Controller for multiple Pixelblaze V3 devices"""
    
    def __init__(self, config: MindShowConfig):
        self.config = config
        self.devices: Dict[str, PixelblazeDevice] = {}
        self.pattern_sync_enabled = True
        self.last_brain_state = "neutral"
        
        # Continuous color mood mapping parameters
        self.color_mood_smoothing = config.color_mood_smoothing
        self.previous_color_mood = 0.5  # Initialize to neutral
        self.color_mood_history = []  # For advanced smoothing if needed
        self.last_attention = 0.5
        self.last_relaxation = 0.5
        self.attention_weight = config.color_mood_attention_weight
        self.relaxation_weight = config.color_mood_relaxation_weight
        self.intensity_scale = config.color_mood_intensity_scale
        
        # Brain state to LED mappings (research-based)
        # Phase 4b: Perceptual color mood integration
        self.state_mappings = {
            'engaged': {
                'pattern_name': 'sparkfire',  # High-energy pattern
                'variables': {
                    'hue': 0.0,           # Red, bright
                    'brightness': 0.9, 
                    'speed': 0.8,
                    'colorMoodBias': 0.2  # Warm bias (0 = full warm, 1 = full cool)
                }
            },
            'relaxed': {
                'pattern_name': 'slow waves',  # Calm pattern  
                'variables': {
                    'hue': 0.67,          # Blue, dim
                    'brightness': 0.5, 
                    'speed': 0.3,
                    'colorMoodBias': 0.8  # Cool bias
                }
            },
            'neutral': {
                'pattern_name': 'rainbow',  # Balanced pattern
                'variables': {
                    'hue': 0.33,          # Green, medium
                    'brightness': 0.7, 
                    'speed': 0.5,
                    'colorMoodBias': 0.5  # Neutral (no bias)
                }
            }
        }
    
    async def discover_and_connect(self) -> int:
        """Discover and connect to Pixelblaze devices"""
        discovered_ips = PixelblazeDiscovery.discover_devices(self.config.discovery_timeout)
        
        if not discovered_ips:
            logger.warning("No Pixelblaze devices found")
            return 0
        
        # Limit to max_controllers
        discovered_ips = discovered_ips[:self.config.max_controllers]
        
        connected_count = 0
        for ip in discovered_ips:
            device = PixelblazeDevice(ip_address=ip, name=f"Pixelblaze-{ip.split('.')[-1]}")
            
            if await self._connect_device(device):
                self.devices[ip] = device
                connected_count += 1
                logger.info(f"✅ Connected to {device.name} at {ip}")
        
        logger.info(f"🎯 Connected to {connected_count}/{len(discovered_ips)} Pixelblaze devices")
        return connected_count
    
    async def _connect_device(self, device: PixelblazeDevice) -> bool:
        """Connect to a single Pixelblaze device"""
        try:
            ws_url = f"ws://{device.ip_address}:{self.config.pixelblaze_port}"
            device.websocket = websocket.create_connection(ws_url, timeout=self.config.connection_timeout)
            
            # Test connection
            device.websocket.send(json.dumps({"ping": True}))
            response = device.websocket.recv()
            
            if json.loads(response).get("ack"):
                device.connected = True
                device.last_seen = time.time()
                
                # Load patterns and current state
                await self._load_device_patterns(device)
                await self._load_device_state(device) 
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to {device.ip_address}: {e}")
            
        return False
    
    async def _load_device_patterns(self, device: PixelblazeDevice):
        """Load available patterns from device using Phase 3 research"""
        try:
            # Send listPrograms command (Phase 3 spec)
            device.websocket.send(json.dumps({"listPrograms": True}))
            
            # Receive and parse pattern list (text-based, Phase 3 spec)
            pattern_list_text = ""
            while True:
                try:
                    data = device.websocket.recv()
                    
                    # Handle binary data
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', errors='ignore')
                    
                    # Skip JSON frames (status updates)
                    if data.startswith("{"):
                        continue
                    
                    # Accumulate pattern list text
                    pattern_list_text += data
                    
                    # Check if we have complete lines
                    if data.endswith("\n") or data.endswith("\r"):
                        break
                        
                except Exception:
                    break
            
            # Parse pattern list (ID<TAB>Name format from Phase 3 research)
            device.patterns = {}
            for line in pattern_list_text.splitlines():
                if line.strip() and '\t' in line:
                    pattern_id, pattern_name = line.split('\t', 1)
                    device.patterns[pattern_id] = pattern_name
            
            logger.info(f"📋 Loaded {len(device.patterns)} patterns from {device.name}")
            
        except Exception as e:
            logger.error(f"Failed to load patterns from {device.name}: {e}")
    
    async def _load_device_state(self, device: PixelblazeDevice):
        """Load current device state"""
        try:
            # Get current variables
            device.websocket.send(json.dumps({"getVars": True}))
            response = device.websocket.recv()
            vars_data = json.loads(response)
            
            if "vars" in vars_data:
                device.variables = vars_data["vars"]
            
        except Exception as e:
            logger.error(f"Failed to load state from {device.name}: {e}")
    
    async def update_from_brain_state(self, brain_state: str, brain_data: Dict[str, Any]):
        """Update all devices based on brain state with continuous color mood mapping"""
        
        # Always update color mood, even if brain state hasn't changed
        # This creates smooth, continuous transitions
        
        # Get current brainwave data
        attention = brain_data.get('attention_score', 0.5) if brain_data else self.last_attention
        relaxation = brain_data.get('relaxation_score', 0.5) if brain_data else self.last_relaxation
        
        # Store for next update
        self.last_attention = attention
        self.last_relaxation = relaxation
        
        # === CONTINUOUS COLOR MOOD CALCULATION ===
        
        # Enhanced mapping with physiological response curve
        # Attention contribution: higher attention → warmer (lower values)
        attention_contribution = (attention - 0.5) * -self.attention_weight
        
        # Relaxation contribution: higher relaxation → cooler (higher values)  
        relaxation_contribution = (relaxation - 0.5) * self.relaxation_weight
        
        # Calculate engagement level (how engaged overall)
        engagement_level = (attention + relaxation) / 2
        
        # Dynamic intensity scaling based on engagement
        # Low engagement = less color shift, high engagement = more dramatic shifts
        intensity = self.intensity_scale + engagement_level * (1.0 - self.intensity_scale)
        
        # Base color mood calculation
        raw_color_mood = 0.5 + (attention_contribution + relaxation_contribution) * intensity
        
        # Clamp to valid range
        raw_color_mood = max(0.0, min(1.0, raw_color_mood))
        
        # Apply S-curve easing for perceptual smoothness
        if raw_color_mood < 0.5:
            eased_color_mood = 0.5 * pow(raw_color_mood * 2, 2)
        else:
            eased_color_mood = 1.0 - 0.5 * pow((1.0 - raw_color_mood) * 2, 2)
        
        # === TEMPORAL SMOOTHING ===
        # Exponential moving average to reduce jitter
        smoothed_color_mood = (self.color_mood_smoothing * eased_color_mood + 
                              (1 - self.color_mood_smoothing) * self.previous_color_mood)
        
        # Update history
        self.previous_color_mood = smoothed_color_mood
        self.color_mood_history.append(smoothed_color_mood)
        if len(self.color_mood_history) > 30:  # Keep last 30 values
            self.color_mood_history.pop(0)
        
        # Round for transmission
        final_color_mood = round(smoothed_color_mood, 3)
        
        # Check if brain state changed for pattern switching
        state_changed = brain_state != self.last_brain_state
        
        if state_changed:
            logger.info(f"🎨 Brain state changed: {self.last_brain_state} → {brain_state}")
            self.last_brain_state = brain_state
        
        # Get mapping for current brain state
        mapping = self.state_mappings.get(brain_state, self.state_mappings['neutral'])
        target_pattern = mapping['pattern_name'] if state_changed else None
        target_variables = mapping['variables'].copy()  # Copy to avoid modifying defaults
        
        # Always update color mood bias
        target_variables['colorMoodBias'] = final_color_mood
        
        # Log color mood info with emoji indicators
        mood_emoji = "🔥" if final_color_mood < 0.3 else "❄️" if final_color_mood > 0.7 else "🌈"
        logger.debug(f"{mood_emoji} Color mood: {final_color_mood:.3f} (raw: {raw_color_mood:.3f}, "
                    f"attention: {attention:.2f}, relaxation: {relaxation:.2f}, "
                    f"engagement: {engagement_level:.2f})")
        
        # Update all connected devices
        update_tasks = []
        for device in self.devices.values():
            if device.connected:
                # Only switch patterns if state changed
                pattern_to_set = target_pattern if state_changed else None
                task = self._update_device_continuous(device, pattern_to_set, target_variables)
                update_tasks.append(task)
        
        # Execute updates in parallel
        if update_tasks:
            await asyncio.gather(*update_tasks, return_exceptions=True)
    
    async def _update_device_continuous(self, device: PixelblazeDevice, pattern_name: Optional[str], variables: Dict[str, float]):
        """Update a single device with continuous color mood support"""
        try:
            # Only switch pattern if specified (state change)
            if pattern_name:
                # Find pattern ID by name (case-insensitive search)
                pattern_id = None
                for pid, pname in device.patterns.items():
                    if pattern_name.lower() in pname.lower():
                        pattern_id = pid
                        break
                
                # Switch pattern if found
                if pattern_id:
                    device.websocket.send(json.dumps({"activeProgramId": pattern_id}))
                    device.active_pattern = pattern_id
                    logger.debug(f"📝 Set pattern on {device.name}: {pattern_name} (ID: {pattern_id})")
            
            # Always update variables (including colorMoodBias)
            device.websocket.send(json.dumps({"setVars": variables}))
            device.variables.update(variables)
            
        except Exception as e:
            logger.error(f"Failed to update {device.name}: {e}")
            device.connected = False
    
    async def _update_device(self, device: PixelblazeDevice, pattern_name: str, variables: Dict[str, float]):
        """Update a single device (legacy method for compatibility)"""
        await self._update_device_continuous(device, pattern_name, variables)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all devices"""
        return {
            'connected_devices': len([d for d in self.devices.values() if d.connected]),
            'total_devices': len(self.devices),
            'devices': [
                {
                    'name': device.name,
                    'ip': device.ip_address,
                    'connected': device.connected,
                    'patterns_count': len(device.patterns),
                    'active_pattern': device.active_pattern,
                    'variables': device.variables
                }
                for device in self.devices.values()
            ],
            'last_brain_state': self.last_brain_state
        }
    
    def disconnect_all(self):
        """Disconnect from all devices"""
        for device in self.devices.values():
            if device.websocket:
                try:
                    device.websocket.close()
                except:
                    pass
                device.connected = False

# =============================================================================
# WEB DASHBOARD
# =============================================================================

class MindShowDashboard:
    """Web dashboard for monitoring and debugging"""
    
    def __init__(self):
        self.app = FastAPI(title="MindShow Integrated Dashboard")
        self.connected_clients: Set[WebSocket] = set()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web routes"""
        
        @self.app.get("/")
        async def dashboard():
            return HTMLResponse(self._get_dashboard_html())
        
        @self.app.get("/api/status")
        async def get_status():
            return {
                "timestamp": datetime.now().isoformat(),
                "system": "online",
                "version": "2.0-integrated"
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.connected_clients.add(websocket)
            logger.info("Dashboard client connected")
            
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
    
    async def broadcast_data(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.connected_clients:
            return
            
        message = json.dumps(data)
        disconnected = []
        
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🧠 MindShow Integrated Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container { max-width: 1400px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .metric { 
                    background: rgba(255,255,255,0.1); 
                    padding: 20px; 
                    border-radius: 10px; 
                    text-align: center;
                }
                .metric-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
                .devices { 
                    background: rgba(255,255,255,0.1); 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 20px;
                }
                .device { 
                    background: rgba(255,255,255,0.1); 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .status-online { color: #4ecdc4; }
                .status-offline { color: #ff6b6b; }
                .brain-state { font-size: 28px; font-weight: bold; text-align: center; padding: 20px; }
                .engaged { color: #ff6b6b; }
                .relaxed { color: #4ecdc4; }
                .neutral { color: #45b7d1; }
                .chart { 
                    background: rgba(255,255,255,0.1); 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 20px;
                    height: 400px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 MindShow Integrated System</h1>
                    <p>Phase 2+3 Implementation - Multi-Pixelblaze Control</p>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <h3>Brain State</h3>
                        <div id="brain-state" class="metric-value brain-state">--</div>
                    </div>
                    <div class="metric">
                        <h3>EEG Source</h3>
                        <div id="eeg-source" class="metric-value">--</div>
                    </div>
                    <div class="metric">
                        <h3>Attention</h3>
                        <div id="attention" class="metric-value">0.000</div>
                    </div>
                    <div class="metric">
                        <h3>Relaxation</h3>
                        <div id="relaxation" class="metric-value">0.000</div>
                    </div>
                    <div class="metric">
                        <h3>Connected Devices</h3>
                        <div id="device-count" class="metric-value">0/0</div>
                    </div>
                </div>
                
                <div class="devices">
                    <h3>🎆 Pixelblaze Controllers</h3>
                    <div id="devices-list">No devices connected</div>
                </div>
                
                <div class="chart">
                    <h3>Real-time Brainwave Activity</h3>
                    <div id="brainwave-chart"></div>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8000/ws');
                const maxDataPoints = 50;
                let brainwaveData = [];
                
                ws.onopen = () => console.log('Dashboard connected');
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                function updateDashboard(data) {
                    if (data.brain_data) {
                        updateBrainData(data.brain_data);
                    }
                    if (data.pixelblaze_status) {
                        updateDevices(data.pixelblaze_status);
                    }
                }
                
                function updateBrainData(brain) {
                    document.getElementById('brain-state').textContent = brain.brain_state.toUpperCase();
                    document.getElementById('brain-state').className = 'metric-value brain-state ' + brain.brain_state;
                    document.getElementById('eeg-source').textContent = brain.source.toUpperCase();
                    document.getElementById('attention').textContent = brain.attention.toFixed(3);
                    document.getElementById('relaxation').textContent = brain.relaxation.toFixed(3);
                    
                    updateChart(brain);
                }
                
                function updateDevices(status) {
                    const deviceCount = document.getElementById('device-count');
                    deviceCount.textContent = status.connected_devices + '/' + status.total_devices;
                    
                    const devicesList = document.getElementById('devices-list');
                    if (status.devices.length === 0) {
                        devicesList.innerHTML = 'No devices connected';
                    } else {
                        devicesList.innerHTML = status.devices.map(device => `
                            <div class="device">
                                <div>
                                    <strong>${device.name}</strong> (${device.ip})<br>
                                    <small>Patterns: ${device.patterns_count}</small>
                                </div>
                                <div class="${device.connected ? 'status-online' : 'status-offline'}">
                                    ${device.connected ? '🟢 Online' : '🔴 Offline'}
                                </div>
                            </div>
                        `).join('');
                    }
                }
                
                function updateChart(brain) {
                    const timestamp = new Date();
                    brainwaveData.push({
                        time: timestamp,
                        delta: brain.band_powers.delta,
                        theta: brain.band_powers.theta,
                        alpha: brain.band_powers.alpha,
                        beta: brain.band_powers.beta,
                        gamma: brain.band_powers.gamma
                    });
                    
                    if (brainwaveData.length > maxDataPoints) {
                        brainwaveData.shift();
                    }
                    
                    const traces = [
                        { name: 'Delta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.delta), line: {color: '#ff6b6b'} },
                        { name: 'Theta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.theta), line: {color: '#4ecdc4'} },
                        { name: 'Alpha', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.alpha), line: {color: '#45b7d1'} },
                        { name: 'Beta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.beta), line: {color: '#96ceb4'} },
                        { name: 'Gamma', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.gamma), line: {color: '#feca57'} }
                    ];
                    
                    const layout = {
                        xaxis: { title: 'Time' },
                        yaxis: { title: 'Power' },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: 'white' },
                        margin: { t: 30, r: 30, b: 50, l: 50 }
                    };
                    
                    Plotly.newPlot('brainwave-chart', traces, layout);
                }
            </script>
        </body>
        </html>
        """

# =============================================================================
# MAIN INTEGRATED SYSTEM
# =============================================================================

class MindShowIntegratedSystem:
    """Main integrated system coordinating all components"""
    
    def __init__(self, config: MindShowConfig):
        self.config = config
        self.running = False
        
        # Initialize components
        self.eeg_processor = IntegratedEEGProcessor(config)
        self.pixelblaze_controller = MultiPixelblazeController(config)
        self.dashboard = MindShowDashboard()
        
        # Statistics
        self.stats = {
            'start_time': time.time(),
            'brain_updates': 0,
            'led_updates': 0,
            'errors': 0
        }
    
    async def start(self):
        """Start the integrated system"""
        logger.info("🚀 Starting MindShow Integrated System")
        
        # Connect EEG
        if not self.eeg_processor.connect():
            logger.error("❌ Failed to connect to EEG source")
            return False
        
        # Discover and connect Pixelblaze devices
        connected_devices = await self.pixelblaze_controller.discover_and_connect()
        if connected_devices == 0:
            logger.warning("⚠️  No Pixelblaze devices connected - continuing without LED control")
        
        # Start web dashboard
        dashboard_task = asyncio.create_task(self._run_dashboard())
        
        # Start main processing loop
        processing_task = asyncio.create_task(self._processing_loop())
        
        self.running = True
        logger.info("✅ MindShow Integrated System started successfully!")
        
        try:
            await asyncio.gather(dashboard_task, processing_task)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
        finally:
            await self.shutdown()
        
        return True
    
    async def _run_dashboard(self):
        """Run web dashboard server"""
        config = uvicorn.Config(
            self.dashboard.app, 
            host="0.0.0.0", 
            port=self.config.web_port, 
            log_level="warning"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def _processing_loop(self):
        """Main processing loop"""
        logger.info("🔄 Starting processing loop...")
        update_interval = 1.0 / self.config.update_rate
        
        while self.running:
            try:
                start_time = time.time()
                
                # Get brain state
                brain_data = self.eeg_processor.get_brain_state()
                
                if brain_data:
                    self.stats['brain_updates'] += 1
                    
                    # Update Pixelblaze controllers
                    await self.pixelblaze_controller.update_from_brain_state(
                        brain_data['brain_state'], brain_data
                    )
                    self.stats['led_updates'] += 1
                    
                    # Broadcast to dashboard
                    # Fix NaN values for JSON compatibility
                    def fix_nan_values(obj):
                        import math
                        if isinstance(obj, dict):
                            return {k: fix_nan_values(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [fix_nan_values(v) for v in obj]
                        elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                            return None
                        else:
                            return obj
                    
                    dashboard_data = {
                        'brain_data': fix_nan_values(brain_data),
                        'pixelblaze_status': self.pixelblaze_controller.get_status(),
                        'stats': self.stats
                    }
                    await self.dashboard.broadcast_data(dashboard_data)
                    
                    # Log periodic status
                    if self.stats['brain_updates'] % 100 == 0:
                        self._log_status()
                
                # Sleep for remaining time
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(1.0)
    
    def _log_status(self):
        """Log periodic status"""
        uptime = time.time() - self.stats['start_time']
        logger.info(f"📊 Status - Uptime: {uptime:.1f}s, Brain Updates: {self.stats['brain_updates']}, LED Updates: {self.stats['led_updates']}, Errors: {self.stats['errors']}")
    
    async def shutdown(self):
        """Shutdown system"""
        logger.info("🔄 Shutting down system...")
        self.running = False
        
        # Disconnect components
        self.eeg_processor.disconnect()
        self.pixelblaze_controller.disconnect_all()
        
        logger.info("✅ System shutdown complete")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger.info("🧠 MindShow Integrated System - Phase 2+3 Implementation")
    
    # Create configuration
    config = MindShowConfig()
    
    # Detect if running on Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'BCM' in f.read():  # Raspberry Pi signature
                config.pi_mode = True
                logger.info("🍓 Raspberry Pi detected - enabling Pi optimizations")
    except:
        pass
    
    # Create and start system
    system = MindShowIntegratedSystem(config)
    await system.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
