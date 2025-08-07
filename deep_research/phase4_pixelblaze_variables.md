# Controlling Pixelblaze V3 Pattern Variables via WebSocket

## Preparing Patterns for External Variable Control

To enable real-time control, the Pixelblaze pattern must export any variables you want to adjust externally. In the Pixelblaze language, you use the `export var` keyword to make a global variable "public." For example, in your pattern code you might have:

```javascript
export var speed = 1.0;     // pattern speed control
export var hue = 0.0;       // base color hue
export var direction = 1;   // direction toggle (1 or -1)
```

Exported globals appear in Pixelblaze's Var Watcher (on the IDE) and are accessible via the WebSocket API. Only exported variables can be changed externally – if a variable isn't exported, external `setVars` commands won't affect it. Likewise, do not reassign exported variables every frame in your code, or your code will override any external changes. In other words, set a default value with `export var` and then use that variable in your animation logic (instead of constantly resetting it in `beforeRender` or `render`). This way, any new value you send over WebSocket will "stick" and influence the pattern.

**Example:** Suppose your pattern uses an exported `speed` variable to control animation speed. In `beforeRender(delta)`, you could use `delta * speed` to scale time, but don't assign `speed` a new value inside `beforeRender`. This ensures `speed` remains whatever value is set externally (or its default).

## WebSocket Message Format for Variables

Pixelblaze V3 exposes a WebSocket server (on port 81) that accepts JSON messages for control. To change a pattern variable, you send a JSON text frame with a `setVars` command. The JSON structure is:

```json
{
  "setVars": {
    "variableName": <newValue>,
    "otherVar": <value2>,
    ...
  }
}
```

Each key under `setVars` corresponds to an exported variable name, and the value is the new value you want to apply. Pixelblaze will update those variables between render frames so the change takes effect cleanly on the next frame. You can set multiple variables at once in one message; all updates in a single frame are applied atomically (simultaneously) in the pattern.

For example, to update the `speed` and `direction` variables exported in the pattern:

```json
{
  "setVars": {
    "speed": 0.5,
    "direction": -1
  }
}
```

This single message will set `speed` to 0.5 and `direction` to -1 together. The pattern will use those new values on the next animation frame. If you have only one variable to change, you can send just that one in the object. For instance, to set an exported `myVar` to 3.14159:

```json
{ "setVars": { "myVar": 3.14159 } }
```

As the Pixelblaze creator notes, "The variable has to be an exported global… Then you can send text/JSON websocket frames to change that variable".

## Reading Current Variables (getVars)

To read the current values of all exported variables in the active pattern, you can send:

```json
{ "getVars": true }
```

Pixelblaze will respond with a JSON object of all exported vars and their values. This is useful for discovering variable names or confirming their states. (In the Pixelblaze Web IDE, the Var Watcher is effectively using `getVars` under the hood.)

## Special Case: Arrays and Complex Variables

Pixelblaze supports arrays as exported variables, which can also be updated via WebSocket. If your pattern does `export var myArray = array(10)`, you can send a JSON array to update it. The `setVars` command is smart enough to copy the values into the existing array. For example:

```json
{
  "setVars": {
    "myArray": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  }
}
```

This will fill `myArray` with the 10 given numbers. Keep in mind that `setVars` is excellent for a handful of control values but not intended for high-frequency, large data streams (like sending hundreds of LED intensities every frame). In other words, updating a few variables or an array of moderate size on the fly is fine, but trying to stream full frame buffers (e.g. 1200 pixel values) each frame via WebSocket will be too slow and inefficient.

## Controlling Brightness and Other Built-in Settings

Pixelblaze has a global brightness setting (the same as the brightness slider in the UI). You can adjust this on the fly via WebSocket with a simple JSON message:

```json
{ "brightness": 0.5 }
```

Brightness is specified as a value from 0.0 (dark/off) to 1.0 (full brightness). The above example would set brightness to 50%. According to the documentation, a brightness change sent over WebSocket "will not be saved between restarts" – it's a temporary setting (unless you explicitly instruct Pixelblaze to save configuration). This is by design so you can adjust brightness freely without wearing out flash memory with frequent saves. In practice, Pixelblaze firmware ensures the brightness change takes effect immediately, but on reboot the controller typically returns to the last saved brightness (usually the value set via the web UI or saved with a command).

**Other controls:** The WebSocket API can also control many aspects of Pixelblaze's state. For example, you can change the active pattern (program) or sequence mode, adjust the pixel count, etc., with different JSON commands. If you have UI controls defined in your pattern (like sliders or color pickers created via `export function sliderX(...)` or `export function colorPicker(...)` in code), those too can be manipulated with WebSocket messages. In particular, there are `setControl` / `setControls` commands to adjust UI slider values, and `setColorControl` for color pickers. The `ctl_name` in those messages corresponds to the control's name (usually derived from the function name in the pattern). However, for most simple use cases, exporting a variable and using `setVars` is sufficient and straightforward.

## Live Example – Python

Using Python, you can connect to the Pixelblaze's WebSocket and send JSON messages. Below is a simple example using the `websocket-client` library to adjust variables and brightness on a Pixelblaze (replace `<PB_IP>` with your controller's IP address):

```python
import json
import websocket

# Connect to Pixelblaze WebSocket (port 81)
ws = websocket.create_connection("ws://<PB_IP>:81")

# Set global brightness to 80%
ws.send(json.dumps({ "brightness": 0.8 }))

# Adjust pattern variables on the fly
update = {
    "setVars": {
        "speed": 0.5,      # slow down the pattern speed
        "direction": -1    # change direction (assuming pattern uses this)
    }
}
ws.send(json.dumps(update))

# (Optional) Read back the current exported variables
ws.send(json.dumps({ "getVars": True }))
response = ws.recv()
print("Current vars:", response)

ws.close()
```

In this example, we connect to the Pixelblaze, set brightness to 80%, then send a `setVars` update that sets the `speed` variable to 0.5 and `direction` to -1. We then request `getVars` to confirm the current state (the Pixelblaze will reply with a JSON of all exported vars). Note that the Pixelblaze expects JSON text, so we use `json.dumps` to format our dictionary.

You could also use the community-made Pixelblaze Python client library, which provides convenient methods like `pb.setVars({...})` or `pb.setBrightness(val)`. For example, using that library, one could simply call `pb.setActiveVariables({'speed':0.5, 'direction':-1})` to achieve the above. Under the hood, it sends the same JSON commands via WebSocket.

## Live Example – JavaScript (Browser or Node)

In JavaScript, the standard WebSocket API can be used. Here's an example that would run in a browser (or in Node.js with a WebSocket library), connecting to the Pixelblaze and then adjusting a variable and brightness:

```javascript
// Connect to Pixelblaze WebSocket (use ws in Node, or WebSocket in browser)
const ws = new WebSocket("ws://<PB_IP>:81");

ws.onopen = () => {
    // Set pattern's "hue" variable (exported in the pattern code) to 0.25
    ws.send(JSON.stringify({ setVars: { hue: 0.25 } }));
    
    // Also dim the global brightness to 40%
    ws.send(JSON.stringify({ brightness: 0.4 }));
};

// Log any responses (e.g., from getVars or acknowledgments)
ws.onmessage = (event) => {
    console.log("Received from Pixelblaze:", event.data);
};
```

This snippet, once connected, sends two messages: one to change an exported variable `hue` to 0.25 (maybe representing a color hue, if your pattern uses it) and another to set brightness to 40%. In a Node.js environment, you could achieve the same using the `ws` package or similar. The format of the messages is identical since it's just JSON sent over the WebSocket.

**Tip:** You can bundle multiple changes into one JSON if you want them to occur together. For example, you could send `ws.send(JSON.stringify({brightness: 0.4, setVars: { hue: 0.25, speed: 1.2 }}));` in one go. Pixelblaze will interpret both the brightness change and the variable updates in one combined message. (Any top-level keys like `brightness`, `sequencerMode`, `setVars`, etc., can be included together in one JSON frame.)

## Limitations and Caveats

### Exported Variable Limits
Pixelblaze V3 greatly increased the capacity for variables – it supports on the order of a few hundred globals (up to 256 exported vars/functions), which is double the limit of V2. In practice, that's plenty for most patterns. However, keep in mind each exported var consumes memory, so don't export more than you need.

### Performance
Sending a few variable updates on the fly (even many times per second) is well within Pixelblaze's capabilities. But avoid trying to push very large data sets or extremely high-frequency updates through `setVars`. The WebSocket API is not meant for streaming full pixel data for every LED; such use can flood the message queue or introduce latency. If you need to drive per-LED colors from an external source, consider other approaches (Pixelblaze supports a binary streaming mode for pixel data in some firmware versions, or use the sensor expansion's serial interface emulation).

### Atomic Updates
As noted, multiple variables sent in one `setVars` JSON are applied together between frames. If you send separate messages rapidly, there's a tiny chance they could apply over successive frames. So if two variables must change in sync (e.g. red and green components), send them in one combined `setVars` message rather than two back-to-back messages.

### Threading and Acknowledgement
The Pixelblaze will queue incoming WebSocket commands. It processes one frame's worth of commands at a time. If you send many messages very fast, ensure you handle the responses or acknowledgments if needed. The Pixelblaze WebSocket protocol typically doesn't send a response for a `setVars` aside from an optional low-level ACK. If using a library (like the Python client), you might see methods like `waitForEmptyQueue()` which can ensure the Pixelblaze has applied all pending commands. This can be useful if you script complex sequences of changes.

### Persistence
By default, changes made via WebSocket (like brightness or pattern selection) do not automatically save to flash memory. This is intentional to avoid wearing out the device's flash with frequent writes. It means if you power-cycle the Pixelblaze, it will revert to whatever was last saved (usually settings from the web UI). Pixelblaze's WebSocket API does allow optional `save: true` flags on certain commands (for example, on pattern change or sequencer commands). Use `save: true` sparingly and only when you need the device to remember a setting after reboot. In most cases, for on-the-fly control, you'll keep save false (the default). The brightness command example above, for instance, is not saved between restarts. If you do want to persist a new brightness or default pattern via WebSocket, you could include `"save":true` at the top level of the JSON message to force a save.

### Firmware and Bugs
Since you mentioned latest firmware, you benefit from the newest fixes and features. Earlier Pixelblaze V3 firmware had a known issue where after ~10–15 minutes of continuous rapid `setVars` updates, the controller could stop applying new values until the connection was reset. This was likely a memory leak or buffer issue, and you should ensure you run a firmware version where this is resolved. In any case, if you plan to send thousands of updates, it's good to test for stability. Generally, moderate update rates (e.g. adjusting a few variables at, say, 10 Hz or 20 Hz) should run indefinitely without trouble.

### Identifying Variable Names
The question of how to identify variables in a user-written pattern is worth touching on. If you wrote the pattern, you'll know which variables you exported. If not (say you downloaded a pattern), you can find exported variables by opening the pattern's source (the Pixelblaze web editor will show any `export var` lines, or look for `export var` in the code). Alternately, connect via WebSocket and use `{"getVars": true}` – the response will list all exported variable names and their current values. Another scenario is patterns with UI controls (sliders, knobs, color pickers) – those controls have internal names (often shown in the UI or code as function names like `sliderFoo`). The Pixelblaze API offers `getControls()` to list current UI control states, which can help identify control names if needed.

## Additional Resources

For more detailed information, the Pixelblaze WebSockets API documentation is a great reference (covering commands like `setVars`, `getVars`, `brightness`, pattern selection, sequencer control, etc.). The Pixelblaze forums also contain numerous examples and community discussions. In particular, the Pixelblaze creator's notes on advanced control provide valuable insights.

You may also check out the open-source Pixelblaze client libraries for inspiration:
- **Pixelblaze Python Client** (by ZRanger1) – illustrates how to structure commands in code.
- **Firestorm** (Node.js) – an official Pixelblaze companion app that relays WebSocket commands to multiple Pixelblazes. Its source code can serve as an example of using the WebSocket API in JavaScript.

By combining the official docs with these examples, you should have a solid understanding of how to tweak pattern parameters live. With an exported variable in your pattern and a well-formed JSON message over WebSocket, you can dial in speeds, colors, brightness, directions, and more – all in real time – on your Pixelblaze V3. Enjoy the light show!

## Sources

1. [Pixelblaze Language Reference - ElectroMage](https://electromage.com/docs/language-reference/)
2. [Pixelblaze Websockets API - ElectroMage](https://electromage.com/docs/websockets-api/)
3. [Connect Arduino UNO to Output Expander - Troubleshooting - ElectroMage Forum](https://forum.electromage.com/t/connect-arduino-uno-to-output-expander/250)
4. [PB Power On/Off strategy - Troubleshooting - ElectroMage Forum](https://forum.electromage.com/t/pb-power-on-off-strategy/1928)
5. [pixelblaze-client · PyPI](https://pypi.org/project/pixelblaze-client/0.9.6/)
6. [Pixelblaze-client: Python 3 library for Pixelblaze - Patterns and Code - ElectroMage Forum](https://forum.electromage.com/t/pixelblaze-client-python-3-library-for-pixelblaze/756?page=4)
7. [Pixelblaze V3 | Crowd Supply](https://www.crowdsupply.com/hencke-technologies/pixelblaze-v3)
8. [[SOLVED] Control LED-strip through Websocket API? - Bindings - openHAB Community](https://community.openhab.org/t/solved-control-led-strip-through-websocket-api/91533)