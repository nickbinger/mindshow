#!/usr/bin/env python3
"""
Test Current Pattern Control
Works with existing patterns without WebSocket conflicts
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_current_pattern():
    """Test control of the current pattern"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Test Current Pattern Control")
    logger.info("=" * 50)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Get current pattern info
        logger.info("Getting current pattern information...")
        await websocket.send(json.dumps({"getActivePattern": True}))
        pattern_response = await websocket.recv()
        pattern_info = json.loads(pattern_response)
        
        logger.info(f"Current Pattern: {pattern_info}")
        
        # Get current variables
        await websocket.send(json.dumps({"getVars": True}))
        vars_response = await websocket.recv()
        vars_info = json.loads(vars_response)
        
        logger.info(f"Available Variables: {vars_info}")
        
        # Test color control
        logger.info("Testing color control...")
        test_colors = [
            (0.0, "RED"),
            (0.33, "GREEN"), 
            (0.66, "BLUE"),
            (1.0, "RED (cycle)")
        ]
        
        for hue, color_name in test_colors:
            logger.info(f"Setting hue to {hue:.2f} ({color_name})")
            
            await websocket.send(json.dumps({"setVars": {"hue": hue}}))
            response = await websocket.recv()
            logger.info(f"  ✅ {color_name} color set successfully!")
            
            await asyncio.sleep(3)  # Wait to see effect
        
        # Test brightness control
        logger.info("Testing brightness control...")
        for brightness in [0.0, 0.5, 1.0]:
            logger.info(f"Setting brightness to {brightness:.2f}")
            
            await websocket.send(json.dumps({"setVars": {"brightness": brightness}}))
            response = await websocket.recv()
            logger.info(f"  ✅ Brightness {brightness:.2f} set successfully!")
            
            await asyncio.sleep(2)
        
        logger.info("=" * 50)
        logger.info("✅ Current pattern control test completed!")
        logger.info("🎨 You should have seen colors and brightness changes on your LEDs!")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_current_pattern()) 