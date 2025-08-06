#!/usr/bin/env python3
"""
Clean WebSocket Disconnect
Connect and disconnect cleanly from Pixelblaze
"""

import websocket
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_disconnect():
    """Connect and disconnect cleanly from WebSocket"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Clean WebSocket Disconnect")
    logger.info("=" * 50)
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        ws = websocket.create_connection(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Send ping to verify connection
        logger.info("Sending ping to verify connection...")
        ws.send(json.dumps({"ping": True}))
        ping_response = ws.recv()
        logger.info(f"Ping response: {ping_response}")
        
        # Disconnect cleanly
        logger.info("Disconnecting cleanly...")
        ws.close()
        logger.info("✅ Cleanly disconnected from Pixelblaze!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_disconnect() 