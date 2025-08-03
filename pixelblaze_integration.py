#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Pixelblaze Integration
Phase 2: Connect brainwave analysis to Pixelblaze LED patterns
"""

import asyncio
import websockets
import json
import logging
import time
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import config
import numpy as np

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class PixelblazeController:
    """Controls Pixelblaze LED patterns based on brainwave analysis"""
    
    def __init__(self, pixelblaze_url="ws://192.168.4.1:81"):
        self.pixelblaze_url = pixelblaze_url
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to Pixelblaze via WebSocket"""
        try:
            logger.info(f"Connecting to Pixelblaze at {self.pixelblaze_url}")
            self.websocket = await websockets.connect(self.pixelblaze_url)
            self.connected = True
            logger.info("✅ Connected to Pixelblaze")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Pixelblaze: {e}")
            return False
    
    async def send_command(self, command):
        """Send a command to Pixelblaze"""
        if not self.connected or not self.websocket:
            return False
        
        try:
            await self.websocket.send(json.dumps(command))
            return True
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            self.connected = False
            return False
    
    async def set_color_palette(self, palette_name):
        """Set the color palette based on brain state"""
        command = {
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": palette_name
        }
        return await self.send_command(command)
    
    async def set_brightness(self, brightness):
        """Set LED brightness (0-1)"""
        command = {
            "cmd": "setVariable", 
            "name": "brightness",
            "value": brightness
        }
        return await self.send_command(command)
    
    async def set_speed(self, speed):
        """Set animation speed (0-1)"""
        command = {
            "cmd": "setVariable",
            "name": "speed", 
            "value": speed
        }
        return await self.send_command(command)

class BrainwaveAnalyzer:
    """Analyzes brainwave data for attention/relaxation states"""
    
    def __init__(self):
        self.board = None
        self.attention_threshold = 0.6
        self.relaxation_threshold = 0.4
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2"""
        try:
            BoardShim.enable_dev_board_logger()
            
            params = BrainFlowInputParams()
            params.mac_address = config.MUSE_MAC_ADDRESS
            
            logger.info("Connecting to Muse S Gen 2...")
            self.board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
            self.board.prepare_session()
            self.board.start_stream()
            
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def calculate_attention_score(self, eeg_data):
        """Calculate attention score based on Beta/Alpha ratio"""
        if len(eeg_data) < 128:
            return 0.5  # Neutral if not enough data
        
        # Apply bandpass filter for Beta (13-30 Hz) and Alpha (8-13 Hz)
        sample_rate = 256
        
        # Filter for Beta waves
        beta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 13.0, 30.0, 4, FilterTypes.BUTTERWORTH, 0)
        alpha_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 8.0, 13.0, 4, FilterTypes.BUTTERWORTH, 0)
        
        # Calculate power in each band
        beta_power = np.mean(beta_filtered ** 2)
        alpha_power = np.mean(alpha_filtered ** 2)
        
        # Calculate attention score (Beta/Alpha ratio)
        if alpha_power > 0:
            attention_score = beta_power / alpha_power
            # Normalize to 0-1 range
            attention_score = min(1.0, max(0.0, attention_score / 2.0))
        else:
            attention_score = 0.5
        
        return attention_score
    
    def calculate_relaxation_score(self, eeg_data):
        """Calculate relaxation score based on Alpha/Theta ratio"""
        if len(eeg_data) < 128:
            return 0.5  # Neutral if not enough data
        
        sample_rate = 256
        
        # Filter for Alpha and Theta waves
        alpha_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 8.0, 13.0, 4, FilterTypes.BUTTERWORTH, 0)
        theta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 4.0, 8.0, 4, FilterTypes.BUTTERWORTH, 0)
        
        # Calculate power
        alpha_power = np.mean(alpha_filtered ** 2)
        theta_power = np.mean(theta_filtered ** 2)
        
        # Calculate relaxation score (Alpha/Theta ratio)
        if theta_power > 0:
            relaxation_score = alpha_power / theta_power
            # Normalize to 0-1 range
            relaxation_score = min(1.0, max(0.0, relaxation_score / 3.0))
        else:
            relaxation_score = 0.5
        
        return relaxation_score
    
    def classify_brain_state(self, attention_score, relaxation_score):
        """Classify brain state based on attention and relaxation scores"""
        if attention_score > self.attention_threshold:
            return "engaged"
        elif relaxation_score > self.relaxation_threshold:
            return "relaxed"
        else:
            return "neutral"

class MindShowController:
    """Main controller for EEG to LED integration"""
    
    def __init__(self):
        self.brain_analyzer = BrainwaveAnalyzer()
        self.pixelblaze = PixelblazeController()
        self.running = False
        
    async def start(self):
        """Start the mind-controlled LED system"""
        logger.info("=== MindShow EEG LED Controller ===")
        
        # Connect to Muse
        if not self.brain_analyzer.connect_to_muse():
            return
        
        # Connect to Pixelblaze
        if not await self.pixelblaze.connect():
            return
        
        self.running = True
        logger.info("Starting real-time brainwave to LED control...")
        
        try:
            while self.running:
                # Get EEG data
                data = self.brain_analyzer.board.get_board_data()
                if data.shape[1] == 0:
                    await asyncio.sleep(0.1)
                    continue
                
                # Use Channel 1 (real EEG data)
                eeg_channel = data[1]
                
                if len(eeg_channel) >= 128:
                    # Calculate brain state scores
                    attention_score = self.brain_analyzer.calculate_attention_score(eeg_channel)
                    relaxation_score = self.brain_analyzer.calculate_relaxation_score(eeg_channel)
                    
                    # Classify brain state
                    brain_state = self.brain_analyzer.classify_brain_state(attention_score, relaxation_score)
                    
                    # Update LED patterns based on brain state
                    await self.update_led_pattern(brain_state, attention_score, relaxation_score)
                    
                    # Log state occasionally
                    if int(time.time()) % 5 == 0:  # Every 5 seconds
                        logger.info(f"Brain State: {brain_state} | Attention: {attention_score:.2f} | Relaxation: {relaxation_score:.2f}")
                
                await asyncio.sleep(0.1)  # 10 Hz update rate
                
        except KeyboardInterrupt:
            logger.info("Stopping MindShow controller...")
        finally:
            await self.stop()
    
    async def update_led_pattern(self, brain_state, attention_score, relaxation_score):
        """Update LED patterns based on brain state"""
        if brain_state == "engaged":
            # Red/orange palette for engaged state
            await self.pixelblaze.set_color_palette("fire")
            await self.pixelblaze.set_brightness(min(1.0, attention_score + 0.3))
            await self.pixelblaze.set_speed(min(1.0, attention_score + 0.2))
            
        elif brain_state == "relaxed":
            # Blue/cyan palette for relaxed state
            await self.pixelblaze.set_color_palette("ocean")
            await self.pixelblaze.set_brightness(min(1.0, relaxation_score + 0.2))
            await self.pixelblaze.set_speed(max(0.1, 1.0 - relaxation_score))
            
        else:  # neutral
            # Purple/neutral palette
            await self.pixelblaze.set_color_palette("aurora")
            await self.pixelblaze.set_brightness(0.5)
            await self.pixelblaze.set_speed(0.5)
    
    async def stop(self):
        """Stop the controller and clean up"""
        self.running = False
        if self.brain_analyzer.board:
            try:
                self.brain_analyzer.board.stop_stream()
                self.brain_analyzer.board.release_session()
                logger.info("Disconnected from Muse")
            except Exception as e:
                logger.error(f"Error disconnecting from Muse: {e}")
        
        if self.pixelblaze.websocket:
            await self.pixelblaze.websocket.close()
            logger.info("Disconnected from Pixelblaze")

async def main():
    """Main function to run the MindShow controller"""
    controller = MindShowController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 