# Controlling Multiple Pixelblaze V3 Controllers via Raspberry Pi WebSockets

## Network Architecture for Low-Latency Multi-Controller Setup

### Single Local Network
For reliable low-latency control, ensure all Pixelblaze units and the Raspberry Pi Zero 2 W are on the same local Wi-Fi network. This avoids internet dependence and minimizes latency. Two common approaches are:

**Pi as Wi-Fi Access Point (AP):** Configure the Raspberry Pi Zero 2 W to host a Wi-Fi network (via hostapd or similar). All Pixelblaze V3 controllers connect as clients to this Pi-hosted network. This centralizes network management on the Pi and tends to be stable for multiple devices. The Pi can use a private subnet (e.g. 192.168.x.0/24) and assign IPs to Pixelblazes via DHCP. This is a recommended setup for a portable/off-grid scenario like Burning Man, as it requires no additional networking gear and keeps latency low.

**One Pixelblaze as Wi-Fi AP:** Pixelblaze controllers can run in AP mode as well. You can designate one Pixelblaze to create a Wi-Fi network (Pixelblaze AP mode) and have the Pi and the other Pixelblazes join it. In AP mode, a Pixelblaze V3 will host a network (SSID starting with "Pixelblaze_...") and is reachable at the default gateway IP 192.168.4.1. This requires minimal hardware (no external router). In fact, Pixelblaze's new sync feature was designed to work even with one Pixelblaze in AP mode hosting others. Pixelblaze's AP can support a handful of devices (in testing, up to about 5–9 devices have worked).

### Trade-offs
Using the Pi as the AP generally offers more control and potentially better throughput (since a Raspberry Pi's Wi-Fi can handle multiple clients and traffic more robustly than an ESP32-based Pixelblaze). A Pixelblaze in AP mode is convenient but could be less robust under load, since that Pixelblaze is also driving LEDs and its microcontroller handles Wi-Fi routing for multiple clients. If you only have one or two controllers, Pixelblaze AP mode may suffice; for 4 or more units, a dedicated Pi-hosted network (or a travel router) is often more stable. In any case, avoid overcrowding the Wi-Fi spectrum – use a clear channel and keep devices close to ensure strong signal (especially in an interference-prone environment like festivals).

## Addressing Pixelblazes Individually vs. Broadcast

### Individual Addressing
Once on the same network, each Pixelblaze can be addressed by its IP address. In station (client) mode, the Pixelblaze will get a DHCP IP from the Pi or AP. You can discover these IPs in several ways:

- **Pixelblaze Discovery:** Pixelblaze controllers periodically broadcast "beacon" packets advertising themselves. The Pixelblaze Python API includes a discovery utility: a PixelblazeEnumerator that listens for Pixelblaze beacon packets and maintains a list of devices. This allows you to programmatically find all Pixelblazes on the network without knowing their IPs in advance.
- **mDNS/Hostnames:** If mDNS is enabled on the Pixelblaze, it may advertise a hostname (check Pixelblaze's settings for a discovery option). In some cases Pixelblaze might support a hostname like pixelblaze.local or a variant, but if not, rely on the enumerator or assign static IPs.
- **Manual/Static IP:** In a controlled setup, you can note each Pixelblaze's IP from the Pixelblaze web UI or the router's client list, and even configure them to static IPs or use DHCP reservations so they don't change. For example: Pixelblaze1 at 192.168.0.101, Pixelblaze2 at 192.168.0.102, etc.

Each Pixelblaze runs a WebSocket server on port 81 for control. To connect, you will use a URL like `ws://<IP_address>:81` for each unit.

### Broadcasting to All
There isn't a built-in multicast or "group" WebSocket command that reaches all Pixelblazes at once – you will typically open separate WebSocket connections to each controller. To send a command to all Pixelblazes, you simply iterate over each connection (or handle them concurrently) and send the same message. For example, if you want to dim all units to 50% brightness or push a variable update to all, your code should loop through the list of Pixelblaze connections and send the command to each. The slight time stagger (on the order of a few milliseconds when done in a loop) is usually not noticeable. If precise synchronization is critical, you can send the commands in parallel (e.g. using threads or asynchronous calls) to minimize any delay between controllers.

Another option for tight sync is to leverage Pixelblaze's time synchronization features. Pixelblaze devices can sync their internal clocks over the network for coordinated animations. The Python PixelblazeEnumerator can even enable time-sync on all Pixelblazes. With synced clocks, you could send a command (like "start pattern X at timestamp T") to each Pixelblaze and have them execute in unison. However, for most use cases simply sending the same command to each device back-to-back is sufficient to "broadcast" an update.

**Example – Individual vs. All:** You might address one Pixelblaze by name or IP, e.g. `pb1 = Pixelblaze("192.168.0.101")`, and call `pb1.setBrightness(0.5)` to dim that one unit. In contrast, to dim all, do: `for pb in all_pixelblazes: pb.setBrightness(0.5)`. This explicit loop (or concurrent sends) is how you broadcast a command to all units.

## Python Libraries and Patterns for Concurrent WebSocket Control

Controlling multiple WebSocket clients in Python can be handled with either synchronous loops, multithreading, or async IO. A few approaches:

### Pixelblaze Python Client Library
The Pixelblaze community provides a convenient library `pixelblaze-client` (Python 3) to simplify control. This library abstracts the WebSocket communication behind a simple API. You can create a Pixelblaze object for each controller (passing its IP), and then call methods on those objects to send commands (e.g. `setVars`, `setActivePattern`, `setBrightness`, etc.). To manage multiple controllers, simply instantiate multiple Pixelblaze objects – one per device. For example:

```python
from pixelblaze import Pixelblaze, PixelblazeEnumerator

# Discover Pixelblaze IPs on the network (or use a known list of IPs)
devices = PixelblazeEnumerator().getPixelblazeList()
pixelblazes = [Pixelblaze(ip) for ip in devices]  # open connections to each Pixelblaze

# Broadcast an update to all Pixelblaze units:
for pb in pixelblazes:
    pb.setVars({"mode": 2})  # send JSON command to set an exported variable 'mode'
```

This library is synchronous; it handles the WebSocket communication internally. It's very straightforward for basic use. Keep in mind that Pixelblaze (ESP32) has a limit on simultaneous connections – avoid multiple redundant connections to the same device. One controller = one Pixelblaze object is a good rule (the Pixelblaze firmware can be "cranky" with too many concurrent connections, so don't, for example, keep both a Python script and the Pixelblaze web UI open indefinitely on the same unit).

### Python websockets (asyncio) or websocket-client
For more control or lightweight setups, you can use standard WebSocket libraries. The `websockets` library (asyncio-based) allows you to manage many connections asynchronously. You can `await` on multiple sends to happen concurrently. Alternatively, `websocket-client` (which pixelblaze-client uses under the hood) can be used in a multithreaded or callback style. The advantage of using these lower-level libraries is flexibility (e.g., handling incoming messages or implementing custom reconnection logic).

### Concurrent Patterns
If using the asyncio approach, you might do something like:

```python
import asyncio, websockets, json

pixelblaze_ips = ["192.168.0.101", "192.168.0.102", "192.168.0.103", "192.168.0.104"]

async def send_command(ip, message):
    uri = f"ws://{ip}:81"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(message))

# Prepare a JSON command (e.g., set a variable or change pattern)
cmd = {"setVars": {"myVar": 3.14159}}

# Send to all Pixelblazes concurrently
asyncio.run(asyncio.gather(*[send_command(ip, cmd) for ip in pixelblaze_ips]))
```

In this example, we broadcast the same `setVars` command to all four Pixelblazes simultaneously. Each connection is opened, the message is sent, and then closed. If you need persistent connections (to send continuous or frequent commands), you would likely keep the WebSocket open for each device and reuse it rather than reconnecting each time.

**Tip:** Using asynchronous IO or threads can help overlap network delays and keep latency low when sending to multiple units. However, for a small number of controllers (like 4), a simple loop sending one after the other often works fine — the delay between the first and last device might be only a few milliseconds, which is generally not perceivable. For larger numbers of devices or higher-frequency updates, consider concurrency to avoid bottlenecks.

## Constraints: Update Frequency, Latency, and Pi Zero Resource Usage

### WebSocket Throughput
Pixelblaze's WebSocket interface is designed for control commands, live coding, and streaming small amounts of data (like sensor readings or preview frames). Quick bursts of commands (toggling patterns, setting variables, etc.) are handled well. However, it's not intended for very high-bandwidth pixel-by-pixel streaming. If you tried to send full frame data to dozens of LEDs at 30–60 FPS over Wi-Fi, you'd likely hit network limits and see lag. Instead, let the Pixelblaze hardware handle the heavy lifting of rendering patterns, and use WebSocket commands to adjust parameters or synchronize events.

For typical control (changing patterns, adjusting brightness, sending sensor values or a few variables), you can send commands at modest rates (e.g. a few to tens of messages per second) with negligible impact. The Pixelblaze can even accept streamed variable updates or sensor data ~40 times a second in sync applications (the built-in sensor broadcast runs at 40 Hz). If you approach or exceed that, you may start to experience latency or buffering. In testing, sending a small JSON message ~10 times per second worked initially but slowed after many minutes due to a client library issue with ping/keepalive (the Pixelblaze appeared to queue messages). This was resolved by ensuring the WebSocket connection sends periodic pings to stay healthy. Bottom line: a Pi Zero 2 W can easily handle a handful of bytes-long messages per second to four devices. Just avoid extremely high frequencies or huge messages, and make sure your library or code maintains the connection (handles ping/pong) for long-running streams.

### Latency
On a local Wi-Fi network with few clients, one-hop latency is quite low (often <10ms). The Raspberry Pi Zero 2 W has only 2.4 GHz Wi-Fi, so in a noisy environment latency could spike if there's interference. Still, controlling 4 devices in proximity should feel instantaneous for human perception. For synchronous pattern changes (e.g., all lights change together), any small latency differences can be mitigated by syncing clocks or sending commands nearly simultaneously. If using Pixelblaze's own grouping feature, one Pixelblaze can broadcast pattern data to others in real-time with very little lag – but if you're doing it from the Pi, just try to send your commands to all controllers as close together as possible.

### Pi Zero 2 W Resource Usage
The Pi Zero 2 W, being a quad-core 1 GHz ARM with 512MB RAM, is capable of running multiple WebSocket connections and even the access point services without much issue. WebSocket control messages are lightweight (JSON text or small binary frames). CPU usage for just shuttling a few messages is minimal. Even running an async event loop or a few threads won't tax the system significantly. The main constraints to watch on the Pi would be:

- **Wi-Fi bandwidth:** The Pi's wireless chip can handle dozens of Mbps; our use-case is only a few kbps. If you were also streaming other data or running a heavy server on the Pi, ensure it doesn't saturate the Wi-Fi.
- **Networking processes:** If using the Pi as an AP, the hostapd and DHCP server will consume a bit of CPU and memory, but again, trivial for a Pi Zero 2 W given a few clients. Just ensure the Pi has a reliable power supply (especially in a mobile setup) because undervoltage can sometimes cause network instability.
- **Thermals:** In the hot environment (like direct sun in the desert), the Pi Zero could thermal throttle. It's wise to keep it shaded/ventilated. Throttling could in theory introduce latency if the CPU frequency drops, but likely not noticeable unless the Pi is doing something heavy in addition to the WebSocket control.

### Simultaneous Connections Limits
Each Pixelblaze (ESP32) can only handle a limited number of simultaneous WebSocket clients. Typically, one or two connections per Pixelblaze is fine (for example, your Pi script plus perhaps one phone connected to its web UI). More than that, and the Pixelblaze may refuse connections or behave erratically. With one Pi controlling four Pixelblazes (one connection each), you are well within safe limits. Just avoid multiple scripts or multiple Pi processes all connecting to the same Pixelblaze.

## Example Code Snippets for Managing and Broadcasting Commands

Below are simplified examples demonstrating how you might set up the connections and send commands. These use the Pixelblaze Python library for clarity:

```python
from pixelblaze import Pixelblaze, PixelblazeEnumerator

# 1. Discover Pixelblaze controllers on the network (via broadcast beacons)
enumerator = PixelblazeEnumerator()
devices = enumerator.getPixelblazeList()  # list of IP addresses of found Pixelblazes
print("Found Pixelblazes:", devices)

# 2. Connect to each Pixelblaze by IP
pixelblazes = [Pixelblaze(ip) for ip in devices]

# 3. Send a command to set a pattern or variable on each Pixelblaze
for pb in pixelblazes:
    pb.setActivePattern("Rainbow")  # switch pattern by name (needs to exist on PB)
    pb.setVars({"globalSpeed": 0.8})  # example: set an exported variable in the pattern
```

In this snippet, we use `setActivePattern()` to change the currently running pattern on each controller, and `setVars()` to broadcast a variable (perhaps adjusting a pattern's speed) across all controllers. The Pixelblaze library handles the WebSocket details for us. According to its documentation, to control multiple Pixelblazes you simply create multiple Pixelblaze objects (one per device).

### Using Async WebSockets (advanced)
If you prefer not to use the Pixelblaze helper library, you can manage the WebSocket connections directly. For example, using Python's asyncio and websockets library:

```python
import asyncio, websockets, json

pixelblaze_ips = ["192.168.0.101", "192.168.0.102", "192.168.0.103", "192.168.0.104"]

async def send_to_pixelblaze(ip, message):
    uri = f"ws://{ip}:81"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(message))

# Example command to broadcast (set a Pixelblaze variable or control)
command = {"setVars": {"brightness": 0.5}}  # JSON command to set brightness variable to 50%

# Send concurrently to all Pixelblazes
asyncio.run(asyncio.gather(*(send_to_pixelblaze(ip, command) for ip in pixelblaze_ips)))
```

This async code opens a WebSocket to each IP and sends a JSON message. The message here uses the Pixelblaze's JSON API to set a variable called brightness (assuming each Pixelblaze pattern exports such a variable). According to Pixelblaze's WebSocket API, you can send JSON frames to control aspects of the device – for example, a `setVars` frame to change exported variables, or other commands to change patterns, brightness, etc. (Changing the active pattern can be done by sending the pattern's ID or name in a JSON message as well.)

### Splitting Commands
You might not always want to send the same command to all devices. You can direct different commands to each Pixelblaze as needed. For instance, you could have Pixelblaze #1 run Pattern A while Pixelblaze #2 runs Pattern B. In your code, you'd simply target them individually:

```python
pixelblazes[0].setActivePattern("Pattern A")
pixelblazes[1].setActivePattern("Pattern B")
```

Each Pixelblaze is addressed separately via its object or connection. You can maintain a mapping of device IDs or names to IP addresses so you know which is which (e.g., Pixelblaze with IP ending .101 is "Left Wall", .102 is "Right Wall", etc.).

## Tips for Scaling Up and Handling Disconnections

### Scaling Beyond 4 Controllers
The general principles remain the same if you have 8 or 10 Pixelblazes, but the network traffic and management complexity increase. Make sure your Wi-Fi network can handle the additional devices – a Raspberry Pi 2 W as an AP should handle ~10 clients fine, but monitor for any dropout. If you encounter Wi-Fi reliability issues at larger scales, consider using a more powerful access point or mesh multiple APs (in a large area like an art installation, multiple APs on non-overlapping channels could ensure coverage). Also, logically, if you have many controllers, you might group them (e.g., send commands to subsets if not all need every update).

### Pixelblaze Group Sync
If your goal is to have all Pixelblazes show the exact same pattern in sync, you can offload some work by using Pixelblaze's built-in sync (firmware v3.40+). In that mode, one Pixelblaze can be set as a "leader" and others as followers; the leader's pattern (and even live code changes) broadcast to followers in real-time. This doesn't replace the need for a network, but it means you could issue one pattern change on the leader (via the Pi or even via the Pixelblaze UI) and all follow automatically. In an environment with spotty Wi-Fi, built-in sync might be more efficient (it sends compiled pattern data and time sync, which is optimized for Pixelblaze). However, using this feature requires pre-configuring the Pixelblazes as a group. If you prefer to manage everything from the Pi in code, you can stick to controlling each independently as discussed.

### Managing Disconnections
In a portable scenario, devices might lose power or go out of range. Your control code should handle exceptions or timeouts gracefully. For example, if a Pixelblaze drops offline, the next WebSocket send will likely raise an error or timeout. Catch these exceptions and possibly attempt a reconnect after a delay. The Pixelblaze Python library will throw a `TimeoutError` if it hasn't heard from a device in a while. You can use try/except around commands to catch this. If using lower-level websockets, you might get a `ConnectionClosed` exception. In both cases, implement a retry logic: try to reconnect a few times or flag that device as unavailable.

### Reconnection Strategy
Especially at an event like Burning Man, Wi-Fi interruptions can happen. It's wise to either run a small loop in the background to ping each Pixelblaze or use the PixelblazeEnumerator which can continuously listen and update the list of "visible" Pixelblazes. If one disappears, you can attempt to reconnect when it comes back. Writing a heartbeat (sending a trivial message or using WebSocket ping frames) can also keep the connection alive and detect drops quickly. (Note: the Pixelblaze client library issue mentioned earlier was related to ping/pong not being handled automatically; make sure whichever method you use sends WebSocket pings or some keep-alive if you maintain long connections.)

### Resource Management
Ensure you close connections when shutting down your script (e.g., call `pb.close()` on each Pixelblaze object or just let the script termination close sockets). Pixelblaze will free up the client slot when you disconnect. If you rapidly reconnect in a loop, add a small delay because too frequent connects/disconnects could overwhelm the Pixelblaze or the Pi.

### Future Expansion Considerations
If you plan to scale to dozens of Pixelblazes, consider using a purpose-built controller software like Pixelblaze Firestorm. Firestorm is a Node.js application that already handles discovering multiple Pixelblazes, synchronizing pattern changes, and providing a web dashboard and HTTP API. It's known to be reliable and lightweight, and it was designed for larger installations (it minimizes network chatter and can resend commands on dropouts). Firestorm can run on the Pi Zero 2 W, but for more than a handful of devices, a Pi 4 or laptop might be safer. Even if you don't use Firestorm, studying its approach (grouping commands, retrying on failure, etc.) can inform how you structure your Python solution.

In summary, controlling four Pixelblaze V3 units from a Pi Zero 2 W is very achievable. Use a solid local network (Pi as AP is often best), address each Pixelblaze via IP or discovery, and maintain separate WebSocket connections to each. The Pixelblaze WebSocket API gives you full control – you can change patterns, adjust brightness, or even feed sensor data in real time. Just be mindful of the update rate and ensure your code handles the multi-connection scenario robustly. With these practices, you'll have a low-latency, synchronized light show ready for the playa (or any place you take it)!

## Sources

1. [Getting Started with PixelBlaze — Ben Hencke](https://www.bhencke.com/pixelblazegettingstarted)
2. [Significant feature release: Sync multiple Pixelblazes - News and Announcements - ElectroMage Forum](https://forum.electromage.com/t/significant-feature-release-sync-multiple-pixelblazes/2891)
3. [Mesh Networking - Sync Pixelblazes - Ideas and Tips - ElectroMage Forum](https://forum.electromage.com/t/mesh-networking-sync-pixelblazes/2586)
4. [pixelblaze-client · PyPI](https://pypi.org/project/pixelblaze-client/0.9.6/)
5. [Connect Arduino UNO to Output Expander - Troubleshooting - ElectroMage Forum](https://forum.electromage.com/t/connect-arduino-uno-to-output-expander/250)
6. [How to use many Pixelblaze on a network (Sync or Firestorm) - Ideas and Tips - ElectroMage Forum](https://forum.electromage.com/t/how-to-use-many-pixelblaze-on-a-network-sync-or-firestorm/18)
7. [Pixelblaze-client: Python 3 library for Pixelblaze - Page 4 - Patterns and Code - ElectroMage Forum](https://forum.electromage.com/t/pixelblaze-client-python-3-library-for-pixelblaze/756?page=4)