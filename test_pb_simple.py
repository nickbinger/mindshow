#!/usr/bin/env python3
"""
Simple Pixelblaze V3 test using basic HTTP
"""

import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_simple_http():
    """Test basic HTTP control of Pixelblaze V3"""
    base_url = "http://192.168.0.241"
    
    try:
        logger.info(f"Testing basic HTTP control for Pixelblaze V3 at {base_url}")
        
        # Test 1: Just get the main page
        logger.info("Getting main page...")
        response = requests.get(base_url)
        if response.status_code == 200:
            logger.info("Main page accessible")
            logger.info(f"Page title: {response.text[:200]}...")
        else:
            logger.warning(f"Main page failed: {response.status_code}")
        
        # Test 2: Try common endpoints
        endpoints = [
            "/",
            "/api",
            "/control",
            "/brightness",
            "/speed",
            "/pattern",
            "/status"
        ]
        
        for endpoint in endpoints:
            logger.info(f"Testing endpoint: {endpoint}")
            try:
                response = requests.get(f"{base_url}{endpoint}")
                logger.info(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    logger.info(f"  Content: {response.text[:100]}...")
            except Exception as e:
                logger.warning(f"  Error: {e}")
        
        # Test 3: Try POST to common endpoints
        logger.info("Testing POST requests...")
        
        # Try setting brightness via POST
        try:
            response = requests.post(f"{base_url}/brightness", data={"value": "0.3"})
            logger.info(f"POST /brightness: {response.status_code}")
        except Exception as e:
            logger.warning(f"POST /brightness error: {e}")
        
        # Try setting speed via POST
        try:
            response = requests.post(f"{base_url}/speed", data={"value": "0.0"})
            logger.info(f"POST /speed: {response.status_code}")
        except Exception as e:
            logger.warning(f"POST /speed error: {e}")
        
        # Try setting pattern via POST
        try:
            response = requests.post(f"{base_url}/pattern", data={"name": "Solid"})
            logger.info(f"POST /pattern: {response.status_code}")
        except Exception as e:
            logger.warning(f"POST /pattern error: {e}")
        
        logger.info("✅ Simple HTTP test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze V3: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=== Simple Pixelblaze V3 HTTP Test ===")
    success = test_simple_http()
    
    if success:
        logger.info("🎉 Simple HTTP test completed!")
        logger.info("Please check the web interface at http://192.168.0.241")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    main() 