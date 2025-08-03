#!/usr/bin/env python3
"""
Real Brainwave Dashboard with Muse Data
Web-only interface using real brainwave data
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global WebSocket clients
connected_clients: Set[WebSocket] = set()

class BrainwaveAnalyzer:
    """Real-time brainwave analysis using BrainFlow"""
    
    def __init__(self):
        self.board = None
        self.connected = False
        self.attention_threshold = 0.55
        self.relaxation_threshold = 0.35
        
    async def connect_to_muse(self):
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
            
            # Send initial keep-alive commands
            self.board.config_board("p50")
            self.board.config_board("p51")
            self.board.config_board("p52")
            
            # Start streaming
            self.board.start_stream()
            logger.info("✅ Connected to Muse! Starting brainwave analysis...")
            
            # Verify connection
            logger.info("Verifying Muse connection...")
            for _ in range(5):
                data = self.board.get_board_data()
                if data.shape[1] > 0:
                    logger.info("✅ Muse connection verified and stable")
                    self.connected = True
                    return True
                await asyncio.sleep(1)
            
            return False
            
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
                
            # Extract EEG channels (channels 0-3 for Muse)
            eeg_data = data[0:4, :]
            
            # Calculate band powers using BrainFlow's native method
            sampling_rate = BoardShim.get_sampling_rate(BoardIds.MUSE_2_BOARD.value)
            band_powers = DataFilter.get_custom_band_powers(eeg_data, sampling_rate, True)
            
            # Extract specific bands
            delta = band_powers[0, 0]  # 0.5-4 Hz
            theta = band_powers[1, 0]  # 4-8 Hz
            alpha = band_powers[2, 0]  # 8-13 Hz
            beta = band_powers[3, 0]   # 13-30 Hz
            gamma = band_powers[4, 0]  # 30-100 Hz
            
            # Calculate attention and relaxation scores
            attention_score = beta / (alpha + 1e-10)  # Beta/Alpha ratio
            relaxation_score = alpha / (theta + 1e-10)  # Alpha/Theta ratio
            
            # Normalize scores
            attention_score = min(1.0, max(0.0, attention_score / 2.0))
            relaxation_score = min(1.0, max(0.0, relaxation_score / 2.0))
            
            return {
                'timestamp': datetime.now().isoformat(),
                'delta': float(delta),
                'theta': float(theta),
                'alpha': float(alpha),
                'beta': float(beta),
                'gamma': float(gamma),
                'attention': float(attention_score),
                'relaxation': float(relaxation_score),
                'brain_state': self.classify_brain_state(attention_score, relaxation_score)
            }
            
        except Exception as e:
            logger.error(f"Error getting brainwave data: {e}")
            return None
    
    def classify_brain_state(self, attention_score, relaxation_score):
        """Classify brain state based on attention and relaxation scores"""
        if attention_score > self.attention_threshold:
            return "engaged"
        elif relaxation_score > self.relaxation_threshold:
            return "relaxed"
        else:
            return "neutral"
    
    def send_keepalive(self):
        """Send keep-alive commands to prevent Muse sleep"""
        if self.connected and self.board:
            try:
                self.board.config_board("p50")
                self.board.config_board("p51")
                self.board.config_board("p52")
                logger.info("Sent keep-alive commands to Muse")
            except Exception as e:
                logger.warning(f"Failed to send keep-alive: {e}")

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
                await self.websocket.send(json.dumps({"setVars": {"hue": 0.66, "brightness": 1.0}}))
            elif brain_state == "engaged":
                # Red tones for engaged state
                await self.websocket.send(json.dumps({"setVars": {"hue": 0.0, "brightness": 1.0}}))
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
        if brain_state == "relaxed": return 0.66
        elif brain_state == "engaged": return 0.0
        else: return 0.33

# FastAPI app for web dashboard
app = FastAPI(title="MindShow Real Brainwave Dashboard")

@app.get("/")
async def root():
    """Root endpoint"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindShow Real Brainwave Dashboard</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 MindShow Real Brainwave Dashboard</h1>
                <p>Real-time brainwave visualization with LED control using actual Muse data</p>
            </div>
            
            <div class="status">
                <h3>Connection Status</h3>
                <p id="connection-status">Connecting to Muse headband...</p>
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
            const maxDataPoints = 100;
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
        "data_source": "Real Muse Headband"
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
    brain_analyzer = BrainwaveAnalyzer()
    led_controller = LEDController()
    
    # Connect to Muse
    if not await brain_analyzer.connect_to_muse():
        logger.error("Failed to connect to Muse. Exiting.")
        return
    
    # Connect to Pixelblaze
    if not await led_controller.connect():
        logger.error("Failed to connect to Pixelblaze. Continuing without LED control.")
    
    logger.info("Starting real brainwave processing...")
    
    last_keepalive = 0
    
    try:
        while True:
            current_time = asyncio.get_event_loop().time()
            
            # Get real brainwave data
            brain_data = brain_analyzer.get_brainwave_data()
            
            if brain_data:
                # Broadcast to web dashboard
                await broadcast_brainwave_data(brain_data)
                
                # Update LEDs
                if led_controller.connected:
                    await led_controller.set_color_palette(brain_data['brain_state'])
                
                logger.info(f"Brain State: {brain_data['brain_state']} | Attention: {brain_data['attention']:.3f} | Relaxation: {brain_data['relaxation']:.3f}")
            
            # Send keep-alive every 5 seconds
            if current_time - last_keepalive >= 5:
                brain_analyzer.send_keepalive()
                last_keepalive = current_time
            
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
    
    logger.info("Starting MindShow Real Brainwave Dashboard...")
    asyncio.run(run_system()) 