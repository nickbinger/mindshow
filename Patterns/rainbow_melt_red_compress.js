/*
  Rainbow melt with Red Compression Slider
  
  This version compresses the hue range toward red as the slider increases,
  creating a smooth transition from full rainbow to red-dominant spectrum.
  
  The redCompress slider (0-1) controls the compression:
  - At 0: Full rainbow spectrum (hue 0-1)
  - At 1: Compressed spectrum centered on red (narrow hue range around 0)
*/

scale = pixelCount / 2

// Slider for red compression (0 = full rainbow, 1 = compressed to red)
export var redCompress = 0

export function sliderRedCompress(v) {
  redCompress = v
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
  
  // Calculate the base hue
  baseHue = c1 + t1
  
  // Compress the hue range based on redCompress
  // At redCompress = 0: hue ranges from 0 to 1 (full spectrum)
  // At redCompress = 1: hue ranges from 0 to ~0.2 (red to orange-yellow)
  // This creates smooth transitions without jarring jumps
  
  // Map the full range to a compressed range
  hueRange = 1 - redCompress * 0.85  // At max compression, use only 15% of spectrum
  
  // Apply compression while keeping red (0) as the anchor point
  compressedHue = (baseHue % 1) * hueRange
  
  // Add a slight warmth boost to saturation when compressed
  saturation = 1 - redCompress * 0.05
  
  // Slightly boost brightness for warmer feel
  brightness = v * (1 + redCompress * 0.1)
  brightness = min(1, brightness)
  
  hsv(compressedHue, saturation, brightness)
}