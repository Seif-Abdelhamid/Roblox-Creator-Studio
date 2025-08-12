"""
Camera System
Handles 3D camera movement, rotation, and projection.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from vector3 import Vector3
import os

class Camera:
    """3D camera for viewing the game world."""
    
    def __init__(self):
        """Initialize the camera."""
        # Position and orientation
        self.position = Vector3(0, 5, 10)
        self.rotation = Vector3(0, 0, 0)  # pitch, yaw, roll
        self.target = Vector3(0, 0, 0)
        
        # Camera settings
        self.fov = 45.0
        self.near_plane = 0.1
        self.far_plane = 1000.0
        self.aspect_ratio = 16.0 / 9.0
        
        # Movement
        self.move_speed = 10.0
        self.rotation_speed = 2.0
        self.zoom_speed = 5.0
        
        # Camera modes
        self.mode = "first_person"  # first_person, third_person, free_camera
        self.follow_target = None
        self.follow_distance = 5.0
        self.follow_height = 2.0
        
        # Smoothing
        self.smooth_factor = 0.1
        self.target_position = self.position.copy()
        self.target_rotation = self.rotation.copy()
        
        # Frustum for culling
        self.frustum = None
        if not str(os.environ.get("HEADLESS", "")).lower() in {"1", "true", "yes"}:
            self.update_frustum()
        
    def update(self, delta_time):
        """Update camera logic."""
        # Update smooth movement
        self.update_smooth_movement(delta_time)
        
        # Update camera mode
        self.update_camera_mode(delta_time)
        
        # Update frustum
        if not str(os.environ.get("HEADLESS", "")).lower() in {"1", "true", "yes"}:
            self.update_frustum()
        
    def update_smooth_movement(self, delta_time):
        """Update smooth camera movement."""
        # Smooth position
        self.position = self.position.lerp(self.target_position, self.smooth_factor)
        
        # Smooth rotation
        self.rotation = self.rotation.lerp(self.target_rotation, self.smooth_factor)
        
    def update_camera_mode(self, delta_time):
        """Update camera based on current mode."""
        if self.mode == "first_person":
            self.update_first_person(delta_time)
        elif self.mode == "third_person":
            self.update_third_person(delta_time)
        elif self.mode == "free_camera":
            self.update_free_camera(delta_time)
            
    def update_first_person(self, delta_time):
        """Update first-person camera."""
        # First-person camera follows the player directly
        if self.follow_target:
            self.position = self.follow_target.position + Vector3(0, 1.7, 0)  # Eye height
            self.rotation = self.follow_target.rotation
            
    def update_third_person(self, delta_time):
        """Update third-person camera."""
        if self.follow_target:
            # Calculate camera position behind the target
            target_pos = self.follow_target.position
            target_rot = self.follow_target.rotation
            
            # Calculate offset based on target rotation
            offset = Vector3(0, self.follow_height, self.follow_distance)
            offset = self.rotate_vector(offset, target_rot)
            
            # Set camera position
            self.target_position = target_pos + offset
            
            # Set camera rotation to look at target
            look_direction = (target_pos - self.target_position).normalized()
            self.target_rotation = self.direction_to_rotation(look_direction)
            
    def update_free_camera(self, delta_time):
        """Update free camera movement."""
        # Free camera movement is handled by input
        pass
        
    def apply(self):
        """Apply camera transformation to OpenGL."""
        glLoadIdentity()
        
        # Apply rotation
        glRotatef(self.rotation.x, 1, 0, 0)  # Pitch
        glRotatef(self.rotation.y, 0, 1, 0)  # Yaw
        glRotatef(self.rotation.z, 0, 0, 1)  # Roll
        
        # Apply translation
        glTranslatef(-self.position.x, -self.position.y, -self.position.z)
        
    def set_projection(self, width, height):
        """Set the projection matrix."""
        self.aspect_ratio = width / height
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect_ratio, self.near_plane, self.far_plane)
        glMatrixMode(GL_MODELVIEW)
        
    def look_at(self, target):
        """Make the camera look at a target point."""
        direction = (target - self.position).normalized()
        self.rotation = self.direction_to_rotation(direction)
        
    def direction_to_rotation(self, direction):
        """Convert a direction vector to rotation angles."""
        # Calculate yaw (horizontal rotation)
        yaw = math.degrees(math.atan2(direction.x, direction.z))
        
        # Calculate pitch (vertical rotation)
        pitch = math.degrees(math.asin(-direction.y))
        
        return Vector3(pitch, yaw, 0)
        
    def rotation_to_direction(self, rotation):
        """Convert rotation angles to a direction vector."""
        # Convert degrees to radians
        pitch_rad = math.radians(rotation.x)
        yaw_rad = math.radians(rotation.y)
        
        # Calculate direction
        x = math.sin(yaw_rad) * math.cos(pitch_rad)
        y = -math.sin(pitch_rad)
        z = math.cos(yaw_rad) * math.cos(pitch_rad)
        
        return Vector3(x, y, z).normalized()
        
    def get_forward_vector(self):
        """Get the forward direction vector."""
        return self.rotation_to_direction(self.rotation)
        
    def get_right_vector(self):
        """Get the right direction vector."""
        forward = self.get_forward_vector()
        up = Vector3(0, 1, 0)
        return forward.cross(up).normalized()
        
    def get_up_vector(self):
        """Get the up direction vector."""
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        return right.cross(forward).normalized()
        
    def move_forward(self, distance):
        """Move the camera forward."""
        direction = self.get_forward_vector()
        self.target_position += direction * distance
        
    def move_right(self, distance):
        """Move the camera right."""
        direction = self.get_right_vector()
        self.target_position += direction * distance
        
    def move_up(self, distance):
        """Move the camera up."""
        direction = self.get_up_vector()
        self.target_position += direction * distance
        
    def rotate_x(self, angle):
        """Rotate the camera around the X axis (pitch)."""
        self.target_rotation.x += angle
        self.target_rotation.x = max(-89, min(89, self.target_rotation.x))  # Clamp pitch
        
    def rotate_y(self, angle):
        """Rotate the camera around the Y axis (yaw)."""
        self.target_rotation.y += angle
        # Keep yaw in range [0, 360)
        self.target_rotation.y = self.target_rotation.y % 360
        
    def rotate_z(self, angle):
        """Rotate the camera around the Z axis (roll)."""
        self.target_rotation.z += angle
        
    def zoom_in(self, factor):
        """Zoom the camera in."""
        if self.mode == "third_person":
            self.follow_distance = max(1.0, self.follow_distance - factor)
        else:
            self.fov = max(10.0, self.fov - factor)
            self.set_projection(1280, 720)  # Update projection
            
    def zoom_out(self, factor):
        """Zoom the camera out."""
        if self.mode == "third_person":
            self.follow_distance = min(20.0, self.follow_distance + factor)
        else:
            self.fov = min(120.0, self.fov + factor)
            self.set_projection(1280, 720)  # Update projection
            
    def set_mode(self, mode):
        """Set the camera mode."""
        self.mode = mode
        
    def set_follow_target(self, target):
        """Set the target to follow."""
        self.follow_target = target
        
    def set_position(self, position):
        """Set the camera position."""
        self.target_position = position
        
    def set_rotation(self, rotation):
        """Set the camera rotation."""
        self.target_rotation = rotation
        
    def get_view_matrix(self):
        """Get the view matrix."""
        # This would return a proper 4x4 view matrix
        # For now, we'll use OpenGL's matrix stack
        return np.identity(4)
        
    def get_projection_matrix(self):
        """Get the projection matrix."""
        # This would return a proper 4x4 projection matrix
        # For now, we'll use OpenGL's matrix stack
        return np.identity(4)
        
    def update_frustum(self):
        """Update the view frustum for culling."""
        # Calculate frustum planes
        self.frustum = self.calculate_frustum()
        
    def calculate_frustum(self):
        """Calculate the view frustum planes."""
        # Get the current modelview and projection matrices
        if str(os.environ.get("HEADLESS", "")).lower() in {"1", "true", "yes"}:
            modelview = np.identity(4)
            projection = np.identity(4)
        else:
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Calculate the combined matrix
        combined = np.dot(projection, modelview)
        
        # Extract frustum planes
        planes = []
        
        # Left plane
        planes.append([
            combined[0][3] + combined[0][0],
            combined[1][3] + combined[1][0],
            combined[2][3] + combined[2][0],
            combined[3][3] + combined[3][0]
        ])
        
        # Right plane
        planes.append([
            combined[0][3] - combined[0][0],
            combined[1][3] - combined[1][0],
            combined[2][3] - combined[2][0],
            combined[3][3] - combined[3][0]
        ])
        
        # Bottom plane
        planes.append([
            combined[0][3] + combined[0][1],
            combined[1][3] + combined[1][1],
            combined[2][3] + combined[2][1],
            combined[3][3] + combined[3][1]
        ])
        
        # Top plane
        planes.append([
            combined[0][3] - combined[0][1],
            combined[1][3] - combined[1][1],
            combined[2][3] - combined[2][1],
            combined[3][3] - combined[3][1]
        ])
        
        # Near plane
        planes.append([
            combined[0][3] + combined[0][2],
            combined[1][3] + combined[1][2],
            combined[2][3] + combined[2][2],
            combined[3][3] + combined[3][2]
        ])
        
        # Far plane
        planes.append([
            combined[0][3] - combined[0][2],
            combined[1][3] - combined[1][2],
            combined[2][3] - combined[2][2],
            combined[3][3] - combined[3][2]
        ])
        
        # Normalize planes
        for plane in planes:
            length = math.sqrt(plane[0]**2 + plane[1]**2 + plane[2]**2)
            if length > 0:
                plane[0] /= length
                plane[1] /= length
                plane[2] /= length
                plane[3] /= length
        
        return planes
        
    def is_point_in_frustum(self, point):
        """Check if a point is inside the view frustum."""
        if not self.frustum:
            return True
            
        for plane in self.frustum:
            distance = (plane[0] * point.x + 
                       plane[1] * point.y + 
                       plane[2] * point.z + 
                       plane[3])
            if distance < 0:
                return False
        return True
        
    def is_sphere_in_frustum(self, center, radius):
        """Check if a sphere is inside the view frustum."""
        if not self.frustum:
            return True
            
        for plane in self.frustum:
            distance = (plane[0] * center.x + 
                       plane[1] * center.y + 
                       plane[2] * center.z + 
                       plane[3])
            if distance < -radius:
                return False
        return True
        
    def is_box_in_frustum(self, min_point, max_point):
        """Check if a bounding box is inside the view frustum."""
        if not self.frustum:
            return True
            
        for plane in self.frustum:
            # Find the farthest point in the negative direction of the plane normal
            farthest_point = Vector3(
                min_point.x if plane[0] > 0 else max_point.x,
                min_point.y if plane[1] > 0 else max_point.y,
                min_point.z if plane[2] > 0 else max_point.z
            )
            
            distance = (plane[0] * farthest_point.x + 
                       plane[1] * farthest_point.y + 
                       plane[2] * farthest_point.z + 
                       plane[3])
            if distance < 0:
                return False
        return True
        
    def rotate_vector(self, vector, rotation):
        """Rotate a vector by rotation angles."""
        # Convert to radians
        pitch_rad = math.radians(rotation.x)
        yaw_rad = math.radians(rotation.y)
        roll_rad = math.radians(rotation.z)
        
        # Apply rotations
        # Yaw (around Y axis)
        cos_y = math.cos(yaw_rad)
        sin_y = math.sin(yaw_rad)
        x = vector.x * cos_y - vector.z * sin_y
        z = vector.x * sin_y + vector.z * cos_y
        vector = Vector3(x, vector.y, z)
        
        # Pitch (around X axis)
        cos_p = math.cos(pitch_rad)
        sin_p = math.sin(pitch_rad)
        y = vector.y * cos_p - vector.z * sin_p
        z = vector.y * sin_p + vector.z * cos_p
        vector = Vector3(vector.x, y, z)
        
        # Roll (around Z axis)
        cos_r = math.cos(roll_rad)
        sin_r = math.sin(roll_rad)
        x = vector.x * cos_r - vector.y * sin_r
        y = vector.x * sin_r + vector.y * cos_r
        vector = Vector3(x, y, vector.z)
        
        return vector
        
    def get_screen_position(self, world_position):
        """Convert a world position to screen coordinates."""
        # Get modelview and projection matrices
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # Convert world coordinates to screen coordinates
        screen_pos = gluProject(
            world_position.x, world_position.y, world_position.z,
            modelview, projection, viewport
        )
        
        if screen_pos:
            return (screen_pos[0], screen_pos[1])
        return None
        
    def get_world_position(self, screen_position, depth):
        """Convert a screen position to world coordinates."""
        # Get modelview and projection matrices
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # Convert screen coordinates to world coordinates
        world_pos = gluUnProject(
            screen_position[0], screen_position[1], depth,
            modelview, projection, viewport
        )
        
        if world_pos:
            return Vector3(world_pos[0], world_pos[1], world_pos[2])
        return None
