#!/usr/bin/env python3
"""
MindShow EEG LED Hat - Real-time EEG Visualizer with Brainwave Analysis
Phase 1, Step 5: Add basic GUI/visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import logging
import time
from collections import deque
from scipy import signal
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class EEGVisualizer:
    """Real-time EEG visualizer with brainwave analysis"""
    
    def __init__(self):
        self.board = None
        self.fig, self.ax = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle('MindShow EEG Real-time Visualization', fontsize=16)
        
        # Data buffers
        self.buffer_size = 1000
        self.eeg_data = deque(maxlen=self.buffer_size)
        self.time_data = deque(maxlen=self.buffer_size)
        
        # Frequency bands (Hz) - Adjusted Gamma range for better scaling
        self.freq_bands = {
            'Delta': (0.5, 4),
            'Theta': (4, 8),
            'Alpha': (8, 13),
            'Beta': (13, 30),
            'Gamma': (30, 50)  # Reduced upper limit from 100 to 50 Hz
        }
        
        # Power tracking
        self.power_history = {band: deque(maxlen=100) for band in self.freq_bands.keys()}
        
        # Initialize plots
        self.setup_plots()
        
    def setup_plots(self):
        """Initialize the matplotlib plots"""
        # EEG Time Series
        self.ax[0, 0].set_title('EEG Time Series (Channel 1)')
        self.ax[0, 0].set_xlabel('Time (s)')
        self.ax[0, 0].set_ylabel('Amplitude (μV)')
        self.line_eeg, = self.ax[0, 0].plot([], [], 'b-', linewidth=1)
        self.ax[0, 0].grid(True, alpha=0.3)
        
        # Power Spectrum
        self.ax[0, 1].set_title('Power Spectrum')
        self.ax[0, 1].set_xlabel('Frequency (Hz)')
        self.ax[0, 1].set_ylabel('Power')
        self.line_spectrum, = self.ax[0, 1].plot([], [], 'r-', linewidth=2)
        self.ax[0, 1].grid(True, alpha=0.3)
        self.ax[0, 1].set_xlim(0, 50)
        
        # Brainwave Power
        self.ax[1, 0].set_title('Brainwave Power')
        self.ax[1, 0].set_ylabel('Power')
        self.bars = self.ax[1, 0].bar(self.freq_bands.keys(), [0]*len(self.freq_bands), 
                                      color=['red', 'orange', 'yellow', 'green', 'blue'])
        self.ax[1, 0].tick_params(axis='x', rotation=45)
        
        # Power History
        self.ax[1, 1].set_title('Power History (Alpha)')
        self.ax[1, 1].set_xlabel('Time')
        self.ax[1, 1].set_ylabel('Alpha Power')
        self.line_alpha, = self.ax[1, 1].plot([], [], 'g-', linewidth=2)
        self.ax[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2"""
        try:
            BoardShim.enable_dev_board_logger()
            
            params = BrainFlowInputParams()
            params.mac_address = config.MUSE_MAC_ADDRESS
            
            logger.info("Connecting to Muse S Gen 2...")
            self.board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
            self.board.prepare_session()
            self.board.start_stream()
            
            logger.info("✅ Connected to Muse! Starting visualization...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def calculate_power_bands(self, data, sample_rate=256):
        """Calculate power in different frequency bands"""
        if len(data) < 128:  # Need enough data for FFT
            return {band: 0 for band in self.freq_bands.keys()}
        
        # Use recent data for better responsiveness
        recent_data = data[-128:] if len(data) >= 128 else data
        
        # Apply window and compute FFT
        window = signal.windows.hann(len(recent_data))
        fft_data = np.fft.fft(recent_data * window)
        freqs = np.fft.fftfreq(len(recent_data), 1/sample_rate)
        
        # Calculate power spectrum
        power_spectrum = np.abs(fft_data)**2
        
        # Calculate power in each band with individual scaling
        power_bands = {}
        for band_name, (low_freq, high_freq) in self.freq_bands.items():
            # Find frequencies in the band
            mask = (freqs >= low_freq) & (freqs <= high_freq)
            if np.any(mask):
                # Use log scale for better visualization
                raw_power = np.mean(power_spectrum[mask])
                power_bands[band_name] = np.log10(raw_power + 1)
            else:
                power_bands[band_name] = 0
                
        return power_bands
    
    def update_plots(self, frame):
        """Update all plots with new data"""
        if self.board is None:
            return
            
        try:
            # Get new data
            data = self.board.get_board_data()
            if data.shape[1] == 0:
                return
                
            # Use first actual EEG channel (index 1) - Channel 0 is a counter
            eeg_channel = data[1]  # This is the real EEG data
            
            # Debug: Print data info occasionally
            if len(self.eeg_data) % 100 == 0:
                logger.info(f"Data shape: {data.shape}, Channel 1 range: {eeg_channel.min():.2f} to {eeg_channel.max():.2f}")
            
            # Add to buffer with proper time tracking
            current_time = time.time()
            for i, sample in enumerate(eeg_channel):
                self.eeg_data.append(sample)
                # Use relative time to avoid overflow
                if len(self.time_data) == 0:
                    self.time_data.append(0)
                else:
                    self.time_data.append(self.time_data[-1] + 1/256)  # 256 Hz sample rate
            
            if len(self.eeg_data) < 100:
                return
                
            # Convert to numpy arrays
            eeg_array = np.array(self.eeg_data)
            time_array = np.array(self.time_data)
            
            # Update EEG time series - show last 5 seconds
            window_size = min(5 * 256, len(eeg_array))  # 5 seconds at 256 Hz
            if len(eeg_array) > window_size:
                recent_eeg = eeg_array[-window_size:]
                recent_time = time_array[-window_size:] - time_array[-window_size]
            else:
                recent_eeg = eeg_array
                recent_time = time_array - time_array[0]
            
            self.line_eeg.set_data(recent_time, recent_eeg)
            self.ax[0, 0].set_xlim(0, 5)  # Show 5 seconds
            self.ax[0, 0].relim()
            self.ax[0, 0].autoscale_view()
            
            # Update power spectrum
            if len(eeg_array) >= 256:
                # Use recent data for spectrum
                recent_data = eeg_array[-256:]  # Use last 256 samples
                
                # Apply window and compute FFT
                window = signal.windows.hann(len(recent_data))
                fft_data = np.fft.fft(recent_data * window)
                freqs = np.fft.fftfreq(len(recent_data), 1/256)
                power_spectrum = np.abs(fft_data)**2
                
                # Only show positive frequencies up to 50 Hz
                pos_mask = (freqs >= 0) & (freqs <= 50)
                self.line_spectrum.set_data(freqs[pos_mask], power_spectrum[pos_mask])
                self.ax[0, 1].set_ylim(0, np.max(power_spectrum[pos_mask]) * 1.1)
                self.ax[0, 1].relim()
                self.ax[0, 1].autoscale_view()
            
            # Calculate and update brainwave power
            power_bands = self.calculate_power_bands(eeg_array)
            
            # Debug power bands occasionally
            if len(self.eeg_data) % 200 == 0 and power_bands:
                logger.info(f"Power bands: {power_bands}")
            
            # Update bar chart with better scaling
            if power_bands:
                # Use individual scaling for each band type
                for i, (band, power) in enumerate(power_bands.items()):
                    # Scale each band type individually for better visibility
                    if band == 'Gamma':
                        # Scale Gamma down to be more comparable
                        scaled_power = power / 7.0  # Gamma typically around 6.6
                    elif band == 'Delta':
                        scaled_power = power / 6.5  # Delta typically around 6.0
                    elif band == 'Theta':
                        scaled_power = power / 5.5  # Theta typically around 5.0
                    elif band == 'Alpha':
                        scaled_power = power / 5.0  # Alpha typically around 4.5
                    elif band == 'Beta':
                        scaled_power = power / 4.5  # Beta typically around 4.0
                    else:
                        scaled_power = power / 6.0
                    
                    # Clamp to 0-1 range
                    scaled_power = max(0, min(1, scaled_power))
                    self.bars[i].set_height(scaled_power)
                    self.power_history[band].append(power)
                
                # Update y-axis limits for better visibility
                self.ax[1, 0].set_ylim(0, 1.1)
            
            # Update alpha power history
            if len(self.power_history['Alpha']) > 0:
                alpha_times = np.arange(len(self.power_history['Alpha']))
                self.line_alpha.set_data(alpha_times, list(self.power_history['Alpha']))
                self.ax[1, 1].relim()
                self.ax[1, 1].autoscale_view()
            
            # Add text annotations for dominant brainwave
            if power_bands:
                dominant_band = max(power_bands, key=power_bands.get)
                dominant_power = power_bands[dominant_band]
                
                # Clear previous text
                for txt in self.ax[1, 0].texts:
                    txt.remove()
                
                # Add new text
                self.ax[1, 0].text(0.5, 0.95, f'Dominant: {dominant_band}\nPower: {dominant_power:.2f}', 
                                   transform=self.ax[1, 0].transAxes, ha='center', va='top',
                                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
            
        except Exception as e:
            logger.error(f"Error updating plots: {e}")
    
    def start_visualization(self):
        """Start the real-time visualization"""
        if not self.connect_to_muse():
            return
            
        try:
            # Create animation
            ani = animation.FuncAnimation(self.fig, self.update_plots, 
                                        interval=100, blit=False)
            
            # Add stop button
            ax_button = plt.axes([0.8, 0.05, 0.1, 0.04])
            button = Button(ax_button, 'Stop')
            
            def stop_visualization(event):
                self.stop_visualization()
                plt.close()
            
            button.on_clicked(stop_visualization)
            
            logger.info("Starting real-time visualization... Press 'Stop' to exit")
            plt.show()
            
        except KeyboardInterrupt:
            logger.info("Visualization stopped by user")
        finally:
            self.stop_visualization()
    
    def stop_visualization(self):
        """Stop the visualization and clean up"""
        if self.board:
            try:
                self.board.stop_stream()
                self.board.release_session()
                logger.info("Disconnected from Muse")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

def main():
    """Main function to run the EEG visualizer"""
    logger.info("=== MindShow EEG Real-time Visualizer ===")
    logger.info("Make sure your Muse S Gen 2 is turned on and in pairing mode")
    
    visualizer = EEGVisualizer()
    visualizer.start_visualization()

if __name__ == "__main__":
    main() 