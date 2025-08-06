import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cursor_pattern():
    """Test controlling the cursor_test pattern with exported variables"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Switch to the cursor_test pattern
            logger.info("Switching to 'cursor_test' pattern...")
            await websocket.send(json.dumps({"setActivePattern": "cursor_test"}))
            response = await websocket.recv()
            logger.info(f"Switch response: {response}")
            
            await asyncio.sleep(3)
            
            # Get the variables for this pattern
            logger.info("Getting pattern variables...")
            await websocket.send(json.dumps({"getVars": True}))
            response = await websocket.recv()
            logger.info(f"Variables response: {response}")
            
            await asyncio.sleep(2)
            
            # Test setting to solid blue
            logger.info("Setting to solid blue (hue = 0.66)...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Blue response: {response}")
            
            await asyncio.sleep(3)
            
            # Test setting to solid red
            logger.info("Setting to solid red (hue = 0.0)...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Red response: {response}")
            
            await asyncio.sleep(3)
            
            # Test setting to solid green
            logger.info("Setting to solid green (hue = 0.33)...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.33, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Green response: {response}")
            
            await asyncio.sleep(3)
            
            # Test turning off
            logger.info("Turning off (brightness = 0)...")
            await websocket.send(json.dumps({"setVars": {"brightness": 0.0}}))
            response = await websocket.recv()
            logger.info(f"Off response: {response}")
            
            await asyncio.sleep(2)
            
            # Test turning back on
            logger.info("Turning back on (brightness = 1.0)...")
            await websocket.send(json.dumps({"setVars": {"brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"On response: {response}")
            
            logger.info("🎉 Cursor test pattern completed! Did you see the LEDs change colors?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_cursor_pattern()) 