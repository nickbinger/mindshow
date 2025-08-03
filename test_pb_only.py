#!/usr/bin/env python3
"""
Test Pixelblaze integration only (without Muse)
"""

import asyncio
import websockets
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pixelblaze_only():
    """Test Pixelblaze control without Muse"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Switch to cursor_test pattern
            logger.info("Switching to cursor_test pattern...")
            await websocket.send(json.dumps({"setActivePattern": "cursor_test"}))
            response = await websocket.recv()
            logger.info(f"Switch response: {response}")
            
            await asyncio.sleep(2)
            
            # Simulate brain states
            brain_states = ["relaxed", "engaged", "neutral", "relaxed", "engaged"]
            
            for i, brain_state in enumerate(brain_states):
                logger.info(f"Simulating brain state: {brain_state}")
                
                if brain_state == "relaxed":
                    # Blue for relaxed
                    await websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
                elif brain_state == "engaged":
                    # Red for engaged
                    await websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
                else:
                    # Green for neutral
                    await websocket.send(json.dumps({"setVars": {"hue": 0.33, "brightness": 1.0}}))
                
                response = await websocket.recv()
                logger.info(f"{brain_state} response: {response}")
                
                await asyncio.sleep(3)
            
            logger.info("🎉 Pixelblaze test completed! Did you see the LEDs change colors?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pixelblaze_only()) 