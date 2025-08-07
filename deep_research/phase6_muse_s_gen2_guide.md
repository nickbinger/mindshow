# Using Muse S Gen 2 with BrainFlow and LSL for Real-Time EEG Streaming (macOS & Raspberry Pi)

## Overview of Muse S Gen 2 and Available Signals

The Muse S (Gen 2) EEG headband is a multi-sensor device that provides four channels of EEG (electroencephalography) along with additional biosignals. It includes 4 EEG electrodes (at positions TP9, AF7, AF8, TP10) plus reference sensors, a 3-axis accelerometer, a 3-axis gyroscope, and a PPG (photoplethysmography) sensor for heart rate, as well as an onboard thermistor¹. These sensors allow you to stream raw brainwave data (EEG), motion data (accelerometer/gyro), heart-rate-related data (PPG), and even temperature. The EEG signals can be processed to extract brainwave bands such as alpha (≈8–12 Hz) or beta (≈13–30 Hz) waves, which are not directly provided by the device but can be derived via filtering or FFT of the raw EEG. Below we outline how to connect to the Muse S Gen2 over Bluetooth LE (BLE) on macOS and Raspberry Pi, stream all available data using both BrainFlow and Lab Streaming Layer (LSL), and integrate the live signals into Python – for example, to drive Pixelblaze LED patterns in real time.

## Connecting to Muse S Gen 2 over Bluetooth LE (BLE)

**BLE Setup on macOS**: Ensure Bluetooth is enabled on your Mac, and have the Muse S headband charged and powered on. On macOS, no special driver is needed for BLE; you can connect directly via software (BrainFlow or muselsl). If using BrainFlow's Python API, you can simply specify the Muse board ID and (optionally) the device's MAC address or name. macOS can auto-discover a Muse if it has been paired before, but it's often easiest to supply the MAC address for reliability². You can find the Muse's MAC via the Bluetooth section of System Information (`system_profiler SPBluetoothDataType`) or by using the `muselsl list` command (from Muse LSL) to scan for devices. On macOS 12+, make sure to grant Bluetooth permissions to your Python app or terminal (in System Preferences → Security & Privacy → Bluetooth), otherwise device scanning may fail³. (Note: macOS 12.0–12.2 had known CoreBluetooth issues; update to 12.3+ to avoid BLE scanning problems⁴.)

**BLE Setup on Raspberry Pi Zero 2 W (Linux)**: The RPi Zero 2 W has built-in BLE, but Linux may require additional setup. First, install BlueZ utilities (`sudo apt-get install bluetooth bluez libbluetooth-dev`) and ensure the Bluetooth service is running. It's recommended to get the Muse's MAC address (e.g. using `bluetoothctl scan` or via muselsl on another device) since on Linux BrainFlow cannot auto-discover by name and needs a MAC for direct BLE connections⁵. When using BrainFlow on Linux, you may need to compile it with BLE support (as the pre-built Python wheel might not include BlueZ support). BrainFlow documentation suggests installing the D-Bus dev package (`libdbus-1-dev`) and building from source with the `--ble` flag to enable Linux BLE support⁶. Alternatively, BrainFlow offers a BLED112 USB dongle method: if you have a Silicon Labs BLED112 dongle, you can plug it into the Pi and use the Muse BLED board IDs, which communicate via a serial COM port without needing BlueZ⁷. This can simplify connection issues, though it requires additional hardware.

**BLE Pairing**: For Muse devices, you typically do not need to formally pair the headband through the OS Bluetooth settings (in fact, Muse may not show up in the standard pairing UI). The connection is usually handled at the application level via BLE. If you use LSL (muselsl) or BrainFlow's direct BLE, they will scan and connect without manual pairing. However, for some BLE APIs on Linux, having the device bonded/paired can help discovery. If you encounter difficulties on Linux, you can try pairing via bluetoothctl (put Muse in pairing mode, trust and pair it), then use its MAC in your program⁸. On Windows (for reference) there is a tool called BlueMuse GUI for connecting Muse to LSL, but on macOS/Linux the muselsl Python package is the recommended approach for LSL⁹.

**Connection Procedure**: To connect via BrainFlow, create a BrainFlowInputParams object and set the appropriate fields. For direct BLE on Muse S Gen2, use the board ID `BoardIds.MUSE_S_BOARD` (which uses native BLE) and set `params.mac_address` to your Muse's MAC (optional but recommended on Linux)¹⁰. If you were using the BLED112 dongle route, you'd instead use `BoardIds.MUSE_S_BLED_BOARD` and set `params.serial_port` to the COM port (e.g. `/dev/ttyACM0`) of the dongle¹¹. For Muse LSL (muselsl), installation is via pip (`pip install muselsl`). You can then use the command-line interface: for example, run `muselsl list` to see available Muse devices, then start a stream with `muselsl stream --address <MAC>` or `muselsl stream --name <Name>`¹². The muselsl tool will handle the BLE connection using the Bleak backend. If you prefer to do it in code, the muselsl library provides a stream() function – you can call `muselsl.stream(address=MAC, ppg_enabled=True, acc_enabled=True, gyro_enabled=True)` to start streaming all data types (EEG, PPG, Accel, Gyro) to LSL¹³.

## Verifying Connection and Signal Status

Once the Muse is connected, verify that data is actually flowing:

• **LED Indicator**: Muse S has a status LED (usually white) that blinks when searching. It should turn solid (or change blink pattern) once a BLE connection is established (for example, when muselsl or BrainFlow connects). This is a quick visual confirmation of connection.

• **Software Output**: In BrainFlow, after calling `board.start_stream()`, you can check if data is arriving by calling `board.get_current_board_data(samples)` periodically. If you see non-zero values changing over time (especially in EEG channels), the stream is live. BrainFlow's logger can be enabled (`BoardShim.enable_dev_board_logger()`) to print connection messages and any errors. In muselsl, you can open a new terminal and run `muselsl view` which launches a real-time EEG graph; if the plot shows moving waveforms for the 4 EEG channels, you have a good connection¹⁴.

• **Quality Checks**: Muse headbands don't provide explicit "contact quality" values per electrode in the open SDK, but you can infer quality by the signal characteristics. A properly worn Muse should show EEG traces that respond to blinks or jaw clenches (large spikes from muscle artifacts) and relatively stable baselines. If all EEG values are near-zero or very noisy (random spikes), check electrode placement and moisture (the Muse S uses dry electrodes; slight dampening on forehead sensors can improve contact). Also verify that the device isn't in standby (Muse will go to sleep if no client is connected). For PPG, you should see a pulsatile waveform around 64 Hz sampling rate – if flat, the LED/photodiode may not be making contact. Accelerometer/gyro should show changes when you move or rotate the device.

• **Device Info**: Neither muselsl nor BrainFlow's Muse API provide battery status in the main data stream by default, but BrainFlow's ancillary data stream can include battery and temperature for some boards¹⁵. If needed, you can retrieve battery level by periodically sending an OSC message via the Muse SDK (outside BrainFlow/LSL) or by reading from the BLE GATT if known – however, this is advanced. For basic verification, ensure the Muse is charged (check in the official Muse app beforehand).

If connection fails: on macOS, re-check Bluetooth permissions and that no other app (e.g. Muse app or BlueMuse on another machine) is currently connected to the headband. On Raspberry Pi, ensure you ran the program as root or gave the Python process BLE access (one trick: `sudo setcap 'cap_net_raw,cap_net_admin+eip' $(which python3)` to allow BLE scans without sudo). If using BrainFlow and it times out scanning, consider using the BLED112 dongle or the muselsl approach as a troubleshooting step.

## Streaming Data with BrainFlow (Python)

BrainFlow provides a unified Python API to start the Muse stream and read data in real-time, without needing a separate LSL process¹⁶. Once you've set up the BoardShim for the Muse S, the usage pattern is:

### 1. Initialize Board:

```python
from brainflow import BoardShim, BrainFlowInputParams, BoardIds

BoardShim.enable_board_logger() # optional: see logs
params = BrainFlowInputParams()
params.mac_address = "XX:XX:XX:XX:XX:XX"
# Muse Bluetooth MAC (optional on macOS)
board = BoardShim(BoardIds.MUSE_S_BOARD, params)
board.prepare_session() # initialize BLE connection
```

This will scan and connect to the Muse. (If you built BrainFlow with BLED112 support and want to use the dongle, you'd set `BoardIds.MUSE_S_BLED_BOARD` and `params.serial_port` instead¹⁷.)

### 2. Start Stream:

```python
board.start_stream(3600) # start streaming with a buffer of 3600 samples
# (for example)
```

At this point the Muse is actively streaming data into an internal ring buffer. You can now retrieve data as needed.

### 3. Retrieve Data: 

BrainFlow gives data as a NumPy array (channels x samples). You can use `BoardShim.get_board_data()` to fetch all accumulated data or `get_current_board_data(n)` to fetch the last n samples. For continuous acquisition, you might loop calling `get_current_board_data` at a certain interval. The channel layout for Muse can be obtained via BrainFlow's API (e.g. `BoardShim.get_eeg_channels(board_id)` returns indices of EEG channels). Typically, Muse's 4 EEG channels will be indexed, followed by accelerometer, gyroscope, PPG, etc., depending on presets. By default, BrainFlow's Default preset includes EEG channels¹⁸, Auxiliary preset includes accel/gyro¹⁹, and Ancillary preset is used for PPG (and possibly battery/temp)²⁰. **Important**: For Muse S, PPG and the 5th EEG channel (if available) are not enabled by default. You must send a configuration command to the board after starting the stream:

To enable the Muse's PPG sensor data stream, call:
```python
board.config_board("p61")
```

This command tells the Muse to start sending PPG data (and on Muse S Gen2, this likely also activates the on-board SpO2 sensor LED)²¹.

To enable the Muse's 5th EEG channel (the auxiliary EEG channel on the forehead reference, if supported), call:
```python
board.config_board("p50")
```

On Muse 2/Muse S devices, "p50" is a command that enables an extra EEG channel (and in some models also activates PPG on Muse 2)²². On Muse S Gen2, BrainFlow indicates "p50" enables the fifth EEG channel, and "p61" enables PPG²³. It's good practice to issue these `config_board` commands after starting the stream, then wait a second or two for the new data types to appear.

### 4. Use the Data: 

Once you have raw data arrays, you can process them. EEG data will be in microvolts (not scaled to 0-1; typically in tens of μV range). You might filter the EEG to specific bands; BrainFlow has built-in DSP functions (e.g. bandpass filters, FFT, band power calculations)²⁴. For example, to compute alpha band power on each channel you could use BrainFlow's DataFilter methods or export data to MNE/PySight. Accelerometer is typically in units of g's (±4g range) and gyro in deg/sec. PPG data from Muse provides a waveform from which heart rate can be derived (by peak detection). BrainFlow does not automatically compute HR, so you'd need to analyze the PPG signal (e.g. count peaks per minute).

### 5. Stopping and Releasing: 

When finished, call `board.stop_stream()` to halt data acquisition and `board.release_session()` to disconnect the BLE link and free resources.

**Note**: BrainFlow's integration means you don't separately run an LSL app – it's all in your Python process²⁵. This allows you to send commands to Muse (as shown) and get data in one program. One limitation is that only one process can own the BLE connection at a time. If you need to share data with multiple consumers, you can combine approaches: e.g. use BrainFlow to grab data then send it out via LSL yourself (see [OpenBCI forum example of BrainFlow → LSL][1]).

## Streaming Data with Lab Streaming Layer (LSL) – Muse LSL

Muse LSL (the muselsl project²⁶) is a convenient way to stream Muse data into the Lab Streaming Layer, which is a standard for sharing time-synchronized data streams between applications. The muse-lsl tool essentially acts as a bridge: it connects to the Muse over BLE and creates named LSL streams for EEG and other signals. This is useful if you want to use existing LSL-compatible software (like recording tools or VR applications) or if you prefer a decoupled architecture.

To use Muse LSL on macOS or Raspberry Pi, install the Python package as noted above and run the muselsl commands. By default, `muselsl stream` will stream EEG data. You can enable additional streams with flags: `--ppg`, `--acc`, `--gyro` to stream photoplethysmograph, accelerometer, and gyroscope data, respectively²⁷. For example:

```bash
muselsl stream --address <Muse_MAC> --ppg --acc --gyro
```

This will create several LSL streams, typically named `Muse` (for EEG), `PPG`, `Accelerometer`, and `Gyroscope`²⁸. Each stream has its own sampling rate (EEG ~256 Hz, PPG ~64 Hz, ACC/Gyro ~52 Hz) and channel format. Once the stream is up, you can use the LabRecorder tool to save data or write a custom client. In Python, you'd use the pylsl library to grab samples. For example:

```python
from pylsl import StreamInlet, resolve_byprop

# Resolve EEG stream
streams = resolve_byprop('name', 'Muse', timeout=5) # or use type='EEG'
inlet = StreamInlet(streams[0])
sample, timestamp = inlet.pull_sample()
print(sample) # e.g. [EEG1, EEG2, EEG3, EEG4, AUX] values
```

You would similarly resolve the PPG stream or others by name or type (`type='PPG'`). The EEG stream from muselsl typically includes 5 channels: the four EEG electrodes plus one AUX channel which might carry relative reference or other info (for Muse 2/S, the AUX channel is often unused for EEG data but is present for compatibility). The muselsl documentation confirms that for Muse 2, once PPG/ACC/Gyro are enabled via arguments, each gets its own LSL stream named accordingly²⁹.

One caveat of using LSL is that it's a separate process producing the data. You must keep the muselsl stream running continuously; if it stops, the streams end. Also, to issue any device config commands (like enabling PPG on older Muse hardware), you'd need that implemented in muselsl – fortunately, muselsl automatically enables PPG on Muse 2 when you use `--ppg` (it handles the BLE command internally). The LSL approach cannot send dynamic commands to the Muse once streaming (aside from the startup flags), whereas BrainFlow could send commands at runtime³⁰.

**Verifying LSL Streams**: You can use the `muselsl view` GUI to see EEG traces live³¹. Additionally, tools like LSL Explorer or LabRecorder (if installed) will show the available streams and their data rates. On a Raspberry Pi, running the viewer might be heavy, so instead you could do a quick Python script with pylsl to print one sample per second from each stream as a sanity check.

## Accessing Raw Data and Derived Metrics (EEG Bands, PPG, etc.)

**Raw EEG**: The raw EEG values from Muse are in microvolts (μV). They often appear as a baseline around 0 with fluctuations in the tens of μV (depending on reference). To extract specific brainwave bands like alpha or beta waves, you will need to apply filters or Fourier transforms on the raw EEG signal. For example, to get alpha waves in real time, you might band-pass filter 8–12 Hz and measure the amplitude (e.g., via a rolling RMS or bandpower calculation). BrainFlow's API provides convenience functions for bandpower – you can use `DataFilter.perform_bandpass()` to filter signals and even `DataFilter.get_psd_welch()` to get the power spectral density, then sum the band of interest. Muse LSL doesn't come with analysis functions, so you'd use libraries like SciPy, MNE, or BrainFlow (BrainFlow can also operate on arrays you supply, not just live data). Keep in mind EEG band values are relative and can be noisy; often you'll compute a ratio or compare to baseline rather than using absolute μV values.

**Accelerometer and Gyro**: Muse's accel/gyro data can be used to detect motion or head orientation. The accelerometer is 3-axis with ~52 Hz sampling; values correspond to acceleration in g's (with 1g when stationary due to gravity). The gyroscope gives angular velocity in deg/sec. These can be used for artifact rejection (e.g., large motion spikes in EEG) or for driving visuals. For instance, you could tilt your head and have that tilt angle control LED color on the Pixelblaze. In BrainFlow, accel and gyro channels are accessible via the Auxiliary preset data³². In LSL, they're separate streams with 3 channels each.

**PPG (Heart Rate)**: The Muse S Gen2 includes a PPG sensor with three LEDs (likely IR, red, green) at 64 Hz³³. The raw PPG signal is a waveform reflecting blood volume changes. To get heart rate (HR), you'll need to detect beats in this waveform. A simple approach is to bandpass filter the PPG around 1–3 Hz (60–180 BPM) and use a peak finding algorithm to identify pulse peaks, then compute the time between peaks. There are open-source heart rate algorithms (e.g., in NeuroKit or HeartPy) that could be applied to the PPG data stream. Keep in mind that if the Muse is worn on the head, PPG is typically measured on the forehead and can be sensitive to motion and fit. The Muse SDK combines PPG from IR and red for accuracy; with raw data, you might have to experiment. BrainFlow will give you the raw PPG channel (once enabled via p61 command as described) in the ancillary data³⁴. Muselsl will stream whatever PPG channel the device provides (for Muse 2 it was one channel waveform).

**Derived Metrics**: Some Muse apps provide metrics like "concentration" or "relaxation" which are proprietary. With BrainFlow, you could utilize their built-in classifiers or metrics if available (BrainFlow has some pre-trained models for focus/relax but they might be geared to OpenBCI). Otherwise, you can create your own metrics from combinations of band powers (e.g., alpha/theta ratio, etc.). This is beyond the scope of just streaming, but be aware of the capability.

## Feeding Muse Data into Pixelblaze for LED Control

**Pixelblaze Overview**: Pixelblaze is a WiFi-enabled LED controller with a scripting engine for LED patterns. It allows real-time input via WebSocket messages containing variables that the pattern code can use. To integrate brain signals with Pixelblaze, you'll stream data into Python (via BrainFlow or LSL as above), then send the relevant metrics to the Pixelblaze over the network.

**Exporting Variables on Pixelblaze**: In your Pixelblaze pattern code, you should define one or more variables (using the export keyword in Pixelblaze's JS-like language) that will represent the EEG metrics. For example, in the Pixelblaze pattern you might have:

```javascript
export var alphaLevel = 0.0;
export var headTilt = 0.0;
```

These exported globals can be set from external code via the Pixelblaze WebSocket API³⁵. Ensure your Pixelblaze is powered on and connected to the same WiFi network as the Raspberry Pi or Mac.

**Using the Pixelblaze WebSocket API**: The Pixelblaze listens on a websocket (port 81 by default) for JSON frames. The format to set variables is a JSON object with a setVars key. For example: `{"alphaLevel": 0.5, "headTilt": 0.1}` when sent to the Pixelblaze will update those exported variables in the currently running pattern. You can implement the WebSocket client yourself (using Python's websocket-client library) or use a helper library like pixelblaze-client in Python. The Pixelblaze Python client by ZRanger1 simplifies connecting and sending data – after installing it (`pip install pixelblaze-client`), you can do something like:

```python
from pixelblaze import Pixelblaze

pb = Pixelblaze("Pixelblaze_IP_address") # or hostname
# Now pb.setVars can be used to send variables:
pb.setVars({ "alphaLevel": 0.8, "headTilt": 0.2 })
```

Under the hood, this sends the appropriate WebSocket JSON frame to the Pixelblaze³⁶. If not using the library, you'd manually open a websocket and send a JSON string like `{"setVars":{"alphaLevel": 0.8}}`³⁷. The Pixelblaze documentation notes that you should only send variables that are exported in the pattern; otherwise they'll be ignored³⁸. Also, if your pattern code continuously overwrites the exported variable internally, external setVars calls would be overridden (so in the pattern, don't reassign the exported var every frame).

### Code Example – Muse to Pixelblaze:

Below is a conceptual example tying it all together (for brevity, it uses BrainFlow for data and a simple alpha power calculation):

```python
from brainflow import BoardShim, BrainFlowInputParams, BoardIds, DataFilter, FilterTypes
from pixelblaze import Pixelblaze
import numpy as np

# Connect to Muse S Gen 2
params = BrainFlowInputParams()
params.mac_address = "AA:BB:CC:DD:EE:FF" # Muse MAC
board = BoardShim(BoardIds.MUSE_S_BOARD, params)
board.prepare_session()
board.start_stream(45000) # 125s buffer @ 256Hz
board.config_board("p61") # enable PPG

# Connect to Pixelblaze
pb = Pixelblaze("192.168.1.50") # use your Pixelblaze's IP

# Main loop: read EEG and send alpha power to Pixelblaze
eeg_channels = BoardShim.get_eeg_channels(BoardIds.MUSE_S_BOARD)
while True:
    data = board.get_current_board_data(256) # 1 second of data
    if data.shape[1] < 256:
        continue # not enough data yet
    
    # Compute alpha power on one channel (e.g., AF7 which is eeg_channels[1])
    eeg = data[eeg_channels[1]]
    # Band-pass filter 8-12Hz
    DataFilter.perform_bandpass(eeg,
        BoardShim.get_sampling_rate(BoardIds.MUSE_S_BOARD), 10.0, 4.0, 4,
        FilterTypes.BUTTERWORTH.value, 0)
    # Simple power estimate
    alpha_power = np.sqrt(np.mean(np.square(eeg)))
    
    # Normalize alpha_power (e.g., 0.0 to 1.0 range expected by Pixelblaze)
    level = float(np.clip(alpha_power/100.0, 0.0, 1.0))
    pb.setVars({"alphaLevel": level})
    
    time.sleep(0.1)
```

In this pseudocode, we continuously send an `alphaLevel` variable to Pixelblaze about 10 times per second. On the Pixelblaze side, the pattern can use the global `alphaLevel` to modulate brightness, color, or effects. For example, a breathing glow that gets stronger with higher alpha amplitude (which might correlate with a relaxed state if eyes are closed).

### Best Practices for Driving Pixelblaze:

- **Rate Limiting**: Do not send data to Pixelblaze at the full 256 Hz EEG rate. Pixelblaze can handle many updates, but there's no need to update LEDs faster than ~20–30 Hz. Use a timer or send updates when you have meaningful changes. In the example above we used 0.1s sleep (~10 Hz updates).
- **Smoothing**: Brain signals are noisy. Use smoothing or averaging to make LED responses more visually pleasant. For instance, you could use a rolling average of the last N seconds of alpha power to avoid rapid flicker. Pixelblaze patterns themselves can also interpolate changes if coded accordingly.
- **Scaling**: Map the signal to a useful range. EEG power numbers might be, say, 0–1000 μV^2 for raw band power. Map or normalize these to 0.0–1.0 or to the range of the effect you want. It often helps to impose a floor and ceiling (clamp extreme values) so outliers don't cause huge jumps.
- **Multiple Inputs**: You can send multiple variables – e.g., `alphaLevel` and `betaLevel`, or perhaps `blinkDetected` as a binary flag. Pixelblaze patterns can react to each. Focus on a simple mapping at first (one signal to one visual parameter) before combining too many.
- **Network Considerations**: Ensure the WiFi network latency is low; Pixelblaze's WebSocket is reasonably fast on a LAN. If using a Raspberry Pi, having it on WiFi along with Pixelblaze is fine, but minimize other network load for best real-time performance. The Pixelblaze-client library handles reconnections if the socket drops, but you should still handle exceptions (e.g., if Pixelblaze reboots or network issues occur).
- **Pixelblaze Pattern Logic**: Write your Pixelblaze pattern to use the variables intelligently. For example, if `alphaLevel` is 0 to 1, you might make LED color shift from blue to green as alpha increases, or brightness pulse with heart rate (if you also detect heart rate from PPG). Use Pixelblaze's `time()` or `wave()` functions combined with variables for creative effects. Remember that any variables set from outside are essentially global state for the pattern.

## OS-Specific Caveats and Known Issues for Muse Gen 2

• **macOS Bluetooth Permissions**: As mentioned, on macOS 12+ you must grant your Python process Bluetooth permission³⁹. If you see errors opening BLE or no devices found, check the macOS security settings. This is a common stumbling block.

• **Linux BlueZ Issues**: On Raspberry Pi OS (Linux), you may need to run as root or give capabilities to use BLE. If you get permissions errors or BlueZ DBus errors, ensure `libbluetooth-dev` was installed before building BrainFlow, and that you have the proper permissions. The BrainFlow docs also mention installing `libdbus-1-dev` and recompiling if needed⁴⁰. In some cases, using the BLED112 dongle can bypass BlueZ issues since it uses a serial API (but it requires buying that dongle).

• **BrainFlow Version and Build**: Make sure you're using a recent BrainFlow version that supports Muse S Gen2. Early BrainFlow (circa 2020) did not support Muse; support was added around BrainFlow v4.3 for Muse 2/S via BLED112⁴¹. Full native BLE support on Mac/Linux came later, so using the latest (BrainFlow 5.x) is recommended. If you installed via pip and it doesn't work on Pi (perhaps no prebuilt wheel for ARM), you might need to build from source on the Pi.

• **Muse LSL on Pi Zero**: The Pi Zero 2 W is relatively low-power. Running muselsl on it is possible (especially since it has BLE and enough CPU), but if you run a heavy viewer or try to do FFT analysis on the Pi, you may hit performance limits. It's wise to offload processing (e.g., send raw data to a more powerful computer via network/LSL, or use BrainFlow's efficient C++ backend for filters). The Pi Zero 2 W is quad-core but only ~1 GHz – still, it can handle streaming and some light processing.

• **BLE Connectivity**: BLE can sometimes drop out, especially in RF-noisy environments. If the Muse disconnects, BrainFlow's `start_stream` will throw an error or stop delivering data. You should implement reconnection logic – e.g., in BrainFlow catch exceptions and call `prepare_session` again, or in muselsl just rerun the stream. Also, keep the Muse fairly close to the receiver, especially with the Pi (the Pi Zero's tiny antenna isn't long-range).

• **Muse S vs Muse 2 Differences**: The Muse S Gen 2 is very similar to Muse 2 in terms of data streams. One difference is Muse S has fabric electrodes and is designed for sleep, but for developers the main difference is that Muse S can be worn comfortably longer. Technically, Muse S (Gen2) supports the same 4 EEG channels and a PPG, and also includes a gyroscope which the older Muse 2016 did not. Just be aware that any Muse-specific quirks (like the "drift" in gyro baseline or slight timing jitter in BLE) apply equally.

• **No Onboard Notch Filter**: Muse devices do not apply a 50/60 Hz notch filter to EEG⁴². If you are in an environment with mains power noise, you may want to apply a notch filter in software to the EEG to remove that hum. BrainFlow's DataFilter can do notch filters; for instance, `perform_bandstop` at 50 or 60 Hz if needed.

• **Battery Life**: Streaming all channels (especially PPG with three LEDs) will use battery faster. A Muse S Gen2 might last around 5-6 hours streaming EEG alone, but if you enable PPG and gyro, expect less. Plan to have it charged or plugged in if doing long sessions. Also, if battery is very low, the signal quality might degrade or device may disconnect unexpectedly – so for important sessions, start with a full charge.

## References and Resources

• Muse LSL (muselsl) GitHub repository – Python tools for streaming Muse via LSL: https://github.com/alexandrebarachant/muse-lsl

• BrainFlow Documentation – Supported Boards (Muse) (details on Muse S, required drivers, presets): https://brainflow.readthedocs.io/en/stable/SupportedBoards.html#muse

• BrainFlow vs LSL – Blog post by BrainFlow creator on differences: https://brainflow.org/2021-02-05-lsl-review/

• Pixelblaze official site (ElectroMage) – info on Pixelblaze and docs links: https://electromage.com/pixelblaze

• Pixelblaze WebSocket API documentation ("Pixelblaze Advanced" by Ben Hencke): https://www.bhencke.com/pixelblaze-advanced (WebSocket control, setVars usage)

• Pixelblaze Python client (pixelblaze-client) on PyPI – for controlling Pixelblaze via Python: https://pypi.org/project/pixelblaze-client/

• Muse S Gen2 Technical Specs (Muse product comparison/tech specs PDF): https://choosemuse.com (see Muse S product page and linked spec sheet for Gen1, similar to Gen2 specs)

• Lab Streaming Layer (LSL) documentation and community: https://labstreaminglayer.org/ (general info on LSL for multi-device synchronization).

• GitHub - abram0v1ch/Mood-hat: https://github.com/abram0v1ch/Mood-hat

• Muse 101 — How to start Developing with the Muse 2 right now | by Anush Mutyala | Medium: https://anushmutyala.medium.com/muse-101-how-to-start-developing-with-the-muse-2-right-now-a1b87119be5c

• Supported Boards — BrainFlow documentation: https://brainflow.readthedocs.io/en/stable/SupportedBoards.html

• GitHub - alexandrebarachant/muse-lsl: Python script to stream EEG data from the muse 2016 headset: https://github.com/alexandrebarachant/muse-lsl

• BrainFlow vs LSL: https://brainflow.org/2021-02-05-lsl-review/

• Pixelblaze Language Reference - ElectroMage: https://electromage.com/docs/language-reference/

• Master-Slave Pixel Blaze Wireless control - #4 by wizard - ElectroMage Forum: https://forum.electromage.com/t/master-slave-pixel-blaze-wireless-control/65/4

• pixelblaze-client · PyPI: https://pypi.org/project/pixelblaze-client/0.9.6/

• BrainFlow 4.3.0: https://brainflow.org/2021-06-22-muse-bled/

---

## Footnotes

¹ Muse S Gen2 includes temperature sensor and thermistor
² macOS BLE auto-discovery with MAC address reliability
³ macOS 12+ Bluetooth permission requirements
⁴ macOS 12.0-12.2 CoreBluetooth issues
⁵ Linux BrainFlow MAC address requirement for BLE
⁶ BrainFlow Linux BLE compilation requirements
⁷ BLED112 dongle alternative for Linux
⁸ Linux bluetoothctl pairing procedure
⁹ muselsl as recommended LSL approach for macOS/Linux
¹⁰ BrainFlow MUSE_S_BOARD configuration
¹¹ BLED112 dongle BoardIds configuration
¹² muselsl command-line interface usage
¹³ muselsl Python API stream function
¹⁴ muselsl view for EEG visualization
¹⁵ BrainFlow ancillary data stream capabilities
¹⁶ BrainFlow unified Python API
¹⁷ BLED112 board ID alternative
¹⁸ BrainFlow Default preset for EEG channels
¹⁹ BrainFlow Auxiliary preset for accel/gyro
²⁰ BrainFlow Ancillary preset for PPG
²¹ p61 command for PPG activation on Muse S Gen2
²² p50 command for 5th EEG channel on Muse 2/S
²³ BrainFlow p50/p61 command documentation
²⁴ BrainFlow built-in DSP functions
²⁵ BrainFlow single-process integration
²⁶ muselsl project reference
²⁷ muselsl streaming flags for additional sensors
²⁸ LSL stream naming convention
²⁹ muselsl documentation for Muse 2 streams
³⁰ LSL vs BrainFlow runtime command capabilities
³¹ muselsl view GUI functionality
³² BrainFlow Auxiliary preset data access
³³ Muse S Gen2 PPG sensor specifications
³⁴ BrainFlow ancillary data PPG access
³⁵ Pixelblaze WebSocket API for exported variables
³⁶ Pixelblaze Python client WebSocket implementation
³⁷ Manual WebSocket JSON format
³⁸ Pixelblaze exported variable requirements
³⁹ macOS 12+ Bluetooth permission requirements
⁴⁰ Linux BrainFlow compilation dependencies
⁴¹ BrainFlow v4.3 Muse support introduction
⁴² Muse devices lack onboard notch filtering