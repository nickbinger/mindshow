#!/usr/bin/env python3
"""
Test Pixelblaze connection before running full integration
"""

import asyncio
import websockets
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_pixelblaze_connection():
    """Test basic connection to Pixelblaze"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Testing connection to Pixelblaze at {pixelblaze_url}")
        
        # Connect to Pixelblaze
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Successfully connected to Pixelblaze!")
        
        # Test basic commands
        test_commands = [
            {"cmd": "getVariable", "name": "brightness"},
            {"cmd": "setVariable", "name": "brightness", "value": 0.5},
            {"cmd": "setVariable", "name": "speed", "value": 0.3},
        ]
        
        for i, command in enumerate(test_commands):
            logger.info(f"Testing command {i+1}: {command}")
            await websocket.send(json.dumps(command))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                logger.info(f"Response: {response}")
            except asyncio.TimeoutError:
                logger.info("No response received (this is normal for set commands)")
            
            await asyncio.sleep(0.5)
        
        # Test color palette change
        logger.info("Testing color palette change to 'fire'")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette", 
            "value": "fire"
        }))
        
        await asyncio.sleep(1)
        
        # Test ocean palette
        logger.info("Testing color palette change to 'ocean'")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "colorPalette",
            "value": "ocean"
        }))
        
        await asyncio.sleep(1)
        
        # Reset to neutral
        logger.info("Resetting to neutral settings")
        await websocket.send(json.dumps({
            "cmd": "setVariable",
            "name": "brightness",
            "value": 0.5
        }))
        await websocket.send(json.dumps({
            "cmd": "setVariable", 
            "name": "speed",
            "value": 0.5
        }))
        
        await websocket.close()
        logger.info("✅ Pixelblaze connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Pixelblaze: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("=== Pixelblaze Connection Test ===")
    success = await test_pixelblaze_connection()
    
    if success:
        logger.info("🎉 Pixelblaze is ready for brainwave integration!")
        logger.info("You can now run: python pixelblaze_integration.py")
    else:
        logger.error("Please check your Pixelblaze IP address and network connection")

if __name__ == "__main__":
    asyncio.run(main()) 