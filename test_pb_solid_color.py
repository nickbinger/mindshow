import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_solid_color():
    """Test setting Pixelblaze to solid blue color"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Test 1: Try to set a solid blue color by setting variables
            logger.info("Setting color variables for solid blue...")
            await websocket.send(json.dumps({"setVar": {"r": 0, "g": 0, "b": 255}}))
            response = await websocket.recv()
            logger.info(f"Color variables response: {response}")
            
            await asyncio.sleep(3)
            
            # Test 2: Try setting brightness to 0 (off) then 100 (full)
            logger.info("Setting brightness to 0 (off)...")
            await websocket.send(json.dumps({"brightness": 0}))
            response = await websocket.recv()
            logger.info(f"Brightness 0 response: {response}")
            
            await asyncio.sleep(2)
            
            logger.info("Setting brightness to 100 (full)...")
            await websocket.send(json.dumps({"brightness": 100}))
            response = await websocket.recv()
            logger.info(f"Brightness 100 response: {response}")
            
            await asyncio.sleep(2)
            
            # Test 3: Try to get the current pattern and set it to a simple one
            logger.info("Getting current pattern info...")
            await websocket.send(json.dumps({"getConfig": True}))
            response = await websocket.recv()
            logger.info(f"Config response: {response}")
            
            await asyncio.sleep(1)
            
            # Test 4: Try setting a specific pattern if we can find one
            logger.info("Trying to set pattern to 'Solid'...")
            await websocket.send(json.dumps({"setActivePattern": "Solid"}))
            response = await websocket.recv()
            logger.info(f"Set pattern response: {response}")
            
            logger.info("🎉 Solid color test completed! Did you see any changes to the LEDs?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_solid_color()) 