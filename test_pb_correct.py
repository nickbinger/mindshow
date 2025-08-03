#!/usr/bin/env python3
"""
Test Pixelblaze with correct WebSocket API format
"""

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_correct_api():
    """Test with correct Pixelblaze API"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Try the correct API format
        logger.info("Testing correct API format...")
        
        # Method 1: Try setting brightness via WebSocket
        await websocket.send(json.dumps({
            "type": "setBrightness",
            "value": 0.3
        }))
        await asyncio.sleep(2)
        
        # Method 2: Try setting a specific pattern
        await websocket.send(json.dumps({
            "type": "setPattern",
            "name": "Solid"
        }))
        await asyncio.sleep(2)
        
        # Method 3: Try setting color via RGB
        await websocket.send(json.dumps({
            "type": "setColor",
            "r": 0,
            "g": 0,
            "b": 255
        }))
        await asyncio.sleep(2)
        
        # Method 4: Try setting speed
        await websocket.send(json.dumps({
            "type": "setSpeed",
            "value": 0.0
        }))
        await asyncio.sleep(2)
        
        # Method 5: Try setting a variable
        await websocket.send(json.dumps({
            "type": "setVariable",
            "name": "brightness",
            "value": 0.8
        }))
        await asyncio.sleep(2)
        
        # Method 6: Try the original format but with different commands
        await websocket.send(json.dumps({
            "cmd": "setBrightness",
            "value": 0.5
        }))
        await asyncio.sleep(2)
        
        await websocket.close()
        logger.info("✅ API test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Pixelblaze Correct API Test ===")
    success = await test_correct_api()
    
    if success:
        logger.info("🎉 API test completed! Did you see any changes?")
    else:
        logger.error("Please check your Pixelblaze connection")

if __name__ == "__main__":
    asyncio.run(main()) 