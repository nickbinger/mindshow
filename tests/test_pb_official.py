#!/usr/bin/env python3
"""
Test Pixelblaze V3 using the official client library
"""

from pixelblaze import *
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_official_client():
    """Test using the official Pixelblaze client library"""
    
    try:
        logger.info("Testing official Pixelblaze client library...")
        
        # Create a Pixelblaze client
        pb = Pixelblaze("192.168.0.241")
        
        # Test 1: Get basic info
        logger.info("Getting basic info...")
        info = pb.getInfo()
        logger.info(f"Pixelblaze info: {info}")
        
        # Test 2: Get current pattern
        logger.info("Getting current pattern...")
        pattern = pb.getCurrentPattern()
        logger.info(f"Current pattern: {pattern}")
        
        # Test 3: Get brightness
        logger.info("Getting brightness...")
        brightness = pb.getBrightness()
        logger.info(f"Current brightness: {brightness}")
        
        # Test 4: Set brightness
        logger.info("Setting brightness to 0.5...")
        pb.setBrightness(0.5)
        time.sleep(2)
        
        # Test 5: Set brightness to 1.0
        logger.info("Setting brightness to 1.0...")
        pb.setBrightness(1.0)
        time.sleep(2)
        
        # Test 6: Get speed
        logger.info("Getting speed...")
        speed = pb.getSpeed()
        logger.info(f"Current speed: {speed}")
        
        # Test 7: Set speed to 0 (static)
        logger.info("Setting speed to 0 (static)...")
        pb.setSpeed(0.0)
        time.sleep(2)
        
        # Test 8: Get variables
        logger.info("Getting variables...")
        variables = pb.getVariables()
        logger.info(f"Variables: {variables}")
        
        # Test 9: Set a variable
        logger.info("Setting brightness variable...")
        pb.setVariable("brightness", 0.3)
        time.sleep(2)
        
        # Test 10: Set another variable
        logger.info("Setting speed variable...")
        pb.setVariable("speed", 0.0)
        time.sleep(2)
        
        # Test 11: Set color palette
        logger.info("Setting color palette to blue...")
        pb.setVariable("colorPalette", "blue")
        time.sleep(2)
        
        # Test 12: Get patterns list
        logger.info("Getting patterns list...")
        patterns = pb.getPatterns()
        logger.info(f"Available patterns: {patterns[:5]}...")  # Show first 5
        
        # Test 13: Set a specific pattern
        if patterns:
            logger.info(f"Setting pattern to: {patterns[0]}")
            pb.setPattern(patterns[0])
            time.sleep(2)
        
        logger.info("✅ Official client test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=== Official Pixelblaze Client Test ===")
    success = test_official_client()
    
    if success:
        logger.info("🎉 Official client test completed! Did you see any changes to the LEDs?")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    main() 