#!/usr/bin/env python3
"""
MindShow EEG Data Monitor - Simple text-based data verification
"""

import time
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class EEGDataMonitor:
    """Simple text-based EEG data monitor"""
    
    def __init__(self):
        self.board = None
        self.running = False
        
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
            
            logger.info("✅ Connected to Muse! Starting data monitoring...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def monitor_data(self, duration=30):
        """Monitor EEG data for specified duration"""
        if not self.connect_to_muse():
            return
            
        self.running = True
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("EEG DATA MONITOR")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        try:
            while self.running and (time.time() - start_time) < duration:
                # Get data
                data = self.board.get_board_data()
                
                if data.shape[1] > 0:
                    # Display data info
                    logger.info(f"Time: {time.time() - start_time:.1f}s")
                    logger.info(f"Data shape: {data.shape}")
                    
                    # Show each channel
                    for i in range(min(4, data.shape[0])):  # Show first 4 channels
                        channel_data = data[i]
                        if len(channel_data) > 0:
                            logger.info(f"Channel {i}: min={channel_data.min():.2f}, max={channel_data.max():.2f}, mean={channel_data.mean():.2f}")
                            logger.info(f"  Recent values: {channel_data[-5:]}")  # Last 5 values
                    
                    # Show signal quality indicators
                    if data.shape[0] >= 4:  # Muse has 4 EEG channels
                        logger.info("Signal Quality:")
                        for i in range(4):
                            channel_data = data[i]
                            if len(channel_data) > 0:
                                # Check for flat lines (bad signal)
                                if channel_data.max() - channel_data.min() < 0.1:
                                    logger.warning(f"  Channel {i}: FLAT LINE - Poor signal")
                                elif channel_data.max() - channel_data.min() > 1000:
                                    logger.warning(f"  Channel {i}: VERY HIGH AMPLITUDE - Possible artifact")
                                else:
                                    logger.info(f"  Channel {i}: Good signal range")
                    
                    logger.info("-" * 40)
                
                time.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring and clean up"""
        self.running = False
        if self.board:
            try:
                self.board.stop_stream()
                self.board.release_session()
                logger.info("Disconnected from Muse")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

def main():
    """Main function to run the data monitor"""
    logger.info("=== MindShow EEG Data Monitor ===")
    logger.info("Make sure your Muse S Gen 2 is turned on and in pairing mode")
    
    monitor = EEGDataMonitor()
    monitor.monitor_data(duration=30)  # Monitor for 30 seconds

if __name__ == "__main__":
    main() 