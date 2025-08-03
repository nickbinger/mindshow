#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Pixelblaze Integration with Native BrainFlow + Graphical GUI
Phase 2: Connect brainwave analysis to Pixelblaze LED patterns with real-time GUI
"""

import asyncio
import websockets
import json
import logging
import time
import os
import threading
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import config
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class BrainwaveGUI:
    """Real-time graphical GUI for brainwave visualization"""
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('🧠 MindShow EEG LED Controller', fontsize=16, fontweight='bold')
        
        # Initialize plots
        self.setup_plots()
        
        # Data storage
        self.time_data = []
        self.attention_scores = []
        self.relaxation_scores = []
        self.brain_states = []
        self.max_points = 100
        
        # Colors for different states
        self.state_colors = {
            'neutral': '#2ecc71',  # Green
            'relaxed': '#3498db',  # Blue
            'engaged': '#e74c3c'   # Red
        }
        
        self.running = False
        
    def setup_plots(self):
        """Setup the matplotlib plots"""
        # Plot 1: Real-time attention and relaxation scores
        self.ax[0, 0].set_title('Brain State Scores')
        self.ax[0, 0].set_ylabel('Score')
        self.ax[0, 0].set_ylim(0, 1)
        self.attention_line, = self.ax[0, 0].plot([], [], 'r-', label='Attention', linewidth=2)
        self.relaxation_line, = self.ax[0, 0].plot([], [], 'b-', label='Relaxation', linewidth=2)
        self.ax[0, 0].legend()
        self.ax[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Brain state indicator
        self.ax[0, 1].set_title('Current Brain State')
        self.ax[0, 1].set_xlim(0, 1)
        self.ax[0, 1].set_ylim(0, 1)
        self.state_indicator = self.ax[0, 1].add_patch(
            patches.Rectangle((0.2, 0.3), 0.6, 0.4, facecolor='gray', alpha=0.5)
        )
        self.state_text = self.ax[0, 1].text(0.5, 0.5, 'NEUTRAL', 
                                              ha='center', va='center', fontsize=20, fontweight='bold')
        self.ax[0, 1].set_xticks([])
        self.ax[0, 1].set_yticks([])
        
        # Plot 3: LED color indicator
        self.ax[1, 0].set_title('Expected LED Color')
        self.ax[1, 0].set_xlim(0, 1)
        self.ax[1, 0].set_ylim(0, 1)
        self.led_indicator = self.ax[1, 0].add_patch(
            patches.Circle((0.5, 0.5), 0.3, facecolor='gray', alpha=0.5)
        )
        self.led_text = self.ax[1, 0].text(0.5, 0.5, 'GREEN', 
                                           ha='center', va='center', fontsize=16, fontweight='bold')
        self.ax[1, 0].set_xticks([])
        self.ax[1, 0].set_yticks([])
        
        # Plot 4: Instructions
        self.ax[1, 1].set_title('Instructions')
        self.ax[1, 1].text(0.1, 0.8, '🔵 Relax → Blue LEDs', fontsize=12, color='blue')
        self.ax[1, 1].text(0.1, 0.6, '🔴 Focus → Red LEDs', fontsize=12, color='red')
        self.ax[1, 1].text(0.1, 0.4, '🟢 Neutral → Green LEDs', fontsize=12, color='green')
        self.ax[1, 1].text(0.1, 0.2, 'Press Ctrl+C to exit', fontsize=10, style='italic')
        self.ax[1, 1].set_xticks([])
        self.ax[1, 1].set_yticks([])
        
        plt.tight_layout()
        
    def update_plots(self, frame):
        """Update the plots with new data"""
        if not self.running or not self.time_data:
            return (self.attention_line, self.relaxation_line, self.state_indicator, self.state_text, self.led_indicator, self.led_text)
            
        # Update time series plot
        self.attention_line.set_data(self.time_data, self.attention_scores)
        self.relaxation_line.set_data(self.time_data, self.relaxation_scores)
        self.ax[0, 0].set_xlim(max(0, self.time_data[-1] - 10), self.time_data[-1])
        
        # Update brain state indicator
        if self.brain_states:
            current_state = self.brain_states[-1]
            color = self.state_colors.get(current_state, 'gray')
            self.state_indicator.set_facecolor(color)
            self.state_text.set_text(current_state.upper())
            
        # Update LED color indicator
        if self.brain_states:
            current_state = self.brain_states[-1]
            if current_state == 'relaxed':
                led_color = '#3498db'  # Blue
                led_text = 'BLUE'
            elif current_state == 'engaged':
                led_color = '#e74c3c'  # Red
                led_text = 'RED'
            else:
                led_color = '#2ecc71'  # Green
                led_text = 'GREEN'
            
            self.led_indicator.set_facecolor(led_color)
            self.led_text.set_text(led_text)
        
        return (self.attention_line, self.relaxation_line, self.state_indicator, self.state_text, self.led_indicator, self.led_text)
    
    def add_data_point(self, attention_score, relaxation_score, brain_state):
        """Add a new data point to the plots"""
        current_time = time.time()
        
        self.time_data.append(current_time)
        self.attention_scores.append(attention_score)
        self.relaxation_scores.append(relaxation_score)
        self.brain_states.append(brain_state)
        
        # Keep only the last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.attention_scores = self.attention_scores[-self.max_points:]
            self.relaxation_scores = self.relaxation_scores[-self.max_points:]
            self.brain_states = self.brain_states[-self.max_points:]
    
    def start_gui(self):
        """Start the GUI in a separate thread"""
        self.running = True
        
        def run_gui():
            self.ani = FuncAnimation(self.fig, self.update_plots, interval=100, blit=True)
            plt.show()
        
        self.gui_thread = threading.Thread(target=run_gui, daemon=True)
        self.gui_thread.start()
    
    def stop_gui(self):
        """Stop the GUI"""
        self.running = False
        plt.close('all')

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
    """Main controller for EEG to LED integration with native BrainFlow analysis and GUI"""
    
    def __init__(self):
        self.brain_analyzer = NativeBrainwaveAnalyzer()
        self.pixelblaze = PixelblazeController()
        self.gui = BrainwaveGUI()
        self.running = False
        
    async def start(self):
        """Start the mind-controlled LED system with native BrainFlow analysis and GUI"""
        logger.info("=== MindShow EEG LED Controller with Native BrainFlow + GUI ===")
        
        # Start the GUI
        self.gui.start_gui()
        
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
                
                # Update GUI with new data
                self.gui.add_data_point(attention_score, relaxation_score, brain_state)
                
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
        
        # Stop the GUI
        self.gui.stop_gui()

async def main():
    """Main function to run the MindShow controller with native BrainFlow analysis and GUI"""
    controller = MindShowController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 