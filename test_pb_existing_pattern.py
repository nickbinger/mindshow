import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_existing_pattern():
    """Test controlling an existing pattern with variables"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Switch to the "Example: ui controls" pattern
            logger.info("Switching to 'Example: ui controls' pattern...")
            await websocket.send(json.dumps({"setActivePattern": "Example: ui controls (lightning ZAP!)"}))
            response = await websocket.recv()
            logger.info(f"Switch response: {response}")
            
            await asyncio.sleep(3)
            
            # Get the variables for this pattern
            logger.info("Getting pattern variables...")
            await websocket.send(json.dumps({"getVars": True}))
            response = await websocket.recv()
            logger.info(f"Variables response: {response}")
            
            await asyncio.sleep(2)
            
            # Try setting some common variables that UI control patterns might have
            logger.info("Testing variable control...")
            await websocket.send(json.dumps({"setVars": {"brightness": 0.3, "speed": 0.1}}))
            response = await websocket.recv()
            logger.info(f"Set vars response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting brightness to 1.0...")
            await websocket.send(json.dumps({"setVars": {"brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Brightness response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting speed to 0.9...")
            await websocket.send(json.dumps({"setVars": {"speed": 0.9}}))
            response = await websocket.recv()
            logger.info(f"Speed response: {response}")
            
            logger.info("🎉 Existing pattern test completed! Did you see the LEDs change?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_existing_pattern()) 