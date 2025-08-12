"""
Game Engine
Core 3D game engine handling rendering, physics, and world management.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
from player import Player
from world import World
from physics_engine import PhysicsEngine
from camera import Camera
from lighting import LightingSystem

class GameEngine:
    """Main game engine class handling 3D rendering and game logic."""
    
    def __init__(self, headless: bool = False):
        """Initialize the game engine."""
        self.is_headless = headless
        self.world = World()
        self.physics_engine = PhysicsEngine()
        self.camera = Camera()
        self.lighting = LightingSystem()
        
        # Player management
        self.local_player = Player()
        self.other_players = {}
        
        # Game state
        self.game_time = 0.0
        self.day_night_cycle = 0.0  # 0.0 = day, 1.0 = night
        
        # Rendering state
        self.frustum_culling = True
        self.occlusion_culling = True
        
        # Performance tracking
        self.fps_counter = 0
        self.frame_time = 0.0
        
        # Initialize systems
        if not self.is_headless:
            self.setup_rendering()
            self.setup_lighting()
        
    def setup_rendering(self):
        """Setup OpenGL rendering settings."""
        # Enable features
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set clear color
        glClearColor(0.5, 0.7, 1.0, 1.0)
        
        # Setup viewport
        glViewport(0, 0, 1280, 720)
        
    def setup_lighting(self):
        """Setup lighting system."""
        self.lighting.setup_ambient_light(0.3, 0.3, 0.3)
        self.lighting.setup_directional_light(0.7, 0.7, 0.7, 1.0, 1.0, 1.0)
        
    def update(self):
        """Update game engine logic."""
        delta_time = 1.0 / 60.0  # Fixed timestep for now
        
        # Update game time
        self.game_time += delta_time
        self.day_night_cycle = (math.sin(self.game_time * 0.1) + 1) / 2
        
        # Update camera
        self.camera.update(delta_time)
        
        # Update local player
        self.local_player.update(delta_time)
        
        # Update physics
        self.physics_engine.update(delta_time)
        
        # Update world
        self.world.update(delta_time)
        
        # Update lighting based on day/night cycle
        if not self.is_headless:
            self.update_lighting()
        
        # Update other players
        for player in self.other_players.values():
            player.update(delta_time)
            
    def update_lighting(self):
        """Update lighting based on day/night cycle."""
        # Day lighting
        day_intensity = 1.0 - self.day_night_cycle
        night_intensity = self.day_night_cycle
        
        # Ambient light
        ambient_r = 0.3 * day_intensity + 0.1 * night_intensity
        ambient_g = 0.3 * day_intensity + 0.1 * night_intensity
        ambient_b = 0.3 * day_intensity + 0.2 * night_intensity
        
        self.lighting.setup_ambient_light(ambient_r, ambient_g, ambient_b)
        
        # Directional light (sun/moon)
        sun_intensity = 0.7 * day_intensity
        moon_intensity = 0.3 * night_intensity
        
        self.lighting.setup_directional_light(
            sun_intensity + moon_intensity,
            sun_intensity + moon_intensity,
            sun_intensity + moon_intensity * 0.5,
            1.0, 1.0, 1.0
        )
        
    def render(self):
        """Render the 3D world."""
        if self.is_headless:
            return
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1280/720, 0.1, 1000.0)
        
        # Setup modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply camera transformation
        self.camera.apply()
        
        # Setup lighting
        self.lighting.apply()
        
        # Render skybox
        self.render_skybox()
        
        # Render world
        self.world.render(self.camera.position, self.camera.frustum)
        
        # Render players
        self.render_players()
        
        # Render UI elements in 3D space
        self.render_3d_ui()
        
    def render_skybox(self):
        """Render the skybox."""
        glPushMatrix()
        glLoadIdentity()
        
        # Disable lighting for skybox
        glDisable(GL_LIGHTING)
        
        # Draw sky gradient
        glBegin(GL_QUADS)
        
        # Top (sky)
        if self.day_night_cycle < 0.5:  # Day
            glColor3f(0.5, 0.7, 1.0)
        else:  # Night
            glColor3f(0.1, 0.1, 0.3)
        glVertex3f(-1000, 500, -1000)
        glVertex3f(1000, 500, -1000)
        glVertex3f(1000, 500, 1000)
        glVertex3f(-1000, 500, 1000)
        
        # Bottom (ground)
        glColor3f(0.2, 0.5, 0.2)
        glVertex3f(-1000, -500, -1000)
        glVertex3f(1000, -500, -1000)
        glVertex3f(1000, -500, 1000)
        glVertex3f(-1000, -500, 1000)
        
        # Sides
        for i in range(4):
            angle = i * 90
            x1 = math.cos(math.radians(angle)) * 1000
            z1 = math.sin(math.radians(angle)) * 1000
            x2 = math.cos(math.radians(angle + 90)) * 1000
            z2 = math.sin(math.radians(angle + 90)) * 1000
            
            # Top to bottom gradient
            glColor3f(0.5, 0.7, 1.0)
            glVertex3f(x1, 500, z1)
            glVertex3f(x2, 500, z2)
            glColor3f(0.2, 0.5, 0.2)
            glVertex3f(x2, -500, z2)
            glVertex3f(x1, -500, z1)
            
        glEnd()
        
        # Re-enable lighting
        glEnable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)  # Reset color
        
        glPopMatrix()
        
    def render_players(self):
        """Render other players in the world."""
        # Placeholder for rendering other players
        pass
        
    def render_3d_ui(self):
        """Render 3D UI elements like markers and indicators."""
        # Placeholder for 3D UI rendering
        pass
        
    def world_to_screen(self, world_pos):
        """Convert 3D world position to 2D screen position."""
        # Get modelview and projection matrices
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # Convert world coordinates to screen coordinates
        screen_pos = gluProject(
            world_pos[0], world_pos[1], world_pos[2],
            modelview, projection, viewport
        )
        
        if screen_pos:
            return (screen_pos[0], screen_pos[1])
        return None
        
    def render_text_2d(self, text, x, y, color=(1.0, 1.0, 1.0), size=16):
        """Render 2D text on screen."""
        # This would use pygame's font rendering
        # For now, we'll just draw a simple rectangle
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x - 50, y - 10)
        glVertex2f(x + 50, y - 10)
        glVertex2f(x + 50, y + 10)
        glVertex2f(x - 50, y + 10)
        glEnd()
        
    def handle_input(self, event):
        """Handle input events."""
        if event.type == KEYDOWN:
            if event.key == K_w:
                self.local_player.move_forward = True
            elif event.key == K_s:
                self.local_player.move_backward = True
            elif event.key == K_a:
                self.local_player.move_left = True
            elif event.key == K_d:
                self.local_player.move_right = True
            elif event.key == K_SPACE:
                self.local_player.jump()
            elif event.key == K_LSHIFT:
                self.local_player.sprint = True
                
        elif event.type == KEYUP:
            if event.key == K_w:
                self.local_player.move_forward = False
            elif event.key == K_s:
                self.local_player.move_backward = False
            elif event.key == K_a:
                self.local_player.move_left = False
            elif event.key == K_d:
                self.local_player.move_right = False
            elif event.key == K_LSHIFT:
                self.local_player.sprint = False
                
        elif event.type == MOUSEMOTION:
            # Handle mouse look
            if event.rel[0] != 0:
                self.camera.rotate_y(-event.rel[0] * 0.1)
            if event.rel[1] != 0:
                self.camera.rotate_x(-event.rel[1] * 0.1)
                
    def add_player(self, player_id, player_data):
        """Add a new player to the game."""
        player = Player()
        player.username = player_data.get("username", f"Player_{player_id}")
        player.position = player_data.get("position", (0, 0, 0))
        self.other_players[player_id] = player
        
    def remove_player(self, player_id):
        """Remove a player from the game."""
        if player_id in self.other_players:
            del self.other_players[player_id]
            
    def get_player_data(self):
        """Get current player data for networking."""
        return {
            "position": self.local_player.position,
            "rotation": self.local_player.rotation,
            "health": self.local_player.health,
            "username": self.local_player.username
        }
