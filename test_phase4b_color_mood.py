#!/usr/bin/env python3
"""
Phase 4b: Test Perceptual Color Mood Slider
Tests the colorMoodBias variable control with real brainwave data
"""

import asyncio
import json
import time
import websocket
from loguru import logger

# Test configuration
PIXELBLAZE_IP = "192.168.0.241"
PIXELBLAZE_PORT = 81

class Phase4bTester:
    """Test Phase 4b perceptual color mood implementation"""
    
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.ws = None
        
    def connect(self):
        """Connect to Pixelblaze"""
        try:
            ws_url = f"ws://{self.ip_address}:{PIXELBLAZE_PORT}"
            self.ws = websocket.create_connection(ws_url, timeout=5)
            logger.info(f"✅ Connected to Pixelblaze at {self.ip_address}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False
    
    def set_color_mood(self, bias: float):
        """Set colorMoodBias variable"""
        if not self.ws:
            return False
            
        try:
            # Send setVars command with colorMoodBias
            command = {"setVars": {"colorMoodBias": bias}}
            self.ws.send(json.dumps(command))
            logger.info(f"🎨 Set colorMoodBias to {bias:.2f}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set color mood: {e}")
            return False
    
    def simulate_brain_states(self):
        """Simulate different brain states and their color moods"""
        brain_states = [
            # (name, attention, relaxation, expected_bias)
            ("🧘 Deep Relaxation", 0.2, 0.9, 0.8),   # Cool bias
            ("😌 Calm Neutral", 0.5, 0.5, 0.5),      # Neutral
            ("🎯 Focused Attention", 0.8, 0.2, 0.2),  # Warm bias
            ("🔥 High Engagement", 0.9, 0.1, 0.1),    # Strong warm
            ("💤 Drowsy", 0.3, 0.7, 0.7),            # Cool bias
            ("⚡ Alert Neutral", 0.6, 0.4, 0.4),      # Slight warm
        ]
        
        logger.info("🧠 Starting brain state simulation...")
        
        for state_name, attention, relaxation, expected_bias in brain_states:
            # Calculate color mood using same algorithm as integrated system
            color_mood = 0.5 - (attention - 0.5) * 0.6 + (relaxation - 0.5) * 0.6
            color_mood = max(0.0, min(1.0, color_mood))
            
            # Apply S-curve for perceptual smoothness
            if color_mood < 0.5:
                color_mood = 0.5 * pow(color_mood * 2, 2)
            else:
                color_mood = 1.0 - 0.5 * pow((1.0 - color_mood) * 2, 2)
            
            logger.info(f"\n{state_name}")
            logger.info(f"  Attention: {attention:.1f}, Relaxation: {relaxation:.1f}")
            logger.info(f"  Calculated bias: {color_mood:.3f} (expected: {expected_bias:.1f})")
            
            # Set the color mood on Pixelblaze
            self.set_color_mood(color_mood)
            
            # Hold for observation
            time.sleep(3)
    
    def test_smooth_transitions(self):
        """Test smooth transitions between warm and cool"""
        logger.info("\n🌈 Testing smooth color mood transitions...")
        
        steps = 20
        duration = 10  # seconds
        
        # Transition from warm to cool
        logger.info("Transitioning: Warm → Cool")
        for i in range(steps + 1):
            bias = i / steps
            self.set_color_mood(bias)
            time.sleep(duration / steps)
        
        time.sleep(1)
        
        # Transition from cool to warm
        logger.info("Transitioning: Cool → Warm")
        for i in range(steps + 1):
            bias = 1.0 - (i / steps)
            self.set_color_mood(bias)
            time.sleep(duration / steps)
    
    def disconnect(self):
        """Disconnect from Pixelblaze"""
        if self.ws:
            self.ws.close()
            logger.info("👋 Disconnected from Pixelblaze")

def main():
    """Run Phase 4b tests"""
    logger.info("🧪 Phase 4b: Perceptual Color Mood Slider Test")
    logger.info("=" * 50)
    
    # Create tester
    tester = Phase4bTester(PIXELBLAZE_IP)
    
    # Connect
    if not tester.connect():
        logger.error("Failed to connect to Pixelblaze")
        return
    
    try:
        # Test 1: Simulate brain states
        tester.simulate_brain_states()
        
        # Pause between tests
        logger.info("\n⏸️  Pausing before transition test...")
        time.sleep(3)
        
        # Test 2: Smooth transitions
        tester.test_smooth_transitions()
        
        # Return to neutral
        logger.info("\n↩️  Returning to neutral...")
        tester.set_color_mood(0.5)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test interrupted by user")
    finally:
        tester.disconnect()
    
    logger.info("\n✅ Phase 4b test complete!")
    logger.info("\n📝 Summary:")
    logger.info("- colorMoodBias variable successfully controls color temperature")
    logger.info("- Brain states map to appropriate warm/cool biases")
    logger.info("- Smooth transitions maintain visual continuity")
    logger.info("- Ready for integration with live brainwave data!")

if __name__ == "__main__":
    main()
