#!/usr/bin/env python3
"""
Activate Sparkfire Direct - Using Guide Method
Skip pattern listing and go straight to activation
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def activate_sparkfire_direct():
    """Activate sparkfire pattern directly using guide method"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Activate Sparkfire Direct")
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
        
        # Activate sparkfire pattern using exact guide method (Section 6.2)
        sparkfire_id = "43MSBYij"
        logger.info(f"🎯 Activating sparkfire pattern...")
        logger.info(f"Command: {{\"activeProgramId\": \"{sparkfire_id}\"}}")
        
        await websocket.send(json.dumps({"activeProgramId": sparkfire_id}))
        activation_response = await websocket.recv()
        logger.info(f"Activation response: {activation_response}")
        
        logger.info("✅ Sparkfire pattern activation completed!")
        logger.info("🎆 You should now see the sparkfire pattern running!")
        logger.info("📝 Pattern is running completely unmodified")
        
        # Close connection immediately to avoid interference
        await websocket.close()
        logger.info("🔌 Connection closed to avoid interference")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(activate_sparkfire_direct()) 