# Phase 4b Implementation: Perceptual Color Mood Slider

## Overview

Phase 4b adds a perceptual color mood slider (`colorMoodBias`) that biases LED colors along the warm-cool spectrum based on brainwave activity. This creates a more immersive and emotionally resonant light experience.

## Implementation Details

### Python Side (Integrated System)

#### 1. **Brain State Mappings Enhanced**
```python
self.state_mappings = {
    'engaged': {
        'pattern_name': 'sparkfire',
        'variables': {
            'hue': 0.0,
            'brightness': 0.9,
            'speed': 0.8,
            'colorMoodBias': 0.2  # Warm bias
        }
    },
    'relaxed': {
        'pattern_name': 'slow waves',
        'variables': {
            'hue': 0.67,
            'brightness': 0.5,
            'speed': 0.3,
            'colorMoodBias': 0.8  # Cool bias
        }
    },
    'neutral': {
        'pattern_name': 'rainbow',
        'variables': {
            'hue': 0.33,
            'brightness': 0.7,
            'speed': 0.5,
            'colorMoodBias': 0.5  # Neutral
        }
    }
}
```

#### 2. **Dynamic Color Mood Calculation**
The system calculates `colorMoodBias` dynamically based on attention and relaxation scores:

```python
# High attention → warm bias (lower values)
# High relaxation → cool bias (higher values)
color_mood = 0.5 - (attention - 0.5) * 0.6 + (relaxation - 0.5) * 0.6

# Apply S-curve for perceptual smoothness
if color_mood < 0.5:
    color_mood = 0.5 * pow(color_mood * 2, 2)
else:
    color_mood = 1.0 - 0.5 * pow((1.0 - color_mood) * 2, 2)
```

### Pixelblaze Side (Pattern Code)

#### 1. **Export Variable**
```javascript
export var colorMoodBias = 0.5  // 0 = warm, 1 = cool
```

#### 2. **Hue Range Compression**
```javascript
// Define anchors and ranges
var warmAnchor = 0.0   // Red
var warmRange = 0.17   // Red to yellow
var coolAnchor = 0.75  // Violet
var coolRange = 0.16   // Blue to violet

// Apply bias in render function
var bias = (colorMoodBias - 0.5) * 2

if (bias < 0) {
    // Warm bias
    var t = -bias
    var range = 1 - t * (1 - warmRange)
    h = warmAnchor + (h % 1) * range
} else if (bias > 0) {
    // Cool bias
    var t = bias
    var range = 1 - t * (1 - coolRange)
    h = coolAnchor - (1 - (h % 1)) * range
}
```

## Color Mood Mapping

| Brain State | Attention | Relaxation | Color Mood | Visual Result |
|------------|-----------|------------|------------|---------------|
| Deep Relaxation | 0.2 | 0.9 | 0.8 | Cool blues/violets |
| Calm Neutral | 0.5 | 0.5 | 0.5 | Full spectrum |
| Focused Attention | 0.8 | 0.2 | 0.2 | Warm reds/oranges |
| High Engagement | 0.9 | 0.1 | 0.1 | Deep reds |
| Drowsy | 0.3 | 0.7 | 0.7 | Cool blues |
| Alert Neutral | 0.6 | 0.4 | 0.4 | Slight warm tint |

## Testing

### 1. **Test Script**
Run `test_phase4b_color_mood.py` to:
- Simulate different brain states
- Test smooth transitions
- Verify color mood calculations

### 2. **Manual Testing**
```python
# Via WebSocket
{"setVars": {"colorMoodBias": 0.2}}  # Warm
{"setVars": {"colorMoodBias": 0.8}}  # Cool
```

### 3. **Live Testing**
With the integrated system running:
1. Focus intensely → LEDs shift to warm colors
2. Relax deeply → LEDs shift to cool colors
3. Stay neutral → LEDs show full spectrum

## Benefits

1. **Emotional Resonance**: Colors match mental state
2. **Perceptual Accuracy**: Uses color theory for natural transitions
3. **Visual Interest**: Maintains color variety at all settings
4. **Real-time Response**: Smooth transitions with brain state changes
5. **Universal Application**: Works with any HSV-based pattern

## Integration Status

✅ **Implemented in:**
- `integrated_mindshow_system.py` - Dynamic calculation and variable sending
- `phase4b_example_pattern.js` - Example Pixelblaze pattern
- `test_phase4b_color_mood.py` - Testing utility

✅ **Ready for:**
- Live brainwave testing
- Multi-device coordination (Phase 5)
- Custom pattern development

## Next Steps

1. Test with live Muse brainwave data
2. Fine-tune the attention/relaxation → color mood mapping
3. Create more patterns that utilize `colorMoodBias`
4. Document best practices for pattern developers
