#!/usr/bin/env python3
"""
Test Pixelblaze V3 using HTTP API
"""

import requests
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pb_http():
    """Test Pixelblaze V3 using HTTP API"""
    base_url = "http://192.168.0.241"
    
    try:
        logger.info(f"Testing HTTP API for Pixelblaze V3 at {base_url}")
        
        # Test 1: Get current status
        logger.info("Getting current status...")
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            logger.info(f"Status: {response.json()}")
        else:
            logger.warning(f"Status request failed: {response.status_code}")
        
        # Test 2: Set brightness
        logger.info("Setting brightness to 0.3...")
        response = requests.post(f"{base_url}/api/brightness", json={"value": 0.3})
        if response.status_code == 200:
            logger.info("Brightness set successfully")
        else:
            logger.warning(f"Brightness request failed: {response.status_code}")
        
        time.sleep(2)
        
        # Test 3: Set speed to 0 (static)
        logger.info("Setting speed to 0 (static)...")
        response = requests.post(f"{base_url}/api/speed", json={"value": 0.0})
        if response.status_code == 200:
            logger.info("Speed set successfully")
        else:
            logger.warning(f"Speed request failed: {response.status_code}")
        
        time.sleep(2)
        
        # Test 4: Set a solid color
        logger.info("Setting solid blue color...")
        response = requests.post(f"{base_url}/api/color", json={"r": 0, "g": 0, "b": 255})
        if response.status_code == 200:
            logger.info("Color set successfully")
        else:
            logger.warning(f"Color request failed: {response.status_code}")
        
        time.sleep(2)
        
        # Test 5: Try setting a pattern
        logger.info("Setting pattern to 'Solid'...")
        response = requests.post(f"{base_url}/api/pattern", json={"name": "Solid"})
        if response.status_code == 200:
            logger.info("Pattern set successfully")
        else:
            logger.warning(f"Pattern request failed: {response.status_code}")
        
        time.sleep(2)
        
        # Test 6: Try setting variables
        logger.info("Setting variables...")
        response = requests.post(f"{base_url}/api/variable", json={"name": "brightness", "value": 0.8})
        if response.status_code == 200:
            logger.info("Variable set successfully")
        else:
            logger.warning(f"Variable request failed: {response.status_code}")
        
        time.sleep(2)
        
        # Test 7: Try direct control endpoint
        logger.info("Trying direct control...")
        response = requests.post(f"{base_url}/api/control", json={
            "brightness": 0.5,
            "speed": 0.0,
            "color": [0, 0, 255]
        })
        if response.status_code == 200:
            logger.info("Direct control successful")
        else:
            logger.warning(f"Direct control failed: {response.status_code}")
        
        logger.info("✅ HTTP API test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze V3: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=== Pixelblaze V3 HTTP API Test ===")
    success = test_pb_http()
    
    if success:
        logger.info("🎉 HTTP API test completed! Did you see any changes to the LEDs?")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    main() 