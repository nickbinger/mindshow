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
    
    # Try to sort by signal strength if available
    try:
        devices = sorted(devices, key=lambda d: getattr(d, 'rssi', -100), reverse=True)
    except:
        pass  # Don't sort if RSSI not available
    
    print(f"\nFound {len(devices)} devices:\n")
    
    for i, device in enumerate(devices, 1):
        name = device.name if device.name else "[No Name]"
        rssi = getattr(device, 'rssi', 'N/A')
        rssi_str = f"(signal: {rssi} dBm)" if rssi != 'N/A' else ""
        print(f"{i:2}. {device.address}  {name:30} {rssi_str}")
        
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