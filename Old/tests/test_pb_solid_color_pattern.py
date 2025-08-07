import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_solid_color_pattern():
    """Create and upload a simple solid color pattern with controllable variables"""
    pixelblaze_url = "ws://192.168.0.241:81"
    
    # Simple solid color pattern with controllable variables
    solid_color_pattern = """
// Simple solid color pattern with controllable variables
export var hue = 0.0        // 0 = red, 0.33 = green, 0.66 = blue
export var saturation = 1.0  // 0 = white, 1 = pure color
export var brightness = 1.0  // 0 = off, 1 = full brightness

export function render(index) {
    hsv(hue, saturation, brightness)
}
"""
    
    try:
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}...")
        async with websockets.connect(pixelblaze_url) as websocket:
            logger.info("✅ Connected to Pixelblaze!")
            
            # Upload the solid color pattern
            logger.info("Uploading solid color pattern...")
            await websocket.send(json.dumps({"putSourceCode": solid_color_pattern}))
            response = await websocket.recv()
            logger.info(f"Upload response: {response}")
            
            await asyncio.sleep(2)
            
            # Switch to the solid color pattern
            logger.info("Switching to solid color pattern...")
            await websocket.send(json.dumps({"setActivePattern": "solid_color"}))
            response = await websocket.recv()
            logger.info(f"Switch response: {response}")
            
            await asyncio.sleep(2)
            
            # Test controlling the variables - set to solid blue
            logger.info("Setting to solid blue...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.66, "saturation": 1.0, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Blue response: {response}")
            
            await asyncio.sleep(3)
            
            # Test setting to solid red
            logger.info("Setting to solid red...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.0, "saturation": 1.0, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Red response: {response}")
            
            await asyncio.sleep(3)
            
            # Test setting to solid green
            logger.info("Setting to solid green...")
            await websocket.send(json.dumps({"setVars": {"hue": 0.33, "saturation": 1.0, "brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"Green response: {response}")
            
            await asyncio.sleep(3)
            
            # Test turning off
            logger.info("Turning off...")
            await websocket.send(json.dumps({"setVars": {"brightness": 0.0}}))
            response = await websocket.recv()
            logger.info(f"Off response: {response}")
            
            await asyncio.sleep(2)
            
            # Test turning back on
            logger.info("Turning back on...")
            await websocket.send(json.dumps({"setVars": {"brightness": 1.0}}))
            response = await websocket.recv()
            logger.info(f"On response: {response}")
            
            logger.info("🎉 Solid color test completed! Did you see the LEDs change colors?")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_solid_color_pattern()) 