"""Configuration with BrainFlow priority for Muse connection"""

# Force BrainFlow as primary EEG source
PREFERRED_EEG_SOURCE = 'brainflow'  # Options: 'brainflow', 'muselsl', 'auto'

# Muse configuration
MUSE_DEVICE_NAME = None  # None = connect to first available
MUSE_MAC_ADDRESS = None  # Optional: specific MAC address

# BrainFlow specific
BRAINFLOW_SERIAL_PORT = ''  # Empty for Bluetooth
BRAINFLOW_BOARD_ID = 22  # 22 = Muse S

# Rest of config from original
PIXELBLAZE_IP = "192.168.0.241"
DEFAULT_PATTERN = "Phase 4b Color Mood Plasma"

# Thresholds
ATTENTION_THRESHOLD = 0.75
RELAXATION_THRESHOLD = 0.65

# Update rates
UPDATE_INTERVAL = 0.1
MIN_UPDATE_INTERVAL = 0.5
CHANGE_THRESHOLD = 0.02

# Dashboard
DASHBOARD_PORT = 8000
DASHBOARD_HOST = "0.0.0.0"
