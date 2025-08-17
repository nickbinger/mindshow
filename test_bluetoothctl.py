#!/usr/bin/env python3
"""
Test Muse connection using bluetoothctl
More reliable on Pi Zero than hcitool
"""

import subprocess
import time
import re

print("MUSE SCAN WITH BLUETOOTHCTL")
print("=" * 40)

def run_bluetoothctl(commands):
    """Run bluetoothctl commands"""
    process = subprocess.Popen(
        ['sudo', 'bluetoothctl'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send commands
    for cmd in commands:
        process.stdin.write(cmd + '\n')
        process.stdin.flush()
        time.sleep(0.5)
    
    # Get output
    time.sleep(5)  # Wait for scan
    process.stdin.write('quit\n')
    process.stdin.flush()
    
    output, error = process.communicate(timeout=10)
    return output

print("1. Powering on Bluetooth...")
output = run_bluetoothctl(['power on'])
if 'Powered: yes' in output or 'succeeded' in output:
    print("   ✓ Bluetooth powered on")

print("\n2. Starting scan (10 seconds)...")
print("   Make sure Muse is ON!")

output = run_bluetoothctl([
    'scan on',
    'devices'
])

# Parse output for devices
lines = output.split('\n')
muse_found = False
all_devices = []

for line in lines:
    # Look for device lines (MAC address pattern)
    if re.search(r'([0-9A-F]{2}:){5}[0-9A-F]{2}', line, re.IGNORECASE):
        all_devices.append(line.strip())
        if 'muse' in line.lower():
            print(f"   ✓ FOUND: {line.strip()}")
            muse_found = True
            
            # Extract MAC address
            mac_match = re.search(r'([0-9A-F]{2}:){5}[0-9A-F]{2}', line, re.IGNORECASE)
            if mac_match:
                mac = mac_match.group(0)
                print(f"   MAC: {mac}")
                
                # Try to connect
                print(f"\n3. Trying to connect to {mac}...")
                connect_output = run_bluetoothctl([
                    f'connect {mac}'
                ])
                
                if 'Connected: yes' in connect_output or 'successful' in connect_output:
                    print("   ✓ Connected!")
                else:
                    print("   ✗ Connection failed")

if not muse_found:
    print(f"\n   ✗ No Muse found among {len(all_devices)} devices")
    if all_devices:
        print("\n   Other devices found:")
        for device in all_devices[:5]:  # Show first 5
            print(f"   - {device}")

print("\n" + "=" * 40)
print("\nIf this doesn't work, try manually:")
print("  sudo bluetoothctl")
print("  > power on")
print("  > scan on")
print("  > devices")
print("  (look for Muse MAC address)")
print("  > connect XX:XX:XX:XX:XX:XX")