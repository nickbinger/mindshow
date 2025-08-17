#!/usr/bin/env python3
"""
Direct Muse connection using Bleak (no BrainFlow)
Much lighter weight for Pi Zero
"""

import asyncio
import sys

print("MUSE TEST WITH BLEAK (Lightweight)")
print("=" * 40)

try:
    from bleak import BleakScanner, BleakClient
except ImportError:
    print("✗ Bleak not installed")
    print("Run: pip3 install bleak")
    sys.exit(1)

async def find_muse():
    """Scan for Muse devices"""
    print("Scanning for Muse (10 seconds)...")
    devices = await BleakScanner.discover(timeout=10.0)
    
    muse_devices = []
    for device in devices:
        if device.name and 'Muse' in device.name:
            muse_devices.append(device)
            print(f"✓ Found: {device.name} [{device.address}]")
    
    if not muse_devices:
        print("✗ No Muse found")
        print(f"  (Found {len(devices)} other BLE devices)")
    
    return muse_devices

async def connect_muse(address):
    """Try to connect to Muse"""
    print(f"\nConnecting to {address}...")
    
    try:
        async with BleakClient(address) as client:
            print(f"✓ Connected: {client.is_connected}")
            
            # List services (method name varies by bleak version)
            try:
                # Newer bleak versions
                services = client.services
            except:
                # Older bleak versions
                try:
                    services = await client.get_services()
                except:
                    services = []
            
            if services:
                print(f"✓ Found {len(services)} services")
                
                # The Muse control service
                MUSE_SERVICE = "0000fe8d-0000-1000-8000-00805f9b34fb"
                
                for service in services:
                    service_uuid = str(service.uuid) if hasattr(service, 'uuid') else str(service)
                    if MUSE_SERVICE in service_uuid.lower():
                        print(f"✓ Found Muse service: {service_uuid}")
            else:
                print("✓ Connected but couldn't list services (that's OK)")
                    
            return True
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

async def main():
    # Find Muse devices
    muse_devices = await find_muse()
    
    if muse_devices:
        # Try to connect to first Muse found
        muse = muse_devices[0]
        success = await connect_muse(muse.address)
        
        if success:
            print("\n✅ SUCCESS! Muse is working")
        else:
            print("\n✗ Could not connect to Muse")
    else:
        print("\nMake sure:")
        print("1. Muse is ON (hold button 3-5 seconds)")
        print("2. Bluetooth is enabled: sudo systemctl start bluetooth")
        print("3. Muse is not connected to another device")

if __name__ == "__main__":
    asyncio.run(main())