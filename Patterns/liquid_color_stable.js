/*
  Liquid Color Flow - Ultra Stable Version
  
  This version removes the speed slider entirely and instead
  uses the color slider to smoothly blend between rainbow and red modes.
  This avoids ALL jarring transitions.
*/

// Slider that blends from rainbow (0) to pure red (1)
export var redAmount = 0

export function sliderRedAmount(v) {
  redAmount = v
}

// Fixed smooth speed
var speed = 0.02

// Phase accumulators
var phase1 = 0
var phase2 = 0
var phase3 = 0

export function beforeRender(delta) {
  // Accumulate phase at constant speed
  phaseIncrement = speed * delta * 0.001
  
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
  
  // Blend layers
  blended = layer1 * 0.4 + layer2 * 0.35 + layer3 * 0.25
  
  // Smooth brightness curve
  brightness = blended * blended * blended * 0.7
  
  // Color logic: blend from rainbow to red based on slider
  if (redAmount == 0) {
    // Full rainbow mode - use position and time for hue
    hue = (pos + phase1) % 1
  } else if (redAmount == 1) {
    // Pure red mode
    hue = 0
  } else {
    // Blend between rainbow and red
    rainbowHue = (pos + phase1) % 1
    // Compress hue range toward red as slider increases
    hue = rainbowHue * (1 - redAmount)
  }
  
  hsv(hue, 1, brightness)
}