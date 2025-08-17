#!/usr/bin/env python3
"""
Minimal Muse test for Raspberry Pi Zero
Tests Bluetooth and basic BrainFlow connection
"""

import sys
import time

print("=" * 40)
print("MINIMAL MUSE TEST FOR PI ZERO")
print("=" * 40)

# 1. Check Bluetooth status
print("\n1. Checking Bluetooth...")
try:
    import subprocess
    result = subprocess.run(['systemctl', 'is-active', 'bluetooth'], 
                          capture_output=True, text=True)
    if result.stdout.strip() == 'active':
        print("✓ Bluetooth service is active")
    else:
        print("✗ Bluetooth service is not active")
        print("  Run: sudo systemctl start bluetooth")
        sys.exit(1)
except Exception as e:
    print(f"✗ Could not check Bluetooth: {e}")

# 2. Check BrainFlow import
print("\n2. Checking BrainFlow...")
try:
    from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
    print("✓ BrainFlow imported successfully")
except ImportError as e:
    print(f"✗ BrainFlow not installed: {e}")
    print("  Run: pip install brainflow")
    sys.exit(1)

# 3. Try to connect to Muse
print("\n3. Attempting Muse connection...")
print("  Make sure Muse is ON (hold button 3-5 seconds)")
print("  Connecting (15 second timeout)...")

params = BrainFlowInputParams()
params.serial_port = ''  # Empty for Bluetooth

# Use board_id 38 (Muse 2 protocol - works with Muse S)
board = BoardShim(38, params)

try:
    # Prepare session (this is where it connects)
    board.prepare_session()
    print("✓ Connected to Muse!")
    
    # Start stream
    print("\n4. Starting data stream...")
    board.start_stream()
    time.sleep(2)
    
    # Get some data
    print("\n5. Reading data...")
    data = board.get_current_board_data(256)
    
    if data.size > 0:
        print(f"✓ Receiving data! Shape: {data.shape}")
        print(f"  Samples received: {data.shape[1]}")
        
        # Show first channel average
        if data.shape[0] > 0 and data.shape[1] > 0:
            avg = data[0, :].mean()
            print(f"  Channel 0 average: {avg:.2f}")
    else:
        print("✗ No data received")
    
    print("\n✅ SUCCESS! Muse is working on Pi Zero")
    
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Is Muse turned ON? (lights should be on)")
    print("2. Is Bluetooth enabled on Pi?")
    print("3. Try: sudo hciconfig hci0 up")
    print("4. Try: sudo rfkill unblock bluetooth")
    print("5. Is Muse already connected to phone/computer?")
    
finally:
    # Clean up
    try:
        board.stop_stream()
        board.release_session()
    except:
        pass

print("\n" + "=" * 40)