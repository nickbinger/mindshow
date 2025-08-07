#!/usr/bin/env python3
"""
Debug Pattern Switching
Check current pattern and try different switching methods
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_pattern_switching():
    """Debug pattern switching issues"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Debug Pattern Switching")
    logger.info("=" * 50)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Send ping for connection stability
        logger.info("Sending ping for connection stability...")
        await websocket.send(json.dumps({"ping": True}))
        ping_response = await websocket.recv()
        logger.info(f"Ping response: {ping_response}")
        
        # Check current active pattern
        logger.info("Checking current active pattern...")
        await websocket.send(json.dumps({"getActivePattern": True}))
        current_pattern_response = await websocket.recv()
        logger.info(f"Current pattern response: {current_pattern_response}")
        
        # Try different pattern switching commands
        sparkfire_id = "43MSBYij"
        
        # Method 1: activeProgramId
        logger.info(f"Method 1: Trying activeProgramId with {sparkfire_id}")
        await websocket.send(json.dumps({"activeProgramId": sparkfire_id}))
        response1 = await websocket.recv()
        logger.info(f"Method 1 response: {response1}")
        
        await asyncio.sleep(2)
        
        # Method 2: setActivePattern (using pattern name)
        logger.info("Method 2: Trying setActivePattern with 'sparkfire'")
        await websocket.send(json.dumps({"setActivePattern": "sparkfire"}))
        response2 = await websocket.recv()
        logger.info(f"Method 2 response: {response2}")
        
        await asyncio.sleep(2)
        
        # Method 3: programId
        logger.info(f"Method 3: Trying programId with {sparkfire_id}")
        await websocket.send(json.dumps({"programId": sparkfire_id}))
        response3 = await websocket.recv()
        logger.info(f"Method 3 response: {response3}")
        
        await asyncio.sleep(2)
        
        # Method 4: setProgram
        logger.info(f"Method 4: Trying setProgram with {sparkfire_id}")
        await websocket.send(json.dumps({"setProgram": sparkfire_id}))
        response4 = await websocket.recv()
        logger.info(f"Method 4 response: {response4}")
        
        await asyncio.sleep(2)
        
        # Check if pattern actually changed
        logger.info("Checking if pattern changed...")
        await websocket.send(json.dumps({"getActivePattern": True}))
        final_pattern_response = await websocket.recv()
        logger.info(f"Final pattern response: {final_pattern_response}")
        
        # Try to get current variables to see what's available
        logger.info("Getting current variables...")
        await websocket.send(json.dumps({"getVars": True}))
        vars_response = await websocket.recv()
        logger.info(f"Variables response: {vars_response}")
        
        logger.info("=" * 50)
        logger.info("✅ Debug pattern switching completed!")
        logger.info("🔍 Check the responses above to see which method worked")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pattern_switching()) 