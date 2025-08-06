#!/usr/bin/env python3
"""
Research-Based Threshold Analysis
Based on actual EEG research for attention and relaxation classification
"""

import asyncio
import logging
from datetime import datetime
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchThresholdAnalyzer:
    """Analyze brainwave data to find optimal thresholds based on research"""
    
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
            logger.info("✅ Connected to Muse! Starting analysis...")
            
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
            
            # Normalize scores
            attention_score = min(1.0, max(0.0, attention_score / 2.0))
            relaxation_score = min(1.0, max(0.0, relaxation_score / 2.0))
            
            return {
                'timestamp': datetime.now().isoformat(),
                'theta': float(theta),
                'alpha': float(alpha),
                'beta': float(beta),
                'gamma': float(gamma),
                'attention': float(attention_score),
                'relaxation': float(relaxation_score)
            }
            
        except Exception as e:
            logger.error(f"Error getting brainwave data: {e}")
            return None

async def main():
    """Main analysis loop"""
    analyzer = ResearchThresholdAnalyzer()
    
    # Connect to Muse
    if not analyzer.connect_to_muse():
        logger.error("Failed to connect to Muse. Exiting.")
        return
    
    logger.info("Starting research-based threshold analysis...")
    logger.info("This will collect 60 seconds of data to analyze optimal thresholds")
    logger.info("Please remain relatively still and relaxed during this time")
    
    # Collect data for analysis
    attention_scores = []
    relaxation_scores = []
    
    try:
        for i in range(60):  # 60 seconds of data
            brain_data = analyzer.get_brainwave_data()
            
            if brain_data:
                attention_scores.append(brain_data['attention'])
                relaxation_scores.append(brain_data['relaxation'])
                
                logger.info(f"Sample {i+1}/60: Attention={brain_data['attention']:.3f}, Relaxation={brain_data['relaxation']:.3f}")
            
            await asyncio.sleep(1)
        
        # Analyze the data
        if attention_scores and relaxation_scores:
            logger.info("\n" + "="*50)
            logger.info("RESEARCH-BASED THRESHOLD ANALYSIS")
            logger.info("="*50)
            
            # Calculate statistics
            attention_mean = sum(attention_scores) / len(attention_scores)
            attention_std = (sum((x - attention_mean) ** 2 for x in attention_scores) / len(attention_scores)) ** 0.5
            attention_min = min(attention_scores)
            attention_max = max(attention_scores)
            
            relaxation_mean = sum(relaxation_scores) / len(relaxation_scores)
            relaxation_std = (sum((x - relaxation_mean) ** 2 for x in relaxation_scores) / len(relaxation_scores)) ** 0.5
            relaxation_min = min(relaxation_scores)
            relaxation_max = max(relaxation_scores)
            
            logger.info(f"ATTENTION SCORES:")
            logger.info(f"  Mean: {attention_mean:.3f}")
            logger.info(f"  Std Dev: {attention_std:.3f}")
            logger.info(f"  Range: {attention_min:.3f} - {attention_max:.3f}")
            logger.info(f"  Current threshold: 0.55")
            
            logger.info(f"\nRELAXATION SCORES:")
            logger.info(f"  Mean: {relaxation_mean:.3f}")
            logger.info(f"  Std Dev: {relaxation_std:.3f}")
            logger.info(f"  Range: {relaxation_min:.3f} - {relaxation_max:.3f}")
            logger.info(f"  Current threshold: 0.35")
            
            # Research-based recommendations
            logger.info(f"\nRESEARCH-BASED RECOMMENDATIONS:")
            logger.info(f"  Based on EEG research, typical thresholds are:")
            logger.info(f"  - Attention: 1.5-2.0 standard deviations above mean")
            logger.info(f"  - Relaxation: 1.5-2.0 standard deviations above mean")
            
            # Calculate new thresholds
            attention_threshold = attention_mean + (1.5 * attention_std)
            relaxation_threshold = relaxation_mean + (1.5 * relaxation_std)
            
            logger.info(f"\nRECOMMENDED THRESHOLDS:")
            logger.info(f"  Attention threshold: {attention_threshold:.3f}")
            logger.info(f"  Relaxation threshold: {relaxation_threshold:.3f}")
            
            # Show what percentage of data would be classified
            attention_above = sum(1 for x in attention_scores if x > attention_threshold)
            relaxation_above = sum(1 for x in relaxation_scores if x > relaxation_threshold)
            
            logger.info(f"\nCLASSIFICATION IMPACT:")
            logger.info(f"  With new thresholds:")
            logger.info(f"  - {attention_above}/{len(attention_scores)} ({attention_above/len(attention_scores)*100:.1f}%) samples would be 'engaged'")
            logger.info(f"  - {relaxation_above}/{len(relaxation_scores)} ({relaxation_above/len(relaxation_scores)*100:.1f}%) samples would be 'relaxed'")
            
            # Current classification
            current_attention_above = sum(1 for x in attention_scores if x > 0.55)
            current_relaxation_above = sum(1 for x in relaxation_scores if x > 0.35)
            
            logger.info(f"\nWith current thresholds:")
            logger.info(f"  - {current_attention_above}/{len(attention_scores)} ({current_attention_above/len(attention_scores)*100:.1f}%) samples would be 'engaged'")
            logger.info(f"  - {current_relaxation_above}/{len(relaxation_scores)} ({current_relaxation_above/len(relaxation_scores)*100:.1f}%) samples would be 'relaxed'")
            
            logger.info(f"\n" + "="*50)
            logger.info("CONCLUSION:")
            logger.info("The new thresholds should provide more stable classification")
            logger.info("with less rapid switching between states.")
            logger.info("="*50)
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    finally:
        if analyzer.board:
            analyzer.board.stop_stream()
            analyzer.board.release_session()

if __name__ == "__main__":
    asyncio.run(main()) 