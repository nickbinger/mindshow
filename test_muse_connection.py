#!/usr/bin/env python3
"""
Test Muse connection with different parameters
"""
import asyncio
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_muse_connection():
    """Test different Muse connection methods"""
    
    # Test 1: Standard connection
    logger.info("=== Test 1: Standard connection ===")
    try:
        BoardShim.enable_dev_board_logger()
        
        params = BrainFlowInputParams()
        params.mac_address = "78744271-945E-2227-B094-D15BC0F0FA0E"
        params.timeout = 15  # Increase timeout
        
        logger.info("Connecting to Muse S Gen 2...")
        board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
        board.prepare_session()
        board.start_stream()
        
        logger.info("✅ Standard connection successful!")
        board.stop_stream()
        board.release_session()
        return True
        
    except Exception as e:
        logger.error(f"Standard connection failed: {e}")
    
    # Test 2: Connection without MAC address (discovery)
    logger.info("=== Test 2: Connection without MAC address ===")
    try:
        BoardShim.enable_dev_board_logger()
        
        params = BrainFlowInputParams()
        params.timeout = 15
        
        logger.info("Connecting to Muse S Gen 2 (discovery mode)...")
        board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
        board.prepare_session()
        board.start_stream()
        
        logger.info("✅ Discovery connection successful!")
        board.stop_stream()
        board.release_session()
        return True
        
    except Exception as e:
        logger.error(f"Discovery connection failed: {e}")
    
    # Test 3: Try Muse S (not Muse S Gen 2)
    logger.info("=== Test 3: Try Muse S (not Gen 2) ===")
    try:
        BoardShim.enable_dev_board_logger()
        
        params = BrainFlowInputParams()
        params.mac_address = "78744271-945E-2227-B094-D15BC0F0FA0E"
        params.timeout = 15
        
        logger.info("Connecting to Muse S...")
        board = BoardShim(BoardIds.MUSE_S_BOARD.value, params)
        board.prepare_session()
        board.start_stream()
        
        logger.info("✅ Muse S connection successful!")
        board.stop_stream()
        board.release_session()
        return True
        
    except Exception as e:
        logger.error(f"Muse S connection failed: {e}")
    
    logger.error("All connection methods failed!")
    return False

if __name__ == "__main__":
    test_muse_connection() 