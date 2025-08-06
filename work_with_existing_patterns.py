#!/usr/bin/env python3
"""
Work with Existing Patterns on Pixelblaze
Following best practices from the comprehensive guide
"""

import asyncio
import json
import logging
import websockets
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def work_with_existing_patterns():
    """Work with existing patterns on the Pixelblaze"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Working with Existing Patterns")
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
        
        # Test variable control with proper throttling
        logger.info("Testing variable control with proper throttling...")
        
        # Test brightness control (limit to 10 commands/sec)
        brightness_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        for brightness in brightness_values:
            logger.info(f"Setting brightness to {brightness:.2f}")
            await websocket.send(json.dumps({"setVars": {"brightness": brightness}}))
            response = await websocket.recv()
            logger.info(f"  ✅ Brightness {brightness:.2f} set successfully!")
            await asyncio.sleep(0.2)  # Throttle to ~5 commands/sec
        
        # Test color control with proper throttling
        logger.info("Testing color control with proper throttling...")
        test_colors = [
            (0.0, "RED"),
            (0.16, "ORANGE"), 
            (0.33, "YELLOW"),
            (0.5, "GREEN"),
            (0.66, "BLUE"),
            (0.83, "VIOLET"),
            (1.0, "RED (cycle)")
        ]
        
        for hue, color_name in test_colors:
            logger.info(f"Setting hue to {hue:.2f} ({color_name})")
            await websocket.send(json.dumps({"setVars": {"hue": hue}}))
            response = await websocket.recv()
            logger.info(f"  ✅ {color_name} color set successfully!")
            await asyncio.sleep(0.2)  # Throttle to ~5 commands/sec
        
        # Test smooth transitions (demonstrating real-time control)
        logger.info("Testing smooth color transitions...")
        for i in range(20):
            hue = i / 20.0
            await websocket.send(json.dumps({"setVars": {"hue": hue}}))
            response = await websocket.recv()
            logger.info(f"  Hue: {hue:.2f}")
            await asyncio.sleep(0.1)  # Faster for smooth transitions
        
        # Test mood-based color control (simulating biometric data)
        logger.info("Testing mood-based color control...")
        moods = [
            (0.8, "Engaged - Red/Orange"),
            (0.5, "Neutral - Green"), 
            (0.2, "Relaxed - Blue/Violet"),
            (-0.2, "Very Relaxed - Deep Blue"),
            (-0.5, "Meditative - Violet"),
            (0.9, "Very Engaged - Bright Red")
        ]
        
        for mood_score, description in moods:
            logger.info(f"Mood: {mood_score:.2f} - {description}")
            
            # Map mood to color (similar to our mood index)
            if mood_score > 0:
                # Engaged: red to orange (0.0 to 0.16)
                hue = 0.0 + (mood_score * 0.16)
            else:
                # Relaxed: blue to violet (0.66 to 0.83)
                hue = 0.66 + (abs(mood_score) * 0.17)
            
            await websocket.send(json.dumps({"setVars": {"hue": hue}}))
            response = await websocket.recv()
            logger.info(f"  ✅ Set hue to {hue:.2f} for {description}")
            await asyncio.sleep(2)  # Longer pause to see mood changes
        
        # Final ping to maintain connection
        logger.info("Sending final ping...")
        await websocket.send(json.dumps({"ping": True}))
        final_ping_response = await websocket.recv()
        logger.info(f"Final ping response: {final_ping_response}")
        
        logger.info("=" * 50)
        logger.info("✅ Existing pattern control test completed!")
        logger.info("🎨 You should have seen smooth color and brightness changes!")
        logger.info("📊 This demonstrates real-time control suitable for biometric data!")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(work_with_existing_patterns()) 