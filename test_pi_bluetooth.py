#!/usr/bin/env python3
"""
Ultra-minimal Bluetooth check for Pi Zero
Just verifies Bluetooth is working
"""

import subprocess
import sys

print("BLUETOOTH CHECK FOR PI ZERO")
print("=" * 30)

# 1. Check Bluetooth service
print("\n1. Bluetooth service:")
result = subprocess.run(['systemctl', 'is-active', 'bluetooth'], 
                      capture_output=True, text=True)
print(f"   Status: {result.stdout.strip()}")

# 2. Check Bluetooth hardware
print("\n2. Bluetooth hardware:")
result = subprocess.run(['hciconfig', '-a'], 
                      capture_output=True, text=True)
if 'UP RUNNING' in result.stdout:
    print("   ✓ Bluetooth adapter is UP")
else:
    print("   ✗ Bluetooth adapter is DOWN")
    print("   Run: sudo hciconfig hci0 up")

# 3. Scan for devices
print("\n3. Scanning for BLE devices (5 seconds)...")
try:
    result = subprocess.run(['timeout', '5', 'hcitool', 'lescan'], 
                          capture_output=True, text=True, 
                          stderr=subprocess.DEVNULL)
    lines = result.stdout.strip().split('\n')
    
    muse_found = False
    for line in lines:
        if 'Muse' in line:
            print(f"   ✓ Found: {line}")
            muse_found = True
        
    if not muse_found:
        print("   No Muse found (make sure it's ON)")
        if len(lines) > 1:
            print(f"   Found {len(lines)-1} other BLE devices")
    
except Exception as e:
    print(f"   Scan failed: {e}")
    print("   Try: sudo hcitool lescan")

print("\n" + "=" * 30)