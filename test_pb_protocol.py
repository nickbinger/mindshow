#!/usr/bin/env python3
"""
Test Pixelblaze V3 using the correct protocol from documentation
"""

import asyncio
import websockets
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_protocol():
    """Test using the correct Pixelblaze protocol"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Testing correct Pixelblaze protocol at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze V3!")
        
        # Test 1: Get configuration (like the webUI does)
        logger.info("Getting configuration...")
        await websocket.send(json.dumps({
            "sendUpdates": False,
            "getConfig": True,
            "listPrograms": True,
            "getUpgradeState": True
        }))
        
        # Wait for responses
        await asyncio.sleep(3)
        
        # Test 2: Set brightness (correct format)
        logger.info("Setting brightness to 0.3...")
        await websocket.send(json.dumps({"brightness": 0.3}))
        await asyncio.sleep(2)
        
        # Test 3: Set brightness to 1.0
        logger.info("Setting brightness to 1.0...")
        await websocket.send(json.dumps({"brightness": 1.0}))
        await asyncio.sleep(2)
        
        # Test 4: Set a variable (correct format)
        logger.info("Setting brightness variable...")
        await websocket.send(json.dumps({"setVar": {"brightness": 0.5}}))
        await asyncio.sleep(2)
        
        # Test 5: Set speed variable
        logger.info("Setting speed variable...")
        await websocket.send(json.dumps({"setVar": {"speed": 0.0}}))
        await asyncio.sleep(2)
        
        # Test 6: Get program list
        logger.info("Getting program list...")
        await websocket.send(json.dumps({"getProgramList": True}))
        await asyncio.sleep(2)
        
        # Test 7: Try to set active pattern (if we have one)
        logger.info("Trying to set active pattern...")
        await websocket.send(json.dumps({"setActivePattern": "Editor"}))
        await asyncio.sleep(2)
        
        # Test 8: Set sequencer mode to off
        logger.info("Setting sequencer mode to off...")
        await websocket.send(json.dumps({"sequencerMode": 0}))
        await asyncio.sleep(2)
        
        # Test 9: Set sequencer to shuffle mode
        logger.info("Setting sequencer to shuffle mode...")
        await websocket.send(json.dumps({"sequencerMode": 1}))
        await asyncio.sleep(2)
        
        # Test 10: Stop sequencer
        logger.info("Stopping sequencer...")
        await websocket.send(json.dumps({"runSequencer": False}))
        await asyncio.sleep(2)
        
        # Test 11: Start sequencer
        logger.info("Starting sequencer...")
        await websocket.send(json.dumps({"runSequencer": True}))
        await asyncio.sleep(2)
        
        # Listen for any responses
        logger.info("Listening for responses...")
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                logger.info(f"Response: {response}")
        except asyncio.TimeoutError:
            logger.info("No more responses")
        
        await websocket.close()
        logger.info("✅ Protocol test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze V3: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Correct Pixelblaze Protocol Test ===")
    success = await test_protocol()
    
    if success:
        logger.info("🎉 Protocol test completed! Did you see any changes to the LEDs?")
    else:
        logger.error("Please check your Pixelblaze V3 connection")

if __name__ == "__main__":
    asyncio.run(main()) 