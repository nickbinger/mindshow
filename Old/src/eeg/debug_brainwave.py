#!/usr/bin/env python3
"""
Debug script to see what's happening with brainwave data processing
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugBrainwaveAnalyzer:
    """Debug version to see what's happening with brainwave data"""
    
    def __init__(self):
        self.board = None
        self.attention_threshold = 0.6
        self.relaxation_threshold = 0.4
        self.data_count = 0
        
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
            self.board.config_board("p50")
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def analyze_data(self, eeg_data):
        """Analyze EEG data and show debug info"""
        self.data_count += 1
        
        print(f"\n=== Data Sample #{self.data_count} ===")
        print(f"Data length: {len(eeg_data)}")
        print(f"Data range: {np.min(eeg_data):.3f} to {np.max(eeg_data):.3f}")
        print(f"Data mean: {np.mean(eeg_data):.3f}")
        print(f"Data std: {np.std(eeg_data):.3f}")
        
        if len(eeg_data) < 128:
            print("❌ Not enough data (need 128+ samples)")
            return None, None, None
        
        # Apply bandpass filter for Beta (13-30 Hz) and Alpha (8-13 Hz)
        sample_rate = 256
        
        try:
            # Filter for Beta waves
            beta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 13.0, 30.0, 4, FilterTypes.BUTTERWORTH, 0)
            alpha_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 8.0, 13.0, 4, FilterTypes.BUTTERWORTH, 0)
            theta_filtered = DataFilter.perform_bandpass(eeg_data, sample_rate, 4.0, 8.0, 4, FilterTypes.BUTTERWORTH, 0)
            
            # Check if filtering was successful
            if beta_filtered is None or alpha_filtered is None or theta_filtered is None:
                print("❌ Filtering failed")
                return None, None, None
            
            # Calculate power in each band
            beta_power = np.mean(beta_filtered ** 2)
            alpha_power = np.mean(alpha_filtered ** 2)
            theta_power = np.mean(theta_filtered ** 2)
            
            print(f"Beta power: {beta_power:.6f}")
            print(f"Alpha power: {alpha_power:.6f}")
            print(f"Theta power: {theta_power:.6f}")
            
            # Calculate attention score (Beta/Alpha ratio)
            if alpha_power > 0:
                attention_score = beta_power / alpha_power
                attention_score = min(1.0, max(0.0, attention_score / 2.0))
            else:
                attention_score = 0.5
            
            # Calculate relaxation score (Alpha/Theta ratio)
            if theta_power > 0:
                relaxation_score = alpha_power / theta_power
                relaxation_score = min(1.0, max(0.0, relaxation_score / 3.0))
            else:
                relaxation_score = 0.5
            
            print(f"Attention score: {attention_score:.3f}")
            print(f"Relaxation score: {relaxation_score:.3f}")
            
            # Classify brain state
            if attention_score > self.attention_threshold:
                brain_state = "engaged"
            elif relaxation_score > self.relaxation_threshold:
                brain_state = "relaxed"
            else:
                brain_state = "neutral"
            
            print(f"Brain state: {brain_state.upper()}")
            
            return brain_state, attention_score, relaxation_score
            
        except Exception as e:
            logger.warning(f"Error in analysis: {e}")
            return None, None, None

class DebugController:
    """Debug controller to test brainwave analysis"""
    
    def __init__(self):
        self.brain_analyzer = DebugBrainwaveAnalyzer()
        
    async def start(self):
        """Start the debug analysis"""
        logger.info("=== Debug Brainwave Analysis ===")
        
        # Connect to Muse
        if not self.brain_analyzer.connect_to_muse():
            return
        
        self.running = True
        logger.info("Starting debug analysis...")
        
        try:
            while self.running:
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
                
                # Analyze the data
                brain_state, attention_score, relaxation_score = self.brain_analyzer.analyze_data(eeg_channel)
                
                if brain_state:
                    print(f"🎯 RESULT: {brain_state.upper()} | Attention: {attention_score:.3f} | Relaxation: {relaxation_score:.3f}")
                else:
                    print("❌ No result")
                
                await asyncio.sleep(2.0)  # Wait 2 seconds between samples
                
        except KeyboardInterrupt:
            logger.info("Stopping debug analysis...")
        finally:
            await self.stop()
    
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

async def main():
    """Main function to run the debug controller"""
    controller = DebugController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 