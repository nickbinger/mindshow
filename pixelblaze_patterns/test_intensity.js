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
    var speedMultiplier = 0.1 + (intensity * 2.9)
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
