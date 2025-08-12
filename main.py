#!/usr/bin/env python3
"""
Roblox Creator Studio - 3D Multiplayer Game
A Python-based 3D multiplayer game inspired by Roblox's vision of connecting people
through immersive digital experiences.

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import json
import threading
import time
from game_engine import GameEngine
from network_manager import NetworkManager
from ui_manager import UIManager
from asset_manager import AssetManager
from config import GameConfig

class RobloxCreatorStudio:
    def __init__(self):
        """Initialize the Roblox Creator Studio game."""
        pygame.init()
        self.config = GameConfig()
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize managers
        self.asset_manager = AssetManager()
        self.network_manager = NetworkManager()
        self.ui_manager = UIManager()
        self.game_engine = GameEngine()
        
        # Setup display
        self.setup_display()
        
        # Game state
        self.current_scene = "main_menu"
        self.player_data = {
            "username": "Player",
            "level": 1,
            "experience": 0,
            "inventory": []
        }
        
    def setup_display(self):
        """Setup the game display and OpenGL context."""
        pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption("Roblox Creator Studio - Connect • Create • Play")
        
        # Setup OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.2, 0.3, 0.5, 1.0)
        
        # Setup perspective
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.config.WINDOW_WIDTH / self.config.WINDOW_HEIGHT), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
    def run(self):
        """Main game loop."""
        self.running = True
        print("🎮 Welcome to Roblox Creator Studio!")
        print("🌍 Connecting to the global community...")
        
        # Start network connection
        self.network_manager.connect()
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.config.FPS)
            
        self.cleanup()
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.current_scene == "game":
                        self.current_scene = "pause_menu"
                    else:
                        self.running = False
                        
            # Handle UI events
            self.ui_manager.handle_event(event, self)
            
    def update(self):
        """Update game logic."""
        if self.current_scene == "game":
            self.game_engine.update()
            self.network_manager.update()
            
        self.ui_manager.update()
        
    def render(self):
        """Render the current scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.current_scene == "main_menu":
            self.render_main_menu()
        elif self.current_scene == "game":
            self.render_game()
        elif self.current_scene == "pause_menu":
            self.render_pause_menu()
        elif self.current_scene == "settings":
            self.render_settings()
            
        pygame.display.flip()
        
    def render_main_menu(self):
        """Render the main menu."""
        # 2D overlay for UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable 3D lighting for 2D rendering
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Render UI elements
        self.ui_manager.render_main_menu()
        
        # Restore 3D settings
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def render_game(self):
        """Render the 3D game world."""
        self.game_engine.render()
        self.ui_manager.render_game_ui()
        
    def render_pause_menu(self):
        """Render the pause menu."""
        self.ui_manager.render_pause_menu()
        
    def render_settings(self):
        """Render the settings menu."""
        self.ui_manager.render_settings()
        
    def cleanup(self):
        """Cleanup resources before exit."""
        print("👋 Thanks for playing Roblox Creator Studio!")
        self.network_manager.disconnect()
        pygame.quit()
        sys.exit()

def main():
    """Main entry point."""
    try:
        game = RobloxCreatorStudio()
        game.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
