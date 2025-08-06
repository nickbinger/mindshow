"""
Configuration settings for MindShow EEG LED Hat Project
"""

# Muse S Gen 2 Settings
MUSE_MAC_ADDRESS = "78744271-945E-2227-B094-D15BC0F0FA0E"  # Your Muse S Gen 2 MAC address
SAMPLE_RATE = 256  # Muse S Gen 2 default sample rate
CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10', 'AUX']  # Muse S Gen 2 channels

# BrainFlow Settings
BOARD_ID = "MUSE_2_BOARD"  # Muse S Gen 2 uses the same board ID as Muse 2

# Data Processing Settings
BUFFER_SIZE = 1000  # Number of samples to buffer
PLOT_UPDATE_RATE = 30  # Hz - how often to update plots

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 