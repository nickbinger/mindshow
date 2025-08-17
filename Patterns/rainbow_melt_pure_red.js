/*
  Rainbow melt with Pure Red Mode Slider
  
  This version properly transitions from full rainbow to pure red spectrum.
  
  The redMode slider (0-1) controls the transition:
  - At 0: Full rainbow spectrum
  - At 1: Pure red only (black to bright red variations)
  - In between: Smooth transition compressing toward red
*/

scale = pixelCount / 2

// Slider for red mode (0 = rainbow, 1 = pure red)
export var redMode = 0

export function sliderRedMode(v) {
  redMode = v
}

export function beforeRender(delta) {
  t1 = time(.1)  // Time it takes for regions to move and melt 
}

export function render(index) {
  c1 = 1 - abs(index - scale) / scale  // 0 at strip endpoints, 1 in the middle
  c2 = wave(c1)
  c3 = wave(c2 + t1)
  
  v = wave(c3 + t1)  // Separate the colors with dark regions
  v = v * v
  
  // Calculate the original hue for rainbow mode
  originalHue = c1 + t1
  
  // Smoothly transition from rainbow to pure red
  // At redMode = 0: use full hue range (0-1)
  // At redMode = 1: use only red (hue = 0)
  
  // Compress the hue range toward red as slider increases
  // This ensures at 100%, we only get red (hue very close to 0)
  maxHue = 1 - redMode  // At redMode=1, maxHue=0 (only red)
  
  // Scale the original hue by the allowed range
  finalHue = (originalHue % 1) * maxHue
  
  // At high red mode, we can also vary saturation for more red variety
  // This creates deeper reds vs bright reds
  if (redMode > 0.8) {
    // Add some saturation variation when mostly red
    satVariation = 0.3 + 0.7 * wave(c1 * 3 + t1)
    finalSaturation = satVariation
  } else {
    finalSaturation = 1
  }
  
  hsv(finalHue, finalSaturation, v)
}