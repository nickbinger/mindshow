#!/usr/bin/env python3
"""
Receive data from MuseLSL stream
Run this AFTER starting: muselsl stream
"""

import time
import sys

print("MUSELSL RECEIVER")
print("=" * 40)

try:
    from pylsl import StreamInlet, resolve_byprop
except ImportError:
    print("✗ PyLSL not installed")
    print("Run: pip3 install pylsl")
    sys.exit(1)

print("Looking for EEG stream...")
streams = resolve_byprop('type', 'EEG', timeout=5)

if not streams:
    print("✗ No EEG stream found")
    print("\nMake sure muselsl stream is running:")
    print("  muselsl stream")
    sys.exit(1)

print(f"✓ Found {len(streams)} EEG stream(s)")

# Connect to first stream
inlet = StreamInlet(streams[0])
print("✓ Connected to stream")

print("\nReceiving data for 10 seconds...")
print("-" * 40)

start_time = time.time()
sample_count = 0

while time.time() - start_time < 10:
    # Get sample
    sample, timestamp = inlet.pull_sample(timeout=1.0)
    
    if sample:
        sample_count += 1
        if sample_count % 100 == 0:  # Print every 100 samples
            # Show first 4 channels (TP9, AF7, AF8, TP10)
            ch_data = [f"{s:.1f}" for s in sample[:4]]
            print(f"Sample {sample_count}: {ch_data}")

print("-" * 40)
print(f"\n✓ Received {sample_count} samples in 10 seconds")
print(f"  Rate: {sample_count/10:.1f} Hz")

if sample_count > 0:
    print("\n✅ SUCCESS! MuseLSL is working")