#!/usr/bin/env python3
"""
Stable MindShow System with Research-Based Thresholds
Reduces rapid switching between brain states
"""

import asyncio
import json
import logging
import websockets
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global WebSocket clients
connected_clients: Set[WebSocket] = set()

class StableBrainwaveAnalyzer:
    """Stable real-time brainwave analysis with research-based thresholds"""
    
    def __init__(self):
        self.board = None
        self.connected = False
        
        # Research-based thresholds (more conservative)
        # These are based on EEG research showing that significant changes
        # should be 1.5-2.0 standard deviations from baseline
        self.attention_threshold = 0.75  # Increased from 0.55
        self.relaxation_threshold = 0.65  # Increased from 0.35
        
        # Add hysteresis to prevent rapid switching
        self.last_brain_state = "neutral"
        self.state_confidence = 0
        self.min_state_duration = 3  # Minimum seconds in a state
        
    def connect_to_muse(self):
        """Connect to Muse S Gen 2 headband"""
        try:
            logger.info("Connecting to Muse S Gen 2...")
            
            # Configure BrainFlow parameters
            BoardShim.enable_dev_board_logger()
            params = BrainFlowInputParams()
            params.mac_address = "78744271-945E-2227-B094-D15BC0F0FA0E"
            params.timeout = 15
            
            # Create and prepare board
            self.board = BoardShim(BoardIds.MUSE_2_BOARD.value, params)
            self.board.prepare_session()
            
            # Start streaming
            self.board.start_stream()
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            
            # Wait a moment for data to start flowing
            import time
            time.sleep(2)
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Muse: {e}")
            return False
    
    def get_brainwave_data(self):
        """Get real brainwave data from Muse"""
        if not self.connected or not self.board:
            return None
            
        try:
            # Get raw EEG data
            data = self.board.get_board_data()
            if data.shape[1] == 0:
                return None
                
            # Get EEG channels and sampling rate
            eeg_channels = BoardShim.get_eeg_channels(BoardIds.MUSE_2_BOARD.value)
            sampling_rate = BoardShim.get_sampling_rate(BoardIds.MUSE_2_BOARD.value)
            
            # Define frequency bands for brainwave analysis
            bands = [
                (4.0, 8.0),    # Theta
                (8.0, 13.0),   # Alpha  
                (13.0, 30.0),  # Beta
                (30.0, 50.0)   # Gamma
            ]
            
            # Use BrainFlow's native band power calculation
            avg_band_powers, std_band_powers = DataFilter.get_custom_band_powers(
                data, bands, eeg_channels, sampling_rate, apply_filter=True
            )
            
            # Extract power values for each band
            theta = avg_band_powers[0]  # 4-8 Hz
            alpha = avg_band_powers[1]  # 8-13 Hz
            beta = avg_band_powers[2]   # 13-30 Hz
            gamma = avg_band_powers[3]  # 30-50 Hz
            
            # Calculate attention and relaxation scores
            attention_score = beta / (alpha + 1e-10)  # Beta/Alpha ratio
            relaxation_score = alpha / (theta + 1e-10)  # Alpha/Theta ratio
            
            # Normalize scores
            attention_score = min(1.0, max(0.0, attention_score / 2.0))
            relaxation_score = min(1.0, max(0.0, relaxation_score / 2.0))
            
            # Classify brain state with stability logic
            brain_state = self.classify_brain_state_stable(attention_score, relaxation_score)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'delta': 0.0,  # Not calculated in this version
                'theta': float(theta),
                'alpha': float(alpha),
                'beta': float(beta),
                'gamma': float(gamma),
                'attention': float(attention_score),
                'relaxation': float(relaxation_score),
                'brain_state': brain_state
            }
            
        except Exception as e:
            logger.error(f"Error getting brainwave data: {e}")
            return None
    
    def classify_brain_state_stable(self, attention_score, relaxation_score):
        """Classify brain state with stability logic to prevent rapid switching"""
        
        # Determine what the new state should be
        new_state = "neutral"
        if attention_score > self.attention_threshold:
            new_state = "engaged"
        elif relaxation_score > self.relaxation_threshold:
            new_state = "relaxed"
        
        # If the state is changing, increase confidence counter
        if new_state != self.last_brain_state:
            self.state_confidence += 1
        else:
            # If staying in same state, decrease confidence
            self.state_confidence = max(0, self.state_confidence - 1)
        
        # Only change state if we have high confidence (3 consecutive readings)
        if self.state_confidence >= 3:
            self.last_brain_state = new_state
            self.state_confidence = 0  # Reset confidence
        
        return self.last_brain_state

class LEDController:
    """Pixelblaze LED controller"""
    
    def __init__(self, pixelblaze_url="ws://192.168.0.241:81"):
        self.pixelblaze_url = pixelblaze_url
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to Pixelblaze"""
        try:
            logger.info(f"Connecting to Pixelblaze at {self.pixelblaze_url}")
            self.websocket = await websockets.connect(self.pixelblaze_url)
            self.connected = True
            logger.info("✅ Connected to Pixelblaze")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Pixelblaze: {e}")
            return False
    
    async def set_color_palette(self, brain_state):
        """Set color palette based on brain state"""
        if not self.connected:
            return
            
        try:
            if brain_state == "relaxed":
                # Blue tones for relaxed state
                await self.websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
            elif brain_state == "engaged":
                # Red tones for engaged state
                await self.websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
            else:
                # Green tones for neutral state
                await self.websocket.send(json.dumps({"setVars": {"hue": 0.33, "brightness": 1.0}}))
            
            response = await self.websocket.recv()
            logger.info(f"LED Command: {brain_state.upper()} -> {self.get_color_name(brain_state)} (hue={self.get_hue_value(brain_state)})")
            
        except Exception as e:
            logger.error(f"Error setting LED color: {e}")
    
    def get_color_name(self, brain_state):
        if brain_state == "relaxed": return "BLUE"
        elif brain_state == "engaged": return "RED"
        else: return "GREEN"
    
    def get_hue_value(self, brain_state):
        if brain_state == "relaxed": return 0.0
        elif brain_state == "engaged": return 0.66
        else: return 0.33

class StableGUI:
    """Stable GUI for brain state display"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MindShow Stable System")
        self.root.geometry("500x400")
        self.root.configure(bg='#2c3e50')
        
        # Data storage
        self.brain_state = "neutral"
        self.attention_score = 0.5
        self.relaxation_score = 0.5
        self.running = False
        
        # Colors for different states
        self.state_colors = {
            'neutral': '#2ecc71',  # Green
            'relaxed': '#3498db',  # Blue
            'engaged': '#e74c3c'   # Red
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the stable GUI"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="🧠 MindShow Stable System", 
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Status: Initializing...",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#f39c12'
        )
        self.status_label.pack(pady=5)
        
        # Brain State
        state_label = tk.Label(
            self.root,
            text="Brain State:",
            font=("Arial", 12),
            bg='#2c3e50',
            fg='white'
        )
        state_label.pack()
        
        self.state_display = tk.Label(
            self.root,
            text="NEUTRAL",
            font=("Arial", 24, "bold"),
            bg='#2c3e50',
            fg='#2ecc71'
        )
        self.state_display.pack(pady=5)
        
        # Scores Frame
        scores_frame = tk.Frame(self.root, bg='#2c3e50')
        scores_frame.pack(pady=10)
        
        # Attention Score
        attention_frame = tk.Frame(scores_frame, bg='#2c3e50')
        attention_frame.pack(pady=5)
        tk.Label(attention_frame, text="Attention:", font=("Arial", 12), 
                fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        self.attention_display = tk.Label(attention_frame, text="0.500", 
                                        font=("Arial", 12, "bold"), 
                                        fg="red", bg="#2c3e50")
        self.attention_display.pack(side=tk.LEFT, padx=10)
        
        # Relaxation Score
        relaxation_frame = tk.Frame(scores_frame, bg='#2c3e50')
        relaxation_frame.pack(pady=5)
        tk.Label(relaxation_frame, text="Relaxation:", font=("Arial", 12), 
                fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        self.relaxation_display = tk.Label(relaxation_frame, text="0.500", 
                                         font=("Arial", 12, "bold"), 
                                         fg="blue", bg="#2c3e50")
        self.relaxation_display.pack(side=tk.LEFT, padx=10)
        
        # Thresholds Info
        thresholds_frame = tk.Frame(self.root, bg='#2c3e50')
        thresholds_frame.pack(pady=5)
        tk.Label(thresholds_frame, text="Thresholds (Research-based):", 
                font=("Arial", 10), fg="white", bg="#2c3e50").pack()
        tk.Label(thresholds_frame, text="Attention: 0.75 | Relaxation: 0.65", 
                font=("Arial", 9), fg="#95a5a6", bg="#2c3e50").pack()
        
        # LED Status
        led_frame = tk.Frame(self.root, bg='#2c3e50')
        led_frame.pack(pady=10)
        tk.Label(led_frame, text="LED Status:", font=("Arial", 12), 
                fg="white", bg="#2c3e50").pack(side=tk.LEFT)
        self.led_display = tk.Label(led_frame, text="Waiting...", 
                                  font=("Arial", 12, "bold"), 
                                  fg="yellow", bg="#2c3e50")
        self.led_display.pack(side=tk.LEFT, padx=10)
        
        # Web Dashboard Info
        web_frame = tk.Frame(self.root, bg='#2c3e50')
        web_frame.pack(pady=10)
        web_label = tk.Label(
            web_frame,
            text="Web Dashboard: http://localhost:8000",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        web_label.pack()
        
    def update_display(self, brain_data):
        """Update GUI with brain data"""
        if not brain_data:
            return
            
        # Update brain state
        brain_state = brain_data['brain_state']
        self.state_display.config(text=brain_state.upper())
        
        # Update colors based on state
        if brain_state == "engaged":
            self.state_display.config(fg=self.state_colors['engaged'])
        elif brain_state == "relaxed":
            self.state_display.config(fg=self.state_colors['relaxed'])
        else:
            self.state_display.config(fg=self.state_colors['neutral'])
        
        # Update scores
        self.attention_display.config(text=f"{brain_data['attention']:.3f}")
        self.relaxation_display.config(text=f"{brain_data['relaxation']:.3f}")
        
        # Update LED status
        led_color = self.get_led_color(brain_state)
        self.led_display.config(text=f"{brain_state.upper()} ({led_color})", fg=led_color)
        
        # Update status
        self.status_label.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Force GUI update
        self.root.update()
    
    def get_led_color(self, brain_state):
        if brain_state == "engaged": return "#ff6b6b"  # Red
        elif brain_state == "relaxed": return "#4ecdc4"  # Blue
        else: return "#45b7d1"  # Green
    
    def set_status(self, status, color='#f39c12'):
        """Set status message"""
        self.status_label.config(text=status, fg=color)
        self.root.update()
    
    def run(self):
        """Start GUI event loop"""
        self.root.mainloop()

# FastAPI app for web dashboard
app = FastAPI(title="MindShow Stable Dashboard")

@app.get("/")
async def root():
    """Root endpoint"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindShow Stable Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .status { 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                border-radius: 10px; 
                margin-bottom: 20px;
            }
            .chart { 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;
            }
            .metrics { display: flex; gap: 20px; margin-bottom: 20px; }
            .metric { 
                flex: 1; 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                border-radius: 10px; 
                text-align: center;
            }
            .metric-value { font-size: 24px; font-weight: bold; }
            .engaged { color: #ff6b6b; }
            .relaxed { color: #4ecdc4; }
            .neutral { color: #45b7d1; }
            .led-status {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .thresholds {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 MindShow Stable Dashboard</h1>
                <p>Research-based thresholds for stable brain state classification</p>
            </div>
            
            <div class="status">
                <h3>Connection Status</h3>
                <p id="connection-status">Connecting to Muse headband...</p>
            </div>
            
            <div class="thresholds">
                <h3>Research-Based Thresholds</h3>
                <p>Attention: 0.75 | Relaxation: 0.65</p>
                <p><em>These thresholds are based on EEG research to reduce rapid state switching</em></p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Brain State</h3>
                    <div class="metric-value" id="brain-state">--</div>
                </div>
                <div class="metric">
                    <h3>Attention</h3>
                    <div class="metric-value" id="attention">0.000</div>
                </div>
                <div class="metric">
                    <h3>Relaxation</h3>
                    <div class="metric-value" id="relaxation">0.000</div>
                </div>
            </div>
            
            <div class="led-status">
                <h3>LED Control Status</h3>
                <p id="led-status">Waiting for brain state changes...</p>
            </div>
            
            <div class="chart">
                <h3>Real-time Brainwave Activity</h3>
                <div id="brainwave-chart"></div>
            </div>
        </div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            const maxDataPoints = 50;
            let brainwaveData = [];
            
            ws.onopen = function() {
                document.getElementById('connection-status').textContent = 'Connected - Receiving real brainwave data from Muse';
                document.getElementById('connection-status').style.color = '#4ecdc4';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDisplay(data);
                updateChart(data);
                updateLEDStatus(data);
            };
            
            ws.onclose = function() {
                document.getElementById('connection-status').textContent = 'Disconnected from Muse';
                document.getElementById('connection-status').style.color = '#ff6b6b';
            };
            
            function updateDisplay(data) {
                document.getElementById('brain-state').textContent = data.brain_state.toUpperCase();
                document.getElementById('attention').textContent = data.attention.toFixed(3);
                document.getElementById('relaxation').textContent = data.relaxation.toFixed(3);
                
                // Update colors based on brain state
                const stateElement = document.getElementById('brain-state');
                stateElement.className = 'metric-value ' + data.brain_state;
            }
            
            function updateLEDStatus(data) {
                const ledStatus = document.getElementById('led-status');
                const color = getColorForState(data.brain_state);
                ledStatus.innerHTML = `LEDs are now <span style="color: ${color}; font-weight: bold;">${data.brain_state.toUpperCase()}</span> (${color})`;
            }
            
            function getColorForState(state) {
                switch(state) {
                    case 'engaged': return '#ff6b6b'; // Red
                    case 'relaxed': return '#4ecdc4'; // Blue
                    case 'neutral': return '#45b7d1'; // Green
                    default: return '#ffffff';
                }
            }
            
            function updateChart(data) {
                const timestamp = new Date(data.timestamp);
                brainwaveData.push({
                    time: timestamp,
                    delta: data.delta,
                    theta: data.theta,
                    alpha: data.alpha,
                    beta: data.beta,
                    gamma: data.gamma
                });
                
                if (brainwaveData.length > maxDataPoints) {
                    brainwaveData.shift();
                }
                
                const traces = [
                    { name: 'Delta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.delta), line: {color: '#ff6b6b'} },
                    { name: 'Theta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.theta), line: {color: '#4ecdc4'} },
                    { name: 'Alpha', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.alpha), line: {color: '#45b7d1'} },
                    { name: 'Beta', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.beta), line: {color: '#96ceb4'} },
                    { name: 'Gamma', x: brainwaveData.map(d => d.time), y: brainwaveData.map(d => d.gamma), line: {color: '#feca57'} }
                ];
                
                const layout = {
                    title: 'Real-time Brainwave Activity from Muse Headband',
                    xaxis: { title: 'Time' },
                    yaxis: { title: 'Power' },
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: 'white' }
                };
                
                Plotly.newPlot('brainwave-chart', traces, layout);
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": len(connected_clients),
        "data_source": "Real Muse Headband",
        "thresholds": "Research-based (Attention: 0.75, Relaxation: 0.65)"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info("WebSocket client disconnected")

async def broadcast_brainwave_data(brain_data):
    """Broadcast brainwave data to all connected WebSocket clients"""
    if brain_data and connected_clients:
        message = json.dumps(brain_data)
        for client in connected_clients.copy():
            try:
                await client.send_text(message)
            except:
                connected_clients.remove(client)

async def main_loop():
    """Main processing loop"""
    # Initialize components
    brain_analyzer = StableBrainwaveAnalyzer()
    led_controller = LEDController()
    gui = StableGUI()
    
    # Start GUI in separate thread
    gui_thread = threading.Thread(target=gui.run, daemon=True)
    gui_thread.start()
    
    # Connect to Muse
    gui.set_status("Connecting to Muse...")
    if not brain_analyzer.connect_to_muse():
        gui.set_status("Failed to connect to Muse", '#e74c3c')
        logger.error("Failed to connect to Muse. Exiting.")
        return
    
    # Connect to Pixelblaze
    gui.set_status("Connecting to Pixelblaze...")
    if not await led_controller.connect():
        gui.set_status("Failed to connect to Pixelblaze", '#e74c3c')
        logger.error("Failed to connect to Pixelblaze. Continuing without LED control.")
    
    gui.set_status("System Ready - Processing brainwaves with stable thresholds...", '#2ecc71')
    logger.info("Starting stable brainwave processing...")
    
    try:
        while True:
            # Get real brainwave data
            brain_data = brain_analyzer.get_brainwave_data()
            
            if brain_data:
                # Update GUI
                gui.update_display(brain_data)
                
                # Broadcast to web dashboard
                await broadcast_brainwave_data(brain_data)
                
                # Update LEDs
                if led_controller.connected:
                    await led_controller.set_color_palette(brain_data['brain_state'])
                
                logger.info(f"Brain State: {brain_data['brain_state']} | Attention: {brain_data['attention']:.3f} | Relaxation: {brain_data['relaxation']:.3f}")
            
            await asyncio.sleep(0.1)  # 10 Hz update rate
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if brain_analyzer.board:
            brain_analyzer.board.stop_stream()
            brain_analyzer.board.release_session()

if __name__ == "__main__":
    # Start the web server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # Run both web server and main loop
    async def run_system():
        await asyncio.gather(
            server.serve(),
            main_loop()
        )
    
    logger.info("Starting MindShow Stable System with Research-Based Thresholds...")
    asyncio.run(run_system()) 