import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def list_and_test_patterns():
    """List available patterns and test switching to one with variables"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Get the list of patterns
            logger.info("Getting pattern list...")
            await websocket.send(json.dumps({"getProgramList": True}))
            response = await websocket.recv()
            logger.info(f"Pattern list response: {response}")
            
            await asyncio.sleep(1)
            
            # Try switching to some common patterns that might have variables
            test_patterns = ["Solid", "Rainbow", "Fire", "Wave", "Pulse", "Sparkle"]
            
            for pattern in test_patterns:
                logger.info(f"Trying to switch to pattern: {pattern}")
                await websocket.send(json.dumps({"setActivePattern": pattern}))
                response = await websocket.recv()
                logger.info(f"Switch to {pattern} response: {response}")
                
                await asyncio.sleep(2)
                
                # Check if this pattern has variables
                logger.info(f"Getting variables for {pattern}...")
                await websocket.send(json.dumps({"getVars": True}))
                response = await websocket.recv()
                logger.info(f"Variables for {pattern}: {response}")
                
                await asyncio.sleep(1)
            
            logger.info("🎉 Pattern testing completed!")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_and_test_patterns()) 