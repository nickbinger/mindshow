import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_colorpalette_control():
    """Test controlling the colorPalette pattern"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Test 1: Try common color palette variables
            logger.info("Setting palette to blue tones...")
            await websocket.send(json.dumps({"setVar": {"palette": 0}}))
            response = await websocket.recv()
            logger.info(f"Palette 0 response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting palette to red tones...")
            await websocket.send(json.dumps({"setVar": {"palette": 1}}))
            response = await websocket.recv()
            logger.info(f"Palette 1 response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting palette to green tones...")
            await websocket.send(json.dumps({"setVar": {"palette": 2}}))
            response = await websocket.recv()
            logger.info(f"Palette 2 response: {response}")
            
            await asyncio.sleep(3)
            
            # Test 2: Try speed control
            logger.info("Setting speed to 0.1 (slow)...")
            await websocket.send(json.dumps({"setVar": {"speed": 0.1}}))
            response = await websocket.recv()
            logger.info(f"Speed 0.1 response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting speed to 0.9 (fast)...")
            await websocket.send(json.dumps({"setVar": {"speed": 0.9}}))
            response = await websocket.recv()
            logger.info(f"Speed 0.9 response: {response}")
            
            await asyncio.sleep(3)
            
            # Test 3: Try brightness control
            logger.info("Setting brightness to 0.3 (dim)...")
            await websocket.send(json.dumps({"setVar": {"brightness": 0.3}}))
            response = await websocket.recv()
            logger.info(f"Brightness 0.3 response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting brightness to 1.0 (full)...")
            await websocket.send(json.dumps({"setVar": {"brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Brightness 1.0 response: {response}")
            
            logger.info("🎉 ColorPalette control test completed! Did you see any changes to the LEDs?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_colorpalette_control()) 