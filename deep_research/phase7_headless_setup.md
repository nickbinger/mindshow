# Phase 7: Headless Setup, Control, and Networking for the Pi & Pixelblazes

## 1. Control Interface Options (User Interaction)

Since you're unsure how the installation will be controlled, here are a few approaches to consider:

• **Autonomous Operation (Playlists)**: You can pre-program the Pixelblaze controllers to run a sequence of LED patterns automatically. The latest Pixelblaze firmware allows creating playlists and shuffling patterns with smooth transitions¹. This way, the installation can run continuously without any user input, cycling through patterns on its own. If you simply want it to "just work" on the playa with minimal intervention, an autonomous playlist could be ideal.

• **Smartphone/Browser Control**: Pixelblaze has a built-in web interface accessible from any modern browser on a phone or laptop. Once the Pixelblazes and Raspberry Pi are on the same Wi-Fi network (more on network setup below), you can connect a smartphone to that network and open the control UI. If you're using the Pixelblaze Firestorm software on the Pi (which provides a centralized dashboard), it runs as a web server and detects all Pixelblaze controllers on the network². You can then use your phone's browser to access Firestorm's UI and switch patterns, adjust brightness, or trigger synchronized animations across all devices³. In practice, this means you could use your phone occasionally as a remote control – just join the Pi's Wi-Fi and browse to the Pi's IP (or a hostname) to bring up the control panel⁴. The Pixelblaze UI is mobile-friendly, and there's even a third-party app ("Pixel Lights") on app stores that interfaces with Pixelblaze controllers⁵, but using the web interface is usually straightforward.

• **Physical Controls (Buttons/Knobs)**: For simple on-site interaction without needing a phone, you might add a physical button or switch to cycle through patterns or toggle the installation on/off. This would require some wiring and code: for example, a big arcade button connected to the Raspberry Pi's GPIO could trigger a script to send a pattern-change command to all Pixelblazes (using the Pixelblaze HTTP/WebSocket API or Firestorm's API). If you prefer a hardware solution and are comfortable coding it, this can make the piece interactive for participants (e.g. "Press the button to change the lights"). Alternatively, Pixelblaze boards themselves have general-purpose input pins – if you have only one Pixelblaze or a designated "master" Pixelblaze, you could attach a potentiometer or button directly to it and use Pixelblaze's code to respond (like changing patterns or brightness). However, given you have multiple Pixelblazes coordinated, a single Pi-side button that commands all of them might be easier to manage. This option is more complex than using a phone, but it provides a tactile, immediate control method. It's an optional enhancement if you want on-playa interactivity without screens⁶.

In summary, a combination approach works well: set the system to run autonomously by default (so it doesn't need constant attention), but enable occasional overrides via phone or a simple button. That way, you have flexibility to tweak things or engage the audience without needing a full keyboard/monitor setup.

## 2. Headless Operation: Status Lights & Buttons for the Pi

Running the Raspberry Pi headless (no monitor/keyboard on the playa) means you should incorporate some basic status indicators and controls for maintenance:

• **Status LED Indicators**: It's wise to have at least one LED that indicates the Pi's status (power, boot, or network activity). The Pi's onboard red and green LEDs already convey some info (power and SD card activity), but you may want something more visible externally. A simple solution is to wire an external LED to a GPIO pin that the Pi controls via a startup/shutdown script. For example, you could use a GPIO pin that turns on or blinks when the Pi has fully booted and your software (network and Firestorm) is running, and then turns off once the Pi shuts down. One approach from the Raspberry Pi community is to set a GPIO high in a startup script (keeping an LED off via an inverter while running) and then let it go low (lighting the LED) when the OS halts – this would show a solid light only when it's safe to power down⁷. In practice, you might not need the inverter trick; simply having an LED that blinks during operation (heartbeat style) and stops when halted can suffice. Even easier: you can repurpose the Pi's TXD serial pin or ACT LED to drive an external LED – for instance, connecting an LED to the Pi's TxD (GPIO14) will naturally show activity (it goes high when the Pi is powered and active, and it drops when the Pi shuts down)⁸. Decide on a scheme that you can implement and test beforehand, so on the playa you have a visual confirmation that the Pi is running your code (and later, that it's truly shut down before you cut power).

• **Shutdown/Reset Button**: It's highly recommended to include a safe shutdown button on the Pi. This can prevent SD card corruption by allowing you to gracefully halt the Pi before cutting power (since you won't have a console attached on playa). The Pi has a built-in mechanism to handle this: if you connect a momentary push-button between GPIO3 (pin 5) and Ground (pin 6) and add `dtoverlay=gpio-shutdown` in `/boot/config.txt`⁹, a press of that button will initiate a clean shutdown⁹. This way, at the end of the night (or in an emergency), you can press the button, wait for your status LED to indicate the Pi has halted, and then safely disconnect power. You could also use a similar button (or the same one with a different press pattern) to reboot or trigger other functions, but at minimum a shutdown button is a simple and crucial addition for headless use.

• **Debug/Mode Indicator**: If feasible, you might use multiple LEDs or an RGB LED to convey different states (for example, one color for "Wi-Fi AP active", another for "Pixelblazes connected", etc.). This isn't strictly necessary, but if you anticipate troubleshooting on playa, an extra LED or two could give hints (like blinking if no Pixelblaze units are detected by Firestorm). Implementing this would require custom scripting (e.g., querying Firestorm or pinging the Pixelblazes and toggling a GPIO), so consider it optional. Often, just knowing that the Pi is up (via a power LED) is enough, since you can check the rest from your phone¹⁰.

Overall, keep the headless setup simple and robust: one button for shutdown, and one or two LEDs to reassure you that everything is powered and running. Test these in advance so you're confident they work as expected (e.g., press the shutdown button and observe that the Pi halts and any activity LED stops blinking).

## 3. Playa Network Configuration (Pi as Wi-Fi Hotspot for Pixelblaze)

On the playa you won't have an external Wi-Fi network or internet access, so your Raspberry Pi and Pixelblaze controllers must form their own local network. The recommended approach is to use the Raspberry Pi as a Wi-Fi Access Point (AP) and have all the Pixelblazes connect to that network¹¹. This creates a private Wi-Fi LAN just for your installation. Key suggestions for setting this up:

• **Use the Pi's Wi-Fi in Access Point mode**: Configure the Pi to broadcast a network (SSID) that the Pixelblaze units (and your phone, if needed) will join. The Raspberry Pi OS supports this via packages like hostapd (for the AP functionality) and dnsmasq (for DHCP service to hand out IP addresses). Follow the official Raspberry Pi documentation or a trusted tutorial to set up a standalone wireless AP. (Many guides exist – Adafruit has one, and the Raspberry Pi site's "routed wireless access point" guide is a good reference¹².) In your case, you don't need to route traffic to the internet, so it's fine to have a closed network. Just be sure to choose a 2.4 GHz Wi-Fi channel, since Pixelblaze (ESP32-based) controllers only work on 2.4 GHz Wi-Fi (they cannot do 5 GHz)¹³.

• **Ensure DHCP is working**: One common pitfall is forgetting to enable the DHCP server on the Pi's hotspot. Without DHCP, devices can connect to the Wi-Fi but won't get an IP address (leading to "Unable to obtain IP" errors on your phone or Pixelblaze). For example, one user found their Pixelblaze couldn't get an IP from a Pi-based AP until they enabled and started the dnsmasq service (the Pi documentation's steps didn't automatically enable it)¹⁴. So after installing and configuring dnsmasq, double-check that it's set to start on boot (`sudo systemctl enable dnsmasq`) and that it's handing out addresses. You can test this with a laptop or phone before heading to the playa – connect to the Pi's SSID and confirm you receive an IP (and can ping the Pi).

• **Network SSID/Password**: Set a network name (SSID) and password that you'll use for all Pixelblaze units. It's convenient to pre-configure the Pixelblazes ahead of time with this SSID and password, so they auto-connect to the Pi when it's powered on at the event. Pixelblaze provides a Wi-Fi setup portal on first boot (or if it can't find its last network)¹⁵. You can use that to join them to your Pi's network before going off-grid. Essentially, at home or during setup, configure the Pi as AP and have each Pixelblaze connect to it (or at least verify the process). Once a Pixelblaze knows the SSID/credentials, it will remember and should reconnect whenever the network is available. Having this done in advance means that on the playa, you can just power everything up and the Pixelblazes will automatically join the Pi's Wi-Fi. (If not, Pixelblaze will fall back to its own AP mode waiting for setup – indicated by an orange LED triple-blink – but we want to avoid that scenario onsite.)

• **Pixelblaze AP vs. Pi AP**: You wondered if the Pi should create the network and Pixelblazes join – yes, that's generally the best way. Pixelblaze controllers can act as an AP themselves, but they support only a few clients when in AP mode and are intended mostly for direct single connections. In fact, the Pixelblaze devs note that a Pixelblaze running as an AP can only host a limited number of devices¹⁶. Using the Raspberry Pi as the central AP will allow you to connect all your Pixelblazes and also your phone/tablet to the same network. This also simplifies synchronization – e.g., the Pi (running Firestorm) can broadcast time-sync packets and coordinate patterns to all controllers on its Wi-Fi network¹¹.

• **Number of Devices and Range**: The Pi's built-in Wi-Fi can handle several devices, but it's not unlimited. Empirically, a Raspberry Pi 3A+ was able to host around 7 Pixelblaze connections (plus a computer) before struggling¹⁷. If your project has only a handful of Pixelblazes (and maybe one phone connected at a time), the Pi AP will be fine. If you ever scaled up to, say, a dozen or more controllers, or found Wi-Fi coverage spotty across a large installation, an external travel router might be worth considering. For now, just be aware of the device count limit. Keep the Pi relatively central if possible, as it will be the Wi-Fi hub – the ESP32 Wi-Fi range is decent, but in the open playa environment you shouldn't have much interference, so it should cover your needs. You can also set the Pi's transmit power to maximum if you need a bit more range.

In summary, configure the Raspberry Pi to create a WPA2-protected 2.4 GHz hotspot, and have the Pixelblaze units pre-configured to join that hotspot. This gives you a local network with the Pi as the "router" and all Pixelblazes as clients. Once everything is connected, you'll be able to use the Pi as a controller (running Firestorm or any custom control software) to manage the LED patterns. Test this setup thoroughly at home: boot the Pi, verify it starts the AP on boot, and that Pixelblazes connect automatically and show up in the controller interface. That way, when you're on the playa with just the Pi and the Pixelblazes, you know the network will self-configure reliably.

## Final Checks and Recommendations

Before heading out, double-check a few final things:

• **Auto-start**: Configure the Pi to launch all necessary services on boot. This includes the hostapd/dnsmasq for the hotspot and the Firestorm server (if you're using it). Using a process manager like pm2 (as suggested in the Firestorm docs) can ensure Firestorm starts on boot and keeps running in case of crashes¹⁸. You won't have a keyboard/mouse to start things manually, so everything should start up automatically after power-on.

• **Testing headless workflow**: Simulate a power cycle and headless operation: turn on the Pi without any peripherals and see if you can connect with your phone to its Wi-Fi, access the interface, and see all Pixelblazes online. Also test the shutdown button in this scenario. This will give you confidence that the system can recover from power loss or reboots on the playa without intervention.

• **Ruggedization**: Since this will run in the desert environment ("on playa"), make sure your Pi and any added buttons/LEDs are enclosed or protected from dust. Use tape or hot glue to secure connections that might vibrate loose. Consider an enclosure that exposes the status LEDs and shutdown button so you can access them easily while keeping the electronics clean.

By following these suggestions, you'll have a Pi-based network that boots up headless, signals its status, and allows you to control your Pixelblaze LED installation either automatically or with on-demand inputs. This setup has been used successfully in similar projects – for instance, others have run multiple Pixelblazes synced through a Raspberry Pi Firestorm controller for art installations – so it should serve you well on the playa. Good luck, and enjoy the light show!

## Sources:

1. Pixelblaze forum – advice on running the Pi as an access point for multiple Pixelblazes¹¹'¹⁷.
2. Pixelblaze forum – troubleshooting Raspberry Pi access point and enabling DHCP (dnsmasq)¹⁴.
3. Raspberry Pi Stack Exchange – method for using a GPIO LED to indicate run/shutdown state⁷'⁸.
4. Pixelblaze Firestorm GitHub – Firestorm provides a web UI to synchronize and control patterns on all Pixelblaze units².
5. Pixelblaze Crowd Supply page – Pixelblaze's web interface can be accessed from any browser-capable device (for phone control).

### Reference Links:

• Significant feature release: Sync multiple Pixelblazes - News and Announcements - ElectroMage Forum: https://forum.electromage.com/t/significant-feature-release-sync-multiple-pixelblazes/2891

• GitHub - simap/Firestorm: Pixelblaze Firestorm is a centralized control console for Pixelblaze WiFi LED controllers: https://github.com/simap/Firestorm

• Trouble with Firestorm on a RaspberryPi - Troubleshooting - ElectroMage Forum: https://forum.electromage.com/t/trouble-with-firestorm-on-a-raspberrypi/168

• PixelBlaze (Pixel Lights) App available - ElectroMage Forum: https://forum.electromage.com/t/pixelblaze-pixel-lights-app-available/2210

• Pixelblaze V3 | Crowd Supply: https://www.crowdsupply.com/hencke-technologies/pixelblaze-v3

• power - Pi Headless: How to confirm that the Pi is shut down - Raspberry Pi Stack Exchange: https://raspberrypi.stackexchange.com/questions/22579/pi-headless-how-to-confirm-that-the-pi-is-shut-down

• External led status lights.possible? - Raspberry Pi Forums: https://forums.raspberrypi.com/viewtopic.php?t=101598

• [SOLVED] Script for a Shutdown Button? - Raspberry Pi Forums: https://forums.raspberrypi.com/viewtopic.php?t=334857

• Overview | Setting up a Raspberry Pi as a WiFi Access Point | Adafruit Learning System: https://learn.adafruit.com/setting-up-a-raspberry-pi-as-a-wifi-access-point?view=all

• PixelBlaze can't connect to Raspberry Pi Access Point - Troubleshooting - ElectroMage Forum: https://forum.electromage.com/t/pixelblaze-cant-connect-to-raspberry-pi-access-point/1962

• Pixelblaze V3 Standard: Quick Start - ElectroMage: https://electromage.com/docs/quickstart-v3-standard/

---

## Footnotes

¹ Pixelblaze playlist and pattern transition features  
² Firestorm centralized dashboard web server functionality  
³ Firestorm UI pattern switching and brightness control  
⁴ Phone browser control via Pi IP/hostname access  
⁵ Third-party "Pixel Lights" app for Pixelblaze controllers  
⁶ Physical button control for on-playa interactivity  
⁷ GPIO LED status indicator using inverter method  
⁸ TxD GPIO14 external LED activity indication  
⁹ GPIO3 shutdown button configuration with dtoverlay  
¹⁰ Phone-based status checking capabilities  
¹¹ Pi as Wi-Fi AP for Pixelblaze network configuration  
¹² Raspberry Pi AP setup documentation references  
¹³ Pixelblaze 2.4 GHz Wi-Fi limitation  
¹⁴ DHCP dnsmasq service configuration requirement  
¹⁵ Pixelblaze Wi-Fi setup portal functionality  
¹⁶ Pixelblaze AP mode device limitations  
¹⁷ Pi 3A+ device connection capacity (~7 Pixelblazes)  
¹⁸ pm2 process manager for Firestorm auto-start