/*
  Smooth Color Waves
  
  A gentle, slow-moving pattern that creates smooth waves of a single color
  fading from black to the target color. No jumps, no white oversaturation.
  
  The colorHue slider controls which color to use:
  - 0 = Red
  - 0.33 = Green  
  - 0.66 = Blue
  - etc.
*/

// Slider for color selection (0-1 maps to hue wheel)
export var colorHue = 0  // Default to red

export function sliderColorHue(v) {
  colorHue = v
}

// Speed control
var speed = 0.03  // Much slower for smooth, relaxing motion

export function beforeRender(delta) {
  t1 = time(speed)  // Primary wave
  t2 = time(speed * 0.7)  // Secondary wave at different speed
}

export function render(index) {
  // Create position-based waves
  position = index / pixelCount
  
  // Layer multiple sine waves for organic motion
  // Using sine instead of wave() for smoother transitions
  wave1 = (1 + sin(position * PI2 + t1 * PI2)) / 2
  wave2 = (1 + sin(position * PI2 * 1.5 - t2 * PI2)) / 2
  
  // Combine waves with different weights for complexity
  combined = wave1 * 0.7 + wave2 * 0.3
  
  // Apply smoothing curve to prevent harsh transitions
  // This creates gentle fades from black to color
  brightness = combined * combined * 0.8  // Max 0.8 to avoid white
  
  // Full saturation for pure colors, no white mixing
  hsv(colorHue, 1, brightness)
}