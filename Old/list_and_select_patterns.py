#!/usr/bin/env python3
"""
List and Select Patterns on Pixelblaze
Using the correct WebSocket API commands
"""

import asyncio
import json
import logging
import websockets
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def list_and_select_patterns():
    """List available patterns and select one to play"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - List and Select Patterns")
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
        
        # Get list of available patterns using the correct command
        logger.info("Requesting list of available patterns...")
        await websocket.send(json.dumps({"listPrograms": True}))
        response = await websocket.recv()
        
        try:
            patterns = json.loads(response)
            logger.info(f"Patterns response: {patterns}")
            
            if 'programList' in patterns:
                logger.info("📋 Available Patterns:")
                logger.info("-" * 30)
                
                pattern_list = []
                for pattern_id, pattern_name in patterns['programList'].items():
                    logger.info(f"  ID: {pattern_id} → Pattern: {pattern_name}")
                    pattern_list.append((pattern_id, pattern_name))
                
                if pattern_list:
                    # Select the first pattern for testing
                    first_pattern_id, first_pattern_name = pattern_list[0]
                    logger.info(f"\n🎯 Selecting first pattern: {first_pattern_name} (ID: {first_pattern_id})")
                    
                    # Activate the pattern
                    await websocket.send(json.dumps({"activeProgramId": first_pattern_id}))
                    activation_response = await websocket.recv()
                    logger.info(f"Pattern activation response: {activation_response}")
                    
                    # Wait a moment for pattern to load
                    await asyncio.sleep(1)
                    
                    # Test variable control on the new pattern
                    logger.info("Testing variable control on the selected pattern...")
                    
                    # Test brightness
                    await websocket.send(json.dumps({"setVars": {"brightness": 0.5}}))
                    brightness_response = await websocket.recv()
                    logger.info("  ✅ Brightness set to 0.5")
                    
                    # Test color
                    await websocket.send(json.dumps({"setVars": {"hue": 0.5}}))
                    color_response = await websocket.recv()
                    logger.info("  ✅ Color set to green (hue=0.5)")
                    
                    # Test a few more colors
                    test_colors = [
                        (0.0, "RED"),
                        (0.33, "GREEN"), 
                        (0.66, "BLUE"),
                        (1.0, "RED (cycle)")
                    ]
                    
                    for hue, color_name in test_colors:
                        logger.info(f"  Setting {color_name} (hue={hue:.2f})")
                        await websocket.send(json.dumps({"setVars": {"hue": hue}}))
                        await websocket.recv()
                        await asyncio.sleep(0.5)  # Allow time to see the color
                    
                    logger.info("✅ Pattern selection and control test completed!")
                    
                else:
                    logger.warning("⚠️  No patterns found in the response")
                    
            else:
                logger.warning(f"⚠️  Unexpected response format: {patterns}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse patterns response as JSON: {e}")
            logger.info(f"Raw response: {response}")
            
        # Final ping to maintain connection
        logger.info("Sending final ping...")
        await websocket.send(json.dumps({"ping": True}))
        final_ping_response = await websocket.recv()
        logger.info(f"Final ping response: {final_ping_response}")
        
        logger.info("=" * 50)
        logger.info("✅ Pattern listing and selection test completed!")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_and_select_patterns()) 