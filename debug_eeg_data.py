#!/usr/bin/env python3
"""
Debug script to test real EEG data processing
"""

import sys
sys.path.append('.')
from integrated_mindshow_system import MindShowConfig, IntegratedEEGProcessor
import time

def test_eeg_processing():
    print("🔍 Testing Real EEG Data Processing")
    print("=" * 50)
    
    # Create config and processor
    config = MindShowConfig()
    processor = IntegratedEEGProcessor(config)
    
    print("🔌 Connecting to EEG source...")
    if not processor.connect():
        print("❌ Failed to connect to EEG source")
        return
    
    print(f"✅ Connected via: {processor.current_source}")
    print("\n📊 Collecting brain state data for 10 seconds...")
    print("   (Try focusing, relaxing, or staying neutral)")
    
    start_time = time.time()
    sample_count = 0
    
    while time.time() - start_time < 10:
        brain_data = processor.get_brain_state()
        
        if brain_data:
            sample_count += 1
            band_powers = brain_data['band_powers']
            attention = brain_data['attention']
            relaxation = brain_data['relaxation']
            brain_state = brain_data['brain_state']
            
            print(f"\n📈 Sample {sample_count}:")
            print(f"   🧠 Brain State: {brain_state}")
            print(f"   🔥 Attention: {attention:.3f}")
            print(f"   ❄️  Relaxation: {relaxation:.3f}")
            print(f"   📊 Band Powers:")
            print(f"      Delta: {band_powers['delta']:.3f}")
            print(f"      Theta: {band_powers['theta']:.3f}")
            print(f"      Alpha: {band_powers['alpha']:.3f}")
            print(f"      Beta: {band_powers['beta']:.3f}")
            print(f"      Gamma: {band_powers['gamma']:.3f}")
            
            # Show raw ratios
            beta_alpha_ratio = band_powers['beta'] / (band_powers['alpha'] + 1e-10)
            alpha_theta_ratio = band_powers['alpha'] / (band_powers['theta'] + 1e-10)
            print(f"   🔢 Raw Ratios:")
            print(f"      Beta/Alpha: {beta_alpha_ratio:.3f}")
            print(f"      Alpha/Theta: {alpha_theta_ratio:.3f}")
            
        time.sleep(1.0)
    
    print(f"\n✅ Collected {sample_count} samples")
    print("🎯 Analysis:")
    print("   - If all values are ~0.5, normalization is too aggressive")
    print("   - If band powers are very small, scaling is needed")
    print("   - If ratios are extreme, thresholds need adjustment")

if __name__ == "__main__":
    test_eeg_processing()
