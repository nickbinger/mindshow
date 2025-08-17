/*
  Liquid Color Flow - Smooth Speed Changes
  
  This version uses accumulated phase instead of time() function
  to prevent jarring jumps when changing speed.
  
  The animation phase accumulates based on speed, so changing
  speed affects how fast we add to phase, not the current position.
*/

// Slider for color hue (0 = red through spectrum)
export var baseHue = 0

export function sliderBaseHue(v) {
  baseHue = v
}

// Slider for flow speed
export var flowSpeed = 0.5  // 0-1 range, 0.5 is medium

export function sliderFlowSpeed(v) {
  flowSpeed = v
}

// Phase accumulators for smooth speed changes
var phase1 = 0
var phase2 = 0
var phase3 = 0

// Smooth speed interpolation
var currentSpeed = 0.02
var targetSpeed = 0.02

export function beforeRender(delta) {
  // Map flowSpeed slider to actual speed (0.001 to 0.1)
  targetSpeed = 0.001 + flowSpeed * flowSpeed * 0.099
  
  // Smoothly interpolate current speed toward target
  currentSpeed = currentSpeed * 0.95 + targetSpeed * 0.05
  
  // Accumulate phase based on current speed
  // delta is in milliseconds, convert to reasonable phase increment
  phaseIncrement = currentSpeed * delta * 0.001
  
  phase1 += phaseIncrement
  phase2 += phaseIncrement * 0.6
  phase3 += phaseIncrement * 1.3
  
  // Keep phases in 0-1 range
  phase1 = phase1 % 1
  phase2 = phase2 % 1
  phase3 = phase3 % 1
}

export function render(index) {
  // Normalized position
  pos = index / pixelCount
  
  // Create multiple layers using accumulated phases
  layer1 = (1 + cos(pos * PI2 * 1.5 + phase1 * PI2)) / 2
  layer2 = (1 + sin(pos * PI2 * 2.2 - phase2 * PI2)) / 2  
  layer3 = (1 + cos(pos * PI2 * 0.8 + phase3 * PI2)) / 2
  
  // Blend layers with different weights
  blended = layer1 * 0.4 + layer2 * 0.35 + layer3 * 0.25
  
  // Smooth curve to create nice black regions
  brightness = blended * blended * blended * 0.7
  
  // Always full saturation for pure color
  hsv(baseHue, 1, brightness)
}