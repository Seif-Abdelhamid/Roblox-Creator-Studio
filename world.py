"""
World Management System
Handles world generation, chunk loading, and terrain management.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
import os
from vector3 import Vector3

class World:
    """World class managing the 3D game world."""
    
    def __init__(self):
        """Initialize the world."""
        self.chunks = {}
        self.chunk_size = 16
        self.world_size = 1000
        self.max_height = 256
        
        # Terrain generation
        self.seed = random.randint(0, 1000000)
        self.noise_scale = 50.0
        self.height_scale = 32.0
        
        # World objects
        self.static_objects = []
        self.dynamic_objects = []
        self.buildings = []
        
        # Lighting
        self.ambient_light = (0.3, 0.3, 0.3)
        self.sun_direction = Vector3(1, 1, 1).normalized()
        
        # Generate initial world
        self.generate_world()
        # In very large worlds this can be heavy; keep initial data small for headless smoke tests
        if os.environ.get("HEADLESS"):
            # Trim chunks to a tiny subset
            keys = list(self.chunks.keys())
            for k in keys[100:]:
                self.chunks.pop(k, None)
        
    def generate_world(self):
        """Generate the initial world."""
        print("🌍 Generating world...")
        
        # Generate terrain
        self.generate_terrain()
        
        # Generate structures
        self.generate_structures()
        
        # Generate vegetation
        self.generate_vegetation()
        
        print("✅ World generation complete!")
        
    def generate_terrain(self):
        """Generate terrain using procedural noise."""
        for x in range(-self.world_size, self.world_size, self.chunk_size):
            for z in range(-self.world_size, self.world_size, self.chunk_size):
                chunk = self.generate_chunk(x, z)
                self.chunks[(x, z)] = chunk
                
    def generate_chunk(self, x, z):
        """Generate a single chunk of terrain."""
        chunk = {
            'position': (x, z),
            'blocks': {},
            'height_map': {},
            'objects': []
        }
        
        # Generate height map using Perlin noise
        for local_x in range(self.chunk_size):
            for local_z in range(self.chunk_size):
                world_x = x + local_x
                world_z = z + local_z
                
                # Generate height using multiple noise layers
                height = self.generate_height(world_x, world_z)
                chunk['height_map'][(local_x, local_z)] = height
                
                # Generate terrain blocks
                for y in range(int(height)):
                    block_type = self.get_block_type(world_x, y, world_z)
                    chunk['blocks'][(local_x, y, local_z)] = block_type
                    
        return chunk
        
    def generate_height(self, x, z):
        """Generate height at a specific position using Perlin noise."""
        # Base terrain
        base_height = self.perlin_noise(x / self.noise_scale, z / self.noise_scale)
        
        # Mountain layer
        mountain_height = self.perlin_noise(x / (self.noise_scale * 0.5), z / (self.noise_scale * 0.5)) * 0.5
        
        # Detail layer
        detail_height = self.perlin_noise(x / (self.noise_scale * 0.25), z / (self.noise_scale * 0.25)) * 0.25
        
        # Combine layers
        total_height = (base_height + mountain_height + detail_height) * self.height_scale
        total_height = max(0, min(self.max_height - 1, total_height))
        
        return total_height
        
    def perlin_noise(self, x, z):
        """Simple Perlin noise implementation."""
        # This is a simplified version - in a real implementation you'd use a proper Perlin noise library
        return (math.sin(x * 0.1) + math.sin(z * 0.1) + math.sin((x + z) * 0.1)) / 3.0
        
    def get_block_type(self, x, y, z):
        """Determine block type based on position and height."""
        height = self.get_height_at(x, z)
        
        if y == 0:
            return "bedrock"
        elif y < height * 0.3:
            return "stone"
        elif y < height * 0.7:
            return "dirt"
        elif y < height:
            return "grass"
        else:
            return "air"
            
    def get_height_at(self, x, z):
        """Get the height at a specific world position."""
        chunk_x = (x // self.chunk_size) * self.chunk_size
        chunk_z = (z // self.chunk_size) * self.chunk_size
        
        if (chunk_x, chunk_z) in self.chunks:
            local_x = x % self.chunk_size
            local_z = z % self.chunk_size
            return self.chunks[(chunk_x, chunk_z)]['height_map'].get((local_x, local_z), 0)
        
        return 0
        
    def generate_structures(self):
        """Generate structures in the world."""
        # Generate spawn point
        self.generate_spawn_point()
        
        # Generate random buildings
        for _ in range(10):
            x = random.randint(-self.world_size, self.world_size)
            z = random.randint(-self.world_size, self.world_size)
            self.generate_building(x, z)
            
    def generate_spawn_point(self):
        """Generate the spawn point area."""
        spawn_building = {
            'type': 'spawn',
            'position': Vector3(0, 0, 0),
            'size': Vector3(10, 5, 10),
            'color': (0.8, 0.8, 1.0)
        }
        self.buildings.append(spawn_building)
        
    def generate_building(self, x, z):
        """Generate a random building."""
        height = self.get_height_at(x, z)
        building_height = random.randint(3, 8)
        building_width = random.randint(4, 8)
        
        building = {
            'type': 'house',
            'position': Vector3(x, height, z),
            'size': Vector3(building_width, building_height, building_width),
            'color': (random.random(), random.random(), random.random())
        }
        self.buildings.append(building)
        
    def generate_vegetation(self):
        """Generate vegetation in the world."""
        for _ in range(50):
            x = random.randint(-self.world_size, self.world_size)
            z = random.randint(-self.world_size, self.world_size)
            height = self.get_height_at(x, z)
            
            # Only place trees on grass
            if self.get_block_type(x, height - 1, z) == "grass":
                tree = {
                    'type': 'tree',
                    'position': Vector3(x, height, z),
                    'size': Vector3(2, random.randint(4, 6), 2),
                    'color': (0.2, 0.6, 0.2)
                }
                self.static_objects.append(tree)
                
    def update(self, delta_time):
        """Update world logic."""
        # Update dynamic objects
        for obj in self.dynamic_objects:
            if hasattr(obj, 'update'):
                obj.update(delta_time)
                
    def render(self, camera_position, frustum):
        """Render the world."""
        # Render terrain
        self.render_terrain(camera_position, frustum)
        
        # Render buildings
        self.render_buildings(camera_position, frustum)
        
        # Render objects
        self.render_objects(camera_position, frustum)
        
    def render_terrain(self, camera_position, frustum):
        """Render the terrain."""
        # Get visible chunks
        visible_chunks = self.get_visible_chunks(camera_position, frustum)
        
        for chunk_pos in visible_chunks:
            if chunk_pos in self.chunks:
                self.render_chunk(self.chunks[chunk_pos])
                
    def render_chunk(self, chunk):
        """Render a single chunk."""
        for (x, y, z), block_type in chunk['blocks'].items():
            if block_type != "air":
                world_x = chunk['position'][0] + x
                world_z = chunk['position'][1] + z
                
                # Set block color
                color = self.get_block_color(block_type)
                glColor3f(*color)
                
                # Render block
                self.render_block(world_x, y, world_z)
                
        glColor3f(1.0, 1.0, 1.0)  # Reset color
        
    def render_block(self, x, y, z):
        """Render a single block."""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(1.0, 1.0, 1.0)
        
        # Draw cube
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
        
        glPopMatrix()
        
    def get_block_color(self, block_type):
        """Get the color for a block type."""
        colors = {
            "bedrock": (0.2, 0.2, 0.2),
            "stone": (0.5, 0.5, 0.5),
            "dirt": (0.6, 0.4, 0.2),
            "grass": (0.2, 0.6, 0.2),
            "sand": (0.8, 0.8, 0.2),
            "water": (0.2, 0.4, 0.8),
            "wood": (0.4, 0.2, 0.1),
            "leaves": (0.1, 0.5, 0.1)
        }
        return colors.get(block_type, (1.0, 1.0, 1.0))
        
    def render_buildings(self, camera_position, frustum):
        """Render buildings."""
        for building in self.buildings:
            if self.is_visible(building['position'], camera_position, frustum):
                self.render_building(building)
                
    def render_building(self, building):
        """Render a single building."""
        glPushMatrix()
        glTranslatef(building['position'].x, building['position'].y, building['position'].z)
        glScalef(building['size'].x, building['size'].y, building['size'].z)
        
        glColor3f(*building['color'])
        
        # Draw building as a cube
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)  # Reset color
        glPopMatrix()
        
    def render_objects(self, camera_position, frustum):
        """Render world objects."""
        for obj in self.static_objects + self.dynamic_objects:
            if self.is_visible(obj['position'], camera_position, frustum):
                self.render_object(obj)
                
    def render_object(self, obj):
        """Render a single object."""
        glPushMatrix()
        glTranslatef(obj['position'].x, obj['position'].y, obj['position'].z)
        glScalef(obj['size'].x, obj['size'].y, obj['size'].z)
        
        glColor3f(*obj['color'])
        
        if obj['type'] == 'tree':
            self.render_tree()
        else:
            # Default cube rendering
            self.render_block(0, 0, 0)
            
        glColor3f(1.0, 1.0, 1.0)  # Reset color
        glPopMatrix()
        
    def render_tree(self):
        """Render a tree object."""
        # Tree trunk
        glColor3f(0.4, 0.2, 0.1)
        glPushMatrix()
        glScalef(0.3, 1.0, 0.3)
        self.render_block(0, 0, 0)
        glPopMatrix()
        
        # Tree leaves
        glColor3f(0.1, 0.5, 0.1)
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glScalef(1.0, 0.8, 1.0)
        self.render_block(0, 0, 0)
        glPopMatrix()
        
    def get_visible_chunks(self, camera_position, frustum):
        """Get chunks visible from the camera position."""
        visible_chunks = []
        render_distance = 100
        
        for x in range(-render_distance, render_distance, self.chunk_size):
            for z in range(-render_distance, render_distance, self.chunk_size):
                chunk_x = (camera_position.x + x) // self.chunk_size * self.chunk_size
                chunk_z = (camera_position.z + z) // self.chunk_size * self.chunk_size
                
                if self.is_chunk_visible((chunk_x, chunk_z), camera_position, frustum):
                    visible_chunks.append((chunk_x, chunk_z))
                    
        return visible_chunks
        
    def is_chunk_visible(self, chunk_pos, camera_position, frustum):
        """Check if a chunk is visible from the camera."""
        # Simple distance check
        chunk_center = Vector3(chunk_pos[0] + self.chunk_size // 2, 0, chunk_pos[1] + self.chunk_size // 2)
        distance = camera_position.distance_to(chunk_center)
        return distance < 200  # Render distance
        
    def is_visible(self, position, camera_position, frustum):
        """Check if an object is visible from the camera."""
        # Simple distance check
        distance = camera_position.distance_to(position)
        return distance < 100  # Visibility distance
        
    def get_block_at(self, x, y, z):
        """Get the block at a specific position."""
        chunk_x = (x // self.chunk_size) * self.chunk_size
        chunk_z = (z // self.chunk_size) * self.chunk_size
        
        if (chunk_x, chunk_z) in self.chunks:
            local_x = x % self.chunk_size
            local_z = z % self.chunk_size
            return self.chunks[(chunk_x, chunk_z)]['blocks'].get((local_x, y, local_z), "air")
        
        return "air"
        
    def set_block_at(self, x, y, z, block_type):
        """Set a block at a specific position."""
        chunk_x = (x // self.chunk_size) * self.chunk_size
        chunk_z = (z // self.chunk_size) * self.chunk_size
        
        if (chunk_x, chunk_z) in self.chunks:
            local_x = x % self.chunk_size
            local_z = z % self.chunk_size
            
            if block_type == "air":
                # Remove block
                if (local_x, y, local_z) in self.chunks[(chunk_x, chunk_z)]['blocks']:
                    del self.chunks[(chunk_x, chunk_z)]['blocks'][(local_x, y, local_z)]
            else:
                # Add/update block
                self.chunks[(chunk_x, chunk_z)]['blocks'][(local_x, y, local_z)] = block_type
                
    def get_spawn_point(self):
        """Get the spawn point position."""
        return Vector3(0, 10, 0)  # Spawn above the spawn building
