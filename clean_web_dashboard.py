#!/usr/bin/env python3
"""
Clean Web Dashboard for Real-time Brainwave Visualization
Shows live brainwave data in your browser
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any
from loguru import logger
import uvicorn
import random
import math

# Create FastAPI app
app = FastAPI(title="MindShow Web Dashboard")

# Store connected WebSocket clients
connected_clients: Set[WebSocket] = set()

# Simulated brainwave data generator
class BrainwaveSimulator:
    def __init__(self):
        self.time = 0
        self.base_attention = 0.5
        self.base_relaxation = 0.3
        
    def generate_data(self):
        """Generate realistic brainwave data"""
        self.time += 0.1
        
        # Create realistic brainwave patterns
        attention = self.base_attention + 0.3 * math.sin(self.time * 0.5) + 0.1 * random.random()
        relaxation = self.base_relaxation + 0.2 * math.sin(self.time * 0.3) + 0.1 * random.random()
        
        # Ensure values are between 0 and 1
        attention = max(0, min(1, attention))
        relaxation = max(0, min(1, relaxation))
        
        # Determine brain state
        if attention > 0.6 and relaxation < 0.3:
            brain_state = "engaged"
        elif relaxation > 0.4 and attention < 0.4:
            brain_state = "relaxed"
        else:
            brain_state = "neutral"
            
        return {
            "timestamp": datetime.now().isoformat(),
            "attention": round(attention, 3),
            "relaxation": round(relaxation, 3),
            "brain_state": brain_state,
            "alpha": round(0.2 + 0.1 * random.random(), 3),
            "beta": round(0.3 + 0.2 * random.random(), 3),
            "theta": round(0.15 + 0.1 * random.random(), 3),
            "delta": round(0.1 + 0.05 * random.random(), 3),
            "gamma": round(0.25 + 0.15 * random.random(), 3)
        }

# Initialize simulator
simulator = BrainwaveSimulator()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindShow - Real-time Brainwave Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status {
                display: inline-block;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px;
            }
            .status.connected { background: #4CAF50; }
            .status.disconnected { background: #f44336; }
            .dashboard {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .brain-state {
                text-align: center;
                font-size: 2em;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
            }
            .engaged { background: #ff4444; }
            .relaxed { background: #4444ff; }
            .neutral { background: #44ff44; }
            .metrics {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            .metric {
                text-align: center;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            .metric-value {
                font-size: 1.5em;
                font-weight: bold;
            }
            .chart-container {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 MindShow Dashboard</h1>
                <div id="connection-status" class="status disconnected">Disconnected</div>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h2>Brain State</h2>
                    <div id="brain-state" class="brain-state neutral">Neutral</div>
                </div>
                
                <div class="card">
                    <h2>Real-time Metrics</h2>
                    <div class="metrics">
                        <div class="metric">
                            <div>Attention</div>
                            <div id="attention" class="metric-value">0.500</div>
                        </div>
                        <div class="metric">
                            <div>Relaxation</div>
                            <div id="relaxation" class="metric-value">0.300</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>Brainwave Activity</h2>
                <div id="brainwave-chart"></div>
            </div>
        </div>

        <script>
            let ws = null;
            let chartData = {
                attention: [],
                relaxation: [],
                alpha: [],
                beta: [],
                theta: [],
                delta: [],
                gamma: [],
                timestamps: []
            };
            
            function connect() {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = function() {
                    document.getElementById('connection-status').textContent = 'Connected';
                    document.getElementById('connection-status').className = 'status connected';
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                    updateChart(data);
                };
                
                ws.onclose = function() {
                    document.getElementById('connection-status').textContent = 'Disconnected';
                    document.getElementById('connection-status').className = 'status disconnected';
                    setTimeout(connect, 1000);
                };
                
                ws.onerror = function() {
                    console.log('WebSocket error');
                };
            }
            
            function updateDashboard(data) {
                // Update brain state
                const brainStateEl = document.getElementById('brain-state');
                brainStateEl.textContent = data.brain_state.charAt(0).toUpperCase() + data.brain_state.slice(1);
                brainStateEl.className = 'brain-state ' + data.brain_state;
                
                // Update metrics
                document.getElementById('attention').textContent = data.attention.toFixed(3);
                document.getElementById('relaxation').textContent = data.relaxation.toFixed(3);
            }
            
            function updateChart(data) {
                const timestamp = new Date(data.timestamp);
                
                // Add new data points
                chartData.timestamps.push(timestamp);
                chartData.attention.push(data.attention);
                chartData.relaxation.push(data.relaxation);
                chartData.alpha.push(data.alpha);
                chartData.beta.push(data.beta);
                chartData.theta.push(data.theta);
                chartData.delta.push(data.delta);
                chartData.gamma.push(data.gamma);
                
                // Keep only last 50 points
                if (chartData.timestamps.length > 50) {
                    chartData.timestamps.shift();
                    chartData.attention.shift();
                    chartData.relaxation.shift();
                    chartData.alpha.shift();
                    chartData.beta.shift();
                    chartData.theta.shift();
                    chartData.delta.shift();
                    chartData.gamma.shift();
                }
                
                // Update chart
                const traces = [
                    { name: 'Attention', y: chartData.attention, line: { color: '#ff4444' } },
                    { name: 'Relaxation', y: chartData.relaxation, line: { color: '#4444ff' } },
                    { name: 'Alpha', y: chartData.alpha, line: { color: '#44ff44' } },
                    { name: 'Beta', y: chartData.beta, line: { color: '#ffaa44' } },
                    { name: 'Theta', y: chartData.theta, line: { color: '#ff44aa' } },
                    { name: 'Delta', y: chartData.delta, line: { color: '#aa44ff' } },
                    { name: 'Gamma', y: chartData.gamma, line: { color: '#44aaff' } }
                ];
                
                const layout = {
                    title: 'Real-time Brainwave Activity',
                    xaxis: { title: 'Time' },
                    yaxis: { title: 'Amplitude' },
                    height: 400,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: 'white' }
                };
                
                Plotly.newPlot('brainwave-chart', traces, layout, {responsive: true});
            }
            
            // Connect when page loads
            connect();
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            # Generate and send brainwave data
            data = simulator.generate_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(0.1)  # 10Hz update rate
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": len(connected_clients)
    }

if __name__ == "__main__":
    logger.info("Starting MindShow Clean Web Dashboard...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 