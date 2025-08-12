"""
Network Manager
Handles multiplayer networking, WebSocket connections, and real-time communication.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import json
import threading
import time
import websocket
import queue
from vector3 import Vector3

class NetworkManager:
    """Network manager for multiplayer functionality."""
    
    def __init__(self):
        """Initialize the network manager."""
        # Connection settings
        self.server_url = "ws://localhost:8080/ws"
        self.connected = False
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # WebSocket connection
        self.websocket = None
        self.connection_thread = None
        
        # Message queues
        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()
        
        # Player data
        self.player_id = None
        self.server_time = 0
        self.ping = 0
        
        # Network state
        self.last_send_time = 0
        self.send_interval = 1.0 / 20.0  # 20 Hz update rate
        
        # Message handlers
        self.message_handlers = {
            "welcome": self.handle_welcome,
            "playerJoined": self.handle_player_joined,
            "playerLeft": self.handle_player_left,
            "playerUpdate": self.handle_player_update,
            "chat": self.handle_chat,
            "build": self.handle_build,
            "interactionResponse": self.handle_interaction_response,
            "serverStats": self.handle_server_stats,
            "error": self.handle_error
        }
        
        # Event callbacks
        self.on_connect = None
        self.on_disconnect = None
        self.on_player_joined = None
        self.on_player_left = None
        self.on_chat_message = None
        self.on_build_action = None
        
    def connect(self):
        """Connect to the game server."""
        if self.connected:
            return
            
        print("🌐 Connecting to server...")
        
        try:
            # Create WebSocket connection
            self.websocket = websocket.WebSocketApp(
                self.server_url,
                on_open=self.on_websocket_open,
                on_message=self.on_websocket_message,
                on_error=self.on_websocket_error,
                on_close=self.on_websocket_close
            )
            
            # Start connection thread
            self.connection_thread = threading.Thread(target=self.websocket.run_forever)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connection_attempts += 1
            
    def disconnect(self):
        """Disconnect from the server."""
        if self.websocket:
            self.websocket.close()
        self.connected = False
        print("🔌 Disconnected from server")
        
    def on_websocket_open(self, ws):
        """Called when WebSocket connection is established."""
        print("✅ Connected to server!")
        self.connected = True
        self.connection_attempts = 0
        
        if self.on_connect:
            self.on_connect()
            
    def on_websocket_message(self, ws, message):
        """Called when a message is received from the server."""
        try:
            data = json.loads(message)
            self.receive_queue.put(data)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON received: {e}")
            
    def on_websocket_error(self, ws, error):
        """Called when a WebSocket error occurs."""
        print(f"❌ WebSocket error: {error}")
        self.connected = False
        
    def on_websocket_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection is closed."""
        print("🔌 WebSocket connection closed")
        self.connected = False
        
        if self.on_disconnect:
            self.on_disconnect()
            
    def update(self):
        """Update network manager."""
        # Process received messages
        while not self.receive_queue.empty():
            try:
                message = self.receive_queue.get_nowait()
                self.process_message(message)
            except queue.Empty:
                break
                
        # Send pending messages
        current_time = time.time()
        if current_time - self.last_send_time >= self.send_interval:
            self.send_pending_messages()
            self.last_send_time = current_time
            
    def process_message(self, message):
        """Process a received message."""
        message_type = message.get("type")
        
        if message_type in self.message_handlers:
            self.message_handlers[message_type](message)
        else:
            print(f"⚠️ Unknown message type: {message_type}")
            
    def handle_welcome(self, message):
        """Handle welcome message from server."""
        data = message.get("data", {})
        self.player_id = data.get("playerId")
        server_info = data.get("serverInfo", {})
        
        print(f"🎮 Welcome! Player ID: {self.player_id}")
        print(f"📊 Server Info: {server_info}")
        
    def handle_player_joined(self, message):
        """Handle player joined message."""
        data = message.get("data", {})
        player_id = data.get("playerId")
        position = data.get("position", {"x": 0, "y": 0, "z": 0})
        
        print(f"👤 Player {player_id} joined at {position}")
        
        if self.on_player_joined:
            self.on_player_joined(player_id, position)
            
    def handle_player_left(self, message):
        """Handle player left message."""
        data = message.get("data", {})
        player_id = data.get("playerId")
        
        print(f"👋 Player {player_id} left")
        
        if self.on_player_left:
            self.on_player_left(player_id)
            
    def handle_player_update(self, message):
        """Handle player update message."""
        data = message.get("data", {})
        player_id = data.get("playerId")
        position = data.get("position")
        rotation = data.get("rotation")
        health = data.get("health")
        energy = data.get("energy")
        
        # Update other player's state
        # This would typically update a player manager
        pass
        
    def handle_chat(self, message):
        """Handle chat message."""
        data = message.get("data", {})
        player_id = data.get("playerId")
        chat_message = data.get("message")
        timestamp = data.get("timestamp")
        
        print(f"💬 [{player_id}]: {chat_message}")
        
        if self.on_chat_message:
            self.on_chat_message(player_id, chat_message, timestamp)
            
    def handle_build(self, message):
        """Handle build action message."""
        data = message.get("data", {})
        player_id = data.get("playerId")
        position = data.get("position")
        block_type = data.get("blockType")
        action = data.get("action")  # place/remove
        
        print(f"🏗️ [{player_id}] {action} {block_type} at {position}")
        
        if self.on_build_action:
            self.on_build_action(player_id, position, block_type, action)
            
    def handle_interaction_response(self, message):
        """Handle interaction response message."""
        data = message.get("data", {})
        interaction_type = data.get("type")
        
        print(f"🎯 Interaction response: {interaction_type}")
        
    def handle_server_stats(self, message):
        """Handle server stats message."""
        data = message.get("data", {})
        player_count = data.get("playerCount")
        max_players = data.get("maxPlayers")
        uptime = data.get("uptime")
        
        print(f"📊 Server Stats: {player_count}/{max_players} players, uptime: {uptime}s")
        
    def handle_error(self, message):
        """Handle error message."""
        data = message.get("data", {})
        error_message = data.get("message", "Unknown error")
        
        print(f"❌ Server error: {error_message}")
        
    def send_message(self, message_type, data=None):
        """Send a message to the server."""
        if not self.connected:
            return False
            
        message = {
            "type": message_type,
            "data": data or {},
            "timestamp": time.time()
        }
        
        self.send_queue.put(message)
        return True
        
    def send_pending_messages(self):
        """Send all pending messages."""
        while not self.send_queue.empty():
            try:
                message = self.send_queue.get_nowait()
                if self.websocket and self.connected:
                    self.websocket.send(json.dumps(message))
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                
    def send_player_update(self, position, rotation, health, energy):
        """Send player state update to server."""
        data = {
            "position": {"x": position.x, "y": position.y, "z": position.z},
            "rotation": {"x": rotation.x, "y": rotation.y, "z": rotation.z},
            "health": health,
            "energy": energy
        }
        
        return self.send_message("playerUpdate", data)
        
    def send_chat_message(self, message):
        """Send a chat message to the server."""
        data = {"message": message}
        return self.send_message("chat", data)
        
    def send_build_action(self, position, block_type, action):
        """Send a build action to the server."""
        data = {
            "position": {"x": position.x, "y": position.y, "z": position.z},
            "blockType": block_type,
            "action": action
        }
        
        return self.send_message("build", data)
        
    def send_interaction(self, object_type, position):
        """Send an interaction request to the server."""
        data = {
            "objectType": object_type,
            "position": {"x": position.x, "y": position.y, "z": position.z}
        }
        
        return self.send_message("interact", data)
        
    def is_connected(self):
        """Check if connected to server."""
        return self.connected
        
    def get_player_id(self):
        """Get the current player ID."""
        return self.player_id
        
    def get_ping(self):
        """Get the current ping to server."""
        return self.ping
        
    def set_server_url(self, url):
        """Set the server URL."""
        self.server_url = url
        
    def set_on_connect_callback(self, callback):
        """Set the connection callback."""
        self.on_connect = callback
        
    def set_on_disconnect_callback(self, callback):
        """Set the disconnection callback."""
        self.on_disconnect = callback
        
    def set_on_player_joined_callback(self, callback):
        """Set the player joined callback."""
        self.on_player_joined = callback
        
    def set_on_player_left_callback(self, callback):
        """Set the player left callback."""
        self.on_player_left = callback
        
    def set_on_chat_message_callback(self, callback):
        """Set the chat message callback."""
        self.on_chat_message = callback
        
    def set_on_build_action_callback(self, callback):
        """Set the build action callback."""
        self.on_build_action = callback

class NetworkStats:
    """Network statistics and monitoring."""
    
    def __init__(self):
        """Initialize network statistics."""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.ping_history = []
        self.connection_time = 0
        self.disconnect_time = 0
        
    def record_message_sent(self, bytes_count):
        """Record a sent message."""
        self.bytes_sent += bytes_count
        self.messages_sent += 1
        
    def record_message_received(self, bytes_count):
        """Record a received message."""
        self.bytes_received += bytes_count
        self.messages_received += 1
        
    def record_ping(self, ping):
        """Record a ping measurement."""
        self.ping_history.append(ping)
        if len(self.ping_history) > 100:
            self.ping_history.pop(0)
            
    def get_average_ping(self):
        """Get the average ping."""
        if not self.ping_history:
            return 0
        return sum(self.ping_history) / len(self.ping_history)
        
    def get_min_ping(self):
        """Get the minimum ping."""
        if not self.ping_history:
            return 0
        return min(self.ping_history)
        
    def get_max_ping(self):
        """Get the maximum ping."""
        if not self.ping_history:
            return 0
        return max(self.ping_history)
        
    def get_bandwidth_usage(self):
        """Get current bandwidth usage in bytes per second."""
        # This would calculate actual bandwidth usage
        return {
            "sent": self.bytes_sent,
            "received": self.bytes_received,
            "total": self.bytes_sent + self.bytes_received
        }
        
    def reset(self):
        """Reset all statistics."""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.ping_history.clear()
        self.connection_time = 0
        self.disconnect_time = 0
