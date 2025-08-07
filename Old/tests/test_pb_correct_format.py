#!/usr/bin/env python3
"""
Test Pixelblaze V3 using correct WebSocket JSON format
"""

import asyncio
import websockets
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_correct_format():
    """Test using the correct WebSocket JSON format"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Testing correct WebSocket format for Pixelblaze V3 at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze V3!")
        
        # Test 1: Set brightness using correct format
        logger.info("Setting brightness to 0.3...")
        await websocket.send(json.dumps({"brightness": 0.3}))
        await asyncio.sleep(2)
        
        # Test 2: Set brightness to 1.0
        logger.info("Setting brightness to 1.0...")
        await websocket.send(json.dumps({"brightness": 1.0}))
        await asyncio.sleep(2)
        
        # Test 3: Set speed to 0 (static)
        logger.info("Setting speed to 0 (static)...")
        await websocket.send(json.dumps({"speed": 0.0}))
        await asyncio.sleep(2)
        
        # Test 4: Set speed to 0.5
        logger.info("Setting speed to 0.5...")
        await websocket.send(json.dumps({"speed": 0.5}))
        await asyncio.sleep(2)
        
        # Test 5: Set a variable
        logger.info("Setting brightness variable...")
        await websocket.send(json.dumps({"setVariable": {"name": "brightness", "value": 0.5}}))
        await asyncio.sleep(2)
        
        # Test 6: Set another variable
        logger.info("Setting speed variable...")
        await websocket.send(json.dumps({"setVariable": {"name": "speed", "value": 0.0}}))
        await asyncio.sleep(2)
        
        # Test 7: Set color palette
        logger.info("Setting color palette to blue...")
        await websocket.send(json.dumps({"setVariable": {"name": "colorPalette", "value": "blue"}}))
        await asyncio.sleep(2)
        
        # Test 8: Try setting a pattern
        logger.info("Setting pattern to 'Solid'...")
        await websocket.send(json.dumps({"setPattern": "Solid"}))
        await asyncio.sleep(2)
        
        # Test 9: Try getting info
        logger.info("Getting info...")
        await websocket.send(json.dumps({"getInfo": True}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Info response: {response}")
        except asyncio.TimeoutError:
            logger.info("No info response received")
        
        # Test 10: Try getting patterns
        logger.info("Getting patterns...")
        await websocket.send(json.dumps({"getPatterns": True}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Patterns response: {response}")
        except asyncio.TimeoutError:
            logger.info("No patterns response received")
        
        await websocket.close()
        logger.info("✅ Correct format test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze V3: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Correct WebSocket Format Test ===")
    success = await test_correct_format()
    
    if success:
        logger.info("🎉 Correct format test completed! Did you see any changes to the LEDs?")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    asyncio.run(main()) 