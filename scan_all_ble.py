#!/usr/bin/env python3
"""
Scan ALL BLE devices and show their names
The Muse might not be advertising as "Muse"
"""

import asyncio

try:
    from bleak import BleakScanner
except ImportError:
    print("Install bleak: pip3 install bleak")
    exit(1)

async def scan():
    print("Scanning ALL BLE devices for 15 seconds...")
    print("Look for anything that might be your Muse")
    print("=" * 50)
    
    devices = await BleakScanner.discover(timeout=15.0)
    
    # Sort by signal strength (RSSI)
    devices = sorted(devices, key=lambda d: d.rssi if d.rssi else -100, reverse=True)
    
    print(f"\nFound {len(devices)} devices (sorted by signal strength):\n")
    
    for i, device in enumerate(devices, 1):
        name = device.name if device.name else "[No Name]"
        print(f"{i:2}. {device.address}  {name:30} (signal: {device.rssi} dBm)")
        
        # Highlight potential Muse devices
        if any(keyword in str(device).lower() for keyword in ['muse', '9190', 'interaxon']):
            print(f"     ^^^ POSSIBLE MUSE! ^^^")

    print("\n" + "=" * 50)
    print("\nNOTE: Your Muse S might show as:")
    print("  - MuseS-XXXX")
    print("  - Muse-XXXX") 
    print("  - Just a MAC address (no name)")
    print("  - Something with '9190' in it")
    print("\nIf you see a device with strong signal (-40 to -60 dBm)")
    print("that appeared when you turned on the Muse, that's probably it!")

asyncio.run(scan())