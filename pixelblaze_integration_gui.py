#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Pixelblaze Integration with GUI
Phase 2: Connect brainwave analysis to Pixelblaze LED patterns with real-time display
"""

import asyncio
import websockets
import json
import logging
import time
import curses
import threading
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

class BrainStateGUI:
    """Real-time text GUI for displaying brain state"""
    
    def __init__(self):
        self.brain_state = "neutral"
        self.attention_score = 0.5
        self.relaxation_score = 0.5
        self.led_color = "Green"
        self.running = False
        
    def start_gui(self):
        """Start the curses GUI in a separate thread"""
        self.running = True
        threading.Thread(target=self._run_gui, daemon=True).start()
    
    def _run_gui(self):
        """Run the curses GUI"""
        curses.wrapper(self._main_gui)
    
    def _main_gui(self, stdscr):
        """Main GUI loop"""
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        
        # Color pairs for different states
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Relaxed
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Engaged
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Neutral
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Default
        
        while self.running:
            stdscr.clear()
            
            # Get screen dimensions
            max_y, max_x = stdscr.getmaxyx()
            
            # Title
            title = "🧠 MindShow EEG LED Controller"
            stdscr.addstr(1, (max_x - len(title)) // 2, title, curses.color_pair(4))
            
            # Brain State Display
            state_y = 3
            stdscr.addstr(state_y, 2, "Brain State:", curses.color_pair(4))
            
            # Color the brain state based on current state
            if self.brain_state == "relaxed":
                color_pair = curses.color_pair(1)
                state_text = "RELAXED"
            elif self.brain_state == "engaged":
                color_pair = curses.color_pair(2)
                state_text = "ENGAGED"
            else:
                color_pair = curses.color_pair(3)
                state_text = "NEUTRAL"
            
            stdscr.addstr(state_y, 15, f"[ {state_text} ]", color_pair)
            
            # Scores
            score_y = 5
            stdscr.addstr(score_y, 2, f"Attention Score: {self.attention_score:.3f}", curses.color_pair(4))
            stdscr.addstr(score_y + 1, 2, f"Relaxation Score: {self.relaxation_score:.3f}", curses.color_pair(4))
            
            # LED Color Display
            led_y = 8
            stdscr.addstr(led_y, 2, "Expected LED Color:", curses.color_pair(4))
            
            if self.brain_state == "relaxed":
                led_color = "🔵 BLUE"
                color_pair = curses.color_pair(1)
            elif self.brain_state == "engaged":
                led_color = "🔴 RED"
                color_pair = curses.color_pair(2)
            else:
                led_color = "🟢 GREEN"
                color_pair = curses.color_pair(3)
            
            stdscr.addstr(led_y, 20, led_color, color_pair)
            
            # Instructions
            inst_y = 11
            stdscr.addstr(inst_y, 2, "Instructions:", curses.color_pair(4))
            stdscr.addstr(inst_y + 1, 4, "• Relax your mind → Blue LEDs", curses.color_pair(1))
            stdscr.addstr(inst_y + 2, 4, "• Focus/engage → Red LEDs", curses.color_pair(2))
            stdscr.addstr(inst_y + 3, 4, "• Neutral state → Green LEDs", curses.color_pair(3))
            stdscr.addstr(inst_y + 4, 4, "• Press Ctrl+C to exit", curses.color_pair(4))
            
            # Status
            status_y = 16
            stdscr.addstr(status_y, 2, "Status: Running", curses.color_pair(4))
            
            # Refresh screen
            stdscr.refresh()
            time.sleep(0.1)
    
    def update_state(self, brain_state, attention_score, relaxation_score):
        """Update the brain state for the GUI"""
        self.brain_state = brain_state
        self.attention_score = attention_score
        self.relaxation_score = relaxation_score
    
    def stop_gui(self):
        """Stop the GUI"""
        self.running = False

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
            
            # Send keep-alive to prevent sleep
            self.board.config_board("p50")  # Keep device awake
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
        
        try:
            # Filter for Beta waves
            beta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 13.0, 30.0, 4, FilterTypes.BUTTERWORTH, 0)
            alpha_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 8.0, 13.0, 4, FilterTypes.BUTTERWORTH, 0)
            
            # Check if filtering was successful
            if beta_filtered is None or alpha_filtered is None:
                return 0.5  # Neutral if filtering failed
            
            # Calculate power in each band
            beta_power = np.mean(beta_filtered ** 2)
            alpha_power = np.mean(alpha_filtered ** 2)
        except Exception as e:
            logger.warning(f"Error in attention score calculation: {e}")
            return 0.5  # Neutral if error
        
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
        
        try:
            # Filter for Alpha and Theta waves
            alpha_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 8.0, 13.0, 4, FilterTypes.BUTTERWORTH, 0)
            theta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 4.0, 8.0, 4, FilterTypes.BUTTERWORTH, 0)
            
            # Check if filtering was successful
            if alpha_filtered is None or theta_filtered is None:
                return 0.5  # Neutral if filtering failed
            
            # Calculate power
            alpha_power = np.mean(alpha_filtered ** 2)
            theta_power = np.mean(theta_filtered ** 2)
        except Exception as e:
            logger.warning(f"Error in relaxation score calculation: {e}")
            return 0.5  # Neutral if error
        
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
    """Main controller for EEG to LED integration with GUI"""
    
    def __init__(self):
        self.brain_analyzer = BrainwaveAnalyzer()
        self.pixelblaze = PixelblazeController()
        self.gui = BrainStateGUI()
        self.running = False
        
    async def start(self):
        """Start the mind-controlled LED system with GUI"""
        logger.info("=== MindShow EEG LED Controller with GUI ===")
        
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
                
                # Use Channel 1 (real EEG data)
                eeg_channel = data[1]
                
                if len(eeg_channel) >= 128:
                    # Calculate brain state scores
                    attention_score = self.brain_analyzer.calculate_attention_score(eeg_channel)
                    relaxation_score = self.brain_analyzer.calculate_relaxation_score(eeg_channel)
                    
                    # Classify brain state
                    brain_state = self.brain_analyzer.classify_brain_state(attention_score, relaxation_score)
                    
                    # Update GUI
                    self.gui.update_state(brain_state, attention_score, relaxation_score)
                    
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
        self.gui.stop_gui()
        
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
    """Main function to run the MindShow controller with GUI"""
    controller = MindShowController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 