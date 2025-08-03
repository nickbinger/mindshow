#!/usr/bin/env python3
"""
Test one color at a time
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_color(hue_value, expected_color):
    """Test a single color and ask user what they see"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            logger.info(f"Setting hue={hue_value} (expected: {expected_color})")
            await websocket.send(json.dumps({"setVars": {"hue": hue_value, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Response: {response}")
            
            logger.info(f"🎨 I set hue={hue_value} (expected {expected_color})")
            logger.info("What color do you see on the LEDs?")
            
            # Keep the color active for 10 seconds
            await asyncio.sleep(10)
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    # Test blue next (hue=0.66)
    asyncio.run(test_single_color(0.66, "BLUE")) 