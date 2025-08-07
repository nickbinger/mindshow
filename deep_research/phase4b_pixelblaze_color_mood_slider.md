# Implementing a Perceptual Color Mood Slider in Pixelblaze Patterns

## Overview of the Warm–Cool Color Bias Challenge

**Goal:** Introduce a dynamic "color mood" slider in Pixelblaze patterns that biases colors from warm tones (reds/oranges) to cool tones (blues/violets) perceptually, without simply rotating all hues around the HSV wheel. This means shifting the output along the ROYGBIV spectrum (red → orange → yellow → green → blue → indigo → violet) in a way that feels like warming or cooling the overall palette, rather than just adding a fixed hue offset (which would send reds into greens, etc., disrupting the warm/cool feel). The slider should be exposed as a real-time variable (e.g. `colorMoodBias`) that can be adjusted externally (via the Raspberry Pi using Pixelblaze's WebSocket `setVars()` interface).

### Key Requirements:

- **In-pattern implementation:** The hue shift must occur inside the Pixelblaze pattern code (not post-processed on the Pi). Every pixel's color is adjusted in the `render()` function before being output.
- **Minimal changes to core logic:** We want a method that can be applied to many patterns with minimal edits. Ideally, we'll just add a small snippet to tweak the hue output, without rewriting the pattern's primary color-generation algorithm.
- **Real-time control:** The bias amount should be tied to an exported variable/slider (e.g. `colorMoodBias`) so it can be changed on the fly via Pixelblaze's UI or external API.
- **Perceptual warm–cool shift:** The transformation should bias colors toward warm or cool end of the spectrum, rather than uniformly rotating hues through all colors. In practice, this means, for example, a slight "cool" bias makes colors a bit more bluish overall, and a full "warm" bias makes everything shades of red/orange – instead of just adding, say, +30° hue (which would turn red to green, etc., not what we want).

## Approaches for Perceptual Color Biasing

There are multiple ways to achieve a warm-to-cool bias. We'll discuss a few approaches, from simple to more advanced, noting their pros, cons, and perceptual effects:

### 1. Hue Adjustment in HSV Space

This approach works directly with the hue value (`h` in HSV) before calling the `hsv()` function. It's intuitive since Pixelblaze patterns commonly use `hsv(h, s, v)` to set colors, and we can tweak `h` without altering the underlying pattern logic.

#### Naive Hue Offset (Not Recommended):

One might first consider simply adding or subtracting a fixed offset to all hue values. For example, a "cooler" bias could mean `h_new = h + 0.1` (shifting all hues 10% forward on the wheel), and a "warmer" bias `h_new = h - 0.1`. However, uniform hue rotation is not perceptually the same as a warm–cool shift. A uniform offset will cycle colors through the entire wheel (e.g., reds shift into greens), which breaks the warm/cool intention. We want to avoid an approach that just rotates through green when aiming for cooler tones, so a simple offset is too crude.

#### Anchored Hue Interpolation:

A better method is to interpolate each hue toward a warm or cool anchor color depending on the slider. We choose two anchor hues representing pure warm and pure cool tones (e.g., `warmAnchor` around red/orange and `coolAnchor` around blue/violet). Then we blend the original hue toward one of these anchors by an amount proportional to the bias slider.

- If the slider `colorMoodBias` is neutral (say 0.5 on a 0–1 scale), we leave `h` unchanged.
- If the slider moves toward the warm end (e.g., 0.0 = fully warm), we interpolate `h` toward the `warmAnchor`. For example, `h_new = mix(h, warmAnchor, warmAmount)`, where `warmAmount` increases as the slider moves to warm. At full warm bias, we might essentially replace every hue with the warm anchor hue (making the output various shades of red/orange).
- Similarly, toward the cool end (e.g., 1.0 = fully cool), we interpolate `h` toward `coolAnchor`.

Linear interpolation formula:

```javascript
if (bias < 0) {
    // Warm bias: bias range [-1, 0]
    h_new = h + (-bias) * (warmAnchor - h);
} else {
    // Cool bias: bias range [0, 1]
    h_new = h + bias * (coolAnchor - h);
}
```

In this pseudocode, `bias` is a normalized value in [-1, 1] (where -1 = full warm, +1 = full cool, 0 = neutral). `warmAnchor` could be 0.0 (red) or an orange hue (~0.08), and `coolAnchor` could be ~0.67 (blue) or ~0.75 (violet). The code blends the original hue toward the chosen anchor.

**Effect:** This preserves some relative differences between hues but gradually tints everything. For example, at half-cool bias, a originally-red hue (0.0) might move toward greenish (halfway to blue/violet) – which may or may not be desirable perceptually. A drawback is that at extreme settings, all hues collapse to a single color (all pixels become red/orange at full warm, or all become blue/violet at full cool). That might be acceptable for a "mood" slider, but it does eliminate color variety at the ends.

#### Constrained Hue Range (Range Compression):

A more nuanced approach is to restrict and compress the hue range that the pattern can output, sliding that range along the spectrum as the slider moves. This way, even at extreme bias, you still get a band of colors (all warm-toned or all cool-toned), rather than one singular hue.

The idea is borrowed from a technique to constrain "rainbow" patterns to a subset of hues². We define:

- `warmAnchor` (start of warm range) – e.g. 0.0 for red.
- `coolAnchor` (end of cool range) – e.g. 0.75 for violet.
- A minimum range width for hues (covering a span within warm or cool tones, not just a point).

For example, we might define that at full warm bias, output hues are limited to [0.0, 0.17] (red through orange-yellow), and at full cool bias, hues are limited to [0.59, 0.75] (blue through violet). At neutral (mid slider), the range would be the full [0.0, 1.0] (no restriction). As the slider moves, we linearly shrink and shift the range of possible hues from the full spectrum down to the targeted warm or cool subset.

Concretely, one formula for this is:

```javascript
export var colorMoodBias = 0.5; // 0 = warm, 1 = cool, 0.5 = neutral

// Define anchors and range extents
var warmAnchor = 0.0; // red as base warm hue
var warmRange = 0.17; // span for warm tones (red to yellow ~60°)
var coolAnchor = 0.75; // violet as end cool hue (270°)
var coolRange = 0.16; // span for cool tones (blue to violet ~60°)

// In render, after computing original h:
var bias = colorMoodBias - 0.5; // convert [0,1] slider to [-0.5, 0.5]
bias *= 2; // now bias is in [-1, 1]

if (bias < 0) {
    // Warm bias: compress hue range toward warmAnchor
    let t = -bias; // t = 0 (no warm shift) to 1 (full warm)
    let range = 1 - t * (1 - warmRange);
    // range linearly shrinks from 1 (neutral) to warmRange (at full warm)
    h = warmAnchor + (h % 1) * range;
    // hue is now mapped into [warmAnchor, warmAnchor+range]
} else {
    // Cool bias: compress hue range toward coolAnchor (from below)
    let t = bias; // t = 0 (neutral) to 1 (full cool)
    let range = 1 - t * (1 - coolRange);
    // range shrinks from 1 to coolRange
    // Map h into [coolAnchor-range, coolAnchor]
    h = coolAnchor - (1 - (h % 1)) * range;
}
```

This approach ensures at full bias the output hues are confined to a narrow band on the warm or cool end, but still vary within that band (so you get, say, reds and oranges, or blues and violets, not just one shade). It essentially scales and offsets the pattern's original hue value into a smaller segment of the spectrum³. At neutral, `range = 1.0` and `warmAnchor=0`, so `h` stays unchanged (full 0–1 range). At partial biases, the range is partially reduced, meaning the pattern's colors appear mostly warm or mostly cool but can still include intermediate hues like green when near the middle of the slider.

**Perceptual note:** This method avoids introducing out-of-place colors. For example, if the slider is set slightly cool, a color that was originally red might shift toward orange/yellow (heading through the spectrum toward greenish-blue) but will not overshoot into pure green if the range is already sliding toward the cool side. Essentially, we're moving the "window" of available hues along ROYGBIV and narrowing it as we approach the ends.

### 2. Post-Processing in RGB Space (Channel Biasing)

Another approach works after the pattern's color is determined, by adjusting the RGB components to tint the output. This is analogous to applying a warming or cooling filter over the entire pattern's output.

**How it works:** Convert the pattern's `hsv(h,s,v)` into RGB (either by using Pixelblaze's internal `hsv()` and then reading the result, or by performing an HSV-to-RGB conversion in code). Then apply a bias to the red vs blue channels:
- For a warm bias, increase the relative contribution of red/orange, and/or decrease blue.
- For a cool bias, increase blue, and/or decrease red.

For example, one could define scale factors `rBias`, `gBias`, `bBias` based on the slider. At neutral, all are 1.0 (no change). Toward warm, set `rBias > 1.0` and `bBias < 1.0` (making everything more reddish and less bluish). Toward cool, do the opposite (`bBias > 1`, `rBias < 1`). Green can often remain ~1, or you can tweak it slightly if needed to fine-tune the tint (since green is roughly neutral between warm and cool).

Example: If we treat bias as -1 (warm) to +1 (cool), we might do:

```javascript
let rBal = 1 - 0.5 * bias; // bias positive (cool) reduces red, negative (warm) increases red
let gBal = 1; // leave green unchanged for simplicity
let bBal = 1 + 0.5 * bias; // bias positive (cool) increases blue, negative reduces blue

// ... after computing hsv to rgb as (r,g,b):
r = r * rBal;
g = g * gBal;
b = b * bBal;
rgb(r, g, b);
```

This is a simplistic linear bias. A more refined implementation could, for instance, add a bit of warm color or cool color rather than multiply, or normalize the brightness afterward to maintain constant luminosity.

Pixelblaze user ZRanger1 demonstrated a similar concept for white-balancing LED output by scaling RGB channels⁵. In that example, they convert hsv to rgb manually and then multiply each channel by a calibrated factor (rBal, gBal, bBal) before output⁶. We can adapt that idea dynamically: our `rBal`, `bBal` would vary with the slider instead of being fixed calibration values.

**Effect:** RGB biasing tends to preserve the original hues' relationships but tints the overall color cast. It's somewhat like adjusting color temperature in photo editing: a cool bias adds a blue tint (whites become bluish, reds become purplish), while a warm bias adds an orange/red tint. One advantage is that it can be applied even if the pattern doesn't use HSV (some patterns set RGB directly). However, one must be careful: multiplying channels can reduce overall brightness or wash out fully saturated colors. For instance, a pure red pixel (1,0,0) under a strong cool bias might end up as (0,0, something) – essentially turning off red entirely, possibly dimming the pixel if blue was originally zero. To counteract that, you might add a bit of the target tint instead of purely scaling down the other channel, or ensure some minimum saturation.

**Trade-off:** This method might not follow the ROYGBIV path as neatly – it linearly mixes colors in RGB space, which is not perceptually uniform. It could introduce slight shifts in saturation or brightness. But it's straightforward and does not require altering the pattern's hue logic at all – you intercept right at the output stage by using a custom `rgb()` call (or a modified hsv function). In Pixelblaze, you'd replace `hsv(h,s,v)` with your own routine: convert to rgb, apply biases, and call `rgb(r, g, b)` to set the pixel.

### 3. Palette-Based Color Mapping

Pixelblaze has the ability to use custom palettes (gradients) and sample them with the `paint()` function⁷. We can exploit this for a more curated warm-to-cool transformation:

- **Define warm and cool palettes:** For example, a warm palette might range from deep red, through orange, to yellow-white; a cool palette might go from turquoise, through blue, to violet. These can be defined as arrays of RGB color stops and activated with `setPalette()`⁸.
- **Use pattern's original hue (or other color index) as input to palette:** Instead of calling `hsv(h,s,v)`, call `paint(value, v)` where `value` is some index (0–1) and `v` is brightness. Pixelblaze will interpolate a color from the current palette.
- **Bias via palette blending:** Now, by changing the palette based on the slider, you effectively recolor the entire pattern. One approach is to interpolate between a warm palette and a cool palette as the slider moves. For example, at mid slider, use a neutral (full rainbow or balanced) palette; at 0% slider, use the warm palette; at 100%, the cool palette. You might dynamically generate a blended palette by mixing corresponding color stops of warm vs cool palette according to the bias.

This approach can yield very pleasing results because you have fine control over exactly what hues appear at each bias setting. It's a bit more advanced and involves more code (to set up palettes and blend them), but it keeps the pattern logic the same — you're just remapping colors after the fact. It's effectively a lookup-table method for color grading the pattern.

**Example concept:** If the original pattern uses `h` from 0–1, at neutral we set the palette to a full rainbow (so `paint(h)` produces the original rainbow). At warm bias, we set the palette to only warm colors. Then `paint(h)` automatically gives warm-toned outputs even as `h` varies. This is similar in spirit to constraining hue ranges as in Approach 1, but using the palette system allows non-linear and hand-picked color mappings (which might be more perceptually uniform than just slicing the HSV wheel).

**Consideration:** Using palettes means you have to manage the palette state whenever the bias slider changes (e.g., recalc palette arrays inside a `sliderColorMoodBias(v)` function). Pixelblaze can handle this, but it's a different style than direct math and may not be as universally drop-in for arbitrary patterns. It's great, however, if you want artistic control over the exact shades of "warm" and "cool" that appear.

## Implementation Example: Adding a Mood Slider to a Pixelblaze Pattern

Let's apply one of the above approaches to the provided pattern. We'll choose the hue-range compression method (Approach 1 variant) for this example, as it maintains variety at extreme settings while achieving the bias effect. The original pattern is a 2D plasma-like effect:

```javascript
// Original Pattern Code (2D plasma example)
w = 8 // width of the 2D matrix
zigzag = true // whether wiring is zigzag

export function beforeRender(delta) {
    tf = 5
    t1 = wave(time(0.15 * tf)) * PI2
    t2 = wave(time(0.19 * tf)) * PI2
    z = 2 + wave(time(0.1 * tf)) * 5
    t3 = wave(time(0.13 * tf))
    t4 = time(0.01 * tf)
}

export function render(index) {
    // 2D pixel coordinates
    y = floor(index / w)
    x = index % w
    if (zigzag) {
        x = (y % 2 == 0) ? x : (w - 1 - x)
    }
    
    // Core color logic for plasma
    h = (1 + sin(x/w * z + t1) + cos(y/w * z + t2)) * 0.5
    v = wave(h + t4)
    v = v * v * v // cube to skew brightness
    h = triangle(h % 1) / 2 + t3 // triangle wave shaping and add time offset
    
    hsv(h, 1, v) // original color output
}
```

In this pattern, `h` is the hue, which is being calculated through some wave functions, and then `hsv(h, 1, v)` sets the pixel color. We want to inject our bias right before the `hsv()` call. We'll also add an exported variable for the slider.

Here's the modified pattern with a color mood bias slider implemented:

```javascript
w = 8
zigzag = true

// Exported slider variable for color bias (0 = warm, 1 = cool)
export var colorMoodBias = 0.5

// Optionally, we can define slider mapping for UI (0–1 range, map to itself here)
export function sliderColorMoodBias(v) {
    colorMoodBias = v // direct assignment; adjust if non-linear mapping desired
}

var warmAnchor = 0.0
var warmRange = 0.17 // warm tones span (red to ~yellow)
var coolAnchor = 0.75
var coolRange = 0.16 // cool tones span (blue to violet)

export function beforeRender(delta) {
    // (unchanged logic)
    tf = 5
    t1 = wave(time(0.15 * tf)) * PI2
    t2 = wave(time(0.19 * tf)) * PI2
    z = 2 + wave(time(0.1 * tf)) * 5
    t3 = wave(time(0.13 * tf))
    t4 = time(0.01 * tf)
}

export function render(index) {
    // Compute coordinates (unchanged)
    y = floor(index / w)
    x = index % w
    if (zigzag) {
        x = (y % 2 == 0) ? x : (w - 1 - x)
    }
    
    // Original color calculations (unchanged)
    h = (1 + sin(x/w * z + t1) + cos(y/w * z + t2)) * 0.5
    v = wave(h + t4)
    v = v * v * v
    h = triangle(h % 1) / 2 + t3
    
    // ** Apply color mood bias to hue **
    let bias = (colorMoodBias - 0.5) * 2 // Map 0–1 to -1–1
    
    if (bias < 0) {
        // Warm bias: compress hue range toward warmAnchor
        let t = -bias // 0 to 1 as bias goes from 0 to -1
        let range = 1 - t * (1 - warmRange)
        h = warmAnchor + (h % 1) * range
    } else {
        // Cool bias: compress hue range toward coolAnchor
        let t = bias // 0 to 1 as bias goes 0 to 1
        let range = 1 - t * (1 - coolRange)
        h = coolAnchor - (1 - (h % 1)) * range
    }
    
    // Output the biased color
    hsv(h, 1, v)
}
```

**What changed:** We added an `export var colorMoodBias` with a default of 0.5 (neutral). In the `render()` function, after computing `h`, we insert a block that adjusts `h` based on the bias. The logic compresses the hue towards either 0.0 or 0.75. For example, if `colorMoodBias = 0` (fully warm), then `bias = -1` and we set `range = warmRange` (0.17), and `h = 0 + h * 0.17`. That means no matter what the original `h` was, now it falls between 0 and 0.17 – i.e. only reds/oranges. If `colorMoodBias = 1` (fully cool), we do the analogous mapping so `h` ends up between 0.59 and 0.75 (approximately between blue and violet). At `colorMoodBias = 0.5`, `bias = 0`, we skip both branches and nothing changes (`h` stays full-range). Intermediate values smoothly interpolate the range and position of allowable hues.

**Real-time control:** Because we exported `colorMoodBias`, the Pixelblaze UI will show a slider for it (named "Color Mood Bias"), and external controllers can call `setVars({colorMoodBias: value})` via WebSocket to adjust it¹. The changes take effect immediately in the next `render()` calls, smoothly shifting the colors.

## Best Practices for Parameterizing Hue Shifts

Designing the slider's behavior deserves attention so that the adjustment feels smooth and intuitive:

- **Slider Range and Mapping:** Typically use 0.0 to 1.0 for sliders. In our example, 0 means maximum warm bias, 1 means maximum cool. We mapped this linearly to -1…1 for ease. You could choose 0=neutral, negative=warm, positive=cool, but Pixelblaze UI sliders usually don't go negative. It's simpler to stick with 0–1 and do the conversion in code.

- **Non-linear Response:** Human perception of color temperature isn't linear, so you might apply an easing curve to the slider. For instance, you could square or sqrt the bias value to make the effect gentler around neutral and stronger at the extremes. (E.g., `t = pow(t, 0.5)` for more sensitivity in mid-range, or use an S-curve.) In Pixelblaze, this can be done inside the `sliderColorMoodBias(v)` function (e.g., map `v` through a function before assigning to `colorMoodBias`).

- **Choosing Anchor Hues:** The exact hue values for "warm" and "cool" anchors can be tweaked. Pure red (0°) and pure blue/violet (around 270°) are logical choices, but consider using a slightly orangish warm anchor (e.g. 20° or 30° hue) if you want the warm end to include rich orange/yellow rather than deep red. Likewise, "cool" might be centered on a blue-cyan if you prefer cooler whites. Test and see which endpoints produce the nicest range of tones for your LEDs.

- **Saturation and Brightness:** We mostly adjust hue, keeping saturation = 1 and V as per pattern. This means colors remain fully saturated. In some cases, extreme bias could make the output too homogeneous. One trick: you could reduce saturation a bit at extreme settings to introduce some neutral white mixing, which can make the effect more natural (like how very warm light has some yellowish white, and very cool light has bluish white). For example, as bias → 1, maybe drop saturation slightly so that the cool colors desaturate toward icy white. This wasn't required by the question, but it's a perceptual tuning idea.

- **Clamping vs Wrapping:** Ensure when manipulating `h` that you handle the wrap-around properly. In our code, we used `(h % 1)` which wraps any hue into [0,1). Pixelblaze's `hsv()` likely wraps hue internally too, but being explicit is good if we modify `h`. Also, when compressing ranges, we deliberately did not allow the range to wrap around the 0/1 boundary – that's on purpose. We treated the warm-to-cool spectrum as linear from 0 up to ~0.75 (270°) and stopped there, so that we don't include the short gap between violet back to red (which would introduce magenta out-of-sequence). This ensures the "rainbow order" is preserved in the bias.

## Where to Integrate the Hue Bias in the Render Flow

The hue-biasing logic should be placed after the pattern's core color computations but before output is set. In practice, this means:

- If the pattern uses `hsv(h, s, v)`, calculate `h` (and `s`, `v` as usual), then adjust `h` according to the slider, then call `hsv()`. In our example, we inserted the bias code right before `hsv(h, 1, v)`.

- If the pattern directly uses `rgb(r, g, b)`, you have two options: (a) convert those r,g,b to HSV or HSL to manipulate the hue (complex, likely not worth it), or (b) apply an RGB bias (Approach 2) to tint the r,g,b values. For instance, if a pattern chooses colors via `rgb()`, you can multiply/add biases to those values similarly before calling `rgb()`.

- If the pattern uses a palette (via `paint()` or similar), you might adjust the palette or the value fed into `paint()`. For example, if `paint(val)` is used and `val` essentially acts like a hue index, you could bias that `val` by skewing it toward a target. However, often it's easier to just change the palette (Approach 3).

- **Avoid altering the core algorithm's variables upstream if possible.** It's best to do the bias as a final step so that you don't interfere with how the pattern evolves or loops. This keeps the "mood filter" concept separate from the pattern logic. Jeff (a Pixelblaze developer) has noted that there's no built-in global color correction, but substituting your own adjusted `hsv()` or scaling the hue before calling it is the way to go⁹.

Practically, when adapting an existing pattern, look for lines like `hsv(` or any place the final color is set. That's your hook. Insert a small block to adjust hue (or RGB) right there. Because this is a self-contained step, you can copy-paste that snippet into many patterns with minimal changes (maybe just the variable names).

## Adapting the Approach to Other Patterns (Tips for LLMs and Users)

When applying this to other Pixelblaze patterns, here are some general tips:

- **Identify the color generation method:** Most patterns either compute a hue (`h`) and call `hsv(h, s, v)`, or pick from a palette, or directly compute r,g,b. Determine which case it is.

- **Hue-based patterns:** Easiest to adapt. Simply insert the hue bias logic as shown. Use the same global `export var colorMoodBias` so the UI slider is available. If a pattern uses a global hue offset (some patterns have a `hueOffset` variable that they add to all `h`), you could integrate bias by adding to or modifying that offset. But be careful not to double-wrap hues incorrectly.

- **Palette-based patterns:** If a pattern uses Pixelblaze's palette features, consider whether adjusting the palette is more sensible than altering indices. Sometimes you can still hijack by converting a palette index to a "hue-like" value and applying a bias, but since palettes can be arbitrary colors, a linear hue bias might not cleanly apply. In such cases, using a predesigned warm/cool palette (Approach 3) might be the better route.

- **Direct RGB patterns:** If conversion to HSV is impractical, implement Approach 2 (channel bias). This might involve just a few lines multiplying the r, g, b values. Make sure to include an `export var colorMoodBias` so the slider is present, and map it appropriately to your bias strength.

- **Preserve other dynamics:** Ensure that the biasing doesn't break things like audio reactivity or time-based transitions in the pattern. It should only recolor the output. For instance, if a pattern blends between two colors internally, apply the bias after it decides the blend, not to the individual source colors (unless you specifically want to).

- **Testing extremes:** After integration, test with `colorMoodBias = 0` and `1`. Verify the output has the expected warm and cool tones. Make sure there are no abrupt hue jumps or odd colors appearing. If you see, say, green when you expected only red/orange at the warm end, you might tighten the warm range or adjust anchor values.

For Large Language Models (LLMs) auto-generating Pixelblaze code: instruct them explicitly with this pattern. For example: "Find the line where `hsv()` is called and insert the following hue adjustment code above it…" and maybe supply the snippet. Consistency in variable naming (using the same `colorMoodBias`) across patterns helps reusability. Also, remind the LLM or user to include the `export var` so the slider is actually created (a step easily overlooked).

## Limitations and Trade-offs

Every approach has some limitations and tuning considerations:

- **Loss of Color Variety:** At extreme bias, you might end up with very monochromatic output (especially with the interpolation-to-anchor approach). Using the range-compression method mitigates this by preserving a span of hues. Decide if you want absolutely only red at full warm, or a mix of red, orange, yellow. Our example preserved a small mix. You can adjust `warmRange`/`coolRange` to set how narrow the palette gets at extremes.

- **Intermediate Hues (Green, Cyan, Magenta):** By focusing on red→violet along the long path of the color wheel, the midpoint bias will inherently pass through greenish hues. If the slider is around 0.5–0.6 (slightly cool), expect some greens or teals to appear, since the "cooler than neutral but not fully cool" part of ROYGBIV includes green and cyan. This is normal in a continuous transition. If you wanted to avoid green entirely (some definitions of warm/cool consider green neutral or slightly cool), you'd have to introduce a non-linear mapping or explicitly desaturate greens. For most use cases, it's fine as is.

- **Brightness and Perceived Intensity:** Changing hue usually doesn't affect brightness if `v` stays same. However, note that human eyes perceive some hues brighter than others at the same `v` (e.g., green appears brighter than blue at equal value). So as colors shift, the overall brightness perception of your display may change slightly. If this is a concern, consider adjusting `v` or gamma correcting after a big hue shift. Our example cubes the `v` for visual effect; we left that intact. The bias doesn't alter `v` at all, so relative brightness from the original pattern is preserved.

- **Precision:** Pixelblaze uses floating point math for these calculations (hue and slider are floats 0–1). The precision is high enough that you won't get banding from the math itself. But LED output is 8-bit per channel (0–255 levels), so extremely fine distinctions might not show if your bias increments are very tiny. In practice, the changes are large enough to see smoothly. If you do heavy non-linear ops (like our `v = v*v*v` or converting to RGB and back), avoid unnecessary complexity that could introduce rounding issues. Keep formulas as straightforward as possible.

- **Performance:** The added math for a hue bias (a few multiplications, conditionals, etc.) is trivial for Pixelblaze's engine – even on large LED counts, this won't be a bottleneck. However, if you went with an advanced approach (like computing in CIE color space or doing many sin/cos operations to rotate hue), that could add up. The presented methods (linear interpolation or small polynomial math) are very fast. So the trade-off here is negligible; prioritize clarity and maintainability of code.

- **RGB Bias Side-Effects:** If using the RGB post-process method, watch out for cases where colors clamp. For instance, scaling red down and blue up might push blue above 1.0 (which clamps to max brightness) and red below 0.0 (clamped to 0). This can reduce contrast. You might combat this by renormalizing (e.g., after scaling, if max(r,g,b) > 1, scale all down to 1). Similarly, adding a bias color could risk exceeding 1.0. Testing with pure white and pure primary colors at extreme bias is a good idea: you should still get something sensible (e.g., pure white might tint slightly warm or cool, not turn fully colored or dim).

- **A Note on Saturation-based Bias:** In some color correction scenarios, one applies bias more to unsaturated colors (whitish tones) and leaves fully saturated colors alone¹⁰. For example, ZRanger1 mentioned applying white-balance correction proportional to the square of (1 - saturation) so that pure colors weren't dulled¹¹. For a mood slider, you might or might not want that. If your pattern has a mix of vivid and pastel colors, you could choose to only heavily shift the pastels (which are closer to white) while keeping pure colors closer to original (so a pure red pixel doesn't turn greenish under a slight cool bias, it stays red). This can be achieved by factoring in saturation: e.g., reduce the bias effect when `s` is 1. Our example pattern uses full saturation (1) throughout, so we didn't do this. But it's something to consider if subtlety is needed – it's a trade-off between color integrity vs. uniform filtering.

In summary, the dynamic color mood slider can be implemented cleanly with a bit of math and thoughtful mapping. By anchoring the hue adjustments in perceptually meaningful warm and cool reference points, we ensure the changes feel natural (like changing the overall "lighting" of the pattern) rather than arbitrary. The pattern's core logic remains intact – we're essentially layering a configurable color filter on top of any Pixelblaze animation. This makes it a powerful technique to reuse across patterns with minimal tweaks, offering a new dimension of interactivity for LED visuals.

## Sources:

1. Pixelblaze WebSocket API documentation on using exported variables for real-time control - [Pixelblaze Websockets API - ElectroMage](https://electromage.com/docs/websockets-api/)

2. Pixelblaze forum discussion on constraining pattern hues to specific ranges, which inspired the hue range compression approach.

3. ZRanger1's white-balancing code and notes on channel scaling and preserving saturated colors (related concept applied here for warm/cool bias) - [White only patterns? - Patterns and Code - ElectroMage Forum](https://forum.electromage.com/t/white-only-patterns/2873)

4. [White Balance/Color Temp - ElectroMage Forum](https://forum.electromage.com/t/white-balance-color-temp/1774)

5. Pixelblaze user ZRanger1 demonstrated a similar concept for white-balancing LED output by scaling RGB channels.

6. In that example, they convert hsv to rgb manually and then multiply each channel by a calibrated factor (rBal, gBal, bBal) before output.

7. Pixelblaze has the ability to use custom palettes (gradients) and sample them with the `paint()` function.

8. These can be defined as arrays of RGB color stops and activated with `setPalette()`.

9. Advice from Pixelblaze developers on adjusting hue and saturation in code for color correction.

10. In some color correction scenarios, one applies bias more to unsaturated colors (whitish tones) and leaves fully saturated colors alone.

11. For example, ZRanger1 mentioned applying white-balance correction proportional to the square of (1 - saturation) so that pure colors weren't dulled.