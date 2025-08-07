import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pixelblaze_control():
    """Test Pixelblaze control using the correct WebSocket protocol"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Test 1: Set brightness to 30%
            logger.info("Setting brightness to 30%...")
            await websocket.send(json.dumps({"brightness": 30}))
            response = await websocket.recv()
            logger.info(f"Brightness response: {response}")
            
            await asyncio.sleep(2)
            
            # Test 2: Set brightness to 100%
            logger.info("Setting brightness to 100%...")
            await websocket.send(json.dumps({"brightness": 100}))
            response = await websocket.recv()
            logger.info(f"Brightness response: {response}")
            
            await asyncio.sleep(2)
            
            # Test 3: Set a variable (this should change the pattern)
            logger.info("Setting 'brightness' variable to 0.5...")
            await websocket.send(json.dumps({"setVar": {"brightness": 0.5}}))
            response = await websocket.recv()
            logger.info(f"setVar response: {response}")
            
            await asyncio.sleep(2)
            
            # Test 4: Set speed variable
            logger.info("Setting 'speed' variable to 0.3...")
            await websocket.send(json.dumps({"setVar": {"speed": 0.3}}))
            response = await websocket.recv()
            logger.info(f"setVar response: {response}")
            
            await asyncio.sleep(2)
            
            # Test 5: Get current info
            logger.info("Getting current info...")
            await websocket.send(json.dumps({"getInfo": True}))
            response = await websocket.recv()
            logger.info(f"Info response: {response}")
            
            logger.info("🎉 Test completed! Did you see any changes to the LEDs?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pixelblaze_control()) 