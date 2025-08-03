import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def discover_patterns():
    """Discover available patterns and current pattern info"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Get the list of patterns
            logger.info("Getting pattern list...")
            await websocket.send(json.dumps({"getProgramList": True}))
            
            # We need to handle binary responses for pattern list
            response = await websocket.recv()
            logger.info(f"Pattern list response type: {type(response)}")
            logger.info(f"Pattern list response: {response}")
            
            await asyncio.sleep(1)
            
            # Get current configuration
            logger.info("Getting current configuration...")
            await websocket.send(json.dumps({"getConfig": True}))
            response = await websocket.recv()
            logger.info(f"Config response: {response}")
            
            await asyncio.sleep(1)
            
            # Get current info
            logger.info("Getting current info...")
            await websocket.send(json.dumps({"getInfo": True}))
            response = await websocket.recv()
            logger.info(f"Info response: {response}")
            
            logger.info("🎉 Pattern discovery completed!")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(discover_patterns()) 