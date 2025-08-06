#!/usr/bin/env python3
"""
Simple test for web dashboard functionality
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger

# Create a simple FastAPI app
app = FastAPI(title="MindShow Test Dashboard")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MindShow Web Dashboard is working!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Dashboard is running"}

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Test HTML page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindShow Test</title>
    </head>
    <body>
        <h1>🎉 MindShow Web Dashboard is Working!</h1>
        <p>This is a test page to verify the web server is running correctly.</p>
        <p>✅ FastAPI is working</p>
        <p>✅ HTML responses are working</p>
        <p>✅ Web server is accessible</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    logger.info("Starting MindShow Test Web Dashboard...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 