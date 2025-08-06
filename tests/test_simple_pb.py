#!/usr/bin/env python3
"""
Simple Pixelblaze test - make LEDs solid blue
"""

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_solid_blue():
    """Test making LEDs solid blue"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Set brightness to full
        logger.info("Setting brightness to 1.0")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "brightness",
            "value": 1.0
        }))
        
        # Set speed to 0 (static)
        logger.info("Setting speed to 0 (static)")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "speed",
            "value": 0.0
        }))
        
        # Set color palette to solid blue
        logger.info("Setting color palette to solid blue")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": "solid_blue"
        }))
        
        # Alternative: try setting a custom blue color
        logger.info("Setting custom blue color")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "customColor",
            "value": [0, 0, 255]  # RGB blue
        }))
        
        await asyncio.sleep(2)
        
        # Test different blue variations
        logger.info("Testing different blue variations...")
        
        # Ocean blue
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": "ocean"
        }))
        await asyncio.sleep(3)
        
        # Cyan blue
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": "cyan"
        }))
        await asyncio.sleep(3)
        
        # Back to solid blue
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": "solid_blue"
        }))
        
        await websocket.close()
        logger.info("✅ Solid blue test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Simple Pixelblaze Test - Solid Blue ===")
    success = await test_solid_blue()
    
    if success:
        logger.info("🎉 LEDs should now be solid blue!")
    else:
        logger.error("Please check your Pixelblaze connection")

if __name__ == "__main__":
    asyncio.run(main()) 