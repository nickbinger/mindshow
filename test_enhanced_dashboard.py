#!/usr/bin/env python3
"""
Test script for enhanced dashboard with color mood visualization
Starts the system and opens the dashboard in browser
"""

import sys
sys.path.append('.')
from integrated_mindshow_system import MindShowIntegratedSystem, MindShowConfig
import asyncio
import webbrowser
import time

async def test_enhanced_dashboard():
    print("🎨 Testing Enhanced Dashboard with Color Mood Mapping")
    print("=" * 60)
    
    # Create system
    config = MindShowConfig()
    config.enable_simulated_data = True  # Use simulated data for demo
    
    system = MindShowIntegratedSystem(config)
    
    print("🚀 Starting MindShow system...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🧠 Features:")
    print("   • Real-time color mood visualization")
    print("   • Continuous transitions (no discrete jumps)")
    print("   • Attention/Relaxation tracking")
    print("   • Color mood bar with live indicator")
    print("   • Mental activity level")
    print("   • Real-time chart with dual y-axes")
    
    print("\n⏱️  Starting system (this may take a few seconds)...")
    
    # Start system in background
    system_task = asyncio.create_task(system.run())
    
    # Wait for system to start
    await asyncio.sleep(3)
    
    print("\n✅ System started!")
    print("🌐 Opening dashboard in browser...")
    
    # Open browser
    try:
        webbrowser.open('http://localhost:8000')
    except:
        print("⚠️  Could not open browser automatically")
        print("   Please manually open: http://localhost:8000")
    
    print("\n📊 Dashboard Features to Test:")
    print("   🎨 Color Mood Display: Shows current value (0.0-1.0)")
    print("   🌡️  Color Temperature Bar: Visual indicator with gradient")
    print("   📈 Live Chart: Attention, Relaxation, and Color Mood trends")
    print("   🔬 Engagement Level: Overall mental activity")
    print("   🧠 Mental Activity: High/Medium/Low indicator")
    print("   🎆 Pixelblaze Status: Connected devices")
    
    print("\n🎯 What to Look For:")
    print("   • Smooth color mood transitions")
    print("   • Real-time value updates")
    print("   • Color-coded mood descriptions")
    print("   • Synchronized chart visualization")
    
    print("\n⚠️  Press Ctrl+C to stop the test")
    
    try:
        # Keep running until interrupted
        await system_task
    except KeyboardInterrupt:
        print("\n🛑 Stopping test...")
        await system.shutdown()
        print("✅ Test complete!")

if __name__ == "__main__":
    print("🚀 MindShow Enhanced Dashboard Test")
    print("This demonstrates the new Phase 4b color mood features")
    print("in the web dashboard with real-time visualization\n")
    
    asyncio.run(test_enhanced_dashboard())



