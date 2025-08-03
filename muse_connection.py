#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Muse Connection Test
Phase 1, Step 3: Connect to Muse via BrainFlow
"""

import logging
import time
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def connect_to_muse():
    """Connect to Muse S Gen 2 and test data acquisition"""
    
    # Enable BrainFlow logging
    BoardShim.enable_dev_board_logger()
    
    # Set up connection parameters
    params = BrainFlowInputParams()
    params.mac_address = config.MUSE_MAC_ADDRESS
    
    board = None
    try:
        logger.info("Initializing Muse S Gen 2 connection...")
        board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
        
        logger.info("Preparing session...")
        board.prepare_session()
        
        logger.info("Starting data stream...")
        board.start_stream()
        
        # Wait for data to accumulate
        logger.info("Collecting data for 5 seconds...")
        time.sleep(5)
        
        # Get the collected data
        data = board.get_board_data()
        logger.info(f"Data shape: {data.shape}")
        logger.info(f"Number of channels: {data.shape[0]}")
        logger.info(f"Number of samples: {data.shape[1]}")
        
        # Print some sample data
        if data.shape[1] > 0:
            logger.info("Sample data from first channel:")
            logger.info(f"First 10 samples: {data[0][:10]}")
            logger.info(f"Data range: {data[0].min():.2f} to {data[0].max():.2f}")
        
        return True, data
        
    except Exception as e:
        logger.error(f"Error connecting to Muse: {e}")
        return False, None
        
    finally:
        if board:
            try:
                logger.info("Stopping data stream...")
                board.stop_stream()
                logger.info("Releasing session...")
                board.release_session()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

def main():
    """Main function to test Muse connection"""
    logger.info("=== MindShow EEG LED Hat - Muse Connection Test ===")
    logger.info("Make sure your Muse S Gen 2 is turned on and in pairing mode")
    logger.info(f"Looking for Muse at MAC address: {config.MUSE_MAC_ADDRESS}")
    
    if config.MUSE_MAC_ADDRESS == "XX:XX:XX:XX:XX:XX":
        logger.error("Please update the MUSE_MAC_ADDRESS in config.py with your Muse's MAC address")
        return
    
    success, data = connect_to_muse()
    
    if success:
        logger.info("✅ Successfully connected to Muse and received data!")
        logger.info("Ready to proceed to visualization step")
    else:
        logger.error("❌ Failed to connect to Muse")
        logger.info("Troubleshooting tips:")
        logger.info("1. Make sure Muse is turned on and in pairing mode")
        logger.info("2. Verify the MAC address in config.py")
        logger.info("3. Check that Bluetooth is enabled on your computer")
        logger.info("4. Try using nRF Connect app to verify Muse is advertising")

if __name__ == "__main__":
    main() 