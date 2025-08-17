#!/usr/bin/env python3
"""
Simplest possible Pi Zero Muse test
No sudo required, minimal dependencies
"""

print("SIMPLE MUSE TEST")
print("=" * 30)

# Just try to import and connect
try:
    from brainflow.board_shim import BoardShim, BrainFlowInputParams
    print("✓ BrainFlow available")
    
    print("\nTrying to connect (15 sec timeout)...")
    print("Make sure Muse is ON!")
    
    params = BrainFlowInputParams()
    board = BoardShim(38, params)  # Board ID 38 for Muse
    
    board.prepare_session()
    print("✓ CONNECTED!")
    
    board.start_stream()
    import time
    time.sleep(1)
    
    data = board.get_current_board_data(10)
    if data.size > 0:
        print(f"✓ Got {data.shape[1]} samples")
    
    board.stop_stream()
    board.release_session()
    
except ImportError:
    print("✗ BrainFlow not installed")
    print("Run: pip3 install brainflow")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTry these commands:")
    print("  sudo systemctl start bluetooth")
    print("  sudo hciconfig hci0 up")

print("=" * 30)