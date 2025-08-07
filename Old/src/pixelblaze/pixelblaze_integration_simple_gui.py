#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Pixelblaze Integration with Simple GUI
Phase 2: Connect brainwave analysis to Pixelblaze LED patterns with simple GUI
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
import tkinter as tk
from tkinter import ttk

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class SimpleBrainwaveGUI:
    """Simple real-time GUI for brainwave visualization"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MindShow EEG LED Controller")
        self.root.geometry("500x300")
        self.root.configure(bg='#2c3e50')
        
        # Data storage
        self.brain_state = "neutral"
        self.attention_score = 0.5
        self.relaxation_score = 0.5
        self.running = False
        
        # Colors for different states
        self.state_colors = {
            'neutral': '#2ecc71',  # Green
            'relaxed': '#3498db',  # Blue
            'engaged': '#e74c3c'   # Red
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the simple GUI"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="🧠 MindShow EEG LED Controller", 
            font=("Arial", 14, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Brain State
        state_label = tk.Label(
            self.root,
            text="Brain State:",
            font=("Arial", 12),
            bg='#2c3e50',
            fg='white'
        )
        state_label.pack()
        
        self.state_display = tk.Label(
            self.root,
            text="NEUTRAL",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='#2ecc71'
        )
        self.state_display.pack(pady=5)
        
        # Scores
        scores_frame = tk.Frame(self.root, bg='#2c3e50')
        scores_frame.pack(pady=10)
        
        # Attention Score
        attention_label = tk.Label(
            scores_frame,
            text="Attention:",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='white'
        )
        attention_label.pack(side=tk.LEFT)
        
        self.attention_display = tk.Label(
            scores_frame,
            text="0.500",
            font=("Arial", 10, "bold"),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        self.attention_display.pack(side=tk.LEFT, padx=10)
        
        # Relaxation Score
        relaxation_label = tk.Label(
            scores_frame,
            text="Relaxation:",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='white'
        )
        relaxation_label.pack(side=tk.LEFT)
        
        self.relaxation_display = tk.Label(
            scores_frame,
            text="0.500",
            font=("Arial", 10, "bold"),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.relaxation_display.pack(side=tk.LEFT, padx=10)
        
        # LED Color
        led_label = tk.Label(
            self.root,
            text="LED Color:",
            font=("Arial", 12),
            bg='#2c3e50',
            fg='white'
        )
        led_label.pack(pady=5)
        
        self.led_display = tk.Label(
            self.root,
            text="🟢 GREEN",
            font=("Arial", 14, "bold"),
            bg='#2c3e50',
            fg='#2ecc71'
        )
        self.led_display.pack()
        
        # Instructions
        instructions_frame = tk.Frame(self.root, bg='#2c3e50')
        instructions_frame.pack(pady=15)
        
        instructions = [
            "🔵 Relax → Blue LEDs",
            "🔴 Focus → Red LEDs", 
            "🟢 Neutral → Green LEDs"
        ]
        
        for instruction in instructions:
            instruction_label = tk.Label(
                instructions_frame,
                text=instruction,
                font=("Arial", 9),
                bg='#2c3e50',
                fg='white'
            )
            instruction_label.pack(pady=1)
        
        # Status
        self.status_display = tk.Label(
            self.root,
            text="Status: Starting...",
            font=("Arial", 9),
            bg='#2c3e50',
            fg='#f39c12'
        )
        self.status_display.pack(pady=10)
        
    def update_display(self, brain_state, attention_score, relaxation_score):
        """Update the GUI display with new data"""
        self.brain_state = brain_state
        self.attention_score = attention_score
        self.relaxation_score = relaxation_score
        
        # Update brain state
        color = self.state_colors.get(brain_state, '#2ecc71')
        self.state_display.config(text=brain_state.upper(), fg=color)
        
        # Update scores
        self.attention_display.config(text=f"{attention_score:.3f}")
        self.relaxation_display.config(text=f"{relaxation_score:.3f}")
        
        # Update LED color
        if brain_state == 'relaxed':
            led_color = '🔵 BLUE'
            led_fg = '#3498db'
        elif brain_state == 'engaged':
            led_color = '🔴 RED'
            led_fg = '#e74c3c'
        else:
            led_color = '🟢 GREEN'
            led_fg = '#2ecc71'
        
        self.led_display.config(text=led_color, fg=led_fg)
        
        # Update status with debug info
        debug_info = f"Status: Running - {time.strftime('%H:%M:%S')} | A:{attention_score:.3f} R:{relaxation_score:.3f} State:{brain_state}"
        self.status_display.config(text=debug_info, fg='#27ae60')
        
        # Update the GUI
        self.root.update()
        
        # Log the state for debugging
        logger.info(f"Brain State: {brain_state} | Attention: {attention_score:.3f} | Relaxation: {relaxation_score:.3f}")
    
    def set_status(self, status, color='#f39c12'):
        """Set the status message"""
        self.status_display.config(text=f"Status: {status}", fg=color)
        self.root.update()
    
    def start_gui(self):
        """Start the GUI"""
        self.running = True
        self.root.mainloop()
    
    def stop_gui(self):
        """Stop the GUI"""
        self.running = False
        self.root.quit()

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
            # Blue tones for relaxed state - FIXED: hue=0.0 (was 0.66)
            await self.websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
        elif brain_state == "engaged":
            # Red tones for engaged state - FIXED: hue=0.66 (was 0.0)
            await self.websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
        else:
            # Green tones for neutral state - unchanged
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
        self.attention_threshold = 0.55  # Lowered from 0.6
        self.relaxation_threshold = 0.35  # Lowered from 0.4
        self.board_id = BoardIds.MUSE_2_BOARD.value
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2"""
        try:
            BoardShim.enable_dev_board_logger()
            
            params = BrainFlowInputParams()
            params.mac_address = config.MUSE_MAC_ADDRESS
            params.timeout = 15  # Increased timeout
            
            logger.info("Connecting to Muse S Gen 2...")
            self.board = BoardShim(self.board_id, params)
            self.board.prepare_session()
            self.board.start_stream()
            
            # Send initial keep-alive to prevent sleep
            self.board.config_board("p50")
            self.board.config_board("p51")
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
        logger.debug(f"Classifying: Attention={attention_score:.3f} (threshold={self.attention_threshold}), Relaxation={relaxation_score:.3f} (threshold={self.relaxation_threshold})")
        
        if attention_score > self.attention_threshold:
            logger.debug(f"Classified as ENGAGED (attention {attention_score:.3f} > {self.attention_threshold})")
            return "engaged"
        elif relaxation_score > self.relaxation_threshold:
            logger.debug(f"Classified as RELAXED (relaxation {relaxation_score:.3f} > {self.relaxation_threshold})")
            return "relaxed"
        else:
            logger.debug(f"Classified as NEUTRAL (attention={attention_score:.3f}, relaxation={relaxation_score:.3f})")
            return "neutral"

class MindShowController:
    """Main controller for EEG to LED integration with native BrainFlow analysis and GUI"""
    
    def __init__(self):
        self.brain_analyzer = NativeBrainwaveAnalyzer()
        self.pixelblaze = PixelblazeController()
        self.gui = SimpleBrainwaveGUI()
        self.running = False
        
    async def start(self):
        """Start the mind-controlled LED system with native BrainFlow analysis and GUI"""
        logger.info("=== MindShow EEG LED Controller with Native BrainFlow + Simple GUI ===")
        
        # Update GUI status
        self.gui.set_status("Connecting to Muse...")
        
        # Connect to Muse
        if not self.brain_analyzer.connect_to_muse():
            self.gui.set_status("Failed to connect to Muse", '#e74c3c')
            return
        
        # Verify Muse connection is stable
        try:
            logger.info("Verifying Muse connection...")
            # Send initial keep-alive commands
            self.brain_analyzer.board.config_board("p50")
            self.brain_analyzer.board.config_board("p51")
            await asyncio.sleep(2)  # Wait for connection to stabilize
            
            # Test data acquisition
            test_data = self.brain_analyzer.board.get_board_data()
            if test_data.shape[1] == 0:
                logger.warning("No initial data from Muse, but continuing...")
            else:
                logger.info("✅ Muse connection verified and stable")
        except Exception as e:
            logger.warning(f"Muse connection verification failed: {e}, but continuing...")
        
        self.gui.set_status("Connecting to Pixelblaze...")
        
        # Connect to Pixelblaze
        if not await self.pixelblaze.connect():
            self.gui.set_status("Failed to connect to Pixelblaze", '#e74c3c')
            return
        
        # Switch to cursor_test pattern
        await self.pixelblaze.websocket.send(json.dumps({"setActivePattern": "cursor_test"}))
        response = await self.pixelblaze.websocket.recv()
        logger.info(f"Switched to cursor_test pattern: {response}")
        
        self.running = True
        self.gui.set_status("Starting brainwave analysis...", '#27ae60')
        logger.info("Starting real-time brainwave to LED control...")
        
        # Keep track of time for periodic tasks
        last_keepalive = time.time()
        last_gui_update = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Send keep-alive every 5 seconds to prevent Muse sleep (more frequent than 30s)
                if current_time - last_keepalive >= 5:
                    try:
                        # Send multiple keep-alive commands like the Muse app
                        self.brain_analyzer.board.config_board("p50")  # Keep-alive
                        self.brain_analyzer.board.config_board("p51")  # Additional keep-alive
                        self.brain_analyzer.board.config_board("p52")  # Status check
                        last_keepalive = current_time
                        logger.info("Sent keep-alive commands to Muse")
                    except Exception as e:
                        logger.warning(f"Keep-alive failed: {e}")
                        # Try to reconnect if keep-alive fails
                        try:
                            logger.info("Attempting to reconnect to Muse...")
                            self.brain_analyzer.board.stop_stream()
                            self.brain_analyzer.board.release_session()
                            await asyncio.sleep(1)
                            self.brain_analyzer.board.prepare_session()
                            self.brain_analyzer.board.start_stream()
                            logger.info("Successfully reconnected to Muse")
                        except Exception as reconnect_error:
                            logger.error(f"Failed to reconnect to Muse: {reconnect_error}")
                
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
                
                # Update GUI FIRST with the current brain state
                self.gui.update_display(brain_state, attention_score, relaxation_score)
                logger.info(f"GUI Updated: {brain_state} | A:{attention_score:.3f} | R:{relaxation_score:.3f}")
                
                # Update LED patterns based on the SAME brain state
                await self.update_led_pattern(brain_state, attention_score, relaxation_score)
                
                await asyncio.sleep(0.1)  # 10 Hz update rate
                
        except KeyboardInterrupt:
            logger.info("Stopping MindShow controller...")
        finally:
            await self.stop()
    
    async def update_led_pattern(self, brain_state, attention_score, relaxation_score):
        """Update LED patterns based on brain state"""
        # Set color palette based on brain state
        if brain_state == "relaxed":
            logger.info(f"LED Command: RELAXED -> BLUE (hue=0.66)")
        elif brain_state == "engaged":
            logger.info(f"LED Command: ENGAGED -> RED (hue=0.0)")
        else:
            logger.info(f"LED Command: NEUTRAL -> GREEN (hue=0.33)")
            
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
        
        # Stop the GUI
        self.gui.stop_gui()

async def main():
    """Main function to run the MindShow controller with native BrainFlow analysis and GUI"""
    controller = MindShowController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 