# BrainFlow Research Documentation

*Based on analysis of [brainflow-dev/brainflow](https://github.com/brainflow-dev/brainflow) repository*

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Core Features](#core-features)
3. [Supported Devices](#supported-devices)
4. [Language Bindings](#language-bindings)
5. [EEG Data Processing](#eeg-data-processing)
6. [Signal Processing Capabilities](#signal-processing-capabilities)
7. [Integration Patterns](#integration-patterns)
8. [Code Examples](#code-examples)
9. [Best Practices](#best-practices)
10. [MindShow Integration](#mindshow-integration)

---

## Repository Overview

[BrainFlow](https://github.com/brainflow-dev/brainflow) is the **industry-standard library** for biosensor data acquisition and processing, with a primary focus on neurointerfaces. It provides a uniform SDK to work with biosensors, including EEG, EMG, ECG, and other biometric data.

### Key Statistics
- **1.5k stars** - Highly regarded by the community
- **356 forks** - Active development and adoption
- **1,389 commits** - Extensive development history
- **98 releases** - Stable, production-ready library
- **57 contributors** - Strong community support

### Core Advantages
- **Powerful API** - Comprehensive signal processing and analysis
- **Multi-language support** - Python, Java, R, C++, C#, Matlab, Julia
- **Board agnostic** - Uniform API across all supported devices
- **Free and open source** - MIT license
- **Active development** - Regular updates and improvements

---

## Core Features

### 1. Data Acquisition
- **Real-time streaming** - Continuous data acquisition
- **Multiple device support** - Muse, OpenBCI, and many others
- **Synchronized data** - Timestamped data streams
- **Error handling** - Robust connection management

### 2. Signal Processing
- **Filtering** - Bandpass, lowpass, highpass filters
- **Denoising** - Advanced noise reduction algorithms
- **Downsampling** - Data rate optimization
- **Feature extraction** - Power spectral density, band powers
- **Artifact removal** - Eye blink, muscle artifact detection

### 3. Development Tools
- **Synthetic board** - Simulated data for testing
- **Streaming board** - Network-based data streaming
- **Logging API** - Comprehensive debugging tools
- **Emulator** - Hardware simulation for development

---

## Supported Devices

### EEG Devices
- **Muse** - Muse 2, Muse S, Muse LSL
- **OpenBCI** - Cyton, Ganglion, Cyton+Daisy
- **NeuroSky** - MindWave, MindWave Mobile
- **Emotiv** - EPOC, EPOC+, Insight
- **g.tec** - g.Nautilus, g.USBamp
- **AntNeuro** - eego, eego mylab
- **Brain Products** - LiveAmp, actiCHamp

### Other Biosensors
- **EMG** - Muscle activity sensors
- **ECG** - Heart rate monitors
- **PPG** - Photoplethysmography
- **GSR** - Galvanic skin response
- **Accelerometer** - Motion sensors
- **Gyroscope** - Orientation sensors

### Development Tools
- **Synthetic Board** - Simulated data for testing
- **Streaming Board** - Network-based data streaming
- **File Board** - Read data from files

---

## Language Bindings

### Python (Primary Focus)
```python
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

# Initialize board
board = BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH)
board.prepare_session()
board.start_stream()
```

### C++
```cpp
#include "board_controller/openbci/cyton_bglib_board.h"
#include "data_filter/data_filter.h"

// Initialize board
CytonBGLibBoard board;
board.prepare_session();
board.start_stream();
```

### Java
```java
import brainflow.BoardShim;
import brainflow.BrainFlowPresets;

// Initialize board
BoardShim board = new BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH);
board.prepare_session();
board.start_stream();
```

### Other Languages
- **R** - Statistical analysis and visualization
- **C#** - .NET applications
- **Matlab** - Academic and research applications
- **Julia** - High-performance computing

---

## EEG Data Processing

### 1. Raw Data Acquisition

```python
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

# Initialize Muse board
board = BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH)

# Prepare and start session
board.prepare_session()
board.start_stream()

# Get data
data = board.get_board_data()
board.stop_stream()
board.release_session()
```

### 2. Channel Information

```python
# Get channel names
channels = board.get_eeg_channels(BrainFlowPresets.MUSE_BOARD)
# Returns: ['TP9', 'AF7', 'AF8', 'TP10']

# Get sampling rate
sampling_rate = board.get_sampling_rate(BrainFlowPresets.MUSE_BOARD)
# Returns: 256 Hz for Muse

# Get data shape
data_shape = data.shape
# Returns: (channels, samples)
```

### 3. Data Filtering

```python
from brainflow.data_filter import DataFilter, FilterTypes

# Apply bandpass filter (1-50 Hz)
filtered_data = DataFilter.perform_bandpass(
    data[channel_index], 
    sampling_rate, 
    1.0,  # Low frequency
    50.0, # High frequency
    4,    # Filter order
    FilterTypes.BUTTERWORTH, 
    0     # Zero phase
)

# Apply notch filter (50/60 Hz power line)
notch_filtered = DataFilter.perform_notch(
    filtered_data, 
    sampling_rate, 
    50.0, # Notch frequency
    4     # Filter order
)
```

### 4. Feature Extraction

```python
# Calculate power spectral density
psd = DataFilter.get_psd_welch(
    notch_filtered, 
    len(notch_filtered), 
    len(notch_filtered) // 2, 
    sampling_rate
)

# Extract band powers
delta_power = DataFilter.get_band_power(psd, 1.0, 4.0)
theta_power = DataFilter.get_band_power(psd, 4.0, 8.0)
alpha_power = DataFilter.get_band_power(psd, 8.0, 13.0)
beta_power = DataFilter.get_band_power(psd, 13.0, 30.0)
gamma_power = DataFilter.get_band_power(psd, 30.0, 50.0)
```

---

## Signal Processing Capabilities

### 1. Filtering Operations

```python
from brainflow.data_filter import DataFilter, FilterTypes

# Lowpass filter
lowpass_data = DataFilter.perform_lowpass(
    data, sampling_rate, 50.0, 4, FilterTypes.BUTTERWORTH, 0
)

# Highpass filter
highpass_data = DataFilter.perform_highpass(
    data, sampling_rate, 1.0, 4, FilterTypes.BUTTERWORTH, 0
)

# Bandpass filter
bandpass_data = DataFilter.perform_bandpass(
    data, sampling_rate, 1.0, 50.0, 4, FilterTypes.BUTTERWORTH, 0
)

# Notch filter (power line interference)
notch_data = DataFilter.perform_notch(
    data, sampling_rate, 50.0, 4
)
```

### 2. Artifact Removal

```python
# Remove eye blinks
clean_data = DataFilter.remove_environmental_noise(
    data, sampling_rate, FilterTypes.BUTTERWORTH
)

# Remove muscle artifacts
muscle_clean = DataFilter.perform_highpass(
    clean_data, sampling_rate, 20.0, 4, FilterTypes.BUTTERWORTH, 0
)
```

### 3. Feature Extraction

```python
# Power spectral density
psd = DataFilter.get_psd_welch(data, len(data), len(data)//2, sampling_rate)

# Band powers
delta = DataFilter.get_band_power(psd, 1.0, 4.0)
theta = DataFilter.get_band_power(psd, 4.0, 8.0)
alpha = DataFilter.get_band_power(psd, 8.0, 13.0)
beta = DataFilter.get_band_power(psd, 13.0, 30.0)
gamma = DataFilter.get_band_power(psd, 30.0, 50.0)

# Spectral edge frequency
edge_freq = DataFilter.get_spectral_edge_frequency(psd, 0.5)

# Spectral entropy
entropy = DataFilter.get_spectral_entropy(psd)
```

### 4. Advanced Processing

```python
# Wavelet decomposition
wavelet_data = DataFilter.perform_wavelet_denoising(
    data, 'db4', 3
)

# ICA (Independent Component Analysis)
ica_data = DataFilter.perform_ica(data, 4)

# Downsampling
downsampled = DataFilter.perform_downsampling(data, 2, AggOperations.MEAN)
```

---

## Integration Patterns

### 1. Real-Time Processing

```python
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
from brainflow.data_filter import DataFilter, FilterTypes

class RealTimeEEGProcessor:
    def __init__(self, board_id=BrainFlowPresets.MUSE_BOARD):
        self.board = BoardShim(board_id, BrainFlowInputPresets.BLUETOOTH)
        self.sampling_rate = self.board.get_sampling_rate(board_id)
        self.channels = self.board.get_eeg_channels(board_id)
        
    def start_streaming(self):
        """Start real-time EEG streaming"""
        self.board.prepare_session()
        self.board.start_stream()
        
    def get_latest_data(self, window_size=256):
        """Get latest EEG data window"""
        data = self.board.get_board_data()
        if data.shape[1] >= window_size:
            return data[:, -window_size:]
        return data
        
    def process_window(self, data):
        """Process EEG data window"""
        # Apply filters
        filtered_data = []
        for channel in range(data.shape[0]):
            # Bandpass filter
            bandpass = DataFilter.perform_bandpass(
                data[channel], self.sampling_rate, 1.0, 50.0, 4, FilterTypes.BUTTERWORTH, 0
            )
            # Notch filter
            notch = DataFilter.perform_notch(
                bandpass, self.sampling_rate, 50.0, 4
            )
            filtered_data.append(notch)
            
        return np.array(filtered_data)
        
    def extract_features(self, filtered_data):
        """Extract features from filtered data"""
        features = {}
        
        for i, channel in enumerate(self.channels):
            # Calculate PSD
            psd = DataFilter.get_psd_welch(
                filtered_data[i], len(filtered_data[i]), 
                len(filtered_data[i])//2, self.sampling_rate
            )
            
            # Extract band powers
            features[f'{channel}_delta'] = DataFilter.get_band_power(psd, 1.0, 4.0)
            features[f'{channel}_theta'] = DataFilter.get_band_power(psd, 4.0, 8.0)
            features[f'{channel}_alpha'] = DataFilter.get_band_power(psd, 8.0, 13.0)
            features[f'{channel}_beta'] = DataFilter.get_band_power(psd, 13.0, 30.0)
            features[f'{channel}_gamma'] = DataFilter.get_band_power(psd, 30.0, 50.0)
            
        return features
        
    def stop_streaming(self):
        """Stop EEG streaming"""
        self.board.stop_stream()
        self.board.release_session()

# Usage
processor = RealTimeEEGProcessor()
processor.start_streaming()

try:
    while True:
        # Get latest data
        raw_data = processor.get_latest_data(256)
        
        # Process data
        filtered_data = processor.process_window(raw_data)
        
        # Extract features
        features = processor.extract_features(filtered_data)
        
        # Use features for control
        print(f"Alpha power: {features['TP9_alpha']:.2f}")
        
        time.sleep(0.1)  # 10 Hz update rate
        
except KeyboardInterrupt:
    processor.stop_streaming()
```

### 2. Attention/Relaxation Calculation

```python
class BiometricCalculator:
    def __init__(self):
        self.attention_threshold = 0.75
        self.relaxation_threshold = 0.65
        self.stability_count = 0
        self.last_state = None
        
    def calculate_attention_score(self, features):
        """Calculate attention score from EEG features"""
        # Average beta/alpha ratio across channels
        beta_alpha_ratios = []
        
        for channel in ['TP9', 'AF7', 'AF8', 'TP10']:
            beta = features[f'{channel}_beta']
            alpha = features[f'{channel}_alpha']
            
            if alpha > 0:  # Avoid division by zero
                ratio = beta / alpha
                beta_alpha_ratios.append(ratio)
                
        if beta_alpha_ratios:
            attention_score = np.mean(beta_alpha_ratios)
            return np.clip(attention_score, 0.0, 2.0) / 2.0  # Normalize to 0-1
        return 0.5
        
    def calculate_relaxation_score(self, features):
        """Calculate relaxation score from EEG features"""
        # Average alpha/theta ratio across channels
        alpha_theta_ratios = []
        
        for channel in ['TP9', 'AF7', 'AF8', 'TP10']:
            alpha = features[f'{channel}_alpha']
            theta = features[f'{channel}_theta']
            
            if theta > 0:  # Avoid division by zero
                ratio = alpha / theta
                alpha_theta_ratios.append(ratio)
                
        if alpha_theta_ratios:
            relaxation_score = np.mean(alpha_theta_ratios)
            return np.clip(relaxation_score, 0.0, 2.0) / 2.0  # Normalize to 0-1
        return 0.5
        
    def get_mood_state(self, attention_score, relaxation_score):
        """Determine mood state with stability logic"""
        current_state = None
        
        if attention_score > self.attention_threshold:
            current_state = 'engaged'
        elif relaxation_score > self.relaxation_threshold:
            current_state = 'relaxed'
        else:
            current_state = 'neutral'
            
        # Stability logic
        if current_state == self.last_state:
            self.stability_count += 1
        else:
            self.stability_count = 0
            self.last_state = current_state
            
        # Require 3 consecutive readings for state change
        if self.stability_count >= 3:
            return current_state
        else:
            return self.last_state if self.last_state else 'neutral'
```

### 3. MindShow Integration

```python
class MindShowBrainFlowIntegration:
    def __init__(self, pixelblaze_controller):
        self.eeg_processor = RealTimeEEGProcessor()
        self.biometric_calculator = BiometricCalculator()
        self.pixelblaze = pixelblaze_controller
        self.running = False
        
    def start(self):
        """Start MindShow with BrainFlow integration"""
        self.eeg_processor.start_streaming()
        self.running = True
        
        try:
            while self.running:
                # Get EEG data
                raw_data = self.eeg_processor.get_latest_data(256)
                
                # Process data
                filtered_data = self.eeg_processor.process_window(raw_data)
                
                # Extract features
                features = self.eeg_processor.extract_features(filtered_data)
                
                # Calculate biometric scores
                attention_score = self.biometric_calculator.calculate_attention_score(features)
                relaxation_score = self.biometric_calculator.calculate_relaxation_score(features)
                
                # Get mood state
                mood_state = self.biometric_calculator.get_mood_state(attention_score, relaxation_score)
                
                # Update Pixelblaze
                self.update_pixelblaze(attention_score, relaxation_score, mood_state)
                
                time.sleep(0.1)  # 10 Hz update rate
                
        except KeyboardInterrupt:
            self.stop()
            
    def update_pixelblaze(self, attention_score, relaxation_score, mood_state):
        """Update Pixelblaze based on biometric data"""
        # Speed control (80%-120% range)
        speed_multiplier = 0.8 + (attention_score * 0.4)
        
        # Color control (ROYGBIV spectrum)
        if mood_state == 'engaged':
            base_hue = 0.0  # Red/orange
        elif mood_state == 'relaxed':
            base_hue = 0.66  # Blue/purple
        else:
            base_hue = 0.33  # Green
            
        # Brightness control
        brightness = 0.5 + (relaxation_score * 0.5)
        
        # Update Pixelblaze variables
        variables = {
            'speed': speed_multiplier,
            'hue': base_hue,
            'brightness': brightness
        }
        
        self.pixelblaze.set_variables(variables)
        
    def stop(self):
        """Stop MindShow"""
        self.running = False
        self.eeg_processor.stop_streaming()

# Usage
pixelblaze = RobustWebSocketController("192.168.0.241")
mindshow = MindShowBrainFlowIntegration(pixelblaze)
mindshow.start()
```

---

## Code Examples

### 1. Basic Muse Connection

```python
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
import time

def basic_muse_connection():
    """Basic connection to Muse headband"""
    try:
        # Initialize Muse board
        board = BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH)
        
        # Prepare session
        board.prepare_session()
        print("Muse session prepared")
        
        # Start streaming
        board.start_stream()
        print("Muse streaming started")
        
        # Collect data for 10 seconds
        time.sleep(10)
        
        # Get data
        data = board.get_board_data()
        print(f"Collected {data.shape[1]} samples")
        
        # Stop and cleanup
        board.stop_stream()
        board.release_session()
        print("Muse session closed")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Run basic connection
data = basic_muse_connection()
```

### 2. Real-Time Feature Extraction

```python
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
from brainflow.data_filter import DataFilter, FilterTypes
import time

def real_time_features():
    """Extract real-time features from Muse"""
    board = BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH)
    board.prepare_session()
    board.start_stream()
    
    sampling_rate = board.get_sampling_rate(BrainFlowPresets.MUSE_BOARD)
    channels = board.get_eeg_channels(BrainFlowPresets.MUSE_BOARD)
    
    try:
        while True:
            # Get latest data
            data = board.get_board_data()
            
            if data.shape[1] >= 256:  # Minimum window size
                # Process each channel
                for i, channel in enumerate(channels):
                    # Get channel data
                    channel_data = data[i, -256:]  # Last 256 samples
                    
                    # Apply filters
                    filtered = DataFilter.perform_bandpass(
                        channel_data, sampling_rate, 1.0, 50.0, 4, FilterTypes.BUTTERWORTH, 0
                    )
                    
                    # Calculate PSD
                    psd = DataFilter.get_psd_welch(
                        filtered, len(filtered), len(filtered)//2, sampling_rate
                    )
                    
                    # Extract band powers
                    alpha = DataFilter.get_band_power(psd, 8.0, 13.0)
                    beta = DataFilter.get_band_power(psd, 13.0, 30.0)
                    
                    print(f"{channel}: Alpha={alpha:.2f}, Beta={beta:.2f}")
                    
            time.sleep(1)  # Update every second
            
    except KeyboardInterrupt:
        board.stop_stream()
        board.release_session()

# Run real-time feature extraction
real_time_features()
```

### 3. Advanced Signal Processing

```python
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import numpy as np

def advanced_signal_processing(eeg_data, sampling_rate):
    """Advanced signal processing pipeline"""
    
    processed_data = []
    
    for channel_data in eeg_data:
        # 1. Remove DC offset
        dc_removed = DataFilter.remove_environmental_noise(
            channel_data, sampling_rate, FilterTypes.BUTTERWORTH
        )
        
        # 2. Apply bandpass filter
        bandpass = DataFilter.perform_bandpass(
            dc_removed, sampling_rate, 1.0, 50.0, 4, FilterTypes.BUTTERWORTH, 0
        )
        
        # 3. Apply notch filter
        notch = DataFilter.perform_notch(
            bandpass, sampling_rate, 50.0, 4
        )
        
        # 4. Wavelet denoising
        wavelet = DataFilter.perform_wavelet_denoising(
            notch, 'db4', 3
        )
        
        processed_data.append(wavelet)
    
    return np.array(processed_data)

def extract_comprehensive_features(processed_data, sampling_rate):
    """Extract comprehensive feature set"""
    features = {}
    
    for i, channel_data in enumerate(processed_data):
        # Power spectral density
        psd = DataFilter.get_psd_welch(
            channel_data, len(channel_data), len(channel_data)//2, sampling_rate
        )
        
        # Band powers
        features[f'channel_{i}_delta'] = DataFilter.get_band_power(psd, 1.0, 4.0)
        features[f'channel_{i}_theta'] = DataFilter.get_band_power(psd, 4.0, 8.0)
        features[f'channel_{i}_alpha'] = DataFilter.get_band_power(psd, 8.0, 13.0)
        features[f'channel_{i}_beta'] = DataFilter.get_band_power(psd, 13.0, 30.0)
        features[f'channel_{i}_gamma'] = DataFilter.get_band_power(psd, 30.0, 50.0)
        
        # Spectral features
        features[f'channel_{i}_spectral_edge'] = DataFilter.get_spectral_edge_frequency(psd, 0.5)
        features[f'channel_{i}_spectral_entropy'] = DataFilter.get_spectral_entropy(psd)
        
        # Statistical features
        features[f'channel_{i}_mean'] = np.mean(channel_data)
        features[f'channel_{i}_std'] = np.std(channel_data)
        features[f'channel_{i}_variance'] = np.var(channel_data)
        
    return features
```

---

## Best Practices

### 1. Error Handling

```python
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputPresets

def robust_board_connection():
    """Robust board connection with error handling"""
    board = None
    
    try:
        # Initialize board
        board = BoardShim(BrainFlowPresets.MUSE_BOARD, BrainFlowInputPresets.BLUETOOTH)
        
        # Prepare session with timeout
        board.prepare_session()
        
        # Start streaming
        board.start_stream()
        
        return board
        
    except brainflow.BrainFlowError as e:
        print(f"BrainFlow error: {e}")
        if board:
            try:
                board.release_session()
            except:
                pass
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        if board:
            try:
                board.release_session()
            except:
                pass
        return None
```

### 2. Data Validation

```python
def validate_eeg_data(data, expected_channels=4, min_samples=256):
    """Validate EEG data quality"""
    if data is None or data.size == 0:
        return False, "No data received"
        
    if data.shape[0] != expected_channels:
        return False, f"Expected {expected_channels} channels, got {data.shape[0]}"
        
    if data.shape[1] < min_samples:
        return False, f"Insufficient samples: {data.shape[1]} < {min_samples}"
        
    # Check for NaN values
    if np.any(np.isnan(data)):
        return False, "Data contains NaN values"
        
    # Check for infinite values
    if np.any(np.isinf(data)):
        return False, "Data contains infinite values"
        
    return True, "Data validation passed"
```

### 3. Performance Optimization

```python
import numpy as np
from collections import deque

class OptimizedEEGProcessor:
    def __init__(self, window_size=256, update_rate=10):
        self.window_size = window_size
        self.update_rate = update_rate
        self.data_buffer = deque(maxlen=window_size)
        self.last_update = 0
        
    def add_data(self, new_data):
        """Add new data to buffer"""
        self.data_buffer.extend(new_data)
        
    def get_processed_window(self):
        """Get processed data window"""
        if len(self.data_buffer) < self.window_size:
            return None
            
        # Convert to numpy array
        data = np.array(list(self.data_buffer)[-self.window_size:])
        
        # Apply processing
        return self.process_data(data)
        
    def process_data(self, data):
        """Process data efficiently"""
        # Apply filters in place to save memory
        filtered = DataFilter.perform_bandpass(
            data, 256, 1.0, 50.0, 4, FilterTypes.BUTTERWORTH, 0
        )
        
        return filtered
```

### 4. Configuration Management

```python
import json
from dataclasses import dataclass

@dataclass
class BrainFlowConfig:
    board_id: int = BrainFlowPresets.MUSE_BOARD
    input_preset: int = BrainFlowInputPresets.BLUETOOTH
    sampling_rate: int = 256
    window_size: int = 256
    update_rate: float = 10.0
    filter_low: float = 1.0
    filter_high: float = 50.0
    notch_freq: float = 50.0
    
    @classmethod
    def from_file(cls, filename):
        """Load configuration from file"""
        with open(filename, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
        
    def save_to_file(self, filename):
        """Save configuration to file"""
        with open(filename, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

# Usage
config = BrainFlowConfig()
config.save_to_file('brainflow_config.json')

loaded_config = BrainFlowConfig.from_file('brainflow_config.json')
```

---

## MindShow Integration

### 1. Complete Integration Class

```python
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputPresets
from brainflow.data_filter import DataFilter, FilterTypes
import numpy as np
import time
from typing import Optional, Dict, Any

class MindShowBrainFlow:
    def __init__(self, pixelblaze_controller, config: Optional[BrainFlowConfig] = None):
        self.config = config or BrainFlowConfig()
        self.pixelblaze = pixelblaze_controller
        self.board = None
        self.running = False
        self.biometric_calculator = BiometricCalculator()
        
    def initialize(self) -> bool:
        """Initialize BrainFlow connection"""
        try:
            self.board = BoardShim(self.config.board_id, self.config.input_preset)
            self.board.prepare_session()
            self.board.start_stream()
            print("BrainFlow initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize BrainFlow: {e}")
            return False
            
    def start(self):
        """Start MindShow with BrainFlow"""
        if not self.initialize():
            return
            
        self.running = True
        print("MindShow started with BrainFlow integration")
        
        try:
            while self.running:
                # Get EEG data
                data = self.board.get_board_data()
                
                # Validate data
                is_valid, message = validate_eeg_data(data)
                if not is_valid:
                    print(f"Data validation failed: {message}")
                    time.sleep(0.1)
                    continue
                    
                # Process data
                processed_data = self.process_eeg_data(data)
                
                # Extract features
                features = self.extract_features(processed_data)
                
                # Calculate biometric scores
                attention_score = self.biometric_calculator.calculate_attention_score(features)
                relaxation_score = self.biometric_calculator.calculate_relaxation_score(features)
                
                # Get mood state
                mood_state = self.biometric_calculator.get_mood_state(attention_score, relaxation_score)
                
                # Update Pixelblaze
                self.update_pixelblaze(attention_score, relaxation_score, mood_state)
                
                # Log metrics
                self.log_metrics(attention_score, relaxation_score, mood_state, features)
                
                time.sleep(1.0 / self.config.update_rate)
                
        except KeyboardInterrupt:
            print("MindShow stopped by user")
        finally:
            self.cleanup()
            
    def process_eeg_data(self, data):
        """Process EEG data with BrainFlow"""
        processed_channels = []
        
        for channel_idx in range(data.shape[0]):
            channel_data = data[channel_idx, -self.config.window_size:]
            
            # Apply filters
            filtered = DataFilter.perform_bandpass(
                channel_data, self.config.sampling_rate,
                self.config.filter_low, self.config.filter_high,
                4, FilterTypes.BUTTERWORTH, 0
            )
            
            # Apply notch filter
            notch = DataFilter.perform_notch(
                filtered, self.config.sampling_rate, self.config.notch_freq, 4
            )
            
            processed_channels.append(notch)
            
        return np.array(processed_channels)
        
    def extract_features(self, processed_data):
        """Extract features from processed data"""
        features = {}
        channels = ['TP9', 'AF7', 'AF8', 'TP10']
        
        for i, channel in enumerate(channels):
            if i < processed_data.shape[0]:
                # Calculate PSD
                psd = DataFilter.get_psd_welch(
                    processed_data[i], len(processed_data[i]),
                    len(processed_data[i])//2, self.config.sampling_rate
                )
                
                # Extract band powers
                features[f'{channel}_delta'] = DataFilter.get_band_power(psd, 1.0, 4.0)
                features[f'{channel}_theta'] = DataFilter.get_band_power(psd, 4.0, 8.0)
                features[f'{channel}_alpha'] = DataFilter.get_band_power(psd, 8.0, 13.0)
                features[f'{channel}_beta'] = DataFilter.get_band_power(psd, 13.0, 30.0)
                features[f'{channel}_gamma'] = DataFilter.get_band_power(psd, 30.0, 50.0)
                
        return features
        
    def update_pixelblaze(self, attention_score, relaxation_score, mood_state):
        """Update Pixelblaze with biometric data"""
        # Calculate control variables
        speed_multiplier = 0.8 + (attention_score * 0.4)  # 80%-120% range
        
        if mood_state == 'engaged':
            base_hue = 0.0  # Red/orange
        elif mood_state == 'relaxed':
            base_hue = 0.66  # Blue/purple
        else:
            base_hue = 0.33  # Green
            
        brightness = 0.5 + (relaxation_score * 0.5)
        
        # Update Pixelblaze
        variables = {
            'speed': speed_multiplier,
            'hue': base_hue,
            'brightness': brightness
        }
        
        try:
            self.pixelblaze.set_variables(variables)
        except Exception as e:
            print(f"Failed to update Pixelblaze: {e}")
            
    def log_metrics(self, attention_score, relaxation_score, mood_state, features):
        """Log biometric metrics"""
        print(f"Attention: {attention_score:.3f}, Relaxation: {relaxation_score:.3f}, Mood: {mood_state}")
        
    def cleanup(self):
        """Cleanup resources"""
        if self.board:
            try:
                self.board.stop_stream()
                self.board.release_session()
                print("BrainFlow session closed")
            except Exception as e:
                print(f"Error during cleanup: {e}")
                
        self.running = False

# Usage
config = BrainFlowConfig()
pixelblaze = RobustWebSocketController("192.168.0.241")
mindshow = MindShowBrainFlow(pixelblaze, config)
mindshow.start()
```

### 2. Configuration File

```json
{
  "board_id": 16,
  "input_preset": 0,
  "sampling_rate": 256,
  "window_size": 256,
  "update_rate": 10.0,
  "filter_low": 1.0,
  "filter_high": 50.0,
  "notch_freq": 50.0,
  "attention_threshold": 0.75,
  "relaxation_threshold": 0.65,
  "stability_count": 3
}
```

---

## Conclusion

[BrainFlow](https://github.com/brainflow-dev/brainflow) provides the **industry-standard foundation** for biosensor data acquisition and processing. Key takeaways for MindShow:

### **🎯 Core Advantages**
- **Comprehensive API** - Complete signal processing pipeline
- **Multi-device support** - Muse, OpenBCI, and many others
- **Multi-language bindings** - Python, Java, C++, and more
- **Production ready** - 1.5k stars, 98 releases, active development

### **⚡ Signal Processing Capabilities**
- **Advanced filtering** - Bandpass, notch, wavelet denoising
- **Feature extraction** - Power spectral density, band powers
- **Artifact removal** - Eye blink, muscle artifact detection
- **Real-time processing** - Optimized for live data streams

### **🚀 MindShow Integration Benefits**
- **Robust EEG processing** - Professional-grade signal analysis
- **Multi-device support** - Can switch between different EEG devices
- **Advanced features** - ICA, wavelet analysis, spectral features
- **Production deployment** - Battle-tested in real-world applications

### **📋 Implementation Strategy**
1. **Install BrainFlow** - `pip install brainflow`
2. **Test with Muse** - Use existing Muse headband
3. **Implement processing** - Add signal processing pipeline
4. **Integrate with Pixelblaze** - Connect processed data to LED control
5. **Scale to production** - Deploy with advanced features

**BrainFlow provides the professional-grade foundation needed for reliable, production-ready biometric LED control!** 🎉

---

*Document generated from analysis of [brainflow-dev/brainflow](https://github.com/brainflow-dev/brainflow) repository* 