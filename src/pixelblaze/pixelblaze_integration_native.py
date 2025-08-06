#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Pixelblaze Integration with Native BrainFlow Band Power Analysis
Phase 2: Connect brainwave analysis to Pixelblaze LED patterns using BrainFlow's native methods
"""

import asyncio
import websockets
import json
import logging
import time
import os
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

class SimpleBrainStateDisplay:
    """Simple text display for brain state"""
    
    def __init__(self):
        self.brain_state = "neutral"
        self.attention_score = 0.5
        self.relaxation_score = 0.5
        self.running = False
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_state(self):
        """Display the current brain state"""
        self.clear_screen()
        
        print("=" * 50)
        print("🧠 MindShow EEG LED Controller")
        print("=" * 50)
        print()
        
        # Brain State
        if self.brain_state == "relaxed":
            state_color = "🔵"
            led_color = "🔵 BLUE"
        elif self.brain_state == "engaged":
            state_color = "🔴"
            led_color = "🔴 RED"
        else:
            state_color = "🟢"
            led_color = "🟢 GREEN"
        
        print(f"Brain State: {state_color} {self.brain_state.upper()}")
        print(f"Attention Score: {self.attention_score:.3f}")
        print(f"Relaxation Score: {self.relaxation_score:.3f}")
        print()
        print(f"Expected LED Color: {led_color}")
        print()
        print("Instructions:")
        print("• Relax your mind → Blue LEDs")
        print("• Focus/engage → Red LEDs")
        print("• Neutral state → Green LEDs")
        print("• Press Ctrl+C to exit")
        print()
        print("Status: Running")
        print("=" * 50)
    
    def update_state(self, brain_state, attention_score, relaxation_score):
        """Update the brain state and display"""
        self.brain_state = brain_state
        self.attention_score = attention_score
        self.relaxation_score = relaxation_score
        self.display_state()

class PixelblazeController:
    """Controls Pixelblaze LED patterns based on brainwave analysis"""
    
    def __init__(self, pixelblaze_url="ws://192.168.0.241:81"):
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
    
    async def set_color_palette(self, brain_state):
        """Set color palette based on brain state"""
        if brain_state == "relaxed":
            # Blue tones for relaxed state
            await self.websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
        elif brain_state == "engaged":
            # Red tones for engaged state
            await self.websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
        else:
            # Green tones for neutral state
            await self.websocket.send(json.dumps({"setVars": {"hue": 0.33, "brightness": 1.0}}))
        
        response = await self.websocket.recv()
        logger.info(f"Color palette response: {response}")
    
    async def set_brightness(self, brightness):
        """Set LED brightness (0-1)"""
        await self.websocket.send(json.dumps({"setVars": {"brightness": brightness}}))
        response = await self.websocket.recv()
        logger.info(f"Brightness response: {response}")

class NativeBrainwaveAnalyzer:
    """Analyzes brainwave data using BrainFlow's native band power methods"""
    
    def __init__(self):
        self.board = None
        self.attention_threshold = 0.6
        self.relaxation_threshold = 0.4
        self.board_id = BoardIds.MUSE_2_BOARD.value
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2"""
        try:
            BoardShim.enable_dev_board_logger()
            
            params = BrainFlowInputParams()
            params.mac_address = config.MUSE_MAC_ADDRESS
            
            logger.info("Connecting to Muse S Gen 2...")
            self.board = BoardShim(self.board_id, params)
            self.board.prepare_session()
            self.board.start_stream()
            
            # Send keep-alive to prevent sleep
            self.board.config_board("p50")
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def analyze_data_native(self, data):
        """Analyze EEG data using BrainFlow's native band power methods"""
        try:
            # Get EEG channels for this board
            eeg_channels = BoardShim.get_eeg_channels(self.board_id)
            sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            
            # Define frequency bands for brainwave analysis
            # Format: [(start_freq, end_freq), ...]
            bands = [
                (4.0, 8.0),    # Theta
                (8.0, 13.0),   # Alpha  
                (13.0, 30.0),  # Beta
                (30.0, 50.0)   # Gamma
            ]
            
            # Use BrainFlow's native band power calculation
            # This applies filters automatically and calculates power in each band
            avg_band_powers, std_band_powers = DataFilter.get_custom_band_powers(
                data, bands, eeg_channels, sampling_rate, apply_filter=True
            )
            
            # Extract power values for each band
            theta_power = avg_band_powers[0]  # 4-8 Hz
            alpha_power = avg_band_powers[1]  # 8-13 Hz
            beta_power = avg_band_powers[2]   # 13-30 Hz
            gamma_power = avg_band_powers[3]  # 30-50 Hz
            
            logger.debug(f"Band powers - Theta: {theta_power:.3f}, Alpha: {alpha_power:.3f}, Beta: {beta_power:.3f}, Gamma: {gamma_power:.3f}")
            
            # Calculate attention score (Beta/Alpha ratio)
            if alpha_power > 0:
                attention_score = beta_power / alpha_power
                # Normalize to 0-1 range
                attention_score = min(1.0, max(0.0, attention_score / 2.0))
            else:
                attention_score = 0.5
            
            # Calculate relaxation score (Alpha/Theta ratio)
            if theta_power > 0:
                relaxation_score = alpha_power / theta_power
                # Normalize to 0-1 range
                relaxation_score = min(1.0, max(0.0, relaxation_score / 3.0))
            else:
                relaxation_score = 0.5
            
            return attention_score, relaxation_score
            
        except Exception as e:
            logger.warning(f"Error in native analysis: {e}")
            return 0.5, 0.5  # Return neutral scores if error
    
    def classify_brain_state(self, attention_score, relaxation_score):
        """Classify brain state based on attention and relaxation scores"""
        if attention_score > self.attention_threshold:
            return "engaged"
        elif relaxation_score > self.relaxation_threshold:
            return "relaxed"
        else:
            return "neutral"

class MindShowController:
    """Main controller for EEG to LED integration with native BrainFlow analysis"""
    
    def __init__(self):
        self.brain_analyzer = NativeBrainwaveAnalyzer()
        self.pixelblaze = PixelblazeController()
        self.display = SimpleBrainStateDisplay()
        self.running = False
        
    async def start(self):
        """Start the mind-controlled LED system with native BrainFlow analysis"""
        logger.info("=== MindShow EEG LED Controller with Native BrainFlow Analysis ===")
        
        # Show initial display
        self.display.display_state()
        
        # Connect to Muse
        if not self.brain_analyzer.connect_to_muse():
            return
        
        # Connect to Pixelblaze
        if not await self.pixelblaze.connect():
            return
        
        # Switch to cursor_test pattern
        await self.pixelblaze.websocket.send(json.dumps({"setActivePattern": "cursor_test"}))
        response = await self.pixelblaze.websocket.recv()
        logger.info(f"Switched to cursor_test pattern: {response}")
        
        self.running = True
        logger.info("Starting real-time brainwave to LED control...")
        
        # Keep track of time for periodic tasks
        last_keepalive = time.time()
        last_display_update = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Send keep-alive every 30 seconds to prevent Muse sleep
                if current_time - last_keepalive >= 30:
                    try:
                        self.brain_analyzer.board.config_board("p50")
                        last_keepalive = current_time
                        logger.debug("Sent keep-alive to Muse")
                    except Exception as e:
                        logger.warning(f"Keep-alive failed: {e}")
                
                # Get EEG data
                try:
                    data = self.brain_analyzer.board.get_board_data()
                    if data.shape[1] == 0:
                        await asyncio.sleep(0.1)
                        continue
                except Exception as e:
                    logger.warning(f"Failed to get EEG data: {e}")
                    await asyncio.sleep(0.5)
                    continue
                
                # Analyze the data using native BrainFlow methods
                attention_score, relaxation_score = self.brain_analyzer.analyze_data_native(data)
                
                # Classify brain state
                brain_state = self.brain_analyzer.classify_brain_state(attention_score, relaxation_score)
                
                # Update display every 0.5 seconds
                if current_time - last_display_update >= 0.5:
                    self.display.update_state(brain_state, attention_score, relaxation_score)
                    last_display_update = current_time
                
                # Update LED patterns based on brain state
                await self.update_led_pattern(brain_state, attention_score, relaxation_score)
                
                await asyncio.sleep(0.1)  # 10 Hz update rate
                
        except KeyboardInterrupt:
            logger.info("Stopping MindShow controller...")
        finally:
            await self.stop()
    
    async def update_led_pattern(self, brain_state, attention_score, relaxation_score):
        """Update LED patterns based on brain state"""
        # Set color palette based on brain state
        await self.pixelblaze.set_color_palette(brain_state)
        
        # Set brightness based on attention/relaxation scores
        if brain_state == "engaged":
            brightness = min(1.0, attention_score + 0.3)
        elif brain_state == "relaxed":
            brightness = min(1.0, relaxation_score + 0.2)
        else:  # neutral
            brightness = 0.5
        
        await self.pixelblaze.set_brightness(brightness)
    
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
    """Main function to run the MindShow controller with native BrainFlow analysis"""
    controller = MindShowController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 