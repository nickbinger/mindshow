#!/usr/bin/env python3
"""
Test Muse Discovery
"""

import asyncio
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_muse_discovery():
    """Test Muse device discovery"""
    try:
        logger.info("Testing Muse device discovery...")
        
        # Configure BrainFlow parameters
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()
        params.timeout = 10  # Shorter timeout for testing
        
        # Try without specific MAC address first
        logger.info("Attempting to discover Muse devices...")
        board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
        
        # This will trigger device discovery
        board.prepare_session()
        logger.info("✅ Muse discovery successful!")
        
        board.release_session()
        return True
        
    except Exception as e:
        logger.error(f"Muse discovery failed: {e}")
        return False

if __name__ == "__main__":
    test_muse_discovery() 