/*
  Smooth Breathing Glow
  
  An even gentler pattern that creates a breathing/pulsing effect
  across the LED strip. Single color gradient from black to color.
  
  Designed for non-jarring, meditative visualization.
*/

// Slider for color selection (0 = red, moving through spectrum)
export var colorHue = 0  // Default to red

export function sliderColorHue(v) {
  colorHue = v
}

// Very slow for breathing effect
var breathSpeed = 0.02

export function beforeRender(delta) {
  // Single time base for unified breathing
  breathTime = time(breathSpeed)
  
  // Create a breathing curve (in and out)
  // Using sin for ultra-smooth transitions
  globalBreath = (1 + sin(breathTime * PI2)) / 2
}

export function render(index) {
  // Spatial variation across the strip
  position = index / pixelCount
  
  // Create a spatial wave that moves slowly
  spatialWave = (1 + sin(position * PI2 * 2 + breathTime * PI2)) / 2
  
  // Combine global breathing with spatial variation
  // More weight on breathing for unified effect
  intensity = globalBreath * 0.6 + spatialWave * 0.4
  
  // Apply a curve to keep things in the lower brightness range
  // This prevents white oversaturation and keeps it moody
  brightness = intensity * intensity * 0.6
  
  // Pure color, no desaturation
  hsv(colorHue, 1, brightness)
}