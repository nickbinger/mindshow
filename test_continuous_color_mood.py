#!/usr/bin/env python3
"""
Test script for continuous color mood mapping
Demonstrates smooth transitions based on simulated brainwave data
"""

import sys
sys.path.append('.')
from integrated_mindshow_system import MultiPixelblazeController, MindShowConfig
import asyncio
import math
import time

async def test_continuous_color_mood():
    print("🎨 Testing Continuous Color Mood Mapping")
    print("=" * 50)
    
    # Create controller with custom config
    config = MindShowConfig()
    config.color_mood_smoothing = 0.3  # Adjust for more/less smoothing
    controller = MultiPixelblazeController(config)
    
    # Discover and connect
    await controller.discover_and_connect()
    
    if not controller.devices:
        print("❌ No Pixelblaze devices found")
        return
    
    device = list(controller.devices.values())[0]
    print(f"✅ Connected to {device.name}")
    
    # Find Phase 4b pattern
    phase4b_id = None
    for pattern_id, pattern_name in device.patterns.items():
        if 'phase 4b' in pattern_name.lower() or 'color mood' in pattern_name.lower():
            phase4b_id = pattern_id
            print(f"🎨 Found Phase 4b pattern: {pattern_name}")
            break
    
    if not phase4b_id:
        print("⚠️  Phase 4b pattern not found")
        return
    
    # Set to Phase 4b pattern
    await controller._update_device(device, device.patterns[phase4b_id], {})
    
    print("\n🌊 Starting continuous color mood demo...")
    print("Watch the LEDs smoothly transition through color temperatures")
    print("Press Ctrl+C to stop\n")
    
    start_time = time.time()
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            # Simulate varying brainwave data with sine waves
            # Attention oscillates faster (focus periods)
            attention = 0.5 + 0.4 * math.sin(elapsed * 0.3)
            
            # Relaxation oscillates slower (calm periods)
            relaxation = 0.5 + 0.4 * math.sin(elapsed * 0.15 + math.pi/2)
            
            # Clamp to valid range
            attention = max(0.0, min(1.0, attention))
            relaxation = max(0.0, min(1.0, relaxation))
            
            # Create brain data
            brain_data = {
                'attention_score': attention,
                'relaxation_score': relaxation
            }
            
            # Determine brain state (this won't change patterns in continuous mode)
            if attention > 0.75:
                brain_state = 'engaged'
            elif relaxation > 0.75:
                brain_state = 'relaxed'
            else:
                brain_state = 'neutral'
            
            # Update with continuous color mood
            await controller.update_from_brain_state(brain_state, brain_data)
            
            # Display current values
            color_mood = controller.previous_color_mood
            mood_bar = create_color_bar(color_mood)
            
            print(f"\r🧠 Attention: {attention:.2f} | "
                  f"Relaxation: {relaxation:.2f} | "
                  f"Color Mood: {color_mood:.3f} {mood_bar}", end='', flush=True)
            
            # Update at 10Hz
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n✅ Test complete!")

def create_color_bar(value):
    """Create a visual representation of color mood"""
    # Map value to emoji scale
    if value < 0.2:
        return "🔥🔥🔥 (very warm)"
    elif value < 0.4:
        return "🔥🔥  (warm)"
    elif value < 0.6:
        return "🌈   (neutral)"
    elif value < 0.8:
        return "❄️❄️  (cool)"
    else:
        return "❄️❄️❄️ (very cool)"

if __name__ == "__main__":
    print("🚀 MindShow Continuous Color Mood Test")
    print("This demonstrates smooth color temperature transitions")
    print("without discrete pattern switching\n")
    
    asyncio.run(test_continuous_color_mood())



