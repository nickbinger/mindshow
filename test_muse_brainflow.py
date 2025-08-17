#!/usr/bin/env python3
"""
Direct test of Muse connection via BrainFlow
This is what actually works with your MuseS-9190
"""

import time
import sys
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter

print("Testing Muse Connection via BrainFlow")
print("=" * 40)

# Your Muse works with board_id 38 (Muse 2 protocol)
BOARD_ID = 38  # This worked in our earlier test!

params = BrainFlowInputParams()
params.serial_port = ''  # Empty for Bluetooth

board = BoardShim(BOARD_ID, params)

try:
    print("1. Preparing session...")
    board.prepare_session()
    print("✓ Connected to Muse!")
    
    print("2. Starting stream...")
    board.start_stream()
    time.sleep(2)
    
    print("3. Getting data...")
    for i in range(5):
        data = board.get_current_board_data(256)
        if data.size > 0:
            eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
            if len(eeg_channels) > 0:
                eeg_data = data[eeg_channels[0], :]
                avg = eeg_data.mean()
                std = eeg_data.std()
                print(f"   Sample {i+1}: Mean={avg:.1f}µV, StdDev={std:.1f}µV")
        time.sleep(1)
    
    print("✓ Successfully receiving EEG data!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Is Bluetooth ON?")
    print("2. Is Muse turned ON? (hold button 3-5 seconds)")
    print("3. Is Muse already connected to another app?")
    
finally:
    try:
        board.stop_stream()
        board.release_session()
    except:
        pass

print("\nIf this works, use: ./start.sh --brainflow")