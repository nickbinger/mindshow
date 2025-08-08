// Phase 4b: Example Pixelblaze Pattern with Perceptual Color Mood Slider
// This pattern demonstrates the hue range compression method from the Phase 4b research

// ===== Configuration =====
w = 8  // width of the 2D matrix
zigzag = true  // whether wiring is zigzag

// ===== Phase 4b: Color Mood Slider =====
// Exported variable for external control via WebSocket setVars()
// 0 = warm (reds/oranges), 1 = cool (blues/violets), 0.5 = neutral
export var colorMoodBias = 0.5

// Speed control (0 = slow, 1 = fast)
export var intensity = 0.5

// Optional: Slider UI in Pixelblaze interface
export function sliderColorMoodBias(v) {
    colorMoodBias = v
}

export function sliderIntensity(v) {
    intensity = v
}

// Color mood anchors and ranges (from Phase 4b research)
var warmAnchor = 0.0   // Red as base warm hue
var warmRange = 0.17   // Warm tones span (red to ~yellow, 60°)
var coolAnchor = 0.75  // Violet as end cool hue (270°)
var coolRange = 0.16   // Cool tones span (blue to violet, 60°)

// ===== Pattern Animation Variables =====
export function beforeRender(delta) {
    // Use intensity to control animation speed
    // Map intensity (0-1) to speed multiplier (0.5-1.5)
    // 0 = 50% normal speed, 1 = 150% normal speed
    var speedMultiplier = 0.5 + (intensity * 1.0)  // 0→0.5, 1→1.5
    
    tf = 5 * speedMultiplier  // Time factor for animation speed
    t1 = wave(time(0.15 * tf)) * PI2
    t2 = wave(time(0.19 * tf)) * PI2
    z = 2 + wave(time(0.1 * tf)) * 5
    t3 = wave(time(0.13 * tf))
    t4 = time(0.01 * tf)
}

// ===== Render Function with Phase 4b Color Mood =====
export function render(index) {
    // Compute 2D coordinates
    y = floor(index / w)
    x = index % w
    if (zigzag) {
        x = (y % 2 == 0) ? x : (w - 1 - x)
    }
    
    // Original plasma color calculations
    h = (1 + sin(x/w * z + t1) + cos(y/w * z + t2)) * 0.5
    v = wave(h + t4)
    v = v * v * v  // Cube for visual effect
    h = triangle(h % 1) / 2 + t3  // Triangle wave shaping
    
    // ===== Phase 4b: Apply Perceptual Color Mood Bias =====
    // Convert slider range [0,1] to bias range [-1,1]
    var bias = (colorMoodBias - 0.5) * 2
    
    if (bias < 0) {
        // Warm bias: compress hue range toward warmAnchor
        var t = -bias  // 0 to 1 as bias goes from 0 to -1
        var range = 1 - t * (1 - warmRange)
        // Map hue into [warmAnchor, warmAnchor + range]
        h = warmAnchor + (h % 1) * range
    } else if (bias > 0) {
        // Cool bias: compress hue range toward coolAnchor
        var t = bias  // 0 to 1 as bias goes from 0 to 1
        var range = 1 - t * (1 - coolRange)
        // Map hue into [coolAnchor - range, coolAnchor]
        h = coolAnchor - (1 - (h % 1)) * range
    }
    // If bias == 0 (neutral), hue remains unchanged
    
    // Output the color with perceptual mood bias applied
    hsv(h, 1, v)
}

// ===== Alternative Patterns to Test =====

// Simple rainbow sweep with color mood bias
export function render2D(index, x, y) {
    // Simple diagonal rainbow - FIXED: use w instead of width/height
    h = (x + y) / (w + w)  // Using w (8) instead of undefined width/height
    
    // Apply Phase 4b color mood bias
    var bias = (colorMoodBias - 0.5) * 2
    
    if (bias < 0) {
        var t = -bias
        var range = 1 - t * (1 - warmRange)
        h = warmAnchor + (h % 1) * range
    } else if (bias > 0) {
        var t = bias
        var range = 1 - t * (1 - coolRange)
        h = coolAnchor - (1 - (h % 1)) * range
    }
    
    hsv(h, 1, 0.8)
}

// ===== Usage Notes =====
// 1. The colorMoodBias variable can be controlled via WebSocket:
//    {"setVars": {"colorMoodBias": 0.2}}  // Warm bias
//    {"setVars": {"colorMoodBias": 0.8}}  // Cool bias
//
// 2. The intensity variable controls animation speed with improved precision:
//    - Range 0.25-0.75 maps to full speed range (0.1-3.0x)
//    - Values below 0.25 = minimum speed
//    - Values above 0.75 = maximum speed
//    {"setVars": {"intensity": 0.25}}  // Slowest
//    {"setVars": {"intensity": 0.75}}  // Fastest
//
// 3. The MindShow system automatically sets colorMoodBias based on:
//    - High attention (engaged) -> warm bias (reds/oranges)
//    - High relaxation -> cool bias (blues/violets)
//    - Neutral state -> balanced spectrum
//
// 3. The hue range compression ensures color variety even at extremes:
//    - Full warm (0.0): Shows only reds through yellows
//    - Full cool (1.0): Shows only blues through violets
//    - Neutral (0.5): Shows full rainbow spectrum
//
// 4. The implementation preserves relative color relationships within
//    the compressed range, maintaining visual interest
