/*
  Rainbow melt with Red Blend Slider
  
  Alternative approach: Instead of shifting hue, this blends the original
  rainbow colors with pure red using RGB mixing for ultra-smooth transitions.
  
  The redBlend slider (0-1) controls the mix:
  - At 0: Pure rainbow
  - At 1: Rainbow tinted heavily with red
*/

scale = pixelCount / 2

// Slider for red blend amount (0 = pure rainbow, 1 = heavily red-tinted)
export var redBlend = 0

export function sliderRedBlend(v) {
  redBlend = v
}

// HSV to RGB conversion helper
function hsv2rgb(h, s, v, rgb) {
  var r, g, b, i, f, p, q, t
  
  i = floor(h * 6)
  f = h * 6 - i
  p = v * (1 - s)
  q = v * (1 - f * s)
  t = v * (1 - (1 - f) * s)
  
  switch (i % 6) {
    case 0: r = v; g = t; b = p; break
    case 1: r = q; g = v; b = p; break
    case 2: r = p; g = v; b = t; break
    case 3: r = p; g = q; b = v; break
    case 4: r = t; g = p; b = v; break
    case 5: r = v; g = p; b = q; break
  }
  
  rgb[0] = r
  rgb[1] = g
  rgb[2] = b
}

var tempRgb = array(3)

export function beforeRender(delta) {
  t1 = time(.1)  // Time it takes for regions to move and melt 
}

export function render(index) {
  c1 = 1 - abs(index - scale) / scale  // 0 at strip endpoints, 1 in the middle
  c2 = wave(c1)
  c3 = wave(c2 + t1)
  
  v = wave(c3 + t1)  // Separate the colors with dark regions
  v = v * v
  
  // Calculate the original rainbow color
  originalHue = c1 + t1
  
  // Convert HSV to RGB for blending
  hsv2rgb(originalHue, 1, v, tempRgb)
  
  // Blend with red (1, 0, 0) based on redBlend amount
  // This creates a smooth tinting effect without jarring transitions
  r = tempRgb[0] * (1 - redBlend * 0.5) + v * redBlend * 0.5
  g = tempRgb[1] * (1 - redBlend * 0.7)
  b = tempRgb[2] * (1 - redBlend * 0.7)
  
  // Ensure values stay in valid range
  r = min(1, r)
  g = max(0, g)
  b = max(0, b)
  
  rgb(r, g, b)
}