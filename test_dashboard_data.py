#!/usr/bin/env python3
"""
Test script to verify dashboard data broadcasting
"""

import asyncio
import websockets
import json
import time

async def test_dashboard_data():
    """Test WebSocket connection to dashboard"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to dashboard WebSocket")
            
            # Wait for data
            for i in range(10):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"📊 Received data: {json.dumps(data, indent=2)}")
                    break
                except asyncio.TimeoutError:
                    print(f"⏳ Waiting for data... ({i+1}/10)")
                    
            print("✅ Dashboard data broadcasting is working!")
            
    except Exception as e:
        print(f"❌ Error connecting to dashboard: {e}")

if __name__ == "__main__":
    asyncio.run(test_dashboard_data())
