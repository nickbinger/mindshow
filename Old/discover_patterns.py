#!/usr/bin/env python3
"""
Discover and Switch Patterns on Pixelblaze
Lists all available patterns and allows switching between them
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def discover_and_switch_patterns():
    """Discover all patterns and switch to a different one"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Pattern Discovery and Switching")
    logger.info("=" * 50)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Get current active pattern
        logger.info("Getting current active pattern...")
        await websocket.send(json.dumps({"getActivePattern": True}))
        current_pattern_response = await websocket.recv()
        current_pattern = json.loads(current_pattern_response)
        
        logger.info(f"Current Pattern: {current_pattern}")
        
        # Try to get all patterns
        logger.info("Discovering all available patterns...")
        await websocket.send(json.dumps({"getPatterns": True}))
        patterns_response = await websocket.recv()
        
        logger.info(f"Patterns response: {patterns_response}")
        
        try:
            patterns = json.loads(patterns_response)
            logger.info(f"Found {len(patterns)} patterns:")
            
            pattern_names = []
            for i, pattern in enumerate(patterns):
                if isinstance(pattern, dict):
                    name = pattern.get('name', f'Pattern_{i}')
                else:
                    name = str(pattern)
                pattern_names.append(name)
                logger.info(f"  {i+1}. {name}")
            
            # If we have multiple patterns, try switching to a different one
            if len(pattern_names) > 1:
                # Find a pattern that's not the current one
                current_name = current_pattern.get('name', 'Unknown')
                alternative_pattern = None
                
                for name in pattern_names:
                    if name != current_name:
                        alternative_pattern = name
                        break
                
                if alternative_pattern:
                    logger.info(f"Switching to pattern: {alternative_pattern}")
                    await websocket.send(json.dumps({"setActivePattern": alternative_pattern}))
                    switch_response = await websocket.recv()
                    logger.info(f"Switch response: {switch_response}")
                    
                    # Verify the switch
                    await websocket.send(json.dumps({"getActivePattern": True}))
                    new_pattern_response = await websocket.recv()
                    new_pattern = json.loads(new_pattern_response)
                    logger.info(f"New active pattern: {new_pattern}")
                    
                    # Test color control on the new pattern
                    logger.info("Testing color control on new pattern...")
                    test_colors = [
                        (0.0, "RED"),
                        (0.33, "GREEN"), 
                        (0.66, "BLUE")
                    ]
                    
                    for hue, color_name in test_colors:
                        logger.info(f"Setting hue to {hue:.2f} ({color_name})")
                        await websocket.send(json.dumps({"setVars": {"hue": hue}}))
                        response = await websocket.recv()
                        logger.info(f"  ✅ {color_name} color set successfully!")
                        await asyncio.sleep(2)
                    
                else:
                    logger.info("No alternative patterns found to switch to")
            else:
                logger.info("Only one pattern available")
                
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse patterns response as JSON: {e}")
            logger.info(f"Raw response: {patterns_response}")
        except Exception as e:
            logger.error(f"Error processing patterns: {e}")
            logger.info(f"Patterns response: {patterns_response}")
        
        logger.info("=" * 50)
        logger.info("✅ Pattern discovery and switching completed!")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(discover_and_switch_patterns()) 