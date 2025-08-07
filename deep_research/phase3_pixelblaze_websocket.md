# Changing Pixelblaze V3 Patterns via WebSocket

Controlling Pixelblaze V3 patterns from an external device (like a laptop or Raspberry Pi) is possible through its WebSocket API. You can retrieve the list of available patterns stored on the Pixelblaze and then send a command to activate any pattern by its unique ID. The Pixelblaze's WebSocket service typically runs on `ws://<pixelblaze_ip>:81`. Below we outline how to list patterns and switch between them, with examples in Python and JavaScript, as well as important considerations and limitations.

## Retrieving the Pattern List

To get the list of all patterns (programs) stored on the Pixelblaze, send a JSON message `{ "listPrograms": true }` over the WebSocket connection. This will prompt the Pixelblaze to return the list of pattern IDs and names. Note: Instead of a single JSON response, Pixelblaze returns the pattern list as a **text block** (one line per pattern) for memory efficiency. Each line contains the pattern's unique ID, followed by a tab character, and then the pattern's name. For example, a portion of the response might look like:

```
LjdRmpPdaZPEdbHhM	My First Pattern
8gjB89jqQojktXgc	Funky Lights
...etc...
```

Each line corresponds to a pattern (`<ID>\t<Name>`). Your code will need to read all incoming text frames and split them by newline and tab to parse the list. Pixelblaze ensures that each WebSocket frame contains whole pattern entries (no pattern line is split across frames), though a long list may arrive in multiple frames.

## Switching Patterns by ID

Every pattern on the Pixelblaze has a unique identifier string. Once you have the desired pattern's ID from the list, you can activate that pattern by sending a JSON message with the pattern ID. The command is: `{ "activeProgramId": "<pattern_id>" }`. This tells the Pixelblaze to switch to the specified pattern. For example, to load the pattern with ID `LjdRmpPdaZPEdbHhM`, you would send:

```json
{ "activeProgramId": "LjdRmpPdaZPEdbHhM" }
```

This will immediately make that pattern the active animation on the Pixelblaze (just as if you selected it in the web interface). The change is persisted as the "last used" pattern – if the device restarts, it will remember and run this pattern by default. You can send such commands repeatedly to switch to different patterns at will.

**Note:** The Pixelblaze WebSocket API primarily uses pattern IDs for selection. If you only know the pattern name, you'll need to first look up its ID from the list. (Tools like the Pixelblaze Firestorm API can accept pattern names by doing an internal lookup, but the device's native WebSocket expects the ID.)

## Python Example

Below is a simple Python example using the `websocket-client` library to retrieve the pattern list and switch to a new pattern. This assumes Pixelblaze is accessible at IP 192.168.1.50 (replace with your device's IP):

```python
import json
import websocket

# Connect to Pixelblaze WebSocket (port 81)
ws = websocket.create_connection("ws://192.168.1.50:81")

# Request the list of available patterns
ws.send(json.dumps({ "listPrograms": True }))

# Receive the response frames for the pattern list
pattern_list_text = ""
while True:
    try:
        data = ws.recv()
    except Exception:
        break  # connection closed or no more data
    if not data:
        break
    
    # Pixelblaze sends some status JSON frames too; filter those out
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
        except:
            data = data.decode('latin-1')  # decode binary as text if possible
    
    if data.startswith("{"):
        # Try to parse JSON (e.g., system info frames) and ignore for this context
        try:
            msg = json.loads(data)
            if "programList" in msg:
                # (Pixelblaze might not use this, but just in case)
                continue
        except:
            pass
        continue
    
    # Accumulate text from pattern list frames
    pattern_list_text += data
    
    # If we received the full list (e.g., end of text contains no partial line), we can break.
    # (Pixelblaze sends complete lines per frame, so breaking at end of frame is fine here.)
    if data.endswith("\n") or data.endswith("\r"):
        # Likely got a complete ending; break loop
        break

# Parse the pattern list text into (id, name) pairs
patterns = []
for line in pattern_list_text.splitlines():
    if line.strip():
        pid, name = line.split("\t", 1)
        patterns.append((pid, name))

print("Available patterns:", patterns)

# Choose a pattern (here, the first one) and send a command to activate it
if patterns:
    target_id = patterns[0][0]
    ws.send(json.dumps({ "activeProgramId": target_id }))
    print(f"Switched to pattern ID {target_id}")

ws.close()
```

In this script, after sending the `{ "listPrograms": true }` request, we continuously read from the WebSocket. We accumulate text data until we believe we've got the full list. Each incoming frame is checked: if it's JSON (the Pixelblaze may also stream status updates or acknowledgments as JSON), we skip it; if it's plain text containing tab characters, we treat it as part of the pattern list. We then split the aggregated text by lines and tabs to get the pattern names and IDs. Finally, we send another JSON message with "activeProgramId" set to one of the retrieved IDs to change the pattern.

**Note:** You may want to add error handling and more robust frame assembly depending on your use case. The Pixelblaze typically sends the whole list quickly, but if you have many patterns, consider a short delay or looping until no more pattern list frames arrive.

## JavaScript Example

In JavaScript (for example, using Node.js with the `ws` library or even in a browser environment), the process is similar. You open a WebSocket to the Pixelblaze, request the list, then parse and send the pattern selection command. Below is a concise Node.js example:

```javascript
const WebSocket = require('ws');
const pixelblazeIP = "192.168.1.50"; // change to your Pixelblaze's IP

const ws = new WebSocket(`ws://${pixelblazeIP}:81`);

ws.on('open', function open() {
    console.log("Connected to Pixelblaze");
    // Request pattern list
    ws.send(JSON.stringify({ listPrograms: true }));
});

ws.on('message', function incoming(data) {
    // Pixelblaze may send binary Buffer for preview or text for list
    let message = data.toString();
    
    if (message.startsWith("{")) {
        try {
            const msgObj = JSON.parse(message);
            console.log("Got JSON frame:", msgObj);
            return; // ignore JSON status frames for this example
        } catch (e) {
            // not JSON, continue to parse as text
        }
    }
    
    if (message.includes("\t")) {
        // Likely received (part of) the pattern list as text
        const lines = message.split("\n").filter(line => line.trim().length > 0);
        const programList = lines.map(entry => {
            const [id, name] = entry.split("\t");
            return { id, name };
        });
        
        console.log("Pattern list received:", programList);
        
        if (programList.length > 0) {
            // Activate the first pattern in the list:
            const firstId = programList[0].id;
            ws.send(JSON.stringify({ activeProgramId: firstId }));
            console.log(`Switching to pattern ID ${firstId}`);
        }
    } else {
        console.log("Received message:", message); // other non-JSON, non-list message
    }
});

// Optionally handle close/error events
ws.on('close', () => console.log("Connection closed"));
ws.on('error', err => console.error("WebSocket error:", err));
```

In this JavaScript example, we send the same `{ listPrograms: true }` request. When messages arrive, we attempt to parse JSON frames (to filter out things like periodic updates or acknowledgments). When a text message containing tab characters is encountered, we split it by newline into individual pattern entries and then by tab to separate ID and name. We log the list and then demonstrate switching to the first pattern by sending `{ "activeProgramId": <ID> }` over the WebSocket.

**Tip:** In a browser context, you can use the standard WebSocket API in JavaScript. Ensure that the Pixelblaze is either on the same network (and you use the IP directly) or that CORS is handled (Pixelblaze's WebSocket might not allow cross-origin from arbitrary websites, so running your JS from a Node script or a local HTML file is simplest).

## Limitations, Constraints, and Notes

### Pattern List Format
As noted, the pattern list is not returned as a JSON array but as **newline-delimited text** with tab-separated fields for ID and name. Your code must parse this format. Due to memory constraints on the Pixelblaze, the entire list might be split across multiple WebSocket frames (especially if many patterns are stored). However, each frame contains complete lines (it won't cut a pattern entry in half), making it easier to assemble the full list.

### Unique Pattern IDs
The pattern IDs are unique identifiers (e.g., "LjdRmpPdaZPEdbHhM") that Pixelblaze uses internally for each pattern. These IDs remain consistent unless the pattern is deleted or the Pixelblaze is factory-reset. When you switch patterns via `activeProgramId`, the selected ID is also saved as the current pattern in flash memory, meaning it will persist as the active pattern after a reboot. Ensure you use the exact ID strings from the `listPrograms` output.

### Firmware Version
The basic WebSocket API for listing and switching patterns has been consistent across Pixelblaze V3 firmware versions (and even similar for V2). Assuming you are on the latest firmware (as of 2025, e.g., 3.x), the commands above (`listPrograms` and `activeProgramId`) are supported. Newer firmware versions have introduced additional features (for example, sequencer APIs in v3.49+ that let patterns themselves advance to the next pattern, and other enhancements), but those do not change the fundamental commands for external control described here. No special enablement is needed — the WebSocket API is always available on Pixelblaze's IP port 81.

### No Direct Pattern Uploads via WS
The WebSocket API allows switching to any preloaded pattern, but it does not directly compile or upload new pattern source code from scratch. Pixelblaze's pattern code is compiled by the web IDE (browser) before being sent to the device. If you need to dynamically load new patterns (code), you would have to use workarounds (e.g. Pixelblaze's Firestorm tool or the Python library perform compilation behind the scenes, or pre-compile patterns). For simply using existing patterns, this is not a concern — just ensure the patterns you want are already saved on the Pixelblaze.

### Real-time Streaming vs. Stored Patterns
Pixelblaze also supports a streaming mode where you can send raw pixel color data in real-time (for example, to display a solid color or generate frames from a PC). This is likely how you achieved basic solid colors via WebSocket. However, running a complex pattern from the Pixelblaze's memory is much simpler – you just activate that pattern as described, and the Pixelblaze's own engine runs it. You do not need to continuously stream data for a stored pattern; the device handles it once activated.

### Continuous Data Frames
By default, Pixelblaze will stream live preview frames and status updates over the WebSocket connection (these come as binary and JSON frames at regular intervals). If you find these interfering or unnecessary for your application, you can disable updates by sending `{ "sendUpdates": false }` to the WebSocket. This will stop the continuous preview/FPS data frames. Keep in mind that if the Pixelblaze web interface is open simultaneously, it may re-enable updates automatically (the web UI toggles updates on/off as needed). In general, if you are controlling the Pixelblaze via script, it's best to close the Pixelblaze's own web UI or disable updates to reduce bandwidth.

### Concurrency
Multiple clients can connect to the Pixelblaze's WebSocket (for example, the Pixelblaze UI and your script, or multiple scripts). The Pixelblaze will accept commands from any client. However, having multiple controllers can lead to conflicts or alternating commands. If you plan to integrate into a larger setup (like home automation), consider using a single control point (or the official Firestorm gateway) to avoid overlap. Firestorm (available on GitHub) provides a REST API and can manage multiple Pixelblazes centrally.

## Tools and References

For further details and official documentation, refer to the Pixelblaze WebSocket API documentation (often called "Pixelblaze Advanced"): https://www.bhencke.com/pixelblaze-advanced. That document by Pixelblaze's creator describes the JSON and binary frames in detail. Additionally, community resources can be very helpful. The ElectroMage forums contain discussions and examples of using the WebSocket API (for example, threads on "Websocket questions" and others). Two particularly useful open-source projects to study are:

### Pixelblaze Firestorm
A Node/React-based controller for Pixelblazes that uses the WebSocket API under the hood (GitHub: https://github.com/simap/Firestorm). Firestorm's code can show how it lists patterns and issues commands (it even supports selecting patterns by name via its own logic).

### Pixelblaze Python Client
A Python 3 library that wraps the WebSocket API (GitHub: https://github.com/zranger1/pixelblaze-client). This library provides functions like `pixelblaze.getPatternList()` and `pixelblaze.setPattern()` which internally do exactly what we described (it even handles the compilation trick for new patterns). If you prefer not to write the low-level WebSocket handling yourself, you can use this library as a shortcut.

## Supporting Documentation & Discussions

- **Pixelblaze WebSocket API Documentation** (Ben Hencke's blog) – Pixelblaze Advanced: https://www.bhencke.com/pixelblaze-advanced
- **ElectroMage Forum** – WebSocket API threads: e.g., "Communicating using websockets" (Loxone support forum summary), "Using Pixelblaze for game immersion" (forum example of activeProgramId), etc. These confirm the use of `listPrograms` and `activeProgramId` for listing and switching patterns.
- **OpenHAB Community** – Pixelblaze control example: "Control LED-strip through WebSocket API" – contains a user-contributed solution and references to the Pixelblaze client library.

By following the above steps, you should be able to query your Pixelblaze V3 for its available patterns and command it to run any of those patterns via WebSocket. This allows powerful remote control – you can script pattern changes, integrate Pixelblaze into shows or home automation, or react to external events by selecting appropriate LED patterns – all in real time over the network.

## Reference Links

1. [Communicating using websockets - ENEN Loxone](https://www.loxone.com/enen/question/communicating-using-websockets/)
2. [Websocket Pattern Creation - ElectroMage Forum](https://forum.electromage.com/t/websocket-pattern-creation/3766)
3. [Pixelblaze Websockets API - ElectroMage](https://electromage.com/docs/websockets-api/)
4. [Websocket questions - Patterns and Code - ElectroMage Forum](https://forum.electromage.com/t/websocket-questions/1092)
5. [API documentation - Troubleshooting - ElectroMage Forum](https://forum.electromage.com/t/api-documentation/205)
6. [Using Pixelblaze for game immersion by watching and reacting to a Journal File - Show and Tell - ElectroMage Forum](https://forum.electromage.com/t/using-pixelblaze-for-game-immersion-by-watching-and-reacting-to-a-journal-file/2956)
7. [[SOLVED] Control LED-strip through Websocket API? - Bindings - openHAB Community](https://community.openhab.org/t/solved-control-led-strip-through-websocket-api/91533)