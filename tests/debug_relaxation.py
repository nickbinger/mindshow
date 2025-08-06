#!/usr/bin/env python3
"""
Debug Relaxation Score Issue
"""

import asyncio
import logging
from datetime import datetime
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugBrainwaveAnalyzer:
    """Debug real-time brainwave analysis"""
    
    def __init__(self):
        self.board = None
        self.connected = False
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2 headband"""
        try:
            logger.info("Connecting to Muse S Gen 2...")
            
            # Configure BrainFlow parameters
            BoardShim.enable_dev_board_logger()
            params = BrainFlowInputParams()
            params.mac_address = "78744271-945E-2227-B094-D15BC0F0FA0E"
            params.timeout = 15
            
            # Create and prepare board
            self.board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
            self.board.prepare_session()
            
            # Start streaming
            self.board.start_stream()
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            
            # Wait a moment for data to start flowing
            import time
            time.sleep(2)
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def get_brainwave_data(self):
        """Get real brainwave data from Muse"""
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
            
            # Define frequency bands for brainwave analysis
            bands = [
                (4.0, 8.0),    # Theta
                (8.0, 13.0),   # Alpha  
                (13.0, 30.0),  # Beta
                (30.0, 50.0)   # Gamma
            ]
            
            # Use BrainFlow's native band power calculation
            avg_band_powers, std_band_powers = DataFilter.get_custom_band_powers(
                data, bands, eeg_channels, sampling_rate, apply_filter=True
            )
            
            # Extract power values for each band
            theta = avg_band_powers[0]  # 4-8 Hz
            alpha = avg_band_powers[1]  # 8-13 Hz
            beta = avg_band_powers[2]   # 13-30 Hz
            gamma = avg_band_powers[3]  # 30-50 Hz
            
            # Calculate attention and relaxation scores
            attention_score = beta / (alpha + 1e-10)  # Beta/Alpha ratio
            relaxation_score = alpha / (theta + 1e-10)  # Alpha/Theta ratio
            
            # Debug: Show raw values
            logger.info(f"RAW VALUES:")
            logger.info(f"  Theta: {theta:.6f}")
            logger.info(f"  Alpha: {alpha:.6f}")
            logger.info(f"  Beta: {beta:.6f}")
            logger.info(f"  Gamma: {gamma:.6f}")
            logger.info(f"  Alpha/Theta ratio: {relaxation_score:.6f}")
            logger.info(f"  Beta/Alpha ratio: {attention_score:.6f}")
            
            # Test different normalizations
            relaxation_norm1 = min(1.0, max(0.0, relaxation_score / 2.0))
            relaxation_norm2 = min(1.0, max(0.0, relaxation_score / 3.0))
            relaxation_norm3 = min(1.0, max(0.0, relaxation_score / 5.0))
            relaxation_norm4 = min(1.0, max(0.0, relaxation_score / 10.0))
            
            logger.info(f"NORMALIZED RELAXATION SCORES:")
            logger.info(f"  /2.0: {relaxation_norm1:.6f}")
            logger.info(f"  /3.0: {relaxation_norm2:.6f} (current)")
            logger.info(f"  /5.0: {relaxation_norm3:.6f}")
            logger.info(f"  /10.0: {relaxation_norm4:.6f}")
            
            # Normalize scores
            attention_score = min(1.0, max(0.0, attention_score / 2.0))
            relaxation_score = min(1.0, max(0.0, relaxation_score / 3.0))
            
            # Classify brain state
            brain_state = "neutral"
            if attention_score > 0.55:
                brain_state = "engaged"
            elif relaxation_score > 0.35:
                brain_state = "relaxed"
            
            logger.info(f"FINAL SCORES:")
            logger.info(f"  Attention: {attention_score:.6f}")
            logger.info(f"  Relaxation: {relaxation_score:.6f}")
            logger.info(f"  Brain State: {brain_state}")
            logger.info("-" * 50)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'delta': 0.0,
                'theta': float(theta),
                'alpha': float(alpha),
                'beta': float(beta),
                'gamma': float(gamma),
                'attention': float(attention_score),
                'relaxation': float(relaxation_score),
                'brain_state': brain_state
            }
            
        except Exception as e:
            logger.error(f"Error getting brainwave data: {e}")
            return None

async def main():
    """Main debug loop"""
    brain_analyzer = DebugBrainwaveAnalyzer()
    
    # Connect to Muse
    if not brain_analyzer.connect_to_muse():
        logger.error("Failed to connect to Muse. Exiting.")
        return
    
    logger.info("Starting debug brainwave analysis...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get real brainwave data
            brain_data = brain_analyzer.get_brainwave_data()
            
            if brain_data:
                logger.info(f"Brain State: {brain_data['brain_state']} | Attention: {brain_data['attention']:.3f} | Relaxation: {brain_data['relaxation']:.3f}")
            
            await asyncio.sleep(2)  # Slower for debugging
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if brain_analyzer.board:
            brain_analyzer.board.stop_stream()
            brain_analyzer.board.release_session()

if __name__ == "__main__":
    asyncio.run(main()) 