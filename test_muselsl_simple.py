#!/usr/bin/env python3
"""
Simple MuseLSL test for Pi Zero
This uses less resources than BrainFlow
"""

print("MUSELSL TEST")
print("=" * 40)

# 1. Check if muselsl is installed
try:
    import muselsl
    print("✓ MuseLSL installed")
except ImportError:
    print("✗ MuseLSL not installed")
    print("Run: pip3 install muselsl")
    exit(1)

# 2. Check if pylsl is installed
try:
    import pylsl
    print("✓ PyLSL installed")
except ImportError:
    print("✗ PyLSL not installed")
    print("Run: pip3 install pylsl")
    exit(1)

# 3. List available Muses
print("\nSearching for Muse devices...")
from muselsl import list_muses

muses = list_muses()
if muses:
    print(f"✓ Found {len(muses)} Muse(s):")
    for i, muse in enumerate(muses):
        print(f"  {i+1}. {muse['name']} - {muse['address']}")
else:
    print("✗ No Muse found")
    print("\nMake sure:")
    print("1. Muse is ON")
    print("2. Bluetooth is enabled")
    print("3. Muse is not connected to another device")
    exit(1)

print("\n" + "=" * 40)
print("\nTo start streaming, run:")
print(f"  muselsl stream --address {muses[0]['address']}")
print("\nThen in another terminal, run:")
print("  python3 test_muselsl_receive.py")