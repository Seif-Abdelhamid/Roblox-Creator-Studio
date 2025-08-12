"""
Physics Engine
Handles collision detection, physics simulation, and object interactions.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from vector3 import Vector3

class PhysicsEngine:
    """Physics engine for realistic game physics."""
    
    def __init__(self):
        """Initialize the physics engine."""
        self.gravity = Vector3(0, -9.81, 0)
        self.air_resistance = 0.98
        self.friction = 0.8
        
        # Physics objects
        self.rigid_bodies = []
        self.colliders = []
        self.constraints = []
        
        # Collision detection
        self.broad_phase = {}
        self.narrow_phase = []
        
        # Performance
        self.max_iterations = 10
        self.time_step = 1.0 / 60.0
        
    def update(self, delta_time):
        """Update physics simulation."""
        # Apply forces
        self.apply_forces(delta_time)
        
        # Update velocities
        self.update_velocities(delta_time)
        
        # Detect collisions
        self.detect_collisions()
        
        # Resolve collisions
        self.resolve_collisions()
        
        # Update positions
        self.update_positions(delta_time)
        
        # Apply constraints
        self.apply_constraints()
        
    def apply_forces(self, delta_time):
        """Apply forces to all physics objects."""
        for body in self.rigid_bodies:
            # Apply gravity
            body.force += self.gravity * body.mass
            
            # Apply air resistance
            if body.velocity.length() > 0.1:
                drag_force = -body.velocity.normalized() * body.velocity.length_squared() * 0.1
                body.force += drag_force
                
    def update_velocities(self, delta_time):
        """Update velocities based on forces."""
        for body in self.rigid_bodies:
            # F = ma, so a = F/m
            acceleration = body.force / body.mass
            
            # Update velocity: v = v0 + at
            body.velocity += acceleration * delta_time
            
            # Apply friction
            if body.on_ground:
                body.velocity.x *= self.friction
                body.velocity.z *= self.friction
                
            # Reset forces
            body.force = Vector3(0, 0, 0)
            
    def update_positions(self, delta_time):
        """Update positions based on velocities."""
        for body in self.rigid_bodies:
            # Update position: x = x0 + vt
            body.position += body.velocity * delta_time
            
            # Update bounding box
            body.update_bounding_box()
            
    def detect_collisions(self):
        """Detect collisions between objects."""
        self.narrow_phase.clear()
        
        # Broad phase - spatial partitioning
        self.broad_phase.clear()
        
        for i, body1 in enumerate(self.rigid_bodies):
            for j, body2 in enumerate(self.rigid_bodies[i+1:], i+1):
                if self.broad_phase_check(body1, body2):
                    collision = self.narrow_phase_check(body1, body2)
                    if collision:
                        self.narrow_phase.append(collision)
                        
    def broad_phase_check(self, body1, body2):
        """Broad phase collision detection using AABB."""
        if not body1.bounding_box or not body2.bounding_box:
            return False
            
        # Check if bounding boxes overlap
        return (body1.bounding_box["min"].x <= body2.bounding_box["max"].x and
                body1.bounding_box["max"].x >= body2.bounding_box["min"].x and
                body1.bounding_box["min"].y <= body2.bounding_box["max"].y and
                body1.bounding_box["max"].y >= body2.bounding_box["min"].y and
                body1.bounding_box["min"].z <= body2.bounding_box["max"].z and
                body1.bounding_box["max"].z >= body2.bounding_box["min"].z)
                
    def narrow_phase_check(self, body1, body2):
        """Narrow phase collision detection."""
        # Simple sphere-sphere collision for now
        if hasattr(body1, 'radius') and hasattr(body2, 'radius'):
            distance = body1.position.distance_to(body2.position)
            min_distance = body1.radius + body2.radius
            
            if distance < min_distance:
                # Calculate collision normal
                normal = (body2.position - body1.position).normalized()
                
                # Calculate penetration depth
                penetration = min_distance - distance
                
                return {
                    'body1': body1,
                    'body2': body2,
                    'normal': normal,
                    'penetration': penetration,
                    'contact_point': body1.position + normal * body1.radius
                }
                
        return None
        
    def resolve_collisions(self):
        """Resolve detected collisions."""
        for collision in self.narrow_phase:
            self.resolve_collision(collision)
            
    def resolve_collision(self, collision):
        """Resolve a single collision."""
        body1 = collision['body1']
        body2 = collision['body2']
        normal = collision['normal']
        penetration = collision['penetration']
        
        # Separate the bodies
        separation = normal * penetration * 0.5
        body1.position -= separation
        body2.position += separation
        
        # Calculate relative velocity
        relative_velocity = body2.velocity - body1.velocity
        
        # Calculate impulse
        restitution = 0.5  # Bounciness
        j = -(1 + restitution) * relative_velocity.dot(normal)
        j /= 1/body1.mass + 1/body2.mass
        
        # Apply impulse
        impulse = normal * j
        body1.velocity -= impulse / body1.mass
        body2.velocity += impulse / body2.mass
        
        # Update bounding boxes
        body1.update_bounding_box()
        body2.update_bounding_box()
        
    def apply_constraints(self):
        """Apply constraints to physics objects."""
        for constraint in self.constraints:
            constraint.solve()
            
    def add_rigid_body(self, body):
        """Add a rigid body to the physics simulation."""
        self.rigid_bodies.append(body)
        
    def remove_rigid_body(self, body):
        """Remove a rigid body from the physics simulation."""
        if body in self.rigid_bodies:
            self.rigid_bodies.remove(body)
            
    def add_constraint(self, constraint):
        """Add a constraint to the physics simulation."""
        self.constraints.append(constraint)
        
    def remove_constraint(self, constraint):
        """Remove a constraint from the physics simulation."""
        if constraint in self.constraints:
            self.constraints.remove(constraint)
            
    def raycast(self, origin, direction, max_distance):
        """Cast a ray and return the first hit."""
        closest_hit = None
        closest_distance = max_distance
        
        for body in self.rigid_bodies:
            hit = self.ray_body_intersection(origin, direction, body)
            if hit and hit['distance'] < closest_distance:
                closest_hit = hit
                closest_distance = hit['distance']
                
        return closest_hit
        
    def ray_body_intersection(self, origin, direction, body):
        """Check if a ray intersects with a body."""
        # Simple sphere intersection for now
        if hasattr(body, 'radius'):
            # Vector from ray origin to sphere center
            oc = body.position - origin
            
            # Project oc onto ray direction
            t = oc.dot(direction)
            
            # Closest point on ray to sphere center
            closest_point = origin + direction * t
            
            # Distance from closest point to sphere center
            distance = closest_point.distance_to(body.position)
            
            if distance <= body.radius:
                # Calculate intersection points
                half_chord = math.sqrt(body.radius * body.radius - distance * distance)
                t1 = t - half_chord
                t2 = t + half_chord
                
                if t1 >= 0 and t1 <= max_distance:
                    return {
                        'body': body,
                        'distance': t1,
                        'point': origin + direction * t1,
                        'normal': (origin + direction * t1 - body.position).normalized()
                    }
                    
        return None
        
    def check_ground_collision(self, body):
        """Check if a body is colliding with the ground."""
        if body.position.y <= 0:
            body.position.y = 0
            body.velocity.y = 0
            body.on_ground = True
        else:
            body.on_ground = False
            
    def apply_impulse(self, body, impulse):
        """Apply an impulse to a body."""
        body.velocity += impulse / body.mass
        
    def set_gravity(self, gravity):
        """Set the gravity vector."""
        self.gravity = gravity
        
    def get_gravity(self):
        """Get the current gravity vector."""
        return self.gravity
        
    def clear(self):
        """Clear all physics objects."""
        self.rigid_bodies.clear()
        self.colliders.clear()
        self.constraints.clear()
        self.narrow_phase.clear()
        self.broad_phase.clear()

class RigidBody:
    """A rigid body for physics simulation."""
    
    def __init__(self, position, mass=1.0, radius=0.5):
        """Initialize a rigid body."""
        self.position = position
        self.velocity = Vector3(0, 0, 0)
        self.force = Vector3(0, 0, 0)
        self.mass = mass
        self.radius = radius
        self.on_ground = False
        
        # Bounding box
        self.bounding_box = None
        self.update_bounding_box()
        
    def update_bounding_box(self):
        """Update the bounding box."""
        self.bounding_box = {
            "min": Vector3(
                self.position.x - self.radius,
                self.position.y - self.radius,
                self.position.z - self.radius
            ),
            "max": Vector3(
                self.position.x + self.radius,
                self.position.y + self.radius,
                self.position.z + self.radius
            )
        }
        
    def apply_force(self, force):
        """Apply a force to this body."""
        self.force += force
        
    def apply_impulse(self, impulse):
        """Apply an impulse to this body."""
        self.velocity += impulse / self.mass
        
    def get_kinetic_energy(self):
        """Get the kinetic energy of this body."""
        return 0.5 * self.mass * self.velocity.length_squared()
        
    def get_momentum(self):
        """Get the momentum of this body."""
        return self.velocity * self.mass

class Constraint:
    """A constraint between two rigid bodies."""
    
    def __init__(self, body1, body2, distance):
        """Initialize a constraint."""
        self.body1 = body1
        self.body2 = body2
        self.distance = distance
        
    def solve(self):
        """Solve the constraint."""
        # Calculate current distance
        current_distance = self.body1.position.distance_to(self.body2.position)
        
        if current_distance > 0:
            # Calculate correction
            correction = (current_distance - self.distance) / current_distance
            
            # Apply correction
            correction_vector = (self.body2.position - self.body1.position) * correction * 0.5
            
            self.body1.position += correction_vector
            self.body2.position -= correction_vector
            
            # Update bounding boxes
            self.body1.update_bounding_box()
            self.body2.update_bounding_box()
