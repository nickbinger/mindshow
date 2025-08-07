# 🌈 Continuous Color Mood Mapping

## Overview

The **Continuous Color Mood Mapping** enhancement for Phase 4b creates smooth, natural transitions in LED color temperature based on real-time brainwave data. Unlike discrete state changes, this system provides a fluid, responsive experience that mirrors the continuous nature of human consciousness.

## 🧠 How It Works

### Core Algorithm

```python
# 1. Weighted Contributions
attention_contribution = (attention - 0.5) * -0.4  # Higher attention → warmer
relaxation_contribution = (relaxation - 0.5) * 0.4  # Higher relaxation → cooler

# 2. Dynamic Intensity
engagement_level = (attention + relaxation) / 2
intensity = 0.5 + engagement_level * 0.5  # Scale based on overall engagement

# 3. Calculate Raw Color Mood
raw_color_mood = 0.5 + (attention_contribution + relaxation_contribution) * intensity

# 4. Apply Perceptual Smoothing
# S-curve easing for natural perception
if raw_color_mood < 0.5:
    eased_color_mood = 0.5 * pow(raw_color_mood * 2, 2)
else:
    eased_color_mood = 1.0 - 0.5 * pow((1.0 - raw_color_mood) * 2, 2)

# 5. Temporal Smoothing
smoothed_color_mood = α * new + (1-α) * previous  # Exponential moving average
```

### Key Features

1. **Continuous Updates**: Color mood updates every 100ms (10Hz) regardless of brain state changes
2. **Temporal Smoothing**: Exponential moving average reduces jitter while maintaining responsiveness
3. **Dynamic Intensity**: Overall engagement level scales the color shift intensity
4. **Perceptual Easing**: S-curve mapping creates more natural transitions

## 🎨 Color Mood Scale

| Value | Range | Visual | Description |
|-------|-------|--------|-------------|
| 0.0-0.2 | Very Warm | 🔥🔥🔥 | Deep reds/oranges (high focus) |
| 0.2-0.4 | Warm | 🔥🔥 | Reds to yellows (engaged) |
| 0.4-0.6 | Neutral | 🌈 | Full spectrum (balanced) |
| 0.6-0.8 | Cool | ❄️❄️ | Blues to greens (relaxed) |
| 0.8-1.0 | Very Cool | ❄️❄️❄️ | Deep blues/violets (deep calm) |

## 🔧 Configuration Parameters

```python
# In MindShowConfig:
color_mood_smoothing: float = 0.3      # Temporal smoothing (0-1, higher = more smooth)
color_mood_intensity_scale: float = 0.5 # Base intensity for shifts
color_mood_attention_weight: float = 0.4 # Attention → warm mapping strength
color_mood_relaxation_weight: float = 0.4 # Relaxation → cool mapping strength
```

### Tuning Guide

- **Smoothing Factor** (0.1-0.5):
  - Lower (0.1): More responsive, may show jitter
  - Higher (0.5): Smoother transitions, less responsive
  - Default (0.3): Good balance

- **Intensity Scale** (0.3-0.7):
  - Lower: Subtle color shifts
  - Higher: More dramatic shifts
  - Adjust based on user preference

- **Weight Parameters** (0.2-0.6):
  - Control how strongly each brainwave type affects color
  - Can create asymmetric responses (e.g., stronger warm shifts)

## 📊 Implementation Details

### Update Flow

1. **Brain data arrives** → Extract attention/relaxation scores
2. **Calculate contributions** → Apply weighted mappings
3. **Scale by engagement** → More engaged = stronger shifts
4. **Apply easing curve** → Perceptual smoothness
5. **Temporal smoothing** → Reduce jitter
6. **Send to Pixelblaze** → Update `colorMoodBias` variable

### Pattern Compatibility

Any Pixelblaze pattern that implements the Phase 4b color mood API will work:

```javascript
// In Pixelblaze pattern:
export var colorMoodBias = 0.5  // Receives continuous updates

// Apply hue range compression based on colorMoodBias
// See phase4b_example_pattern.js for implementation
```

## 🧪 Testing

Use the provided test script to see continuous color mood in action:

```bash
python test_continuous_color_mood.py
```

This simulates varying brainwave data and shows smooth transitions through the color temperature spectrum.

## 🎯 Benefits

1. **Natural Experience**: Mirrors the continuous nature of mental states
2. **Responsive Feedback**: Immediate visual response to mental changes
3. **Reduced Jarring**: No sudden pattern switches during minor fluctuations
4. **Enhanced Immersion**: Creates a more connected brain-to-light experience
5. **Customizable**: Easily tuned for different users and contexts

## 🚀 Future Enhancements

- **Adaptive Learning**: Adjust parameters based on user patterns
- **Multi-dimensional Mapping**: Include other EEG features (alpha, theta waves)
- **Context Awareness**: Different mappings for meditation vs focus sessions
- **Color Palette Modes**: Support different color schemes beyond warm-cool
