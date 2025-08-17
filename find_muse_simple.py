#!/usr/bin/env python3
"""
Simple Muse finder for Pi Zero
"""

import subprocess
import time

print("FINDING MUSE - SIMPLE METHOD")
print("=" * 40)

# Make sure Bluetooth is on
subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'], capture_output=True)
subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'], capture_output=True)

print("1. Turn OFF your Muse")
print("2. Press ENTER when ready")
input()

print("\nScanning without Muse (baseline)...")
result1 = subprocess.run(['sudo', 'timeout', '5', 'bluetoothctl', 'scan', 'on'], 
                        capture_output=True, text=True)

print("\n3. Now turn ON your Muse (hold button 3-5 seconds)")
print("4. Press ENTER when Muse lights are on")
input()

print("\nScanning WITH Muse...")
# Use bluetoothctl interactively
process = subprocess.Popen(
    ['sudo', 'bluetoothctl'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send commands
commands = [
    'scan on\n',
    'devices\n'
]

for cmd in commands:
    process.stdin.write(cmd)
    process.stdin.flush()
    time.sleep(5)

process.stdin.write('quit\n')
process.stdin.flush()

output, _ = process.communicate(timeout=10)

# Show all devices found
print("\nDevices found:")
print("-" * 40)
lines = output.split('\n')
for line in lines:
    if 'Device' in line or ':' in line:
        print(line)
        # Check for Muse-like patterns
        if any(x in line.upper() for x in ['MUSE', '9190', '00:55:DA', '00:14:ED']):
            print("  ^^^ THIS MIGHT BE YOUR MUSE! ^^^")

print("\n" + "=" * 40)
print("\nLook for any NEW device that appeared after turning on Muse")
print("Muse MAC addresses often start with 00:55:DA or 00:14:ED")