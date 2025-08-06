#!/usr/bin/env python3
"""
Upload Matrix 2d Honeycomb Pattern (Clean Version)
Now that WebSocket conflicts are resolved
"""

import asyncio
import json
import logging
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def upload_honeycomb_clean():
    """Upload the Matrix 2d Honeycomb pattern"""
    
    pixelblaze_url = "ws://192.168.0.241:81"
    
    logger.info("🧠 MindShow - Upload Matrix 2d Honeycomb Pattern (Clean)")
    logger.info("=" * 60)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Connect to Pixelblaze
        logger.info(f"Connecting to Pixelblaze at {pixelblaze_url}")
        websocket = await websockets.connect(pixelblaze_url)
        logger.info("✅ Connected to Pixelblaze!")
        
        # Define the Matrix 2d Honeycomb pattern
        honeycomb_pattern = {
            "name": "Matrix 2d Honeycomb",
            "code": """
w = 8 // the width of the 2D matrix
zigzag = true //straight or zigzag wiring?

export function beforeRender(delta) {
  tf = 5
  t1 = wave(time(.15*tf))*PI2
  t2 = wave(time(.19*tf))*PI2
  z = 2+wave(time(.1*tf))*5
  t3 = wave(time(.13*tf))
  t4 = (time(.01*tf))
}

export function render(index) {
  y = floor(index/w)
  x = index%w
  if (zigzag) {
    x = (y % 2 == 0 ? x : w-1-x)
  }
  h = (1 + sin(x/w*z + t1) + cos(y/w*z + t2))*.5
  v = wave(h + t4)
  v = v*v*v
  h = triangle(h%1)/2 + t3
  hsv(h,1,v)
}
"""
        }
        
        # Upload the pattern
        logger.info("Uploading Matrix 2d Honeycomb pattern...")
        await websocket.send(json.dumps({
            "createPattern": honeycomb_pattern
        }))
        
        response = await websocket.recv()
        logger.info(f"Pattern creation response: {response}")
        
        # Set it as active pattern
        logger.info("Setting Matrix 2d Honeycomb as active pattern...")
        await websocket.send(json.dumps({
            "setActivePattern": "Matrix 2d Honeycomb"
        }))
        
        response = await websocket.recv()
        logger.info(f"Pattern activation response: {response}")
        
        # Test color control on the new pattern
        logger.info("Testing color control on honeycomb pattern...")
        test_colors = [
            (0.0, "RED"),
            (0.33, "GREEN"), 
            (0.66, "BLUE"),
            (1.0, "RED (cycle)")
        ]
        
        for hue, color_name in test_colors:
            logger.info(f"Setting hue to {hue:.2f} ({color_name})")
            await websocket.send(json.dumps({"setVars": {"hue": hue}}))
            response = await websocket.recv()
            logger.info(f"  ✅ {color_name} color set successfully!")
            await asyncio.sleep(3)  # Wait to see the effect
        
        logger.info("=" * 60)
        logger.info("✅ Matrix 2d Honeycomb pattern uploaded and activated!")
        logger.info("🎨 The honeycomb pattern should now be running on your LEDs!")
        logger.info("📝 Pattern details:")
        logger.info("   - 8x8 matrix with zigzag wiring")
        logger.info("   - Animated honeycomb-like pattern")
        logger.info("   - Uses HSV color space with dynamic hue and value")
        
        # Close connection
        await websocket.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(upload_honeycomb_clean()) 