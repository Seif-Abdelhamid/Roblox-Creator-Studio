"""
Player Class
Handles player movement, physics, and rendering in the 3D world.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from vector3 import Vector3

class Player:
    """Player class representing a player in the 3D world."""
    
    def __init__(self):
        """Initialize the player."""
        # Position and movement
        self.position = Vector3(0, 2, 0)
        self.velocity = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)  # pitch, yaw, roll
        
        # Movement state
        self.move_forward = False
        self.move_backward = False
        self.move_left = False
        self.move_right = False
        self.sprint = False
        self.on_ground = False
        
        # Player stats
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        self.level = 1
        self.experience = 0
        
        # Player info
        self.username = "Player"
        self.player_id = None
        self.team = None
        
        # Physics
        self.gravity = -9.81
        self.jump_force = 8.0
        self.move_speed = 5.0
        self.sprint_multiplier = 1.5
        
        # Collision
        self.height = 1.8
        self.width = 0.6
        self.bounding_box = None
        
        # Animation
        self.animation_time = 0.0
        self.walking = False
        self.running = False
        
        # Inventory
        self.inventory = []
        self.selected_item = 0
        
        # Networking
        self.interpolation_time = 0.0
        self.target_position = None
        self.target_rotation = None
        
    def update(self, delta_time):
        """Update player logic."""
        # Update movement
        self.update_movement(delta_time)
        
        # Update physics
        self.update_physics(delta_time)
        
        # Update animation
        self.update_animation(delta_time)
        
        # Update interpolation for networked players
        if self.target_position:
            self.update_interpolation(delta_time)
            
    def update_movement(self, delta_time):
        """Update player movement based on input."""
        # Calculate movement direction
        move_direction = Vector3(0, 0, 0)
        
        if self.move_forward:
            move_direction.z -= 1
        if self.move_backward:
            move_direction.z += 1
        if self.move_left:
            move_direction.x -= 1
        if self.move_right:
            move_direction.x += 1
            
        # Normalize movement direction
        if move_direction.length() > 0:
            move_direction.normalize()
            
            # Apply rotation to movement direction
            yaw_rad = math.radians(self.rotation.y)
            cos_yaw = math.cos(yaw_rad)
            sin_yaw = math.sin(yaw_rad)
            
            rotated_x = move_direction.x * cos_yaw - move_direction.z * sin_yaw
            rotated_z = move_direction.x * sin_yaw + move_direction.z * cos_yaw
            
            # Calculate speed
            speed = self.move_speed
            if self.sprint and self.energy > 0:
                speed *= self.sprint_multiplier
                self.energy -= 10 * delta_time  # Drain energy while sprinting
                
            # Apply movement
            self.velocity.x = rotated_x * speed
            self.velocity.z = rotated_z * speed
            
            # Update animation state
            self.walking = True
            self.running = self.sprint
        else:
            # Apply friction when not moving
            self.velocity.x *= 0.8
            self.velocity.z *= 0.8
            self.walking = False
            self.running = False
            
        # Regenerate energy when not sprinting
        if not self.sprint and self.energy < self.max_energy:
            self.energy += 20 * delta_time
            self.energy = min(self.energy, self.max_energy)
            
    def update_physics(self, delta_time):
        """Update player physics."""
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            
        # Update position
        self.position += self.velocity * delta_time
        
        # Ground collision (simple)
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Update bounding box
        self.update_bounding_box()
        
    def update_animation(self, delta_time):
        """Update player animation."""
        self.animation_time += delta_time
        
        # Simple walking/running animation
        if self.walking:
            # Bob up and down
            bob_height = math.sin(self.animation_time * 10) * 0.1
            self.position.y += bob_height
            
    def update_interpolation(self, delta_time):
        """Update position interpolation for smooth networking."""
        self.interpolation_time += delta_time
        
        if self.target_position and self.interpolation_time < 0.1:
            # Interpolate position
            alpha = self.interpolation_time / 0.1
            self.position = self.position.lerp(self.target_position, alpha)
            
        if self.target_rotation and self.interpolation_time < 0.1:
            # Interpolate rotation
            alpha = self.interpolation_time / 0.1
            self.rotation = self.rotation.lerp(self.target_rotation, alpha)
            
    def jump(self):
        """Make the player jump."""
        if self.on_ground:
            self.velocity.y = self.jump_force
            self.on_ground = False
            
    def take_damage(self, damage):
        """Take damage and update health."""
        self.health -= damage
        self.health = max(0, self.health)
        
        if self.health <= 0:
            self.die()
            
    def heal(self, amount):
        """Heal the player."""
        self.health += amount
        self.health = min(self.health, self.max_health)
        
    def add_experience(self, amount):
        """Add experience and check for level up."""
        self.experience += amount
        
        # Simple level up system
        experience_needed = self.level * 100
        if self.experience >= experience_needed:
            self.level_up()
            
    def level_up(self):
        """Level up the player."""
        self.level += 1
        self.experience = 0
        self.max_health += 10
        self.health = self.max_health
        self.max_energy += 10
        self.energy = self.max_energy
        
        print(f"🎉 Level up! You are now level {self.level}")
        
    def die(self):
        """Handle player death."""
        print("💀 You died!")
        # Reset position to spawn point
        self.position = Vector3(0, 2, 0)
        self.velocity = Vector3(0, 0, 0)
        self.health = self.max_health
        
    def update_bounding_box(self):
        """Update the player's bounding box for collision detection."""
        half_width = self.width / 2
        half_height = self.height / 2
        
        self.bounding_box = {
            "min": Vector3(
                self.position.x - half_width,
                self.position.y - half_height,
                self.position.z - half_width
            ),
            "max": Vector3(
                self.position.x + half_width,
                self.position.y + half_height,
                self.position.z + half_width
            )
        }
        
    def render(self):
        """Render the player model."""
        glPushMatrix()
        
        # Apply player transformation
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation.y, 0, 1, 0)  # Yaw rotation
        
        # Render player body
        self.render_body()
        
        # Render player head
        self.render_head()
        
        # Render player arms
        self.render_arms()
        
        # Render player legs
        self.render_legs()
        
        glPopMatrix()
        
    def render_body(self):
        """Render the player's body."""
        glColor3f(0.2, 0.4, 0.8)  # Blue shirt
        
        # Body (torso)
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glScalef(0.4, 0.6, 0.2)
        self.draw_cube()
        glPopMatrix()
        
    def render_head(self):
        """Render the player's head."""
        glColor3f(0.9, 0.7, 0.5)  # Skin color
        
        # Head
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        glScalef(0.3, 0.3, 0.3)
        self.draw_cube()
        glPopMatrix()
        
    def render_arms(self):
        """Render the player's arms."""
        glColor3f(0.9, 0.7, 0.5)  # Skin color
        
        # Left arm
        glPushMatrix()
        glTranslatef(-0.5, 0.5, 0)
        glScalef(0.15, 0.5, 0.15)
        self.draw_cube()
        glPopMatrix()
        
        # Right arm
        glPushMatrix()
        glTranslatef(0.5, 0.5, 0)
        glScalef(0.15, 0.5, 0.15)
        self.draw_cube()
        glPopMatrix()
        
    def render_legs(self):
        """Render the player's legs."""
        glColor3f(0.2, 0.2, 0.2)  # Dark pants
        
        # Left leg
        glPushMatrix()
        glTranslatef(-0.15, -0.2, 0)
        glScalef(0.15, 0.6, 0.15)
        self.draw_cube()
        glPopMatrix()
        
        # Right leg
        glPushMatrix()
        glTranslatef(0.15, -0.2, 0)
        glScalef(0.15, 0.6, 0.15)
        self.draw_cube()
        glPopMatrix()
        
    def draw_cube(self):
        """Draw a simple cube."""
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, 1)
        
        # Back face
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, 1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, -1, -1)
        
        # Top face
        glVertex3f(-1, 1, -1)
        glVertex3f(-1, 1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(1, 1, -1)
        
        # Bottom face
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, -1, 1)
        glVertex3f(-1, -1, 1)
        
        # Right face
        glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 1)
        glVertex3f(1, -1, 1)
        
        # Left face
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, -1, 1)
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, 1, -1)
        
        glEnd()
        
    def get_data(self):
        """Get player data for networking."""
        return {
            "position": self.position.to_list(),
            "rotation": self.rotation.to_list(),
            "health": self.health,
            "energy": self.energy,
            "username": self.username,
            "level": self.level,
            "walking": self.walking,
            "running": self.running
        }
        
    def set_data(self, data):
        """Set player data from networking."""
        if "position" in data:
            self.target_position = Vector3(*data["position"])
        if "rotation" in data:
            self.target_rotation = Vector3(*data["rotation"])
        if "health" in data:
            self.health = data["health"]
        if "energy" in data:
            self.energy = data["energy"]
        if "username" in data:
            self.username = data["username"]
        if "level" in data:
            self.level = data["level"]
            
        self.interpolation_time = 0.0
