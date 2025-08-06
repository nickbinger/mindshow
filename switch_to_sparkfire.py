#!/usr/bin/env python3
"""
Switch to Sparkfire Pattern - No Modifications
Simply activate the pattern and leave it alone
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def switch_to_sparkfire():
    """Switch to sparkfire pattern without any modifications"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Switch to Sparkfire Pattern")
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
        
        # Switch to sparkfire pattern
        sparkfire_id = "43MSBYij"
        logger.info(f"🎯 Switching to sparkfire pattern (ID: {sparkfire_id})")
        
        await websocket.send(json.dumps({"activeProgramId": sparkfire_id}))
        activation_response = await websocket.recv()
        logger.info(f"Pattern activation response: {activation_response}")
        
        logger.info("✅ Sparkfire pattern activated!")
        logger.info("🎆 You should now see the sparkfire pattern running as intended!")
        logger.info("📝 Pattern is running completely unmodified - no color or brightness changes")
        
        # Close connection immediately to avoid any interference
        await websocket.close()
        logger.info("🔌 Connection closed to avoid interference with pattern")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(switch_to_sparkfire()) 