import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_pattern_variables():
    """Get the current variables from the colorPalette pattern"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Get the current variables from the pattern
            logger.info("Getting current pattern variables...")
            await websocket.send(json.dumps({"getVars": True}))
            response = await websocket.recv()
            logger.info(f"Variables response: {response}")
            
            await asyncio.sleep(1)
            
            # Try to get the source code of the current pattern
            logger.info("Getting current pattern source code...")
            await websocket.send(json.dumps({"getSourceCode": True}))
            response = await websocket.recv()
            logger.info(f"Source code response: {response}")
            
            logger.info("🎉 Variable discovery completed!")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_pattern_variables()) 