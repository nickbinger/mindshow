/*
  Rainbow melt with Red Hue Addition Slider
  
  Based on the rainbow melt pattern, but adds a slider that smoothly
  blends in red hue without jarring transitions.
  
  The redInfluence slider (0-1) controls how much the pattern shifts toward red:
  - At 0: Normal rainbow behavior
  - At 1: Heavily red-shifted rainbow
*/

scale = pixelCount / 2

// Slider for red influence (0 = normal rainbow, 1 = heavy red shift)
export var redInfluence = 0

export function sliderRedInfluence(v) {
  redInfluence = v
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
  
  // Calculate the original hue
  originalHue = c1 + t1
  
  // At redInfluence = 0: full rainbow (originalHue)
  // At redInfluence = 1: pure red (hue = 0)
  // We need to interpolate the hue AND reduce saturation variance
  
  if (redInfluence < 1) {
    // Blend between rainbow and red
    // As we approach 1, we want to converge all hues to 0 (red)
    finalHue = originalHue * (1 - redInfluence)
    
    // Keep full saturation for colors
    finalSaturation = 1
  } else {
    // At full red influence, only show red (hue = 0)
    finalHue = 0
    
    // Use saturation to create variation instead of hue
    // This gives us black -> dark red -> bright red variations
    finalSaturation = 1
  }
  
  // Brightness stays controlled by the wave pattern
  finalBrightness = v
  
  hsv(finalHue, finalSaturation, finalBrightness)
}