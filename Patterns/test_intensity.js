// Simple test pattern for intensity control
// This pattern should show clear speed changes with intensity

export var colorMoodBias = 0.5
export var intensity = 0.5

export function sliderColorMoodBias(v) {
    colorMoodBias = v
}

export function sliderIntensity(v) {
    intensity = v
}

export function beforeRender(delta) {
    // Use intensity to control animation speed
    // Map intensity (0-1) to speed multiplier (0.5-1.5)
    // 0 = 50% normal speed (slow), 1 = 150% normal speed (fast)
    var speedMultiplier = 0.5 + (intensity * 1.0)  // 0→0.5, 1→1.5
    
    tf = 5 * speedMultiplier
}

export function render(index) {
    // Simple moving dot pattern
    var pos = (index + time(tf) * 64) % 64
    var brightness = index == pos ? 1 : 0.1
    
    // Use colorMoodBias for hue
    var hue = colorMoodBias
    
    hsv(hue, 1, brightness)
}
