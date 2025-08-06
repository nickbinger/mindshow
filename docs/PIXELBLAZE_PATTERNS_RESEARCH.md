# PixelblazePatterns Research Documentation

*Based on analysis of [zranger1/PixelblazePatterns](https://github.com/zranger1/PixelblazePatterns) repository*

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Pattern Categories](#pattern-categories)
3. [Key Pattern Analysis](#key-pattern-analysis)
4. [Advanced Techniques](#advanced-techniques)
5. [Integration Patterns](#integration-patterns)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)
8. [Performance Optimization](#performance-optimization)
9. [Biometric Integration Opportunities](#biometric-integration-opportunities)
10. [Implementation Guide](#implementation-guide)

---

## Repository Overview

The [PixelblazePatterns](https://github.com/zranger1/PixelblazePatterns) repository contains **139+ patterns** created by ZRanger1, a leading expert in Pixelblaze development. This is the most comprehensive collection of production-ready patterns available.

### Repository Structure
```
PixelblazePatterns/
├── 1D/                    # Linear strip patterns
├── 2D_and_3D/            # Matrix and volumetric patterns
├── Experimental/          # Work-in-progress patterns
├── LuxLavalier/          # Specialized patterns
├── Multisegment/         # Multi-segment patterns
└── Toolkit/              # Utility patterns and tools
```

### Key Statistics
- **53 stars** - Highly regarded by the community
- **139 commits** - Active development
- **98.4% JavaScript** - Pixelblaze pattern language
- **1.6% Python** - Supporting tools and utilities

---

## Pattern Categories

### 1. 1D Patterns (Linear Strips)

**Purpose**: Patterns designed for linear LED strips, perfect for our initial testing.

**Key Patterns**:
- `cellularautomata1d.js` - Star Trek-style computer lights
- `midpointdisplacement1d.js` - Organic plasma effects
- `hypersnow.js` - Relaxing random flashes
- `darkbolt.js` - Accelerating darkness bolts
- `badfluorescent.js` - Failing fluorescent simulation

**Biometric Integration Potential**:
- **Cellular automata** - Could respond to brainwave complexity
- **Plasma effects** - Smooth transitions for mood changes
- **Random flashes** - Intensity based on attention levels

### 2. 2D and 3D Patterns (Matrix/Volumetric)

**Purpose**: Complex patterns for 2D LED matrices and 3D volumetric displays.

**Key Patterns**:
- `matrixgreenwaterfall.js` - Matrix-style waterfall
- `spinwheel2d.js` - Colorful radial spinner
- `rgbplasma2d.js` - Bright color plasma
- `nbodygravity2D.js` - Gravity simulation
- `conwaysllife2d.js` - Game of Life cellular automaton
- `mandelbrot2D.js` - Animated Mandelbrot set
- `bouncer3D.js` - Bouncing balls (2D/3D)

**Biometric Integration Potential**:
- **Gravity simulation** - Particle count based on engagement
- **Cellular automata** - Rule changes based on brainwave patterns
- **Mandelbrot zoom** - Speed based on attention levels

### 3. Experimental Patterns

**Purpose**: Cutting-edge patterns and research projects.

**Key Patterns**:
- `voronoimix2D.js` - Animated Voronoi patterns
- `rule30flasher.js` - Random bit generation
- `linesplash.js` - Wave simulation
- `oasis.js` - Peaceful light dances

**Biometric Integration Potential**:
- **Voronoi patterns** - Cell density based on brainwave complexity
- **Wave simulation** - Wave frequency based on relaxation
- **Oasis effects** - Color palette based on mood

### 4. Multisegment Patterns

**Purpose**: Advanced patterns for complex LED installations.

**Key Patterns**:
- `multisegmentforautomation.js` - Home automation version
- `multisegmentdemo.js` - Demonstration version

**Biometric Integration Potential**:
- **Segment control** - Different segments for different brainwave bands
- **Automation integration** - Combine with MQTT for remote control

### 5. Toolkit Patterns

**Purpose**: Utility patterns and synchronization tools.

**Key Patterns**:
- `gpiosynchronizer.js` - Synchronize multiple Pixelblazes
- Various utility functions

**Biometric Integration Potential**:
- **Multi-device sync** - Synchronize multiple LED installations
- **Distributed control** - Control multiple devices from single brainwave source

---

## Key Pattern Analysis

### 1. Matrix Green Waterfall (`matrixgreenwaterfall.js`)

**Description**: Basic green "The Matrix"-style waterfall display adapted for 2D LED displays.

**Key Features**:
- Fast and lightweight
- Usable as background or texture
- Green color scheme
- Waterfall animation

**Biometric Integration**:
```javascript
// Potential modifications for biometric control
export function render(index) {
    // Original matrix waterfall code
    // ... existing code ...
    
    // Add biometric control
    h = triangle(h%1)/2 + t3 + (attention_score * 0.1)  // Speed based on attention
    v = wave(h + t4) * (0.5 + relaxation_score * 0.5)   // Brightness based on relaxation
    
    hsv(h,1,v)
}
```

### 2. Spinwheel 2D (`spinwheel2d.js`)

**Description**: Fast, colorful, flowerlike radial spinner with complex waveforms.

**Key Features**:
- Complex waveform combinations
- Radial animation
- Colorful effects
- Unpredictable patterns

**Biometric Integration**:
```javascript
// Potential modifications for biometric control
export function beforeRender(delta) {
    // Original spinwheel code
    // ... existing code ...
    
    // Add biometric speed control
    tf = 5 * (0.8 + attention_score * 0.4)  // Speed range: 80%-120%
    
    // Add biometric color control
    base_hue = relaxation_score * 0.33  // ROYGBIV spectrum
}
```

### 3. N-Body Gravity 2D (`nbodygravity2D.js`)

**Description**: 2D n-body gravity simulator with particle dynamics.

**Key Features**:
- Physics simulation
- Particle system
- Collapse and merge dynamics
- Gravity control

**Biometric Integration**:
```javascript
// Potential modifications for biometric control
export function beforeRender(delta) {
    // Original gravity simulation code
    // ... existing code ...
    
    // Add biometric particle control
    particle_count = 10 + Math.floor(attention_score * 20)  // 10-30 particles
    
    // Add biometric gravity control
    gravity_strength = 0.5 + relaxation_score * 0.5  // Gravity based on relaxation
}
```

### 4. Cellular Automata 1D (`cellularautomata1d.js`)

**Description**: Elementary cellular automata rendering with Star Trek-style effects.

**Key Features**:
- Cellular automaton rules
- Linear strip optimization
- Computer-like blinking
- Rule-based patterns

**Biometric Integration**:
```javascript
// Potential modifications for biometric control
export function beforeRender(delta) {
    // Original cellular automata code
    // ... existing code ...
    
    // Add biometric rule control
    rule_number = 30 + Math.floor(attention_score * 100)  // Rule 30-130
    
    // Add biometric speed control
    update_rate = 0.1 + relaxation_score * 0.2  // Speed based on relaxation
}
```

### 5. Oasis (`oasis.js`)

**Description**: Peaceful light dances on waves of green and blue.

**Key Features**:
- Calming effects
- Wave-based animation
- Green/blue color palette
- Relaxing patterns

**Biometric Integration**:
```javascript
// Potential modifications for biometric control
export function render(index) {
    // Original oasis code
    // ... existing code ...
    
    // Add biometric color control
    if (attention_score > 0.7) {
        // Engaged: More red/orange
        h = 0.0 + (attention_score - 0.7) * 0.1
    } else if (relaxation_score > 0.6) {
        // Relaxed: More blue/purple
        h = 0.66 + relaxation_score * 0.33
    } else {
        // Neutral: Green/blue
        h = 0.33
    }
    
    hsv(h, 1, v)
}
```

---

## Advanced Techniques

### 1. Waveform Combinations

**Pattern**: `spinwheel2d.js`

**Technique**: Combining simple waveforms to create complex, unpredictable patterns.

```javascript
export function beforeRender(delta) {
    tf = 5
    t1 = wave(time(.15*tf))*PI2
    t2 = wave(time(.19*tf))*PI2
    z = 2+wave(time(.1*tf))*5
    t3 = wave(time(.13*tf))
    t4 = (time(.01*tf))
}
```

**Biometric Application**:
- Use attention score to control waveform frequencies
- Use relaxation score to control waveform amplitudes
- Create mood-responsive complex patterns

### 2. Physics Simulation

**Pattern**: `nbodygravity2D.js`

**Technique**: Real-time physics simulation with particle systems.

```javascript
// Particle physics simulation
for (i = 0; i < particle_count; i++) {
    // Calculate forces between particles
    // Update positions and velocities
    // Handle collisions and merging
}
```

**Biometric Application**:
- Particle count based on attention level
- Gravity strength based on relaxation
- Collision behavior based on brainwave complexity

### 3. Cellular Automata

**Pattern**: `cellularautomata1d.js`

**Technique**: Rule-based pattern generation with mathematical precision.

```javascript
// Cellular automaton rule application
function applyRule(left, center, right) {
    // Apply rule 30 or other rules
    return (left + center*2 + right*4) & 1
}
```

**Biometric Application**:
- Rule selection based on attention patterns
- Update rate based on relaxation
- Pattern complexity based on brainwave bands

### 4. Color Palette Control

**Pattern**: `oasis.js`

**Technique**: Smooth color transitions and palette management.

```javascript
// Color palette control
h = triangle(h%1)/2 + t3
v = wave(h + t4)
v = v*v*v  // Gamma correction
hsv(h, 1, v)
```

**Biometric Application**:
- ROYGBIV spectrum mapping to mood
- Saturation based on attention intensity
- Brightness based on relaxation level

---

## Integration Patterns

### 1. Biometric Speed Control

**Pattern**: Any pattern with timing variables

**Implementation**:
```javascript
export function beforeRender(delta) {
    // Base timing
    base_speed = 1.0
    
    // Biometric speed control (80%-120% range)
    speed_multiplier = 0.8 + (attention_score * 0.4)
    
    // Apply to timing variables
    tf = 5 * speed_multiplier
    t1 = wave(time(.15*tf))*PI2
    t2 = wave(time(.19*tf))*PI2
}
```

### 2. Biometric Color Control

**Pattern**: Any pattern with color variables

**Implementation**:
```javascript
export function render(index) {
    // Base color calculation
    h = triangle(h%1)/2 + t3
    
    // Biometric color mapping
    if (attention_score > 0.7) {
        // Engaged: ROY (Red, Orange, Yellow)
        h = (h + 0.0) % 1.0
    } else if (relaxation_score > 0.6) {
        // Relaxed: BIV (Blue, Indigo, Violet)
        h = (h + 0.66) % 1.0
    } else {
        // Neutral: Green
        h = (h + 0.33) % 1.0
    }
    
    hsv(h, 1, v)
}
```

### 3. Biometric Complexity Control

**Pattern**: Physics-based patterns

**Implementation**:
```javascript
export function beforeRender(delta) {
    // Base complexity
    base_complexity = 10
    
    // Biometric complexity control
    complexity_multiplier = 0.5 + (attention_score * 1.0)
    
    // Apply to simulation parameters
    particle_count = Math.floor(base_complexity * complexity_multiplier)
    gravity_strength = 0.5 + (relaxation_score * 0.5)
}
```

---

## Code Examples

### 1. Biometric Matrix Waterfall

```javascript
// matrixgreenwaterfall_biometric.js
// Based on matrixgreenwaterfall.js with biometric integration

export var attention_score = 0.5
export var relaxation_score = 0.5

export function beforeRender(delta) {
    // Speed control based on attention
    speed_multiplier = 0.8 + (attention_score * 0.4)
    tf = 5 * speed_multiplier
    
    t1 = wave(time(.15*tf))*PI2
    t2 = wave(time(.19*tf))*PI2
    z = 2+wave(time(.1*tf))*5
    t3 = wave(time(.13*tf))
    t4 = (time(.01*tf))
}

export function render(index) {
    y = floor(index/w)
    x = index%w
    
    if (zigzag) {
        x = (y % 2 == 0 ? x : w-1-x)
    }
    
    h = (1 + sin(x/w*z + t1) + cos(y/w*z + t2))*.5
    v = wave(h + t4)
    v = v*v*v
    
    // Biometric color control
    if (attention_score > 0.7) {
        // Engaged: More red/orange
        h = (h + 0.0) % 1.0
    } else if (relaxation_score > 0.6) {
        // Relaxed: More blue/green
        h = (h + 0.66) % 1.0
    } else {
        // Neutral: Green
        h = (h + 0.33) % 1.0
    }
    
    // Biometric brightness control
    v = v * (0.5 + relaxation_score * 0.5)
    
    hsv(h, 1, v)
}
```

### 2. Biometric Spinwheel

```javascript
// spinwheel2d_biometric.js
// Based on spinwheel2d.js with biometric integration

export var attention_score = 0.5
export var relaxation_score = 0.5

export function beforeRender(delta) {
    // Biometric speed control
    speed_multiplier = 0.8 + (attention_score * 0.4)
    tf = 5 * speed_multiplier
    
    t1 = wave(time(.15*tf))*PI2
    t2 = wave(time(.19*tf))*PI2
    z = 2+wave(time(.1*tf))*5
    t3 = wave(time(.13*tf))
    t4 = (time(.01*tf))
}

export function render(index) {
    y = floor(index/w)
    x = index%w
    
    if (zigzag) {
        x = (y % 2 == 0 ? x : w-1-x)
    }
    
    h = (1 + sin(x/w*z + t1) + cos(y/w*z + t2))*.5
    v = wave(h + t4)
    v = v*v*v
    
    // Biometric color palette control
    base_hue = relaxation_score * 0.33  // ROYGBIV spectrum
    h = (h + base_hue) % 1.0
    
    // Biometric brightness control
    v = v * (0.6 + relaxation_score * 0.4)
    
    hsv(h, 1, v)
}
```

### 3. Biometric Gravity Simulation

```javascript
// nbodygravity2D_biometric.js
// Based on nbodygravity2D.js with biometric integration

export var attention_score = 0.5
export var relaxation_score = 0.5

export function beforeRender(delta) {
    // Biometric particle count control
    particle_count = 10 + Math.floor(attention_score * 20)  // 10-30 particles
    
    // Biometric gravity control
    gravity_strength = 0.5 + relaxation_score * 0.5
    
    // Update physics simulation
    updatePhysics(delta)
}

function updatePhysics(delta) {
    // Physics simulation with biometric parameters
    for (i = 0; i < particle_count; i++) {
        // Calculate forces with gravity_strength
        // Update particle positions
        // Handle collisions
    }
}

export function render(index) {
    // Render particles based on physics simulation
    // Color based on velocity and position
    
    // Biometric color control
    if (attention_score > 0.7) {
        // Engaged: Bright, energetic colors
        h = 0.0 + (attention_score - 0.7) * 0.2
    } else if (relaxation_score > 0.6) {
        // Relaxed: Cool, calming colors
        h = 0.66 + relaxation_score * 0.33
    } else {
        // Neutral: Balanced colors
        h = 0.33
    }
    
    hsv(h, 1, v)
}
```

---

## Best Practices

### 1. Performance Optimization

**Pattern**: All patterns

**Techniques**:
```javascript
// Use efficient math operations
h = triangle(h%1)/2 + t3  // Fast modulo and triangle wave

// Minimize function calls in render loop
v = v*v*v  // Fast gamma correction

// Use pre-calculated values
tf = 5  // Calculate once in beforeRender
```

### 2. Color Management

**Pattern**: All patterns

**Techniques**:
```javascript
// Consistent color space usage
hsv(h, 1, v)  // Always use HSV for consistency

// Gamma correction for LED strips
v = v*v*v  // Apply gamma correction

// Smooth color transitions
h = triangle(h%1)/2 + t3  // Smooth hue transitions
```

### 3. Variable Control

**Pattern**: All patterns

**Techniques**:
```javascript
// Export variables for external control
export var attention_score = 0.5
export var relaxation_score = 0.5

// Use slider functions for UI control
export function sliderAttention(v) {
    attention_score = v
}

export function sliderRelaxation(v) {
    relaxation_score = v
}
```

### 4. Modular Design

**Pattern**: Complex patterns

**Techniques**:
```javascript
// Separate calculation and rendering
export function beforeRender(delta) {
    // All calculations here
    calculatePhysics(delta)
    calculateColors()
}

export function render(index) {
    // Only rendering here
    renderPixel(index)
}
```

---

## Performance Optimization

### 1. Frame Rate Optimization

**Pattern**: All patterns

**Techniques**:
```javascript
// Minimize calculations in render loop
export function beforeRender(delta) {
    // Pre-calculate expensive operations
    expensive_calculation = calculateOnce()
}

export function render(index) {
    // Use pre-calculated values
    result = expensive_calculation[index]
}
```

### 2. Memory Management

**Pattern**: Physics simulations

**Techniques**:
```javascript
// Reuse arrays and objects
var particle_array = array(100)  // Pre-allocate

// Avoid creating new objects in render loop
function updateParticle(particle) {
    // Modify existing particle object
    particle.x += particle.vx
    particle.y += particle.vy
}
```

### 3. Algorithm Optimization

**Pattern**: Complex patterns

**Techniques**:
```javascript
// Use efficient algorithms
function fastDistance(x1, y1, x2, y2) {
    // Use squared distance to avoid sqrt
    return (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)
}

// Use lookup tables for expensive operations
var sin_table = array(256)
for (i = 0; i < 256; i++) {
    sin_table[i] = sin(i/256*PI2)
}
```

---

## Biometric Integration Opportunities

### 1. Attention-Based Control

**Patterns**: All patterns with speed/timing

**Integration Points**:
- **Speed control**: 80%-120% range based on attention
- **Complexity control**: Particle count, rule complexity
- **Color intensity**: Brighter colors for higher attention

### 2. Relaxation-Based Control

**Patterns**: All patterns with color/brightness

**Integration Points**:
- **Color palette**: ROYGBIV spectrum mapping
- **Brightness control**: Dimmer for more relaxed states
- **Animation smoothness**: Slower, smoother transitions

### 3. Brainwave Band Control

**Patterns**: Complex patterns with multiple parameters

**Integration Points**:
- **Alpha waves**: Relaxation and calm patterns
- **Beta waves**: Attention and engagement patterns
- **Theta waves**: Creative and dreamy patterns
- **Delta waves**: Deep relaxation patterns

### 4. Multi-Parameter Control

**Patterns**: Physics simulations, cellular automata

**Integration Points**:
- **Particle count**: Based on attention level
- **Gravity strength**: Based on relaxation level
- **Rule complexity**: Based on brainwave complexity
- **Color palette**: Based on overall mood

---

## Implementation Guide

### 1. Pattern Selection Strategy

**For Initial Testing**:
1. Start with `matrixgreenwaterfall.js` - Simple, fast, reliable
2. Test with `spinwheel2d.js` - Good color control
3. Experiment with `oasis.js` - Calming effects

**For Production**:
1. Use `nbodygravity2D.js` - Complex, engaging
2. Implement `cellularautomata1d.js` - Rule-based control
3. Deploy `multisegmentforautomation.js` - Automation ready

### 2. Biometric Integration Steps

**Step 1**: Add export variables
```javascript
export var attention_score = 0.5
export var relaxation_score = 0.5
```

**Step 2**: Modify timing in beforeRender
```javascript
speed_multiplier = 0.8 + (attention_score * 0.4)
tf = 5 * speed_multiplier
```

**Step 3**: Modify colors in render
```javascript
// Add biometric color control
if (attention_score > 0.7) {
    h = (h + 0.0) % 1.0  // Red/orange for engaged
} else if (relaxation_score > 0.6) {
    h = (h + 0.66) % 1.0  // Blue/purple for relaxed
}
```

**Step 4**: Test and calibrate
```javascript
// Add calibration sliders
export function sliderAttention(v) {
    attention_score = v
}

export function sliderRelaxation(v) {
    relaxation_score = v
}
```

### 3. Production Deployment

**Step 1**: Pattern preparation
- Select appropriate patterns from repository
- Add biometric integration code
- Test with manual controls

**Step 2**: Integration testing
- Connect to real brainwave data
- Calibrate thresholds and ranges
- Test with multiple users

**Step 3**: Performance optimization
- Optimize for target frame rate
- Minimize latency
- Ensure smooth transitions

**Step 4**: Production deployment
- Deploy to target hardware
- Monitor performance
- Collect user feedback

---

## Conclusion

The [PixelblazePatterns](https://github.com/zranger1/PixelblazePatterns) repository provides an extensive collection of production-ready patterns that can be adapted for biometric control. Key takeaways:

### **🎯 Pattern Selection**
- **1D patterns** - Perfect for initial testing and linear strips
- **2D/3D patterns** - Complex effects for advanced installations
- **Experimental patterns** - Cutting-edge techniques for research
- **Multisegment patterns** - Scalable for large installations

### **⚡ Performance Optimization**
- **Efficient algorithms** - Fast rendering for real-time control
- **Memory management** - Optimized for embedded systems
- **Frame rate control** - Consistent performance across devices

### **🎨 Biometric Integration**
- **Speed control** - 80%-120% range based on attention
- **Color control** - ROYGBIV spectrum based on mood
- **Complexity control** - Particle count and rule complexity
- **Brightness control** - Based on relaxation levels

### **🚀 Production Readiness**
- **139+ patterns** - Extensive library to choose from
- **Well-documented** - Clear code and explanations
- **Community tested** - 53 stars indicate quality
- **Active development** - Regular updates and improvements

### **📋 Implementation Strategy**
1. **Start simple** - Use 1D patterns for initial testing
2. **Add biometric control** - Integrate brainwave data
3. **Optimize performance** - Ensure real-time responsiveness
4. **Scale up** - Move to complex patterns for production

This repository provides the foundation for creating sophisticated, biometric-responsive LED installations that can adapt to users' mental states in real-time.

---

*Document generated from analysis of [zranger1/PixelblazePatterns](https://github.com/zranger1/PixelblazePatterns) repository* 