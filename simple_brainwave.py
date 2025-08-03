#!/usr/bin/env python3
"""
Simple brainwave analysis using FFT instead of bandpass filtering
"""

import asyncio
import websockets
import json
import logging
import time
import os
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import config
import numpy as np
from scipy.fft import fft
from scipy.signal import windows

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBrainwaveAnalyzer:
    """Simple brainwave analysis using FFT"""
    
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
    
    def analyze_data_simple(self, eeg_data):
        """Analyze EEG data using simple FFT analysis"""
        self.data_count += 1
        
        print(f"\n=== Data Sample #{self.data_count} ===")
        print(f"Data length: {len(eeg_data)}")
        print(f"Data range: {np.min(eeg_data):.3f} to {np.max(eeg_data):.3f}")
        print(f"Data mean: {np.mean(eeg_data):.3f}")
        print(f"Data std: {np.std(eeg_data):.3f}")
        
        if len(eeg_data) < 128:
            print("❌ Not enough data (need 128+ samples)")
            return None, None, None
        
        try:
            # Apply window to reduce spectral leakage
            window = windows.hann(len(eeg_data))
            windowed_data = eeg_data * window
            
            # Compute FFT
            fft_result = fft(windowed_data)
            fft_magnitude = np.abs(fft_result)
            
            # Calculate frequency bins
            sample_rate = 256
            freq_bins = np.fft.fftfreq(len(eeg_data), 1/sample_rate)
            
            # Define frequency bands
            theta_mask = (freq_bins >= 4) & (freq_bins <= 8)
            alpha_mask = (freq_bins >= 8) & (freq_bins <= 13)
            beta_mask = (freq_bins >= 13) & (freq_bins <= 30)
            
            # Calculate power in each band
            theta_power = np.mean(fft_magnitude[theta_mask] ** 2) if np.any(theta_mask) else 0
            alpha_power = np.mean(fft_magnitude[alpha_mask] ** 2) if np.any(alpha_mask) else 0
            beta_power = np.mean(fft_magnitude[beta_mask] ** 2) if np.any(beta_mask) else 0
            
            print(f"Theta power: {theta_power:.6f}")
            print(f"Alpha power: {alpha_power:.6f}")
            print(f"Beta power: {beta_power:.6f}")
            
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

class SimpleController:
    """Simple controller to test brainwave analysis"""
    
    def __init__(self):
        self.brain_analyzer = SimpleBrainwaveAnalyzer()
        
    async def start(self):
        """Start the simple analysis"""
        logger.info("=== Simple Brainwave Analysis ===")
        
        # Connect to Muse
        if not self.brain_analyzer.connect_to_muse():
            return
        
        self.running = True
        logger.info("Starting simple analysis...")
        
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
                brain_state, attention_score, relaxation_score = self.brain_analyzer.analyze_data_simple(eeg_channel)
                
                if brain_state:
                    print(f"🎯 RESULT: {brain_state.upper()} | Attention: {attention_score:.3f} | Relaxation: {relaxation_score:.3f}")
                else:
                    print("❌ No result")
                
                await asyncio.sleep(2.0)  # Wait 2 seconds between samples
                
        except KeyboardInterrupt:
            logger.info("Stopping simple analysis...")
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
    """Main function to run the simple controller"""
    controller = SimpleController()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main()) 