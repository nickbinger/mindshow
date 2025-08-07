import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_pattern():
    """Create and upload a simple test pattern with controllable variables"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    # Simple test pattern with controllable variables
    test_pattern_code = """
// Simple test pattern with controllable variables
export var brightness = 1.0
export var speed = 0.5
export var hue = 0.0

export function beforeRender(delta) {
    // Update hue based on speed
    hue += speed * delta * 0.001
    if (hue > 1) hue -= 1
}

export function render(index) {
    // Create a wave pattern
    var wave = wave(time(speed * 0.1) + index * 0.1)
    var color = hsv(hue + wave * 0.3, 1, brightness)
    setPixelColor(index, color)
}
"""
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Upload the test pattern
            logger.info("Uploading test pattern...")
            await websocket.send(json.dumps({"putSourceCode": test_pattern_code}))
            response = await websocket.recv()
            logger.info(f"Upload response: {response}")
            
            await asyncio.sleep(2)
            
            # Switch to the test pattern
            logger.info("Switching to test pattern...")
            await websocket.send(json.dumps({"setActivePattern": "test"}))
            response = await websocket.recv()
            logger.info(f"Switch response: {response}")
            
            await asyncio.sleep(2)
            
            # Get the variables
            logger.info("Getting pattern variables...")
            await websocket.send(json.dumps({"getVars": True}))
            response = await websocket.recv()
            logger.info(f"Variables response: {response}")
            
            await asyncio.sleep(2)
            
            # Test controlling the variables
            logger.info("Testing variable control...")
            await websocket.send(json.dumps({"setVars": {"brightness": 0.3, "speed": 0.1, "hue": 0.5}}))
            response = await websocket.recv()
            logger.info(f"Set vars response: {response}")
            
            await asyncio.sleep(3)
            
            logger.info("Setting brightness to 1.0...")
            await websocket.send(json.dumps({"setVars": {"brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Brightness response: {response}")
            
            logger.info("🎉 Test pattern created and tested! Did you see the LEDs change?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_pattern()) 