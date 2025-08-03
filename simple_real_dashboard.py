#!/usr/bin/env python3
"""
Simple Real Brainwave Dashboard
Guaranteed to show real Muse data
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

class SimpleBrainwaveAnalyzer:
    """Simple real-time brainwave analysis"""
    
    def __init__(self):
        self.board = None
        self.connected = False
        
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
            relaxation_score = min(1.0, max(0.0, relaxation_score / 2.0))  # Changed from 3.0 to 2.0
            
            # Classify brain state
            brain_state = "neutral"
            if attention_score > 0.55:
                brain_state = "engaged"
            elif relaxation_score > 0.35:
                brain_state = "relaxed"
            
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

# FastAPI app for web dashboard
app = FastAPI(title="Simple Real Brainwave Dashboard")

@app.get("/")
async def root():
    """Root endpoint"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Real Brainwave Dashboard</title>
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
                <h1>🧠 Simple Real Brainwave Dashboard</h1>
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
    brain_analyzer = SimpleBrainwaveAnalyzer()
    
    # Connect to Muse
    if not brain_analyzer.connect_to_muse():
        logger.error("Failed to connect to Muse. Exiting.")
        return
    
    logger.info("Starting simple brainwave processing...")
    
    try:
        while True:
            # Get real brainwave data
            brain_data = brain_analyzer.get_brainwave_data()
            
            if brain_data:
                # Broadcast to web dashboard
                await broadcast_brainwave_data(brain_data)
                
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
    
    logger.info("Starting Simple Real Brainwave Dashboard...")
    asyncio.run(run_system()) 