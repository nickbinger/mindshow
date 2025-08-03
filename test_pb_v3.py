#!/usr/bin/env python3
"""
Test Pixelblaze V3 with correct API
"""

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_pb_v3():
    """Test Pixelblaze V3 API"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze V3 at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze V3!")
        
        # V3 API: Get current status first
        logger.info("Getting current status...")
        await websocket.send(json.dumps({"type": "getStatus"}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Status: {response}")
        except asyncio.TimeoutError:
            logger.info("No status response")
        
        # V3 API: Try setting brightness
        logger.info("Setting brightness to 0.3...")
        await websocket.send(json.dumps({
            "type": "setBrightness",
            "value": 0.3
        }))
        await asyncio.sleep(2)
        
        # V3 API: Try setting a solid color
        logger.info("Setting solid blue color...")
        await websocket.send(json.dumps({
            "type": "setColor",
            "r": 0,
            "g": 0,
            "b": 255
        }))
        await asyncio.sleep(2)
        
        # V3 API: Try setting speed to 0 (static)
        logger.info("Setting speed to 0 (static)...")
        await websocket.send(json.dumps({
            "type": "setSpeed",
            "value": 0.0
        }))
        await asyncio.sleep(2)
        
        # V3 API: Try setting a specific pattern
        logger.info("Setting pattern to 'Solid'...")
        await websocket.send(json.dumps({
            "type": "setPattern",
            "name": "Solid"
        }))
        await asyncio.sleep(2)
        
        # V3 API: Try setting variables
        logger.info("Setting variables...")
        await websocket.send(json.dumps({
            "type": "setVariable",
            "name": "brightness",
            "value": 0.8
        }))
        await asyncio.sleep(1)
        
        await websocket.send(json.dumps({
            "type": "setVariable",
            "name": "speed",
            "value": 0.0
        }))
        await asyncio.sleep(1)
        
        await websocket.send(json.dumps({
            "type": "setVariable",
            "name": "colorPalette",
            "value": "blue"
        }))
        await asyncio.sleep(2)
        
        await websocket.close()
        logger.info("✅ V3 API test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze V3: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Pixelblaze V3 API Test ===")
    success = await test_pb_v3()
    
    if success:
        logger.info("🎉 V3 API test completed! Did you see any changes to the LEDs?")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    asyncio.run(main()) 