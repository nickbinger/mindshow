#!/usr/bin/env python3
"""
WebSocket Client Test - Using websocket-client library
Following the guide exactly with the recommended library
"""

import websocket
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_websocket_client():
    """Test pattern switching using websocket-client library"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - WebSocket Client Test")
    logger.info("=" * 50)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze using websocket-client
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        ws = websocket.create_connection(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Send ping for connection stability
        logger.info("Sending ping for connection stability...")
        ws.send(json.dumps({"ping": True}))
        ping_response = ws.recv()
        logger.info(f"Ping response: {ping_response}")
        
        # Try to get current pattern info
        logger.info("Getting current pattern information...")
        ws.send(json.dumps({"getActivePattern": True}))
        current_response = ws.recv()
        logger.info(f"Current pattern response: {current_response}")
        
        # Try to get pattern list
        logger.info("Getting pattern list...")
        ws.send(json.dumps({"listPrograms": True}))
        list_response = ws.recv()
        logger.info(f"Pattern list response type: {type(list_response)}")
        logger.info(f"Pattern list response length: {len(list_response)}")
        
        # Try to activate sparkfire pattern
        sparkfire_id = "43MSBYij"
        logger.info(f"🎯 Activating sparkfire pattern (ID: {sparkfire_id})...")
        logger.info(f"Command: {{\"activeProgramId\": \"{sparkfire_id}\"}}")
        
        ws.send(json.dumps({"activeProgramId": sparkfire_id}))
        activation_response = ws.recv()
        logger.info(f"Activation response: {activation_response}")
        
        # Wait a moment to see if pattern changes
        time.sleep(2)
        
        # Try alternative method - setActivePattern with name
        logger.info("Trying alternative method with pattern name...")
        ws.send(json.dumps({"setActivePattern": "sparkfire"}))
        alt_response = ws.recv()
        logger.info(f"Alternative method response: {alt_response}")
        
        # Wait a moment
        time.sleep(2)
        
        # Try programId method
        logger.info("Trying programId method...")
        ws.send(json.dumps({"programId": sparkfire_id}))
        prog_response = ws.recv()
        logger.info(f"ProgramId response: {prog_response}")
        
        logger.info("✅ WebSocket client test completed!")
        logger.info("🎆 Check if you can see the sparkfire pattern now!")
        
        # Close connection
        ws.close()
        logger.info("🔌 Connection closed")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    test_websocket_client() 