#!/usr/bin/env python3
"""
Simple test to verify color mapping on Pixelblaze
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_colors():
    """Test different hue values to see what colors they produce"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Test different hue values
            test_colors = [
                (0.0, "RED"),
                (0.33, "GREEN"), 
                (0.66, "BLUE"),
                (0.5, "CYAN"),
                (0.17, "YELLOW"),
                (0.83, "MAGENTA")
            ]
            
            for hue, color_name in test_colors:
                logger.info(f"Testing {color_name} with hue={hue}")
                await websocket.send(json.dumps({"setVars": {"hue": hue, "brightness": 1.0}}))
                response = await websocket.recv()
                logger.info(f"Response: {response}")
                
                # Wait 3 seconds so you can see the color
                await asyncio.sleep(3)
                
            logger.info("🎨 Color test completed! What colors did you see for each hue value?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_colors()) 