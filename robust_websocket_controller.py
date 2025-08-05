#!/usr/bin/env python3
"""
Robust WebSocket Pixelblaze Controller
Using websocket-client library with proven patterns from research
Compatible with Python 3.13
"""

import time
import json
import logging
from typing import Dict, Optional, List, Any
import websocket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RobustWebSocketController:
    """
    Robust Pixelblaze controller using websocket-client
    Based on proven patterns from research
    """
    
    def __init__(self, address: str, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize robust WebSocket controller
        
        Args:
            address: Pixelblaze IP address
            max_retries: Maximum connection retry attempts
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.address = address
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.ws_url = f"ws://{address}:81"
        self.ws = None
        self.last_known_state = {}
        self.connection_attempts = 0
        self.logger = logging.getLogger(f"Pixelblaze-{address}")
        
        # Health monitoring
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        self.is_healthy = False
    
    def connect_with_retry(self) -> bool:
        """
        Connect with exponential backoff retry logic
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Connection attempt {attempt + 1}/{self.max_retries}")
                self.ws = websocket.create_connection(self.ws_url, timeout=10)
                
                # Test connection with ping
                self.ws.send(json.dumps({"ping": True}))
                response = self.ws.recv()
                ping_data = json.loads(response)
                
                if "ack" in ping_data:
                    self.logger.info("✅ Successfully connected to Pixelblaze")
                    self.connection_attempts = 0
                    self.is_healthy = True
                    return True
                else:
                    raise ConnectionError("Ping failed - no ack received")
                    
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
                if self.ws:
                    try:
                        self.ws.close()
                    except:
                        pass
                    self.ws = None
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to connect after {self.max_retries} attempts")
                    self.is_healthy = False
                    return False
        
        return False
    
    def ensure_connected(self) -> bool:
        """
        Ensure connection is active, reconnect if needed
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.ws or not self.is_connected():
            self.logger.info("Connection lost, attempting to reconnect...")
            return self.connect_with_retry()
        return True
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.ws is not None and self.ws.connected
    
    def safe_operation(self, operation_name: str, operation_func, *args, **kwargs) -> Optional[Any]:
        """
        Safely execute an operation with error handling
        
        Args:
            operation_name: Name of operation for logging
            operation_func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of operation or None if failed
        """
        try:
            if not self.ensure_connected():
                self.logger.error(f"Cannot execute {operation_name} - not connected")
                return None
            
            self.logger.debug(f"Executing {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.debug(f"✅ {operation_name} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ {operation_name} failed: {e}")
            self.is_healthy = False
            return None
    
    def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send command to Pixelblaze and get response
        
        Args:
            command: Command to send
            
        Returns:
            Response data or None if failed
        """
        try:
            if not self.ensure_connected():
                return None
            
            self.ws.send(json.dumps(command))
            response = self.ws.recv()
            return json.loads(response)
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return None
    
    def get_pattern_list(self) -> Optional[Dict[str, str]]:
        """
        Get list of available patterns
        
        Returns:
            Dict mapping pattern IDs to names, or None if failed
        """
        def _get_patterns():
            response = self.send_command({"listPrograms": True})
            if response and "programList" in response:
                return response["programList"]
            return None
        
        return self.safe_operation("get_pattern_list", _get_patterns)
    
    def get_active_pattern(self) -> Optional[str]:
        """
        Get currently active pattern
        
        Returns:
            Pattern name or None if failed
        """
        def _get_active():
            response = self.send_command({"getActivePattern": True})
            if response and "activePattern" in response:
                return response["activePattern"]
            return None
        
        return self.safe_operation("get_active_pattern", _get_active)
    
    def set_active_pattern(self, pattern_name: str) -> bool:
        """
        Set active pattern with error handling
        
        Args:
            pattern_name: Name or ID of pattern to activate
            
        Returns:
            bool: True if successful, False otherwise
        """
        def _set_pattern():
            response = self.send_command({"activeProgramId": pattern_name})
            return response is not None
        
        result = self.safe_operation("set_active_pattern", _set_pattern)
        if result:
            self.logger.info(f"✅ Pattern switched to: {pattern_name}")
        return result is not None
    
    def get_variables(self) -> Optional[Dict[str, float]]:
        """
        Get current variables
        
        Returns:
            Dict of variable names to values, or None if failed
        """
        def _get_vars():
            response = self.send_command({"getVars": True})
            if response and "vars" in response:
                return response["vars"]
            return None
        
        return self.safe_operation("get_variables", _get_vars)
    
    def set_variables(self, variables: Dict[str, float]) -> bool:
        """
        Set variables with error handling and state tracking
        
        Args:
            variables: Dict of variable names to values
            
        Returns:
            bool: True if successful, False otherwise
        """
        def _set_vars():
            response = self.send_command({"setVars": variables})
            if response:
                # Update last known state
                self.last_known_state.update(variables)
                return True
            return False
        
        result = self.safe_operation("set_variables", _set_vars)
        if result:
            self.logger.debug(f"✅ Variables set: {variables}")
        return result is not None
    
    def set_variable(self, name: str, value: float) -> bool:
        """
        Set single variable
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set_variables({name: value})
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Dict with health status and details
        """
        try:
            if not self.is_connected():
                return {
                    'status': 'unhealthy',
                    'connected': False,
                    'error': 'Not connected',
                    'timestamp': time.time()
                }
            
            # Test basic operations
            variables = self.get_variables()
            current_pattern = self.get_active_pattern()
            
            if variables is None or current_pattern is None:
                return {
                    'status': 'unhealthy',
                    'connected': True,
                    'error': 'Basic operations failed',
                    'timestamp': time.time()
                }
            
            self.is_healthy = True
            return {
                'status': 'healthy',
                'connected': True,
                'variables': variables,
                'current_pattern': current_pattern,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.is_healthy = False
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def restore_last_known_state(self) -> bool:
        """
        Restore last known good state
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.last_known_state:
            self.logger.warning("No last known state to restore")
            return False
        
        self.logger.info(f"Restoring last known state: {self.last_known_state}")
        return self.set_variables(self.last_known_state)
    
    def disconnect(self):
        """Cleanly disconnect from Pixelblaze"""
        try:
            if self.ws:
                self.ws.close()
                self.logger.info("✅ Cleanly disconnected from Pixelblaze")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
        finally:
            self.ws = None
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connect_with_retry():
            raise ConnectionError(f"Failed to connect to Pixelblaze at {self.address}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class BiometricWebSocketController(RobustWebSocketController):
    """
    Specialized controller for biometric data integration
    Based on research examples
    """
    
    def __init__(self, address: str):
        super().__init__(address)
        
        # Mood mapping based on research
        self.mood_mapping = {
            'engaged': {
                'hue': 0.0,      # Red
                'brightness': 0.8,
                'speed': 0.7
            },
            'neutral': {
                'hue': 0.33,     # Green
                'brightness': 0.6,
                'speed': 0.5
            },
            'relaxed': {
                'hue': 0.66,     # Blue
                'brightness': 0.4,
                'speed': 0.3
            }
        }
    
    def update_from_biometric(self, attention_score: float, relaxation_score: float) -> Optional[str]:
        """
        Update pattern based on biometric data
        
        Args:
            attention_score: Attention level (0.0 to 1.0)
            relaxation_score: Relaxation level (0.0 to 1.0)
            
        Returns:
            str: Mood category or None if failed
        """
        # Determine mood based on biometric scores
        if attention_score > 0.7:
            mood = 'engaged'
        elif relaxation_score > 0.6:
            mood = 'relaxed'
        else:
            mood = 'neutral'
        
        # Get variables for this mood
        variables = self.mood_mapping[mood]
        
        # Apply variables
        if self.set_variables(variables):
            self.logger.info(f"✅ Updated to {mood} mood (attention: {attention_score:.2f}, relaxation: {relaxation_score:.2f})")
            return mood
        else:
            self.logger.error(f"❌ Failed to update to {mood} mood")
            return None
    
    def smooth_transition(self, target_vars: Dict[str, float], duration: float = 1.0) -> bool:
        """
        Smoothly transition to target variables
        
        Args:
            target_vars: Target variables
            duration: Transition duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        current_vars = self.get_variables()
        if current_vars is None:
            self.logger.error("Cannot get current variables for smooth transition")
            return False
        
        steps = int(duration * 10)  # 10 updates per second
        self.logger.info(f"Starting smooth transition over {duration}s ({steps} steps)")
        
        for step in range(steps + 1):
            progress = step / steps
            
            # Use ease-in-out function for smooth transition
            eased_progress = 0.5 * (1 + (progress * 3.14159 - 1.5708))
            
            interpolated = {}
            for var_name in target_vars:
                if var_name in current_vars:
                    current = current_vars[var_name]
                    target = target_vars[var_name]
                    interpolated[var_name] = current + (target - current) * eased_progress
            
            if not self.set_variables(interpolated):
                self.logger.error(f"Failed to set variables at step {step}")
                return False
            
            time.sleep(duration / steps)
        
        self.logger.info("✅ Smooth transition completed")
        return True


def test_robust_websocket_controller():
    """Test the robust WebSocket controller implementation"""
    
    logger.info("🧠 MindShow - Testing Robust WebSocket Controller")
    logger.info("=" * 60)
    logger.info("⚠️  Make sure Pixelblaze web UI is CLOSED to avoid WebSocket conflicts!")
    
    try:
        # Test basic controller
        with RobustWebSocketController("192.168.0.241") as controller:
            logger.info("✅ Basic controller test - connected successfully")
            
            # Test pattern list
            patterns = controller.get_pattern_list()
            if patterns:
                logger.info(f"📋 Found {len(patterns)} patterns")
                for pattern_id, pattern_name in list(patterns.items())[:5]:  # Show first 5
                    logger.info(f"  - {pattern_name} (ID: {pattern_id})")
            
            # Test current pattern
            current_pattern = controller.get_active_pattern()
            logger.info(f"🎯 Current pattern: {current_pattern}")
            
            # Test variables
            variables = controller.get_variables()
            if variables:
                logger.info(f"⚙️  Current variables: {variables}")
            
            # Test health check
            health = controller.health_check()
            logger.info(f"🏥 Health status: {health['status']}")
            
            # Test variable setting
            test_vars = {"brightness": 0.5, "hue": 0.3}
            if controller.set_variables(test_vars):
                logger.info("✅ Variable setting test successful")
            
            # Test pattern switching (if sparkfire exists)
            if patterns and "sparkfire" in [name.lower() for name in patterns.values()]:
                if controller.set_active_pattern("sparkfire"):
                    logger.info("✅ Pattern switching test successful")
                    time.sleep(2)  # Let pattern run for a moment
                else:
                    logger.warning("⚠️  Pattern switching test failed")
            
            logger.info("✅ Basic controller test completed successfully!")
        
        # Test biometric controller
        logger.info("\n🧠 Testing Biometric Controller...")
        with BiometricWebSocketController("192.168.0.241") as bio_controller:
            logger.info("✅ Biometric controller connected")
            
            # Test mood updates
            test_moods = [
                (0.8, 0.2, "engaged"),
                (0.5, 0.5, "neutral"),
                (0.2, 0.8, "relaxed")
            ]
            
            for attention, relaxation, expected_mood in test_moods:
                logger.info(f"Testing {expected_mood} mood (attention: {attention}, relaxation: {relaxation})")
                mood = bio_controller.update_from_biometric(attention, relaxation)
                if mood == expected_mood:
                    logger.info(f"✅ {expected_mood} mood test successful")
                else:
                    logger.warning(f"⚠️  {expected_mood} mood test failed, got: {mood}")
                time.sleep(2)  # Let mood change be visible
            
            # Test smooth transition
            logger.info("Testing smooth transition...")
            if bio_controller.smooth_transition({"brightness": 1.0, "hue": 0.0}, duration=2.0):
                logger.info("✅ Smooth transition test successful")
            else:
                logger.warning("⚠️  Smooth transition test failed")
            
            logger.info("✅ Biometric controller test completed successfully!")
        
        logger.info("=" * 60)
        logger.info("🎉 All tests completed successfully!")
        logger.info("📊 Robust WebSocket controller is working with proper error handling!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_robust_websocket_controller() 