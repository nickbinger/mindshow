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
    // Use intensity to control animation speed with improved precision
    // Map intensity (0.25-0.75) to speed multiplier (0.1-3.0)
    var normalizedIntensity = (intensity - 0.25) / 0.5  // Map 0.25-0.75 to 0-1
    normalizedIntensity = clamp(normalizedIntensity, 0, 1)  // Clamp to valid range
    var speedMultiplier = 0.1 + (normalizedIntensity * 2.9)
    
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
