#!/usr/bin/env python3
"""
Simple BLE scanner to find Muse S Gen 2 MAC address
"""

import asyncio
import logging
from bleak import BleakScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scan_for_devices():
    """Scan for BLE devices and look for Muse"""
    logger.info("Scanning for BLE devices...")
    logger.info("Make sure your Muse S Gen 2 is turned on and in pairing mode")
    
    devices = await BleakScanner.discover(timeout=10.0)
    
    logger.info(f"Found {len(devices)} devices:")
    logger.info("-" * 50)
    
    muse_devices = []
    
    for device in devices:
        logger.info(f"Device: {device.name or 'Unknown'}")
        logger.info(f"  Address: {device.address}")
        try:
            logger.info(f"  RSSI: {device.rssi}")
        except AttributeError:
            logger.info(f"  RSSI: Not available")
        try:
            if device.metadata:
                logger.info(f"  Metadata: {device.metadata}")
        except AttributeError:
            pass
        logger.info("")
        
        # Look for Muse devices
        if device.name and "muse" in device.name.lower():
            muse_devices.append(device)
    
    if muse_devices:
        logger.info("🎯 Found Muse devices:")
        for device in muse_devices:
            logger.info(f"  Name: {device.name}")
            logger.info(f"  MAC Address: {device.address}")
            try:
                logger.info(f"  RSSI: {device.rssi}")
            except AttributeError:
                logger.info(f"  RSSI: Not available")
    else:
        logger.info("❌ No Muse devices found")
        logger.info("Make sure your Muse is:")
        logger.info("1. Turned on")
        logger.info("2. In pairing mode (blinking light)")
        logger.info("3. Within range")

if __name__ == "__main__":
    try:
        asyncio.run(scan_for_devices())
    except ImportError:
        logger.error("Bleak library not installed. Install it with:")
        logger.error("pip install bleak")
    except Exception as e:
        logger.error(f"Error scanning: {e}") 