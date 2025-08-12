"""
Vector3 Class
A simple 3D vector class for mathematical operations.
"""

import math

class Vector3:
    """3D vector class with common mathematical operations."""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """Initialize a Vector3 with x, y, z components."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __add__(self, other):
        """Add two vectors."""
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vector3(self.x + other, self.y + other, self.z + other)
            
    def __sub__(self, other):
        """Subtract two vectors."""
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Vector3(self.x - other, self.y - other, self.z - other)
            
    def __mul__(self, other):
        """Multiply vector by scalar or component-wise multiplication."""
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return Vector3(self.x * other, self.y * other, self.z * other)
            
    def __truediv__(self, other):
        """Divide vector by scalar or component-wise division."""
        if isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            return Vector3(self.x / other, self.y / other, self.z / other)
            
    def __eq__(self, other):
        """Check if two vectors are equal."""
        if isinstance(other, Vector3):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False
        
    def __str__(self):
        """String representation of the vector."""
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
        
    def __repr__(self):
        """Detailed string representation of the vector."""
        return f"Vector3(x={self.x}, y={self.y}, z={self.z})"
        
    def length(self):
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        
    def length_squared(self):
        """Calculate the squared magnitude of the vector."""
        return self.x * self.x + self.y * self.y + self.z * self.z
        
    def normalize(self):
        """Normalize the vector (make it unit length)."""
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return self
        
    def normalized(self):
        """Return a normalized copy of the vector."""
        length = self.length()
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3(0, 0, 0)
        
    def dot(self, other):
        """Calculate the dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z
        
    def cross(self, other):
        """Calculate the cross product with another vector."""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
        
    def distance_to(self, other):
        """Calculate the distance to another vector."""
        return (self - other).length()
        
    def distance_squared_to(self, other):
        """Calculate the squared distance to another vector."""
        return (self - other).length_squared()
        
    def lerp(self, other, t):
        """Linear interpolation between this vector and another."""
        t = max(0.0, min(1.0, t))  # Clamp t between 0 and 1
        return Vector3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t
        )
        
    def slerp(self, other, t):
        """Spherical linear interpolation between this vector and another."""
        # This is a simplified slerp - for full slerp you'd need quaternions
        return self.lerp(other, t)
        
    def angle_to(self, other):
        """Calculate the angle between this vector and another."""
        dot_product = self.dot(other)
        lengths = self.length() * other.length()
        if lengths > 0:
            cos_angle = dot_product / lengths
            cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
            return math.acos(cos_angle)
        return 0.0
        
    def rotate_around_axis(self, axis, angle):
        """Rotate this vector around an axis by the given angle."""
        # Rodrigues' rotation formula
        axis = axis.normalized()
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        rotated = (self * cos_angle + 
                  axis.cross(self) * sin_angle + 
                  axis * axis.dot(self) * (1 - cos_angle))
        
        self.x = rotated.x
        self.y = rotated.y
        self.z = rotated.z
        return self
        
    def rotate_around_axis_copy(self, axis, angle):
        """Return a rotated copy of this vector around an axis."""
        result = Vector3(self.x, self.y, self.z)
        return result.rotate_around_axis(axis, angle)
        
    def reflect(self, normal):
        """Reflect this vector off a surface with the given normal."""
        normal = normal.normalized()
        dot_product = self.dot(normal)
        return self - normal * (2 * dot_product)
        
    def refract(self, normal, refraction_index):
        """Refract this vector through a surface."""
        normal = normal.normalized()
        dot_product = self.dot(normal)
        
        # Calculate refraction
        k = 1.0 - refraction_index * refraction_index * (1.0 - dot_product * dot_product)
        if k < 0:
            return Vector3(0, 0, 0)  # Total internal reflection
        else:
            return self * refraction_index - normal * (refraction_index * dot_product + math.sqrt(k))
            
    def to_list(self):
        """Convert vector to a list."""
        return [self.x, self.y, self.z]
        
    def to_tuple(self):
        """Convert vector to a tuple."""
        return (self.x, self.y, self.z)
        
    def copy(self):
        """Create a copy of this vector."""
        return Vector3(self.x, self.y, self.z)
        
    def set(self, x, y, z):
        """Set the components of this vector."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        return self
        
    def set_from_vector(self, other):
        """Set this vector's components from another vector."""
        self.x = other.x
        self.y = other.y
        self.z = other.z
        return self
        
    def zero(self):
        """Set all components to zero."""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        return self
        
    def is_zero(self):
        """Check if this vector is the zero vector."""
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0
        
    def is_unit(self):
        """Check if this vector is a unit vector (length = 1)."""
        return abs(self.length() - 1.0) < 0.001
        
    def clamp(self, min_val, max_val):
        """Clamp the components of this vector between min and max values."""
        self.x = max(min_val, min(max_val, self.x))
        self.y = max(min_val, min(max_val, self.y))
        self.z = max(min_val, min(max_val, self.z))
        return self
        
    def clamp_length(self, max_length):
        """Clamp the length of this vector to a maximum value."""
        if self.length() > max_length:
            self.normalize()
            self.x *= max_length
            self.y *= max_length
            self.z *= max_length
        return self
        
    def project(self, other):
        """Project this vector onto another vector."""
        other_normalized = other.normalized()
        return other_normalized * self.dot(other_normalized)
        
    def reject(self, other):
        """Reject this vector from another vector (perpendicular component)."""
        return self - self.project(other)
        
    @classmethod
    def zero_vector(cls):
        """Create a zero vector."""
        return cls(0.0, 0.0, 0.0)
        
    @classmethod
    def one_vector(cls):
        """Create a vector with all components set to 1."""
        return cls(1.0, 1.0, 1.0)
        
    @classmethod
    def up_vector(cls):
        """Create a unit vector pointing up (positive Y)."""
        return cls(0.0, 1.0, 0.0)
        
    @classmethod
    def down_vector(cls):
        """Create a unit vector pointing down (negative Y)."""
        return cls(0.0, -1.0, 0.0)
        
    @classmethod
    def forward_vector(cls):
        """Create a unit vector pointing forward (negative Z)."""
        return cls(0.0, 0.0, -1.0)
        
    @classmethod
    def backward_vector(cls):
        """Create a unit vector pointing backward (positive Z)."""
        return cls(0.0, 0.0, 1.0)
        
    @classmethod
    def right_vector(cls):
        """Create a unit vector pointing right (positive X)."""
        return cls(1.0, 0.0, 0.0)
        
    @classmethod
    def left_vector(cls):
        """Create a unit vector pointing left (negative X)."""
        return cls(-1.0, 0.0, 0.0)
