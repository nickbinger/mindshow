#!/usr/bin/env python3
"""
Debug Pixelblaze - check available patterns and variables
"""

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_pixelblaze():
    """Debug what's available on Pixelblaze"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Get current status
        logger.info("Getting current status...")
        await websocket.send(json.dumps({"cmd": "getStatus"}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Status response: {response}")
        except asyncio.TimeoutError:
            logger.info("No status response received")
        
        # Try to get current pattern
        logger.info("Getting current pattern...")
        await websocket.send(json.dumps({"cmd": "getPattern"}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Pattern response: {response}")
        except asyncio.TimeoutError:
            logger.info("No pattern response received")
        
        # Try to get variables
        logger.info("Getting variables...")
        await websocket.send(json.dumps({"cmd": "getVariables"}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Variables response: {response}")
        except asyncio.TimeoutError:
            logger.info("No variables response received")
        
        # Try to get pattern list
        logger.info("Getting pattern list...")
        await websocket.send(json.dumps({"cmd": "getPatterns"}))
        
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            logger.info(f"Patterns response: {response}")
        except asyncio.TimeoutError:
            logger.info("No patterns response received")
        
        # Try simple commands that might work
        logger.info("Testing simple commands...")
        
        # Try setting brightness directly
        await websocket.send(json.dumps({
            "cmd": "setBrightness",
            "value": 0.5
        }))
        await asyncio.sleep(1)
        
        # Try setting a specific pattern
        await websocket.send(json.dumps({
            "cmd": "setPattern",
            "name": "Solid"
        }))
        await asyncio.sleep(1)
        
        # Try setting color directly
        await websocket.send(json.dumps({
            "cmd": "setColor",
            "r": 0,
            "g": 0, 
            "b": 255
        }))
        await asyncio.sleep(1)
        
        await websocket.close()
        logger.info("✅ Debug completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze: {e}")
        return False

async def main():
    """Main debug function"""
    logger.info("=== Pixelblaze Debug ===")
    success = await debug_pixelblaze()
    
    if success:
        logger.info("🎉 Debug completed! Check the logs above for available commands.")
    else:
        logger.error("Please check your Pixelblaze connection")

if __name__ == "__main__":
    asyncio.run(main()) 