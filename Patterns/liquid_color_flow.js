/*
  Liquid Color Flow
  
  Smooth, liquid-like motion in a single color.
  Creates flowing regions of black to color intensity.
  
  Perfect base for adding a color control slider without jarring transitions.
*/

// Slider for color hue (0 = red through spectrum)
export var baseHue = 0

export function sliderBaseHue(v) {
  baseHue = v
}

// Slider for flow speed
export var flowSpeed = 0.02

export function sliderFlowSpeed(v) {
  flowSpeed = v * 0.1  // Scale to reasonable range
}

export function beforeRender(delta) {
  t1 = time(flowSpeed)
  t2 = time(flowSpeed * 0.6)  // Different speed for layering
  t3 = time(flowSpeed * 1.3)  // Third layer
}

export function render(index) {
  // Normalized position
  pos = index / pixelCount
  
  // Create multiple layers of smooth waves
  // Using cosine for different phase
  layer1 = (1 + cos(pos * PI2 * 1.5 + t1 * PI2)) / 2
  layer2 = (1 + sin(pos * PI2 * 2.2 - t2 * PI2)) / 2  
  layer3 = (1 + cos(pos * PI2 * 0.8 + t3 * PI2)) / 2
  
  // Blend layers with different weights
  blended = layer1 * 0.4 + layer2 * 0.35 + layer3 * 0.25
  
  // Smooth curve to create nice black regions
  // Power of 3 creates deeper blacks and smoother gradients
  brightness = blended * blended * blended * 0.7
  
  // Always full saturation for pure color
  hsv(baseHue, 1, brightness)
}