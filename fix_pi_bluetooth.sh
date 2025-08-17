#!/bin/bash

# Fix Bluetooth on Raspberry Pi Zero
echo "Fixing Bluetooth on Pi Zero"
echo "============================"

# 1. Reset Bluetooth
echo "1. Resetting Bluetooth..."
sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
sleep 2

# 2. Reset the adapter
echo "2. Resetting adapter..."
sudo hciconfig hci0 down
sudo hciconfig hci0 reset
sleep 1
sudo hciconfig hci0 up
sudo hciconfig hci0 noscan

# 3. Restart Bluetooth service
echo "3. Restarting Bluetooth service..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
sleep 2

# 4. Check status
echo "4. Checking status..."
sudo hciconfig hci0
echo ""

# 5. Try a simple scan
echo "5. Testing scan..."
sudo hciconfig hci0 piscan
timeout 5 sudo hcitool scan

# 6. Alternative scan method
echo ""
echo "6. Testing BLE scan with bluetoothctl..."
echo -e "power on\nscan on\n" | timeout 5 sudo bluetoothctl | grep -i muse

echo ""
echo "If you see 'Input/output error', try:"
echo "  sudo rfkill unblock all"
echo "  sudo invoke-rc.d bluetooth restart"
echo ""
echo "Or reboot: sudo reboot"