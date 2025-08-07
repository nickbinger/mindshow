# Areas Lacking Context in the Codebase

## Pixelblaze Integration
*Files: robust_websocket_controller.py & LED control code*

### Missing or Unclear Context
How the Pixelblaze is configured and controlled is not fully explained. For example, the code assumes a Pixelblaze WebSocket connection (port 81) but doesn't clarify how to obtain the device's IP or switch patterns. It's unclear how the system selects or loads Pixelblaze patterns, or how variables on Pixelblaze are linked to brainwave data.

### Additional Info That Would Help
Provide context on setting up the Pixelblaze (network configuration, obtaining its IP address), and instructions for managing patterns. For instance, explain how to retrieve a list of available Pixelblaze patterns and switch between them via WebSocket, and note that patterns must export variables (like speed, color, brightness) for external control. Code comments or docs should illustrate example JSON commands for changing patterns and setting variables, so developers know how to extend or modify patterns.

---

## Muse S Gen 2 Headband Connection
*Files: test_muse_discovery.py & Muse init in stable_unified_system.py*

### Missing or Unclear Context
The process for connecting to and using the Muse S Gen 2 EEG headband lacks detail. The repository doesn't clearly state which library or method is used to acquire Muse data (BrainFlow, Muse LSL, or another). There's no explanation of how to pair the headband or ensure a BLE connection. A new developer might be unsure if any special dongles or OS-specific steps are needed to get data streaming from the Muse.

### Additional Info That Would Help
Add documentation or comments about the Muse connection procedure. For example, clarify whether the code uses BrainFlow's BLE interface or an LSL stream to get data from the Muse. Include steps to pair the Muse S Gen 2 (ensuring the device is in pairing mode and BLE is enabled on the host) and how to verify the signal. It would help to mention any prerequisites (like needing the Muse app or a specific BLE adapter on certain platforms) and how the code discovers the Muse (e.g., by name or MAC address). This extra context ensures developers know how to set up the headband and troubleshoot connection issues.

---

## BrainFlow / Muse LSL EEG Implementation

### Missing or Unclear Context
The choice and setup of the EEG data pipeline (BrainFlow vs. Muse LSL) is not clearly documented in the code. The project references both BrainFlow and MuseLSL, but it's unclear which is currently implemented or how to switch between them. There's no in-code guide on configuring BrainFlow (board IDs, parameters for Muse S) or on running an LSL stream. A developer might not know how to enable one method or the other, or what adjustments are needed for each.

### Additional Info That Would Help
Include a short guide on EEG data integration within the code or docs. For instance, if using BrainFlow, note how to initialize it for Muse S Gen 2 (which BrainFlow board ID to use, any MAC address or dongle required, etc.), and how to install BrainFlow's Python package on the system. If using Muse LSL, provide instructions on setting up the LSL stream (for example, using the muselsl library or a Muse mobile app to broadcast EEG data). Clarify in comments or a config switch how to select between BrainFlow and LSL modes. This additional context would help others understand how to get EEG data flowing into the system and adjust the implementation if needed.

---

## Raspberry Pi Zero 2 W Setup & Deployment

### Missing or Unclear Context
There is no documentation on deploying this project to a Raspberry Pi Zero 2 W, despite it being a planned phase. Developers lack guidance on OS setup, required configurations, or performance considerations for the Pi. Important details like enabling Wi-Fi/Bluetooth, installing dependencies on ARM, or optimizing for the Pi's limited resources are not mentioned. Without this, it's unclear how to replicate the development environment on the Pi or what modifications might be needed.

### Additional Info That Would Help
Provide a setup guide specific to the Pi Zero 2 W. This should cover selecting and installing a suitable OS (e.g. Raspberry Pi OS Lite 32-bit vs 64-bit), enabling Bluetooth and any necessary BLE permissions for the Muse, and installing project dependencies (BrainFlow, WebSocket libraries, etc.) on ARM architecture. Include any configuration tweaks (like using a static IP or mDNS for Pixelblaze discovery on the Pi's network, or adjusting performance settings given the Pi's CPU/RAM constraints). Also, note any steps for running the system on boot (for example, using a systemd service or cron job). Such context will help developers successfully deploy and run the project on a Pi Zero 2 W without guesswork.