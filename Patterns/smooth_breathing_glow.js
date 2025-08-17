/*
  Smooth Breathing Glow - Blue to Purple to Red
  
  An even gentler pattern that creates a breathing/pulsing effect
  across the LED strip. Color transitions from dark blue through purple to red.
  
  Designed for non-jarring, meditative visualization.
*/

// Slider for color transition (0 = dark blue, 0.5 = purple, 1 = red)
export var colorBlend = 0  // Default to dark blue

export function sliderColorBlend(v) {
  colorBlend = v
}

// Slider for breathing speed (0 = very slow, 1 = faster)
export var speedControl = 0.2  // Default to slow

export function sliderSpeedControl(v) {
  speedControl = v
}

export function beforeRender(delta) {
  // Map speed control to actual speed (0.005 = very slow, 0.1 = faster)
  breathSpeed = 0.005 + speedControl * 0.095
  
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
  
  // Map slider to color transition
  // 0 = dark blue (hue ~0.6), 0.5 = purple (hue ~0.83), 1 = red (hue ~0)
  if (colorBlend <= 0.5) {
    // Transition from dark blue to purple
    // Blue is at 0.6, purple is at 0.83
    t = colorBlend * 2  // Map 0-0.5 to 0-1
    hue = 0.6 + t * 0.23  // Interpolate from 0.6 to 0.83
  } else {
    // Transition from purple to red
    // Purple is at 0.83, red is at 0 (or 1)
    t = (colorBlend - 0.5) * 2  // Map 0.5-1 to 0-1
    hue = 0.83 + t * 0.17  // Interpolate from 0.83 to 1 (which wraps to red)
  }
  
  // Pure color, no desaturation
  hsv(hue, 1, brightness)
}