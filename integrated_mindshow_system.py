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
    discovery_timeout: float = 10.0  # Increased from 5.0 to 10.0
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
    
    # EEG Processing Parameters (for real-time adjustment)
    attention_min: float = 0.0  # Minimum value for attention normalization
    attention_max: float = 10.0  # Maximum value for attention normalization
    relaxation_min: float = 0.0  # Minimum value for relaxation normalization
    relaxation_max: float = 5.0  # Maximum value for relaxation normalization

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
        
        # Dynamic range tracking for adaptive normalization
        self.attention_range_history = []
        self.relaxation_range_history = []
        self.max_history_size = 100
        
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
        
        # Calculate attention and relaxation scores with robust fallbacks
        band_powers = raw_data['band_powers']
        
        # Debug: Log all band powers
        logger.debug(f"🧠 Raw EEG - Alpha: {band_powers['alpha']:.4f}, Beta: {band_powers['beta']:.4f}, Theta: {band_powers['theta']:.4f}, Delta: {band_powers['delta']:.4f}")
        
        # Attention calculation (Beta/Alpha ratio)
        if band_powers['alpha'] > 0:
            attention_score = band_powers['beta'] / band_powers['alpha']
        else:
            attention_score = 0.5  # Neutral if no alpha activity
            logger.debug("🔄 No alpha activity, using neutral attention")
        
        # Relaxation calculation with multiple fallback methods
        relaxation_score = self._calculate_relaxation_robust(band_powers)
        
        # Debug: Log raw ratios
        logger.debug(f"🧠 Raw Ratios - Attention: {attention_score:.4f}, Relaxation: {relaxation_score:.4f}")
        
        # Normalize scores using configurable parameters
        attention_range = self.config.attention_max - self.config.attention_min
        relaxation_range = self.config.relaxation_max - self.config.relaxation_min
        
        attention_score = min(1.0, max(0.0, (attention_score - self.config.attention_min) / attention_range))
        relaxation_score = min(1.0, max(0.0, (relaxation_score - self.config.relaxation_min) / relaxation_range))
        
        # Debug: Log normalized values
        logger.debug(f"🎛️ Normalized - Attention: {attention_score:.4f}, Relaxation: {relaxation_score:.4f}")
        logger.debug(f"🎛️ Config - Att Min: {self.config.attention_min}, Att Max: {self.config.attention_max}")
        logger.debug(f"🎛️ Config - Relax Min: {self.config.relaxation_min}, Relax Max: {self.config.relaxation_max}")
        
        # Final fallback: If normalization results in 0, use dynamic scaling
        if relaxation_score == 0.0:
            logger.warning("⚠️ Relaxation normalized to 0, using dynamic scaling")
            relaxation_score = self._dynamic_relaxation_scaling(band_powers)
            logger.debug(f"🔄 Dynamic scaling - Relaxation: {relaxation_score:.4f}")
        
        if attention_score == 0.0:
            logger.warning("⚠️ Attention normalized to 0, using dynamic scaling")
            attention_score = self._dynamic_attention_scaling(band_powers)
            logger.debug(f"🔄 Dynamic scaling - Attention: {attention_score:.4f}")
        
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
    
    def _calculate_relaxation_robust(self, band_powers: Dict[str, float]) -> float:
        """Calculate relaxation with multiple fallback methods"""
        
        # Method 1: Alpha/Theta ratio (primary)
        if not np.isnan(band_powers['theta']) and band_powers['theta'] > 0:
            relaxation_score = band_powers['alpha'] / band_powers['theta']
            logger.debug(f"🔄 Method 1 (Alpha/Theta): {relaxation_score:.4f}")
            return relaxation_score
        
        # Method 2: Alpha/Delta ratio (fallback 1)
        if not np.isnan(band_powers['delta']) and band_powers['delta'] > 0:
            relaxation_score = band_powers['alpha'] / band_powers['delta']
            logger.debug(f"🔄 Method 2 (Alpha/Delta): {relaxation_score:.4f}")
            return relaxation_score
        
        # Method 3: Alpha power only (fallback 2)
        if not np.isnan(band_powers['alpha']) and band_powers['alpha'] > 0:
            # Scale alpha power to reasonable range (0-5)
            relaxation_score = min(5.0, band_powers['alpha'] / 10.0)
            logger.debug(f"🔄 Method 3 (Alpha power): {relaxation_score:.4f}")
            return relaxation_score
        
        # Method 4: Relative alpha dominance (fallback 3)
        total_power = sum([v for v in band_powers.values() if not np.isnan(v) and v > 0])
        if total_power > 0 and not np.isnan(band_powers['alpha']):
            relaxation_score = band_powers['alpha'] / total_power * 5.0  # Scale to 0-5 range
            logger.debug(f"🔄 Method 4 (Alpha dominance): {relaxation_score:.4f}")
            return relaxation_score
        
        # Method 5: Last resort - neutral value
        logger.warning("⚠️ All relaxation calculation methods failed, using neutral value")
        return 0.5
    
    def _dynamic_relaxation_scaling(self, band_powers: Dict[str, float]) -> float:
        """Dynamic scaling for relaxation when normalization fails"""
        
        # Try different scaling approaches based on available data
        if not np.isnan(band_powers['alpha']) and band_powers['alpha'] > 0:
            # Scale alpha power directly
            scaled_relaxation = band_powers['alpha'] / 20.0  # Assume max alpha around 20
            return min(1.0, max(0.0, scaled_relaxation))
        
        elif not np.isnan(band_powers['theta']) and band_powers['theta'] > 0:
            # Use inverse theta (lower theta = higher relaxation)
            inverse_theta = 1.0 / (band_powers['theta'] + 0.1)
            return min(1.0, max(0.0, inverse_theta / 10.0))
        
        else:
            # Use a combination of available bands
            available_powers = [v for v in band_powers.values() if not np.isnan(v) and v > 0]
            if available_powers:
                avg_power = sum(available_powers) / len(available_powers)
                return min(1.0, max(0.0, avg_power / 10.0))
            else:
                return 0.5  # Neutral fallback
    
    def _dynamic_attention_scaling(self, band_powers: Dict[str, float]) -> float:
        """Dynamic scaling for attention when normalization fails"""
        
        # Try different scaling approaches based on available data
        if not np.isnan(band_powers['beta']) and band_powers['beta'] > 0:
            # Scale beta power directly
            scaled_attention = band_powers['beta'] / 15.0  # Assume max beta around 15
            return min(1.0, max(0.0, scaled_attention))
        
        elif not np.isnan(band_powers['alpha']) and band_powers['alpha'] > 0:
            # Use inverse alpha (lower alpha = higher attention)
            inverse_alpha = 1.0 / (band_powers['alpha'] + 0.1)
            return min(1.0, max(0.0, inverse_alpha / 10.0))
        
        else:
            # Use a combination of available bands
            available_powers = [v for v in band_powers.values() if not np.isnan(v) and v > 0]
            if available_powers:
                avg_power = sum(available_powers) / len(available_powers)
                return min(1.0, max(0.0, avg_power / 10.0))
            else:
                return 0.5  # Neutral fallback
    
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
        attention = brain_data.get('attention', 0.5) if brain_data else self.last_attention
        relaxation = brain_data.get('relaxation', 0.5) if brain_data else self.last_relaxation
        
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
            logger.debug(f"🎯 Sending variables to {device.name}: {variables}")
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
        
        @self.app.post("/api/update_config")
        async def update_config(request: dict):
            """Update configuration parameters in real-time"""
            try:
                parameter = request.get("parameter")
                value = request.get("value")
                
                if parameter is None or value is None:
                    return {"success": False, "error": "Missing parameter or value"}
                
                # Validate parameter names
                valid_params = {
                    "color_mood_smoothing",
                    "color_mood_intensity_scale", 
                    "color_mood_attention_weight",
                    "color_mood_relaxation_weight",
                    "attention_min",
                    "attention_max",
                    "relaxation_min",
                    "relaxation_max"
                }
                
                if parameter not in valid_params:
                    return {"success": False, "error": f"Invalid parameter: {parameter}"}
                
                # Update the configuration using the main system
                if hasattr(self, 'main_system'):
                    success = self.main_system.update_config(parameter, value)
                    return {"success": success, "parameter": parameter, "value": value}
                else:
                    logger.warning("Main system not available for config update")
                    return {"success": False, "error": "Main system not available"}
                
            except Exception as e:
                logger.error(f"Error updating config: {e}")
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/manual_mood")
        async def manual_mood(request: dict):
            """Send manual mood and intensity values to Pixelblaze"""
            try:
                color_mood = request.get('color_mood', 0.5)
                intensity = request.get('intensity', 0.5)
                
                # Validate inputs
                if not (0 <= color_mood <= 1 and 0 <= intensity <= 1):
                    return {"success": False, "error": "Values must be between 0 and 1"}
                
                if hasattr(self, 'main_system'):
                    success = await self.main_system.send_manual_mood(color_mood, intensity)
                    return {"success": success, "color_mood": color_mood, "intensity": intensity}
                else:
                    return {"success": False, "error": "System not initialized"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/send_intensity")
        async def send_intensity(request: dict):
            """Send intensity value only to Pixelblaze (no color change)"""
            try:
                intensity = request.get('intensity', 0.5)
                
                # Validate input
                if not (0 <= intensity <= 1):
                    return {"success": False, "error": "Intensity must be between 0 and 1"}
                
                if hasattr(self, 'main_system'):
                    success = await self.main_system.send_intensity_only(intensity)
                    return {"success": success, "intensity": intensity}
                else:
                    return {"success": False, "error": "System not initialized"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.get("/api/get_patterns")
        async def get_patterns(device: str):
            """Get available patterns for a specific device"""
            try:
                if not device:
                    return {"success": False, "error": "Device parameter required"}
                
                # Get patterns from main system
                if hasattr(self, 'main_system'):
                    patterns = self.main_system.get_device_patterns(device)
                    return {"success": True, "patterns": patterns}
                else:
                    logger.warning("Main system not available for pattern retrieval")
                    return {"success": False, "error": "Main system not available"}
                
            except Exception as e:
                logger.error(f"Error getting patterns: {e}")
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/switch_pattern")
        async def switch_pattern(request: dict):
            """Switch to a specific pattern on a device"""
            try:
                device = request.get("device")
                pattern = request.get("pattern")
                
                if not device or not pattern:
                    return {"success": False, "error": "Device and pattern parameters required"}
                
                # Switch pattern using main system
                if hasattr(self, 'main_system'):
                    success, pattern_name = self.main_system.switch_device_pattern(device, pattern)
                    if success:
                        return {"success": True, "pattern_name": pattern_name}
                    else:
                        return {"success": False, "error": pattern_name}  # pattern_name contains error message
                else:
                    logger.warning("Main system not available for pattern switching")
                    return {"success": False, "error": "Main system not available"}
                
            except Exception as e:
                logger.error(f"Error switching pattern: {e}")
                return {"success": False, "error": str(e)}
    
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
                
                /* Phase 4b: Color Mood Styles */
                .color-mood-display { 
                    border: 2px solid rgba(255,255,255,0.3); 
                    background: rgba(255,255,255,0.05); 
                }
                .color-mood-bar {
                    height: 20px;
                    background: linear-gradient(90deg, 
                        #ff4444 0%,     /* Deep warm */
                        #ff8844 25%,    /* Warm */
                        #44ff44 50%,    /* Neutral */
                        #4488ff 75%,    /* Cool */
                        #8844ff 100%);  /* Deep cool */
                    border-radius: 10px;
                    margin: 10px 0;
                    position: relative;
                    border: 1px solid rgba(255,255,255,0.3);
                }
                .color-mood-indicator {
                    position: absolute;
                    top: -2px;
                    width: 4px;
                    height: 24px;
                    background: white;
                    border: 2px solid #333;
                    border-radius: 2px;
                    box-shadow: 0 0 10px rgba(255,255,255,0.8);
                    transition: left 0.3s ease;
                }
                .color-mood-description {
                    font-size: 14px;
                    opacity: 0.8;
                    margin-top: 5px;
                }
                .warm-mood { color: #ff6b6b; }
                .cool-mood { color: #4ecdc4; }
                .neutral-mood { color: #45b7d1; }
                
                /* Phase 4b: Slider Controls */
                .slider-control {
                    margin: 15px 0;
                    padding: 10px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .slider-control label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: bold;
                    color: #fff;
                }
                .slider-control input[type="range"] {
                    width: 100%;
                    height: 8px;
                    border-radius: 4px;
                    background: rgba(255,255,255,0.2);
                    outline: none;
                    -webkit-appearance: none;
                }
                .slider-control input[type="range"]::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    appearance: none;
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    background: #4ecdc4;
                    cursor: pointer;
                    border: 2px solid #fff;
                }
                .slider-control input[type="range"]::-moz-range-thumb {
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    background: #4ecdc4;
                    cursor: pointer;
                    border: 2px solid #fff;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 MindShow Integrated System</h1>
                    <p>Phase 4b: Continuous Color Mood Mapping - Real-time Brain-to-Light Control</p>
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
                
                <!-- Phase 4b: Color Mood Visualization -->
                <div class="metrics">
                    <div class="metric color-mood-display">
                        <h3>🎨 Color Mood</h3>
                        <div id="color-mood-value" class="metric-value">0.500</div>
                        <div id="color-mood-bar" class="color-mood-bar">
                            <div id="color-mood-indicator" class="color-mood-indicator"></div>
                        </div>
                        <div id="color-mood-description" class="color-mood-description">Neutral</div>
                    </div>
                    <div class="metric">
                        <h3>🔬 Engagement Level</h3>
                        <div id="engagement-level" class="metric-value">0.500</div>
                    </div>
                    <div class="metric">
                        <h3>🧠 Mental Activity</h3>
                        <div id="mental-activity" class="metric-value">--</div>
                    </div>
                </div>
                
                <!-- Phase 4b: Color Mood Control Sliders -->
                <div class="metrics">
                    <div class="metric">
                        <h3>🎛️ Color Mood Controls</h3>
                        <div class="slider-control">
                            <label for="smoothing-slider">Smoothing: <span id="smoothing-value">0.3</span></label>
                            <input type="range" id="smoothing-slider" min="0.0" max="1.0" step="0.1" value="0.3">
                        </div>
                        <div class="slider-control">
                            <label for="intensity-slider">Intensity Scale: <span id="intensity-value">0.5</span></label>
                            <input type="range" id="intensity-slider" min="0.0" max="1.0" step="0.1" value="0.5">
                        </div>
                        <div class="slider-control">
                            <label for="attention-weight-slider">Attention Weight: <span id="attention-weight-value">0.4</span></label>
                            <input type="range" id="attention-weight-slider" min="0.0" max="1.0" step="0.1" value="0.4">
                        </div>
                        <div class="slider-control">
                            <label for="relaxation-weight-slider">Relaxation Weight: <span id="relaxation-weight-value">0.4</span></label>
                            <input type="range" id="relaxation-weight-slider" min="0.0" max="1.0" step="0.1" value="0.4">
                        </div>
                    </div>
                </div>
                
                <!-- EEG Processing Controls -->
                <div class="metrics">
                    <div class="metric">
                        <h3>🧠 EEG Processing Controls</h3>
                        <div class="slider-control">
                            <label for="attention-min-slider">Attention Min: <span id="attention-min-value">0.0</span></label>
                            <input type="range" id="attention-min-slider" min="0.0" max="1.0" step="0.05" value="0.0">
                        </div>
                        <div class="slider-control">
                            <label for="attention-max-slider">Attention Max: <span id="attention-max-value">10.0</span></label>
                            <input type="range" id="attention-max-slider" min="1.0" max="10.0" step="0.5" value="10.0">
                        </div>
                        <div class="slider-control">
                            <label for="relaxation-min-slider">Relaxation Min: <span id="relaxation-min-value">0.0</span></label>
                            <input type="range" id="relaxation-min-slider" min="0.0" max="1.0" step="0.05" value="0.0">
                        </div>
                        <div class="slider-control">
                            <label for="relaxation-max-slider">Relaxation Max: <span id="relaxation-max-value">5.0</span></label>
                            <input type="range" id="relaxation-max-slider" min="1.0" max="10.0" step="0.5" value="5.0">
                        </div>
                    </div>
                </div>
                
                <!-- Manual Mood Control -->
                <div class="metrics">
                    <div class="metric">
                        <h3>🎛️ Manual Mood Control</h3>
                        <p style="font-size: 12px; opacity: 0.8; margin-bottom: 15px;">
                            Test different color moods when no brain data is available
                        </p>
                        <div class="slider-control">
                            <label for="manual-mood-slider">Color Mood (🔥 Warm → ❄️ Cool): <span id="manual-mood-value">0.5</span></label>
                            <input type="range" id="manual-mood-slider" min="0.0" max="1.0" step="0.01" value="0.5">
                        </div>
                        <div class="slider-control">
                            <label for="manual-intensity-slider">Intensity: <span id="manual-intensity-value">0.5</span></label>
                            <input type="range" id="manual-intensity-slider" min="0.0" max="1.0" step="0.01" value="0.5">
                        </div>
                        <button id="send-manual-mood" style="margin-top: 10px; padding: 8px 16px; background: #4ecdc4; border: none; border-radius: 5px; color: white; cursor: pointer;">
                            🎨 Send to Pixelblaze
                        </button>
                        <div id="manual-mood-status" style="margin-top: 10px; font-size: 12px; opacity: 0.8;"></div>
                    </div>
                </div>
                
                <!-- Pattern Selector -->
                <div class="metrics">
                    <div class="metric">
                        <h3>🎭 Pattern Selector</h3>
                        <p style="font-size: 12px; opacity: 0.8; margin-bottom: 15px;">
                            Switch between available Pixelblaze patterns
                        </p>
                        <div style="margin-bottom: 15px;">
                            <label for="device-selector">Device:</label>
                            <select id="device-selector" style="margin-left: 10px; padding: 5px; border-radius: 3px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3);">
                                <option value="">Select a device...</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label for="pattern-selector">Pattern:</label>
                            <select id="pattern-selector" style="margin-left: 10px; padding: 5px; border-radius: 3px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3); width: 200px;">
                                <option value="">Select a pattern...</option>
                            </select>
                        </div>
                        <button id="switch-pattern" style="padding: 8px 16px; background: #ff6b6b; border: none; border-radius: 5px; color: white; cursor: pointer; margin-right: 10px;">
                            🎭 Switch Pattern
                        </button>
                        <button id="refresh-patterns" style="padding: 8px 16px; background: #45b7d1; border: none; border-radius: 5px; color: white; cursor: pointer;">
                            🔄 Refresh
                        </button>
                        <div id="pattern-status" style="margin-top: 10px; font-size: 12px; opacity: 0.8;"></div>
                    </div>
                </div>
                
                <div class="devices">
                    <h3>🎆 Pixelblaze Controllers</h3>
                    <div id="devices-list">No devices connected</div>
                </div>
                
                <div class="chart">
                    <h3>🎨 Real-time Brain State & Color Mood</h3>
                    <div id="brainwave-chart"></div>
                </div>
                
                <!-- Debug Messages -->
                <div class="metrics">
                    <div class="metric">
                        <h3>🐛 Debug Messages</h3>
                        <div id="debug-messages" style="height: 150px; overflow-y: scroll; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;">
                            <div>System started. Ready for slider adjustments...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8000/ws');
                const maxDataPoints = 50;
                let brainwaveData = [];
                let lastUpdateTime = 0;
                const UPDATE_THROTTLE = 2000; // Only update UI every 2 seconds
                let isUserInteracting = false;
                
                ws.onopen = () => console.log('Dashboard connected');
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    const now = Date.now();
                    
                    // Throttle updates to prevent UI flickering
                    // Don't update if user is interacting with dropdowns
                    if (now - lastUpdateTime > UPDATE_THROTTLE && !isUserInteracting) {
                        updateDashboard(data);
                        lastUpdateTime = now;
                    }
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
                    
                    // Update Phase 4b color mood visualization
                    if (brain.color_mood !== undefined) {
                        updateColorMood(brain.color_mood, brain.engagement_level, brain.attention, brain.relaxation);
                    }
                    
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
                    
                    // Update pattern selector device list
                    if (window.updateDeviceSelector) {
                        window.updateDeviceSelector(status.devices);
                    }
                }
                
                function updateColorMood(colorMood, engagementLevel, attention, relaxation) {
                    // Update numerical value
                    document.getElementById('color-mood-value').textContent = colorMood.toFixed(3);
                    document.getElementById('engagement-level').textContent = engagementLevel.toFixed(3);
                    
                    // Update position of indicator on color bar
                    const indicator = document.getElementById('color-mood-indicator');
                    const position = colorMood * 100; // Convert to percentage
                    indicator.style.left = `calc(${position}% - 2px)`;
                    
                    // Update description and styling
                    const description = document.getElementById('color-mood-description');
                    const moodValue = document.getElementById('color-mood-value');
                    
                    if (colorMood < 0.3) {
                        description.textContent = '🔥 Warm (Engaged/Focus)';
                        description.className = 'color-mood-description warm-mood';
                        moodValue.className = 'metric-value warm-mood';
                    } else if (colorMood > 0.7) {
                        description.textContent = '❄️ Cool (Relaxed/Calm)';
                        description.className = 'color-mood-description cool-mood';
                        moodValue.className = 'metric-value cool-mood';
                    } else {
                        description.textContent = '🌈 Neutral (Balanced)';
                        description.className = 'color-mood-description neutral-mood';
                        moodValue.className = 'metric-value neutral-mood';
                    }
                    
                    // Update mental activity indicator
                    const mentalActivity = (attention + relaxation) / 2;
                    const activityElement = document.getElementById('mental-activity');
                    if (mentalActivity > 0.75) {
                        activityElement.textContent = '🔥 High';
                        activityElement.className = 'metric-value warm-mood';
                    } else if (mentalActivity > 0.5) {
                        activityElement.textContent = '⚡ Medium';
                        activityElement.className = 'metric-value neutral-mood';
                    } else {
                        activityElement.textContent = '😴 Low';
                        activityElement.className = 'metric-value cool-mood';
                    }
                }
                
                function updateChart(brain) {
                    const timestamp = new Date();
                    brainwaveData.push({
                        time: timestamp,
                        delta: brain.band_powers ? brain.band_powers.delta : 0,
                        theta: brain.band_powers ? brain.band_powers.theta : 0,
                        alpha: brain.band_powers ? brain.band_powers.alpha : 0,
                        beta: brain.band_powers ? brain.band_powers.beta : 0,
                        gamma: brain.band_powers ? brain.band_powers.gamma : 0,
                        attention: brain.attention || 0,
                        relaxation: brain.relaxation || 0,
                        colorMood: brain.color_mood || 0.5
                    });
                    
                    if (brainwaveData.length > maxDataPoints) {
                        brainwaveData.shift();
                    }
                    
                    const traces = [
                        { 
                            name: 'Attention', 
                            x: brainwaveData.map(d => d.time), 
                            y: brainwaveData.map(d => d.attention), 
                            type: 'scatter',
                            mode: 'lines',
                            line: {color: '#ff6b6b', width: 2} 
                        },
                        { 
                            name: 'Relaxation', 
                            x: brainwaveData.map(d => d.time), 
                            y: brainwaveData.map(d => d.relaxation), 
                            type: 'scatter',
                            mode: 'lines',
                            line: {color: '#4ecdc4', width: 2} 
                        },
                        { 
                            name: 'Color Mood', 
                            x: brainwaveData.map(d => d.time), 
                            y: brainwaveData.map(d => d.colorMood), 
                            type: 'scatter',
                            mode: 'lines',
                            line: {color: '#ffaa00', width: 3},
                            yaxis: 'y2'
                        }
                    ];
                    
                    const layout = {
                        title: 'Real-time Brain State & Color Mood',
                        xaxis: { 
                            title: 'Time',
                            gridcolor: 'rgba(255,255,255,0.2)',
                            color: 'white'
                        },
                        yaxis: { 
                            title: 'Attention/Relaxation Score',
                            range: [0, 1],
                            gridcolor: 'rgba(255,255,255,0.2)',
                            color: 'white'
                        },
                        yaxis2: {
                            title: 'Color Mood (🔥→❄️)',
                            titlefont: { color: '#ffaa00' },
                            tickfont: { color: '#ffaa00' },
                            overlaying: 'y',
                            side: 'right',
                            range: [0, 1],
                            gridcolor: 'rgba(255,255,255,0.1)'
                        },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: 'white' },
                        margin: { t: 50, r: 80, b: 50, l: 60 },
                        legend: { 
                            x: 0, 
                            y: 1,
                            bgcolor: 'rgba(0,0,0,0.3)'
                        }
                    };
                    
                    Plotly.newPlot('brainwave-chart', traces, layout);
                }
                
                // Phase 4b: Slider Controls
                function setupSliders() {
                    const sliders = [
                        { id: 'smoothing-slider', valueId: 'smoothing-value', param: 'color_mood_smoothing' },
                        { id: 'intensity-slider', valueId: 'intensity-value', param: 'color_mood_intensity_scale' },
                        { id: 'attention-weight-slider', valueId: 'attention-weight-value', param: 'color_mood_attention_weight' },
                        { id: 'relaxation-weight-slider', valueId: 'relaxation-weight-value', param: 'color_mood_relaxation_weight' },
                        { id: 'attention-min-slider', valueId: 'attention-min-value', param: 'attention_min' },
                        { id: 'attention-max-slider', valueId: 'attention-max-value', param: 'attention_max' },
                        { id: 'relaxation-min-slider', valueId: 'relaxation-min-value', param: 'relaxation_min' },
                        { id: 'relaxation-max-slider', valueId: 'relaxation-max-value', param: 'relaxation_max' }
                    ];
                    
                    sliders.forEach(slider => {
                        const sliderElement = document.getElementById(slider.id);
                        const valueElement = document.getElementById(slider.valueId);
                        
                        sliderElement.addEventListener('input', (e) => {
                            const value = parseFloat(e.target.value);
                            valueElement.textContent = value.toFixed(1);
                            updateConfig(slider.param, value);
                        });
                    });
                }
                
                function updateConfig(param, value) {
                    fetch('/api/update_config', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            parameter: param,
                            value: value
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            console.log(`✅ Updated ${param} to ${value}`);
                            showDebugMessage(`✅ Updated ${param} to ${value}`);
                        } else {
                            console.error('Failed to update config:', data.error);
                            showDebugMessage(`❌ Failed to update ${param}: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        console.error('Error updating config:', error);
                        showDebugMessage(`❌ Error updating ${param}: ${error}`);
                    });
                }
                
                function showDebugMessage(message) {
                    const debugDiv = document.getElementById('debug-messages');
                    if (debugDiv) {
                        const timestamp = new Date().toLocaleTimeString();
                        debugDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
                        debugDiv.scrollTop = debugDiv.scrollHeight;
                    }
                }
                
                // Manual Mood Control
                function setupManualMoodControl() {
                    const moodSlider = document.getElementById('manual-mood-slider');
                    const moodValue = document.getElementById('manual-mood-value');
                    const intensitySlider = document.getElementById('manual-intensity-slider');
                    const intensityValue = document.getElementById('manual-intensity-value');
                    const sendButton = document.getElementById('send-manual-mood');
                    const statusDiv = document.getElementById('manual-mood-status');
                    
                    moodSlider.addEventListener('input', (e) => {
                        const value = parseFloat(e.target.value);
                        moodValue.textContent = value.toFixed(2);
                    });
                    
                    intensitySlider.addEventListener('input', (e) => {
                        const value = parseFloat(e.target.value);
                        intensityValue.textContent = value.toFixed(2);
                        // Send intensity immediately when slider changes
                        sendIntensityOnly(value);
                    });
                    
                    sendButton.addEventListener('click', () => {
                        const moodValue = parseFloat(moodSlider.value);
                        const intensityValue = parseFloat(intensitySlider.value);
                        
                        sendManualMood(moodValue, intensityValue);
                    });
                }
                
                function sendIntensityOnly(intensity) {
                    fetch('/api/send_intensity', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            intensity: intensity
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showDebugMessage(`⚡ Intensity updated: ${intensity.toFixed(2)}`);
                        } else {
                            showDebugMessage(`❌ Intensity failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        showDebugMessage(`❌ Intensity error: ${error}`);
                    });
                }
                
                function sendManualMood(mood, intensity) {
                    const statusDiv = document.getElementById('manual-mood-status');
                    statusDiv.textContent = '🔄 Sending to Pixelblaze...';
                    
                    fetch('/api/manual_mood', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            color_mood: mood,
                            intensity: intensity
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            statusDiv.textContent = `✅ Sent: Mood=${mood.toFixed(2)}, Intensity=${intensity.toFixed(2)}`;
                            statusDiv.style.color = '#4ecdc4';
                            showDebugMessage(`✅ Manual mood sent: ${mood.toFixed(2)} (intensity: ${intensity.toFixed(2)})`);
                        } else {
                            statusDiv.textContent = `❌ Failed: ${data.error}`;
                            statusDiv.style.color = '#ff6b6b';
                            showDebugMessage(`❌ Manual mood failed: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        statusDiv.textContent = `❌ Error: ${error}`;
                        statusDiv.style.color = '#ff6b6b';
                        showDebugMessage(`❌ Manual mood error: ${error}`);
                    });
                }
                
                // Pattern Selector
                function setupPatternSelector() {
                    const deviceSelector = document.getElementById('device-selector');
                    const patternSelector = document.getElementById('pattern-selector');
                    const switchButton = document.getElementById('switch-pattern');
                    const refreshButton = document.getElementById('refresh-patterns');
                    const statusDiv = document.getElementById('pattern-status');
                    
                    // Populate device selector when devices are available
                    function updateDeviceSelector(devices) {
                        // Don't update if user is interacting
                        if (isUserInteracting) return;
                        
                        // Preserve current selection
                        const currentSelection = deviceSelector.value;
                        
                        // Only update if the device list has actually changed
                        const currentOptions = Array.from(deviceSelector.options).map(opt => opt.value);
                        const newOptions = devices.filter(d => d.connected).map(d => d.ip);
                        
                        // Check if the lists are different
                        const hasChanged = currentOptions.length !== newOptions.length || 
                                         !currentOptions.every((opt, i) => opt === newOptions[i]);
                        
                        if (hasChanged) {
                            deviceSelector.innerHTML = '<option value="">Select a device...</option>';
                            devices.forEach(device => {
                                if (device.connected) {
                                    const option = document.createElement('option');
                                    option.value = device.ip;
                                    option.textContent = `${device.name} (${device.ip})`;
                                    deviceSelector.appendChild(option);
                                }
                            });
                            
                            // Restore selection if it still exists
                            if (currentSelection && newOptions.includes(currentSelection)) {
                                deviceSelector.value = currentSelection;
                            }
                        }
                    }
                    
                    // Add interaction detection
                    deviceSelector.addEventListener('focus', () => {
                        isUserInteracting = true;
                    });
                    
                    deviceSelector.addEventListener('blur', () => {
                        setTimeout(() => { isUserInteracting = false; }, 100);
                    });
                    
                    patternSelector.addEventListener('focus', () => {
                        isUserInteracting = true;
                    });
                    
                    patternSelector.addEventListener('blur', () => {
                        setTimeout(() => { isUserInteracting = false; }, 100);
                    });
                    
                    // Populate pattern selector when device is selected
                    deviceSelector.addEventListener('change', () => {
                        const selectedDevice = deviceSelector.value;
                        patternSelector.innerHTML = '<option value="">Select a pattern...</option>';
                        
                        if (selectedDevice) {
                            // Find the selected device and populate patterns
                            fetch('/api/get_patterns?device=' + selectedDevice)
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success && data.patterns) {
                                        data.patterns.forEach(pattern => {
                                            const option = document.createElement('option');
                                            option.value = pattern.id;
                                            option.textContent = pattern.name;
                                            patternSelector.appendChild(option);
                                        });
                                        statusDiv.textContent = `✅ Loaded ${data.patterns.length} patterns`;
                                        statusDiv.style.color = '#4ecdc4';
                                    } else {
                                        statusDiv.textContent = `❌ Failed to load patterns: ${data.error}`;
                                        statusDiv.style.color = '#ff6b6b';
                                    }
                                })
                                .catch(error => {
                                    statusDiv.textContent = `❌ Error loading patterns: ${error}`;
                                    statusDiv.style.color = '#ff6b6b';
                                });
                        }
                    });
                    
                    // Switch pattern button
                    switchButton.addEventListener('click', () => {
                        const selectedDevice = deviceSelector.value;
                        const selectedPattern = patternSelector.value;
                        
                        if (!selectedDevice || !selectedPattern) {
                            statusDiv.textContent = '❌ Please select both device and pattern';
                            statusDiv.style.color = '#ff6b6b';
                            return;
                        }
                        
                        statusDiv.textContent = '🔄 Switching pattern...';
                        
                        fetch('/api/switch_pattern', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                device: selectedDevice,
                                pattern: selectedPattern
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                statusDiv.textContent = `✅ Switched to: ${data.pattern_name}`;
                                statusDiv.style.color = '#4ecdc4';
                                showDebugMessage(`✅ Pattern switched: ${data.pattern_name} on ${selectedDevice}`);
                            } else {
                                statusDiv.textContent = `❌ Failed: ${data.error}`;
                                statusDiv.style.color = '#ff6b6b';
                                showDebugMessage(`❌ Pattern switch failed: ${data.error}`);
                            }
                        })
                        .catch(error => {
                            statusDiv.textContent = `❌ Error: ${error}`;
                            statusDiv.style.color = '#ff6b6b';
                            showDebugMessage(`❌ Pattern switch error: ${error}`);
                        });
                    });
                    
                    // Refresh patterns button
                    refreshButton.addEventListener('click', () => {
                        statusDiv.textContent = '🔄 Refreshing patterns...';
                        // Trigger a device status update to refresh the list
                        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                            window.ws.send(JSON.stringify({action: 'refresh_patterns'}));
                        }
                        statusDiv.textContent = '✅ Refreshed pattern list';
                        statusDiv.style.color = '#4ecdc4';
                    });
                    
                    // Update device selector when devices are updated
                    window.updateDeviceSelector = updateDeviceSelector;
                }
                
                // Initialize sliders when page loads
                document.addEventListener('DOMContentLoaded', () => {
                    setupSliders();
                    setupManualMoodControl();
                    setupPatternSelector();
                });
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
        
        # Connect dashboard to main system for API calls
        self.dashboard.main_system = self
        
        # Statistics
        self.stats = {
            'start_time': time.time(),
            'brain_updates': 0,
            'led_updates': 0,
            'errors': 0
        }
    
    def update_config(self, parameter: str, value: float) -> bool:
        """Update configuration parameters in real-time"""
        try:
            if hasattr(self.config, parameter):
                setattr(self.config, parameter, value)
                
                # Update the pixelblaze controller with new config
                if hasattr(self.pixelblaze_controller, parameter):
                    setattr(self.pixelblaze_controller, parameter, value)
                
                logger.info(f"✅ Updated config: {parameter} = {value}")
                return True
            else:
                logger.error(f"❌ Invalid config parameter: {parameter}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return False
    
    async def send_manual_mood(self, color_mood: float, intensity: float) -> bool:
        """Send manual mood values to Pixelblaze without pattern switching"""
        try:
            # Create variables dictionary with manual mood
            manual_variables = {
                'colorMoodBias': color_mood,
                'intensity': intensity
            }
            
            # Update all connected devices with variables only (no pattern switch)
            update_tasks = []
            for device in self.pixelblaze_controller.devices.values():
                if device.connected:
                    task = self.pixelblaze_controller._update_device_continuous(
                        device, None, manual_variables  # None = no pattern switch
                    )
                    update_tasks.append(task)
            
            # Execute updates in parallel
            if update_tasks:
                await asyncio.gather(*update_tasks, return_exceptions=True)
            
            logger.info(f"🎨 Manual mood sent: {color_mood:.3f} (intensity: {intensity:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send manual mood: {e}")
            return False
    
    async def send_intensity_only(self, intensity: float) -> bool:
        """Send intensity value only to Pixelblaze (no color change)"""
        try:
            # Create variables dictionary with intensity only
            intensity_variables = {
                'intensity': intensity
            }
            
            # Update all connected devices with intensity only (no pattern switch)
            update_tasks = []
            for device in self.pixelblaze_controller.devices.values():
                if device.connected:
                    task = self.pixelblaze_controller._update_device_continuous(
                        device, None, intensity_variables  # None = no pattern switch
                    )
                    update_tasks.append(task)
            
            # Execute updates in parallel
            if update_tasks:
                await asyncio.gather(*update_tasks, return_exceptions=True)
            
            logger.info(f"⚡ Intensity only sent: {intensity:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send intensity only: {e}")
            return False
    
    def get_device_patterns(self, device_ip: str) -> List[Dict[str, str]]:
        """Get available patterns for a specific device"""
        try:
            # Find the device in the devices dictionary
            device = self.pixelblaze_controller.devices.get(device_ip)
            if device and device.connected:
                # Convert patterns dict to list format
                patterns = []
                for pattern_id, pattern_name in device.patterns.items():
                    patterns.append({
                        "id": pattern_id,
                        "name": pattern_name
                    })
                logger.info(f"📋 Retrieved {len(patterns)} patterns for device {device_ip}")
                return patterns
            
            logger.warning(f"❌ Device {device_ip} not found or not connected")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting patterns for {device_ip}: {e}")
            return []
    
    def switch_device_pattern(self, device_ip: str, pattern_id: str) -> Tuple[bool, str]:
        """Switch to a specific pattern on a device"""
        try:
            # Find the device in the devices dictionary
            device = self.pixelblaze_controller.devices.get(device_ip)
            if device and device.connected:
                # Find the pattern name
                pattern_name = device.patterns.get(pattern_id, "Unknown")
                
                # Switch the pattern
                asyncio.create_task(self.pixelblaze_controller._update_device(
                    device, pattern_name, {}
                ))
                
                logger.info(f"🎭 Switched device {device_ip} to pattern: {pattern_name}")
                return True, pattern_name
            
            logger.warning(f"❌ Device {device_ip} not found or not connected")
            return False, f"Device {device_ip} not found or not connected"
            
        except Exception as e:
            logger.error(f"❌ Error switching pattern on {device_ip}: {e}")
            return False, str(e)
    
    async def start(self):
        """Start the integrated system"""
        logger.info("🚀 Starting MindShow Integrated System")
        
        # Connect EEG
        eeg_connected = self.eeg_processor.connect()
        if not eeg_connected:
            logger.warning("⚠️  No EEG source available - starting in demo mode")
            logger.info("💡 Connect your Muse headband and restart to enable brainwave control")
        
        # Discover and connect Pixelblaze devices with retry logic
        connected_devices = 0
        max_retries = 3
        for attempt in range(max_retries):
            logger.info(f"🔍 Attempting Pixelblaze discovery (attempt {attempt + 1}/{max_retries})")
            connected_devices = await self.pixelblaze_controller.discover_and_connect()
            if connected_devices > 0:
                logger.info(f"✅ Successfully connected to {connected_devices} Pixelblaze device(s)")
                break
            elif attempt < max_retries - 1:
                logger.warning(f"⚠️  No devices found on attempt {attempt + 1}, retrying in 2 seconds...")
                await asyncio.sleep(2)
        
        if connected_devices == 0:
            logger.warning("⚠️  No Pixelblaze devices connected after all retries - continuing without LED control")
        
        # Start web dashboard
        dashboard_task = asyncio.create_task(self._run_dashboard())
        
        # Start main processing loop
        processing_task = asyncio.create_task(self._processing_loop())
        
        self.running = True
        logger.info("✅ MindShow Integrated System started successfully!")
        
        if eeg_connected:
            logger.info("🧠 Brainwave control enabled")
        else:
            logger.info("🎭 Demo mode - dashboard available for testing")
        
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
                
                if brain_data:
                    self.stats['brain_updates'] += 1
                    
                    # Update Pixelblaze controllers
                    await self.pixelblaze_controller.update_from_brain_state(
                        brain_data['brain_state'], brain_data
                    )
                    self.stats['led_updates'] += 1
                    
                    # Enhance brain_data with color mood information
                    enhanced_brain_data = brain_data.copy() if brain_data else {}
                    if brain_data:
                        # Get real attention/relaxation values from brain_data
                        attention = brain_data.get('attention', 0.5)
                        relaxation = brain_data.get('relaxation', 0.5)
                        engagement_level = (attention + relaxation) / 2
                        
                        # Add Phase 4b metrics
                        enhanced_brain_data.update({
                            'color_mood': self.pixelblaze_controller.previous_color_mood,
                            'engagement_level': engagement_level,
                            'attention': attention,
                            'relaxation': relaxation,
                            'color_mood_smoothing': self.pixelblaze_controller.color_mood_smoothing,
                            'color_mood_history_length': len(self.pixelblaze_controller.color_mood_history)
                        })
                    
                    dashboard_data = {
                        'brain_data': fix_nan_values(enhanced_brain_data),
                        'pixelblaze_status': self.pixelblaze_controller.get_status(),
                        'stats': self.stats
                    }
                    await self.dashboard.broadcast_data(dashboard_data)
                    
                    # Log periodic status
                    if self.stats['brain_updates'] % 100 == 0:
                        self._log_status()
                else:
                    # No EEG data available - send demo data
                    demo_brain_data = {
                        'brain_state': 'neutral',
                        'source': 'demo',
                        'attention': 0.5,
                        'relaxation': 0.5,
                        'engagement_level': 0.5,
                        'color_mood': 0.5,
                        'color_mood_smoothing': self.pixelblaze_controller.color_mood_smoothing,
                        'color_mood_history_length': len(self.pixelblaze_controller.color_mood_history),
                        'demo_mode': True
                    }
                    
                    dashboard_data = {
                        'brain_data': fix_nan_values(demo_brain_data),
                        'pixelblaze_status': self.pixelblaze_controller.get_status(),
                        'stats': self.stats
                    }
                    await self.dashboard.broadcast_data(dashboard_data)
                
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
    
    # Set up signal handlers for clean shutdown
    def signal_handler(signum, frame):
        logger.info(f"🔄 Received signal {signum}, initiating shutdown...")
        asyncio.create_task(system.shutdown())
    
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("🔄 Keyboard interrupt received, shutting down...")
        await system.shutdown()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        await system.shutdown()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ System failed to start: {e}")
        sys.exit(1)
