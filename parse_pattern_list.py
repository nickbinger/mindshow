#!/usr/bin/env python3
"""
Parse Pattern List from Pixelblaze
Handle the binary response format for pattern listing
"""

import asyncio
import json
import logging
import websockets
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_binary_pattern_list(binary_data):
    """Parse the binary pattern list response from Pixelblaze"""
    try:
        # Convert binary data to string
        data_str = binary_data.decode('utf-8', errors='ignore')
        logger.info(f"Raw binary data length: {len(binary_data)}")
        logger.info(f"Decoded string: {data_str[:200]}...")  # Show first 200 chars
        
        # Look for pattern ID and name pairs
        # Pattern IDs appear to be 8-character strings
        # Pattern names appear to be separated by tabs or newlines
        pattern_matches = re.findall(r'([A-Za-z0-9]{8})\t([^\t\n]+)', data_str)
        
        patterns = {}
        for pattern_id, pattern_name in pattern_matches:
            patterns[pattern_id] = pattern_name.strip()
            
        return patterns
        
    except Exception as e:
        logger.error(f"Error parsing binary data: {e}")
        return {}

async def get_pattern_list():
    """Get and parse the list of available patterns"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Parse Pattern List")
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
        
        # Try different commands to get pattern list
        commands_to_try = [
            {"listPrograms": True},
            {"getPrograms": True},
            {"listPatterns": True},
            {"getPatterns": True},
            {"programList": True}
        ]
        
        patterns = {}
        
        for i, command in enumerate(commands_to_try):
            logger.info(f"Trying command {i+1}: {command}")
            await websocket.send(json.dumps(command))
            response = await websocket.recv()
            
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response length: {len(response)}")
            
            if isinstance(response, bytes):
                # Binary response - try to parse it
                logger.info("Binary response detected, attempting to parse...")
                patterns = parse_binary_pattern_list(response)
                if patterns:
                    logger.info(f"✅ Successfully parsed {len(patterns)} patterns!")
                    break
            else:
                # Text response - try to parse as JSON
                try:
                    json_response = json.loads(response)
                    logger.info(f"JSON response: {json_response}")
                    if 'programList' in json_response:
                        patterns = json_response['programList']
                        logger.info(f"✅ Found {len(patterns)} patterns in JSON response!")
                        break
                except json.JSONDecodeError:
                    logger.info(f"Response is not JSON: {response[:200]}...")
            
            await asyncio.sleep(0.5)  # Brief pause between commands
        
        if patterns:
            logger.info("📋 Available Patterns:")
            logger.info("-" * 50)
            
            pattern_list = []
            for pattern_id, pattern_name in patterns.items():
                logger.info(f"  ID: {pattern_id} → Pattern: {pattern_name}")
                pattern_list.append((pattern_id, pattern_name))
            
            # Show some interesting patterns
            interesting_patterns = [
                "honeycomb", "fire", "rainbow", "spark", "pulse", 
                "color", "twinkle", "spiral", "cube", "matrix"
            ]
            
            logger.info("\n🎯 Interesting patterns found:")
            for pattern_id, pattern_name in pattern_list:
                if any(keyword in pattern_name.lower() for keyword in interesting_patterns):
                    logger.info(f"  ⭐ {pattern_name} (ID: {pattern_id})")
            
            # Try to select a honeycomb pattern if available
            honeycomb_patterns = [(pid, pname) for pid, pname in pattern_list if "honeycomb" in pname.lower()]
            if honeycomb_patterns:
                selected_id, selected_name = honeycomb_patterns[0]
                logger.info(f"\n🎯 Selecting honeycomb pattern: {selected_name} (ID: {selected_id})")
                
                # Activate the pattern
                await websocket.send(json.dumps({"activeProgramId": selected_id}))
                activation_response = await websocket.recv()
                logger.info(f"Pattern activation response: {activation_response}")
                
                # Test control on the selected pattern
                await asyncio.sleep(1)
                logger.info("Testing control on selected pattern...")
                
                # Test a few colors
                test_colors = [(0.0, "RED"), (0.5, "GREEN"), (0.66, "BLUE")]
                for hue, color_name in test_colors:
                    logger.info(f"  Setting {color_name} (hue={hue:.2f})")
                    await websocket.send(json.dumps({"setVars": {"hue": hue}}))
                    await websocket.recv()
                    await asyncio.sleep(1)
                
                logger.info("✅ Pattern selection and control test completed!")
            else:
                logger.info("No honeycomb patterns found, but we have the pattern list!")
                
        else:
            logger.warning("⚠️  No patterns found with any command")
            
        # Final ping
        logger.info("Sending final ping...")
        await websocket.send(json.dumps({"ping": True}))
        final_ping_response = await websocket.recv()
        logger.info(f"Final ping response: {final_ping_response}")
        
        logger.info("=" * 50)
        logger.info("✅ Pattern list parsing completed!")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_pattern_list()) 