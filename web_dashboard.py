#!/usr/bin/env python3
"""
FastAPI Web Dashboard for Real-time Brainwave Visualization
Based on research from comprehensive development documentation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any
from loguru import logger
import uvicorn

# Import our existing components
from pixelblaze_integration_simple_gui import MindShowController
from enhanced_led_controller import EnhancedLEDController

app = FastAPI(title="MindShow Brainwave Dashboard")

# Store active WebSocket connections
connected_clients: Set[WebSocket] = set()

# Global references to hardware controllers
mindshow_controller = None
led_controller = None

@app.on_event("startup")
async def startup_event():
    """Initialize hardware on startup"""
    global mindshow_controller, led_controller
    
    logger.info("Starting MindShow Web Dashboard...")
    
    # Initialize LED controller
    led_controller = EnhancedLEDController(num_pixels=60)
    
    # Initialize MindShow controller (without GUI)
    mindshow_controller = MindShowController()
    
    # Start data processing loop
    asyncio.create_task(biometric_processing_loop())

async def biometric_processing_loop():
    """Main loop for processing biometric data and updating LEDs"""
    logger.info("Starting biometric processing loop...")
    
    while True:
        try:
            # Simulate brainwave data for demonstration
            # In real implementation, this would read from actual Muse
            simulated_data = generate_simulated_brainwave_data()
            
            # Process the data
            attention_score = simulated_data['attention']
            relaxation_score = simulated_data['relaxation']
            brain_state = classify_brain_state(attention_score, relaxation_score)
            
            # Update LED visualization
            led_controller.set_brain_state_colors(brain_state, attention_score, relaxation_score)
            
            # Prepare data for web clients
            web_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'brainwave_data',
                'data': {
                    'brain_state': brain_state,
                    'attention_score': attention_score,
                    'relaxation_score': relaxation_score,
                    'eeg_bands': simulated_data['eeg_bands']
                }
            }
            
            await broadcast_to_clients(web_data)
            
        except Exception as e:
            logger.error(f"Error in biometric processing: {e}")
        
        await asyncio.sleep(0.1)  # 10Hz update rate

def generate_simulated_brainwave_data() -> Dict[str, Any]:
    """Generate simulated brainwave data for demonstration"""
    import random
    import math
    
    # Simulate realistic brainwave patterns
    time_factor = datetime.now().timestamp() * 0.1
    
    # Simulate attention and relaxation scores
    attention_base = 0.5 + 0.3 * math.sin(time_factor)
    relaxation_base = 0.5 + 0.3 * math.cos(time_factor * 0.7)
    
    attention_score = max(0, min(1, attention_base + random.uniform(-0.1, 0.1)))
    relaxation_score = max(0, min(1, relaxation_base + random.uniform(-0.1, 0.1)))
    
    # Simulate EEG band powers
    eeg_bands = {
        'TP9': {
            'delta': random.uniform(10, 50),
            'theta': random.uniform(20, 80),
            'alpha': random.uniform(30, 120),
            'beta': random.uniform(40, 150),
            'gamma': random.uniform(20, 100)
        },
        'AF7': {
            'delta': random.uniform(10, 50),
            'theta': random.uniform(20, 80),
            'alpha': random.uniform(30, 120),
            'beta': random.uniform(40, 150),
            'gamma': random.uniform(20, 100)
        },
        'AF8': {
            'delta': random.uniform(10, 50),
            'theta': random.uniform(20, 80),
            'alpha': random.uniform(30, 120),
            'beta': random.uniform(40, 150),
            'gamma': random.uniform(20, 100)
        },
        'TP10': {
            'delta': random.uniform(10, 50),
            'theta': random.uniform(20, 80),
            'alpha': random.uniform(30, 120),
            'beta': random.uniform(40, 150),
            'gamma': random.uniform(20, 100)
        }
    }
    
    return {
        'attention': attention_score,
        'relaxation': relaxation_score,
        'eeg_bands': eeg_bands
    }

def classify_brain_state(attention_score: float, relaxation_score: float) -> str:
    """Classify brain state based on attention and relaxation scores"""
    if attention_score > 0.6:
        return "engaged"
    elif relaxation_score > 0.6:
        return "relaxed"
    else:
        return "neutral"

async def broadcast_to_clients(data: dict):
    """Broadcast data to all connected WebSocket clients"""
    message = json.dumps(data)
    disconnected = set()
    
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            disconnected.add(client)
    
    # Remove disconnected clients
    connected_clients.difference_update(disconnected)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            # Keep connection alive and handle commands
            data = await websocket.receive_text()
            
            # Handle client commands
            try:
                command = json.loads(data)
                if command.get('type') == 'set_brightness':
                    brightness = command.get('value', 0.3)
                    if led_controller:
                        led_controller.brightness = brightness
                    logger.info(f"Brightness set to {brightness}")
                    
                elif command.get('type') == 'set_animation':
                    animation_type = command.get('animation', 'brain_state')
                    if led_controller and animation_type == 'wave':
                        # Start wave animation
                        base_color = (255, 100, 0)  # Orange
                        asyncio.create_task(
                            led_controller.create_wave_effect(base_color, wave_speed=1.0)
                        )
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindShow Brainwave Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                color: #fff; 
                min-height: 100vh;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .status { 
                padding: 15px; 
                background: rgba(255, 255, 255, 0.1); 
                border-radius: 10px; 
                margin: 20px 0; 
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .connected { color: #4CAF50; font-weight: bold; }
            .disconnected { color: #f44336; font-weight: bold; }
            
            .metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .metric { 
                background: rgba(255, 255, 255, 0.1); 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .metric:hover {
                transform: translateY(-5px);
            }
            .metric h3 {
                margin: 0 0 15px 0;
                color: #4ecdc4;
                font-size: 1.2em;
            }
            .metric-value {
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }
            .brain-state {
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .state-relaxed { background: linear-gradient(45deg, #2196F3, #03DAC6); }
            .state-engaged { background: linear-gradient(45deg, #f44336, #ff9800); }
            .state-neutral { background: linear-gradient(45deg, #4CAF50, #8BC34A); }
            
            .charts {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 30px 0;
            }
            .chart { 
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .chart-container {
                width: 100%;
                height: 400px;
            }
            
            .controls {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .control-group {
                display: flex;
                align-items: center;
                gap: 15px;
                margin: 10px 0;
            }
            .control-group label {
                min-width: 150px;
                font-weight: bold;
            }
            input[type="range"] {
                flex: 1;
                height: 8px;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.2);
                outline: none;
            }
            input[type="range"]::-webkit-slider-thumb {
                appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #4ecdc4;
                cursor: pointer;
            }
            button {
                background: linear-gradient(45deg, #4ecdc4, #44a08d);
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                transition: transform 0.2s ease;
            }
            button:hover {
                transform: scale(1.05);
            }
            
            @media (max-width: 768px) {
                .charts {
                    grid-template-columns: 1fr;
                }
                .metrics {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 MindShow Brainwave Dashboard</h1>
                <p>Real-time brainwave visualization and LED control</p>
            </div>
            
            <div class="status">
                Connection Status: <span id="status" class="disconnected">Disconnected</span>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Brain State</h3>
                    <div id="brain-state" class="brain-state state-neutral">Neutral</div>
                </div>
                
                <div class="metric">
                    <h3>Attention Score</h3>
                    <div id="attention-score" class="metric-value">0.50</div>
                    <div>Focus Level</div>
                </div>
                
                <div class="metric">
                    <h3>Relaxation Score</h3>
                    <div id="relaxation-score" class="metric-value">0.50</div>
                    <div>Calm Level</div>
                </div>
                
                <div class="metric">
                    <h3>Alpha Power</h3>
                    <div id="alpha-power" class="metric-value">0.00</div>
                    <div>μV²</div>
                </div>
            </div>
            
            <div class="charts">
                <div class="chart">
                    <h3>EEG Band Powers</h3>
                    <div id="eeg-chart" class="chart-container"></div>
                </div>
                
                <div class="chart">
                    <h3>Brain State Over Time</h3>
                    <div id="state-chart" class="chart-container"></div>
                </div>
            </div>
            
            <div class="controls">
                <h3>LED Controls</h3>
                <div class="control-group">
                    <label>Brightness:</label>
                    <input type="range" id="brightness" min="0" max="100" value="30" />
                    <span id="brightness-value">30%</span>
                </div>
                <div class="control-group">
                    <label>Animation:</label>
                    <button onclick="setAnimation('brain_state')">Brain State</button>
                    <button onclick="setAnimation('wave')">Wave Effect</button>
                    <button onclick="setAnimation('pulse')">Pulse</button>
                </div>
            </div>
        </div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            const maxDataPoints = 200;
            
            // Initialize charts
            const eegData = {
                delta: {x: [], y: [], name: 'Delta', line: {color: '#6400C8'}},
                theta: {x: [], y: [], name: 'Theta', line: {color: '#0000FF'}},
                alpha: {x: [], y: [], name: 'Alpha', line: {color: '#00FFFF'}},
                beta: {x: [], y: [], name: 'Beta', line: {color: '#00FF00'}},
                gamma: {x: [], y: [], name: 'Gamma', line: {color: '#FF6400'}}
            };
            
            const stateData = {
                x: [], y: [], type: 'scatter', mode: 'lines+markers',
                name: 'Brain State', line: {color: '#4ecdc4', width: 3},
                marker: {size: 8}
            };
            
            const eegLayout = {
                title: 'EEG Band Powers',
                xaxis: {title: 'Time', color: '#fff'},
                yaxis: {title: 'Power (μV²)', color: '#fff'},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: {color: '#fff'},
                legend: {font: {color: '#fff'}},
                margin: {t: 50, b: 50, l: 50, r: 50}
            };
            
            const stateLayout = {
                title: 'Brain State Over Time',
                xaxis: {title: 'Time', color: '#fff'},
                yaxis: {title: 'State', color: '#fff', tickmode: 'array', 
                       ticktext: ['Relaxed', 'Neutral', 'Engaged'], 
                       tickvals: [0, 1, 2]},
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: {color: '#fff'},
                margin: {t: 50, b: 50, l: 50, r: 50}
            };
            
            Plotly.newPlot('eeg-chart', Object.values(eegData), eegLayout, {responsive: true});
            Plotly.newPlot('state-chart', [stateData], stateLayout, {responsive: true});
            
            // WebSocket handlers
            ws.onopen = function() {
                document.getElementById('status').textContent = 'Connected';
                document.getElementById('status').className = 'connected';
            };
            
            ws.onclose = function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'disconnected';
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                const timestamp = new Date(message.timestamp);
                
                if (message.type === 'brainwave_data') {
                    const data = message.data;
                    
                    // Update brain state
                    const brainStateEl = document.getElementById('brain-state');
                    brainStateEl.textContent = data.brain_state.toUpperCase();
                    brainStateEl.className = 'brain-state state-' + data.brain_state;
                    
                    // Update scores
                    document.getElementById('attention-score').textContent = 
                        (data.attention_score * 100).toFixed(0);
                    document.getElementById('relaxation-score').textContent = 
                        (data.relaxation_score * 100).toFixed(0);
                    
                    // Update EEG chart
                    const avgPowers = {};
                    for (const band in eegData) {
                        const values = [];
                        for (const channel in data.eeg_bands) {
                            values.push(data.eeg_bands[channel][band]);
                        }
                        avgPowers[band] = values.reduce((a, b) => a + b) / values.length;
                        
                        eegData[band].x.push(timestamp);
                        eegData[band].y.push(avgPowers[band]);
                        
                        // Limit data points
                        if (eegData[band].x.length > maxDataPoints) {
                            eegData[band].x.shift();
                            eegData[band].y.shift();
                        }
                    }
                    
                    // Update alpha power display
                    document.getElementById('alpha-power').textContent = 
                        avgPowers.alpha.toFixed(1);
                    
                    // Update state chart
                    const stateValues = {relaxed: 0, neutral: 1, engaged: 2};
                    stateData.x.push(timestamp);
                    stateData.y.push(stateValues[data.brain_state]);
                    
                    if (stateData.x.length > maxDataPoints) {
                        stateData.x.shift();
                        stateData.y.shift();
                    }
                    
                    Plotly.update('eeg-chart', Object.values(eegData));
                    Plotly.update('state-chart', [stateData]);
                }
            };
            
            // Controls
            const brightnessSlider = document.getElementById('brightness');
            const brightnessValue = document.getElementById('brightness-value');
            
            brightnessSlider.oninput = function() {
                const value = this.value;
                brightnessValue.textContent = value + '%';
                
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'set_brightness',
                        value: value / 100
                    }));
                }
            };
            
            function setAnimation(animationType) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'set_animation',
                        animation: animationType
                    }));
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_clients": len(connected_clients)
    }

if __name__ == "__main__":
    logger.info("Starting MindShow Web Dashboard...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 