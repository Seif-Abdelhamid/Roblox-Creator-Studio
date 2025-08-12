"""
Lighting System
Handles dynamic lighting, shadows, and atmospheric effects.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from vector3 import Vector3

class LightingSystem:
    """Dynamic lighting system for the game world."""
    
    def __init__(self):
        """Initialize the lighting system."""
        # Light sources
        self.lights = []
        self.ambient_light = (0.3, 0.3, 0.3)
        self.global_light = (1.0, 1.0, 1.0)
        
        # Shadow settings
        self.shadows_enabled = True
        self.shadow_map_size = 1024
        self.shadow_bias = 0.005
        
        # Atmospheric effects
        self.fog_enabled = True
        self.fog_color = (0.5, 0.7, 1.0)
        self.fog_start = 50.0
        self.fog_end = 200.0
        
        # Day/night cycle
        self.time_of_day = 0.0  # 0.0 = noon, 0.5 = sunset, 1.0 = midnight
        self.day_length = 1200.0  # seconds for full day cycle
        
        # Initialize lighting
        self.setup_lighting()
        
    def setup_lighting(self):
        """Setup OpenGL lighting."""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Setup material properties
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Setup ambient light
        self.setup_ambient_light(*self.ambient_light)
        
        # Setup directional light (sun)
        self.setup_directional_light(*self.global_light, 1.0, 1.0, 1.0)
        
    def update(self, delta_time):
        """Update lighting system."""
        # Update day/night cycle
        self.update_day_night_cycle(delta_time)
        
        # Update light positions and intensities
        self.update_lights()
        
        # Update atmospheric effects
        self.update_atmospheric_effects()
        
    def update_day_night_cycle(self, delta_time):
        """Update the day/night cycle."""
        self.time_of_day += delta_time / self.day_length
        if self.time_of_day > 1.0:
            self.time_of_day -= 1.0
            
        # Calculate sun position
        sun_angle = self.time_of_day * 2 * math.pi
        sun_height = math.sin(sun_angle)
        sun_intensity = max(0.0, sun_height)
        
        # Update global lighting based on time of day
        if sun_height > 0:
            # Day time
            ambient_intensity = 0.3 + 0.4 * sun_intensity
            self.ambient_light = (ambient_intensity, ambient_intensity, ambient_intensity)
            self.global_light = (sun_intensity, sun_intensity, sun_intensity * 0.8)
        else:
            # Night time
            moon_intensity = abs(sun_height) * 0.3
            self.ambient_light = (0.1, 0.1, 0.2)
            self.global_light = (moon_intensity, moon_intensity, moon_intensity * 1.2)
            
        # Update fog color based on time of day
        if sun_height > 0.2:
            # Day fog
            self.fog_color = (0.5, 0.7, 1.0)
        elif sun_height > -0.2:
            # Sunset/sunrise fog
            self.fog_color = (1.0, 0.6, 0.3)
        else:
            # Night fog
            self.fog_color = (0.1, 0.1, 0.3)
            
    def update_lights(self):
        """Update all light sources."""
        for light in self.lights:
            if hasattr(light, 'update'):
                light.update()
                
    def update_atmospheric_effects(self):
        """Update atmospheric effects like fog."""
        if self.fog_enabled:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_LINEAR)
            glFogf(GL_FOG_START, self.fog_start)
            glFogf(GL_FOG_END, self.fog_end)
            glFogfv(GL_FOG_COLOR, self.fog_color + (1.0,))
        else:
            glDisable(GL_FOG)
            
    def setup_ambient_light(self, r, g, b):
        """Setup ambient lighting."""
        self.ambient_light = (r, g, b)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (r, g, b, 1.0))
        
    def setup_directional_light(self, r, g, b, x, y, z):
        """Setup directional lighting (sun)."""
        self.global_light = (r, g, b)
        glLightfv(GL_LIGHT0, GL_POSITION, (x, y, z, 0.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (r, g, b, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (r, g, b, 1.0))
        
    def add_light(self, light):
        """Add a light source to the scene."""
        self.lights.append(light)
        
    def remove_light(self, light):
        """Remove a light source from the scene."""
        if light in self.lights:
            self.lights.remove(light)
            
    def apply(self):
        """Apply lighting to the current scene."""
        # Apply ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.ambient_light + (1.0,))
        
        # Apply directional light
        sun_direction = self.get_sun_direction()
        glLightfv(GL_LIGHT0, GL_POSITION, (sun_direction.x, sun_direction.y, sun_direction.z, 0.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.global_light + (1.0,))
        
        # Apply all other lights
        for i, light in enumerate(self.lights):
            light.apply(i + 1)  # Start from LIGHT1 since LIGHT0 is the sun
            
    def get_sun_direction(self):
        """Get the current sun direction vector."""
        sun_angle = self.time_of_day * 2 * math.pi
        sun_height = math.sin(sun_angle)
        sun_azimuth = math.cos(sun_angle)
        
        # Calculate sun position in sky
        sun_x = math.cos(sun_angle) * 1000
        sun_y = sun_height * 1000
        sun_z = math.sin(sun_angle) * 1000
        
        # Return normalized direction vector
        return Vector3(sun_x, sun_y, sun_z).normalized()
        
    def get_light_at_position(self, position):
        """Get the total light intensity at a specific position."""
        total_light = Vector3(*self.ambient_light)
        
        # Add directional light (sun)
        sun_direction = self.get_sun_direction()
        sun_intensity = max(0, sun_direction.y)  # Only positive Y contributes
        total_light += Vector3(*self.global_light) * sun_intensity
        
        # Add all other lights
        for light in self.lights:
            light_intensity = light.get_intensity_at(position)
            total_light += light_intensity
            
        return total_light
        
    def set_shadows_enabled(self, enabled):
        """Enable or disable shadows."""
        self.shadows_enabled = enabled
        
    def set_fog_enabled(self, enabled):
        """Enable or disable fog."""
        self.fog_enabled = enabled
        
    def set_fog_parameters(self, start, end, color):
        """Set fog parameters."""
        self.fog_start = start
        self.fog_end = end
        self.fog_color = color
        
    def get_time_of_day(self):
        """Get the current time of day (0.0 to 1.0)."""
        return self.time_of_day
        
    def set_time_of_day(self, time):
        """Set the time of day (0.0 to 1.0)."""
        self.time_of_day = max(0.0, min(1.0, time))
        
    def is_day(self):
        """Check if it's currently day time."""
        return self.time_of_day < 0.5
        
    def is_night(self):
        """Check if it's currently night time."""
        return self.time_of_day >= 0.5
        
    def get_day_progress(self):
        """Get the progress through the current day (0.0 to 1.0)."""
        return self.time_of_day

class Light:
    """Base class for light sources."""
    
    def __init__(self, position, color, intensity=1.0):
        """Initialize a light source."""
        self.position = position
        self.color = color
        self.intensity = intensity
        self.enabled = True
        
    def update(self):
        """Update light logic."""
        pass
        
    def apply(self, light_id):
        """Apply this light to OpenGL."""
        if not self.enabled:
            return
            
        glEnable(GL_LIGHT0 + light_id)
        glLightfv(GL_LIGHT0 + light_id, GL_POSITION, (self.position.x, self.position.y, self.position.z, 1.0))
        glLightfv(GL_LIGHT0 + light_id, GL_DIFFUSE, self.color + (1.0,))
        glLightfv(GL_LIGHT0 + light_id, GL_SPECULAR, self.color + (1.0,))
        
    def get_intensity_at(self, position):
        """Get the light intensity at a specific position."""
        if not self.enabled:
            return Vector3(0, 0, 0)
            
        distance = self.position.distance_to(position)
        if distance > self.range:
            return Vector3(0, 0, 0)
            
        # Calculate attenuation
        attenuation = 1.0 / (1.0 + distance * distance * self.attenuation)
        intensity = self.intensity * attenuation
        
        return Vector3(*self.color) * intensity
        
    def set_enabled(self, enabled):
        """Enable or disable this light."""
        self.enabled = enabled
        
    def set_position(self, position):
        """Set the light position."""
        self.position = position
        
    def set_color(self, color):
        """Set the light color."""
        self.color = color
        
    def set_intensity(self, intensity):
        """Set the light intensity."""
        self.intensity = intensity

class PointLight(Light):
    """A point light source that emits light in all directions."""
    
    def __init__(self, position, color, intensity=1.0, range=10.0, attenuation=0.1):
        """Initialize a point light."""
        super().__init__(position, color, intensity)
        self.range = range
        self.attenuation = attenuation
        
    def apply(self, light_id):
        """Apply this point light to OpenGL."""
        if not self.enabled:
            return
            
        glEnable(GL_LIGHT0 + light_id)
        glLightfv(GL_LIGHT0 + light_id, GL_POSITION, (self.position.x, self.position.y, self.position.z, 1.0))
        glLightfv(GL_LIGHT0 + light_id, GL_DIFFUSE, self.color + (1.0,))
        glLightfv(GL_LIGHT0 + light_id, GL_SPECULAR, self.color + (1.0,))
        
        # Set attenuation
        glLightf(GL_LIGHT0 + light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0 + light_id, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0 + light_id, GL_QUADRATIC_ATTENUATION, self.attenuation)

class SpotLight(Light):
    """A spotlight that emits light in a cone."""
    
    def __init__(self, position, direction, color, intensity=1.0, range=10.0, 
                 cutoff=30.0, attenuation=0.1):
        """Initialize a spotlight."""
        super().__init__(position, color, intensity)
        self.direction = direction.normalized()
        self.range = range
        self.cutoff = cutoff
        self.attenuation = attenuation
        
    def apply(self, light_id):
        """Apply this spotlight to OpenGL."""
        if not self.enabled:
            return
            
        glEnable(GL_LIGHT0 + light_id)
        glLightfv(GL_LIGHT0 + light_id, GL_POSITION, (self.position.x, self.position.y, self.position.z, 1.0))
        glLightfv(GL_LIGHT0 + light_id, GL_DIFFUSE, self.color + (1.0,))
        glLightfv(GL_LIGHT0 + light_id, GL_SPECULAR, self.color + (1.0,))
        
        # Set spotlight direction
        glLightfv(GL_LIGHT0 + light_id, GL_SPOT_DIRECTION, (self.direction.x, self.direction.y, self.direction.z))
        glLightf(GL_LIGHT0 + light_id, GL_SPOT_CUTOFF, self.cutoff)
        glLightf(GL_LIGHT0 + light_id, GL_SPOT_EXPONENT, 1.0)
        
        # Set attenuation
        glLightf(GL_LIGHT0 + light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0 + light_id, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0 + light_id, GL_QUADRATIC_ATTENUATION, self.attenuation)
        
    def get_intensity_at(self, position):
        """Get the light intensity at a specific position."""
        if not self.enabled:
            return Vector3(0, 0, 0)
            
        # Calculate distance
        to_position = position - self.position
        distance = to_position.length()
        
        if distance > self.range:
            return Vector3(0, 0, 0)
            
        # Calculate angle from spotlight direction
        to_position_normalized = to_position.normalized()
        angle = math.degrees(math.acos(self.direction.dot(to_position_normalized)))
        
        if angle > self.cutoff:
            return Vector3(0, 0, 0)
            
        # Calculate attenuation
        distance_attenuation = 1.0 / (1.0 + distance * distance * self.attenuation)
        angle_attenuation = 1.0 - (angle / self.cutoff)
        intensity = self.intensity * distance_attenuation * angle_attenuation
        
        return Vector3(*self.color) * intensity

class DirectionalLight(Light):
    """A directional light source (like the sun)."""
    
    def __init__(self, direction, color, intensity=1.0):
        """Initialize a directional light."""
        super().__init__(Vector3(0, 0, 0), color, intensity)
        self.direction = direction.normalized()
        
    def apply(self, light_id):
        """Apply this directional light to OpenGL."""
        if not self.enabled:
            return
            
        glEnable(GL_LIGHT0 + light_id)
        glLightfv(GL_LIGHT0 + light_id, GL_POSITION, (self.direction.x, self.direction.y, self.direction.z, 0.0))
        glLightfv(GL_LIGHT0 + light_id, GL_DIFFUSE, self.color + (1.0,))
        glLightfv(GL_LIGHT0 + light_id, GL_SPECULAR, self.color + (1.0,))
        
    def get_intensity_at(self, position):
        """Get the light intensity at a specific position."""
        if not self.enabled:
            return Vector3(0, 0, 0)
            
        # Directional light has constant intensity everywhere
        return Vector3(*self.color) * self.intensity
