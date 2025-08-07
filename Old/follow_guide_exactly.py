#!/usr/bin/env python3
"""
Follow Guide Exactly - Section 6.2 Pattern Activation
Using the exact method from the comprehensive guide
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def follow_guide_exactly():
    """Follow the guide exactly for pattern activation"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Follow Guide Exactly (Section 6.2)")
    logger.info("=" * 50)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Send ping for connection stability (Section 4.2)
        logger.info("Sending ping for connection stability...")
        await websocket.send(json.dumps({"ping": True}))
        ping_response = await websocket.recv()
        logger.info(f"Ping response: {ping_response}")
        
        # Get list of patterns first (Section 6.1)
        logger.info("Getting list of available patterns...")
        await websocket.send(json.dumps({"listPrograms": True}))
        response = await websocket.recv()
        
        try:
            patterns = json.loads(response)
            logger.info(f"Patterns response: {patterns}")
            
            if 'programList' in patterns:
                logger.info("📋 Available Patterns:")
                for pattern_id, pattern_name in patterns['programList'].items():
                    logger.info(f"  ID: {pattern_id} → Pattern: {pattern_name}")
                
                # Select sparkfire pattern
                sparkfire_id = "43MSBYij"
                logger.info(f"\n🎯 Activating sparkfire pattern using guide method...")
                logger.info(f"Command: {{\"activeProgramId\": \"{sparkfire_id}\"}}")
                
                # Activate pattern using exact guide method (Section 6.2)
                await websocket.send(json.dumps({"activeProgramId": sparkfire_id}))
                activation_response = await websocket.recv()
                logger.info(f"Activation response: {activation_response}")
                
                logger.info("✅ Pattern activation completed using guide method!")
                logger.info("🎆 You should now see the sparkfire pattern!")
                
            else:
                logger.warning(f"⚠️  No programList in response: {patterns}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse patterns response as JSON: {e}")
            logger.info(f"Raw response: {response}")
            
        # Close connection
        await websocket.close()
        logger.info("🔌 Connection closed")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(follow_guide_exactly()) 