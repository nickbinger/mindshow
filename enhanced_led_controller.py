#!/usr/bin/env python3
"""
Enhanced LED Controller with advanced animation patterns
Based on research from comprehensive development documentation
"""

import numpy as np
import time
from typing import Tuple, List, Optional, Dict
from loguru import logger
import asyncio

try:
    import board
    import neopixel
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logger.warning("NeoPixel hardware not available - using simulation mode")

class EnhancedLEDController:
    """Advanced LED controller with smooth animations and wave effects"""
    
    def __init__(self, num_pixels: int = 60, pin=None, brightness: float = 0.3):
        """Initialize LED controller with hardware optimization"""
        self.num_pixels = num_pixels
        self.brightness = brightness
        self.current_colors = np.zeros((num_pixels, 3), dtype=np.uint8)
        self.target_colors = np.zeros((num_pixels, 3), dtype=np.uint8)
        
        if HARDWARE_AVAILABLE and pin:
            # Initialize NeoPixels with manual write for better performance
            self.pixels = neopixel.NeoPixel(
                pin, num_pixels, 
                brightness=brightness, 
                auto_write=False,  # Manual control for batch updates
                pixel_order=neopixel.GRB
            )
            self.hardware_mode = True
        else:
            # Simulation mode for development
            self.pixels = None
            self.hardware_mode = False
            logger.info("Running in simulation mode - no actual LEDs")
        
        # Animation state
        self.animation_running = False
        self.last_update = time.time()
        
        logger.info(f"Initialized {num_pixels} LED controller (hardware: {self.hardware_mode})")
    
    def map_biometric_to_color(self, value: float, 
                              min_val: float, max_val: float,
                              color_map: str = 'rainbow') -> Tuple[int, int, int]:
        """Map biometric value to RGB color with advanced color mapping"""
        # Normalize value to 0-1 range
        normalized = np.clip((value - min_val) / (max_val - min_val), 0, 1)
        
        if color_map == 'rainbow':
            # HSV to RGB conversion for smooth rainbow
            hue = normalized * 360
            rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
        elif color_map == 'heat':
            # Blue -> Green -> Yellow -> Red heat map
            if normalized < 0.25:
                r, g, b = 0, 0, int(255 * (normalized * 4))
            elif normalized < 0.5:
                r, g, b = 0, int(255 * ((normalized - 0.25) * 4)), 255
            elif normalized < 0.75:
                r, g, b = int(255 * ((normalized - 0.5) * 4)), 255, int(255 * (1 - (normalized - 0.5) * 4))
            else:
                r, g, b = 255, int(255 * (1 - (normalized - 0.75) * 4)), 0
            rgb = (r, g, b)
        elif color_map == 'brainwave':
            # Special mapping for brainwave states
            if normalized < 0.33:
                # Relaxed - blue tones
                rgb = (0, 0, int(255 * normalized * 3))
            elif normalized < 0.66:
                # Neutral - green tones
                rgb = (0, int(255 * (normalized - 0.33) * 3), 0)
            else:
                # Engaged - red tones
                rgb = (int(255 * (normalized - 0.66) * 3), 0, 0)
        else:
            # Default gradient: blue to red
            r = int(255 * normalized)
            b = int(255 * (1 - normalized))
            rgb = (r, 0, b)
            
        return rgb
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB color space"""
        h = h / 60.0
        c = v * s
        x = c * (1 - abs((h % 2) - 1))
        m = v - c
        
        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    async def animate_heart_rate(self, bpm: float, duration: float = 1.0):
        """Animate LEDs based on heart rate with pulse effect"""
        if self.animation_running:
            return
            
        self.animation_running = True
        
        # Map BPM to color (blue=calm, red=elevated)
        base_color = self.map_biometric_to_color(bpm, 50, 120, 'heat')
        
        # Calculate pulse frequency from BPM
        pulse_freq = bpm / 60.0  # Hz
        
        start_time = time.time()
        while (time.time() - start_time) < duration and self.animation_running:
            # Calculate pulse intensity
            elapsed = time.time() - start_time
            intensity = (np.sin(2 * np.pi * pulse_freq * elapsed) + 1) / 2
            
            # Apply intensity to all pixels with wave effect
            for i in range(self.num_pixels):
                # Create expanding wave from center
                center = self.num_pixels // 2
                distance = abs(i - center) / center
                pixel_intensity = intensity * (1 - distance * 0.5)
                
                # Apply color with intensity
                color = tuple(int(c * pixel_intensity) for c in base_color)
                self.current_colors[i] = color
                
                if self.hardware_mode:
                    self.pixels[i] = color
            
            if self.hardware_mode:
                self.pixels.show()
            
            await asyncio.sleep(0.016)  # ~60 FPS
        
        self.animation_running = False
    
    def visualize_eeg_bands(self, band_powers: Dict[str, Dict[str, float]]):
        """Visualize EEG frequency bands across LED strip with enhanced patterns"""
        # Divide strip into sections for each band
        bands = ['delta', 'theta', 'alpha', 'beta', 'gamma']
        section_size = self.num_pixels // len(bands)
        
        # Band-specific colors with enhanced palette
        band_colors = {
            'delta': (100, 0, 200),   # Purple
            'theta': (0, 0, 255),     # Blue
            'alpha': (0, 255, 255),   # Cyan
            'beta': (0, 255, 0),      # Green
            'gamma': (255, 100, 0)    # Orange
        }
        
        for i, band in enumerate(bands):
            start_idx = i * section_size
            end_idx = start_idx + section_size
            
            # Get average power across all channels
            powers = [band_powers.get(ch, {}).get(band, 0) 
                     for ch in ['TP9', 'AF7', 'AF8', 'TP10']]
            avg_power = np.mean(powers)
            
            # Map power to color intensity with logarithmic scaling
            intensity = np.clip(np.log10(avg_power + 1) / 3, 0, 1)  # Log scale
            
            base_color = band_colors.get(band, (255, 255, 255))
            color = tuple(int(c * intensity) for c in base_color)
            
            # Set section color with smooth transition
            for idx in range(start_idx, min(end_idx, self.num_pixels)):
                self.target_colors[idx] = color
                if self.hardware_mode:
                    self.pixels[idx] = color
        
        if self.hardware_mode:
            self.pixels.show()
    
    async def smooth_transition(self, target_colors: List[Tuple[int, int, int]], 
                              duration: float = 0.5, easing: str = 'ease_in_out'):
        """Smoothly transition to target colors with easing functions"""
        if self.animation_running:
            return
            
        self.animation_running = True
        steps = int(duration * 60)  # 60 FPS
        
        # Store current colors
        start_colors = self.current_colors.copy()
        
        # Interpolate over time
        for step in range(steps):
            t = step / steps
            
            # Apply easing function
            if easing == 'ease_in_out':
                t = 0.5 * (1 + np.sin((t * np.pi) - (np.pi/2)))
            elif easing == 'ease_in':
                t = t * t
            elif easing == 'ease_out':
                t = 1 - (1 - t) * (1 - t)
            
            for i in range(min(len(target_colors), self.num_pixels)):
                start = start_colors[i]
                target = target_colors[i]
                
                # Linear interpolation with easing
                interpolated = tuple(
                    int(start[j] + (target[j] - start[j]) * t)
                    for j in range(3)
                )
                self.current_colors[i] = interpolated
                
                if self.hardware_mode:
                    self.pixels[i] = interpolated
            
            if self.hardware_mode:
                self.pixels.show()
            
            await asyncio.sleep(1/60)
        
        self.animation_running = False
    
    def set_brain_state_colors(self, brain_state: str, attention_score: float, 
                              relaxation_score: float):
        """Set colors based on brain state with enhanced mapping"""
        if brain_state == "relaxed":
            # Blue tones for relaxed state with intensity based on relaxation score
            intensity = np.clip(relaxation_score, 0.3, 1.0)
            color = (0, 0, int(255 * intensity))
        elif brain_state == "engaged":
            # Red tones for engaged state with intensity based on attention score
            intensity = np.clip(attention_score, 0.3, 1.0)
            color = (int(255 * intensity), 0, 0)
        else:
            # Green tones for neutral state
            color = (0, 255, 0)
        
        # Apply color to all pixels
        for i in range(self.num_pixels):
            self.current_colors[i] = color
            if self.hardware_mode:
                self.pixels[i] = color
        
        if self.hardware_mode:
            self.pixels.show()
        
        logger.info(f"Set brain state colors: {brain_state} -> {color}")
    
    def create_wave_effect(self, base_color: Tuple[int, int, int], 
                          wave_speed: float = 1.0, wave_width: float = 0.3):
        """Create a moving wave effect across the LED strip"""
        if self.animation_running:
            return
            
        self.animation_running = True
        
        start_time = time.time()
        while self.animation_running:
            elapsed = time.time() - start_time
            
            for i in range(self.num_pixels):
                # Calculate wave position
                position = (i / self.num_pixels) + (wave_speed * elapsed)
                wave = np.sin(2 * np.pi * position) * 0.5 + 0.5
                
                # Apply wave intensity to color
                intensity = wave * wave_width + (1 - wave_width)
                color = tuple(int(c * intensity) for c in base_color)
                
                self.current_colors[i] = color
                if self.hardware_mode:
                    self.pixels[i] = color
            
            if self.hardware_mode:
                self.pixels.show()
            
            time.sleep(0.016)  # ~60 FPS
    
    def stop_animation(self):
        """Stop any running animations"""
        self.animation_running = False
    
    def get_simulation_display(self) -> str:
        """Get a text representation of current LED state for simulation mode"""
        if self.hardware_mode:
            return "Hardware mode - LEDs controlled directly"
        
        # Create a simple text representation
        display = []
        for i in range(0, self.num_pixels, 10):  # Show every 10th LED
            color = self.current_colors[i]
            r, g, b = color
            display.append(f"LED{i:02d}: RGB({r:3d},{g:3d},{b:3d})")
        
        return "\n".join(display)

# Test the enhanced controller
if __name__ == "__main__":
    import asyncio
    
    async def test_controller():
        """Test the enhanced LED controller"""
        controller = EnhancedLEDController(num_pixels=60)
        
        # Test brain state colors
        print("Testing brain state colors...")
        controller.set_brain_state_colors("relaxed", 0.3, 0.8)
        print(controller.get_simulation_display())
        
        await asyncio.sleep(1)
        
        controller.set_brain_state_colors("engaged", 0.9, 0.2)
        print(controller.get_simulation_display())
        
        await asyncio.sleep(1)
        
        # Test smooth transition
        print("Testing smooth transition...")
        target_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)] * 20
        await controller.smooth_transition(target_colors, duration=2.0)
        
        print("Enhanced LED controller test complete!")
    
    asyncio.run(test_controller()) 