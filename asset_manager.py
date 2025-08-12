"""
Asset Manager
Handles loading, caching, and management of game assets (textures, models, sounds, etc.).
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import json
import threading
import time
from PIL import Image
from vector3 import Vector3

class AssetManager:
    """Asset manager for loading and managing game resources."""
    
    def __init__(self):
        """Initialize the asset manager."""
        # Asset storage
        self.textures = {}
        self.models = {}
        self.sounds = {}
        self.music = {}
        self.fonts = {}
        self.shaders = {}
        
        # Asset paths
        self.asset_paths = {
            "textures": "assets/textures/",
            "models": "assets/models/",
            "sounds": "assets/sounds/",
            "music": "assets/music/",
            "fonts": "assets/fonts/",
            "shaders": "assets/shaders/"
        }
        
        # Loading state
        self.loading_queue = []
        self.loaded_assets = set()
        self.failed_assets = set()
        self.loading_thread = None
        self.loading_complete = False
        
        # Cache settings
        self.max_texture_cache = 100
        self.max_model_cache = 50
        self.max_sound_cache = 30
        
        # Asset metadata
        self.asset_metadata = {}
        
        # Initialize asset directories
        self.create_asset_directories()
        
        # Load asset metadata
        self.load_asset_metadata()
        
    def create_asset_directories(self):
        """Create asset directories if they don't exist."""
        for path in self.asset_paths.values():
            os.makedirs(path, exist_ok=True)
            
    def load_asset_metadata(self):
        """Load asset metadata from JSON files."""
        metadata_file = "assets/metadata.json"
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    self.asset_metadata = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load asset metadata: {e}")
                
    def save_asset_metadata(self):
        """Save asset metadata to JSON file."""
        metadata_file = "assets/metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(self.asset_metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save asset metadata: {e}")
            
    def start_loading(self):
        """Start the asset loading process."""
        if self.loading_thread is None:
            self.loading_thread = threading.Thread(target=self.load_all_assets)
            self.loading_thread.daemon = True
            self.loading_thread.start()
            
    def load_all_assets(self):
        """Load all assets in the background."""
        print("📦 Loading game assets...")
        
        # Load essential assets first
        self.load_essential_assets()
        
        # Load remaining assets
        self.load_textures()
        self.load_models()
        self.load_sounds()
        self.load_music()
        self.load_fonts()
        self.load_shaders()
        
        self.loading_complete = True
        print("✅ Asset loading complete!")
        
    def load_essential_assets(self):
        """Load essential assets that are needed immediately."""
        # Load basic textures
        essential_textures = [
            "grass.png",
            "stone.png", 
            "dirt.png",
            "wood.png",
            "water.png"
        ]
        
        for texture_name in essential_textures:
            self.load_texture(texture_name)
            
    def load_textures(self):
        """Load all texture assets."""
        texture_path = self.asset_paths["textures"]
        
        if not os.path.exists(texture_path):
            return
            
        for filename in os.listdir(texture_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
                self.load_texture(filename)
                
    def load_texture(self, filename):
        """Load a single texture."""
        if filename in self.textures:
            return self.textures[filename]
            
        texture_path = os.path.join(self.asset_paths["textures"], filename)
        
        if not os.path.exists(texture_path):
            print(f"⚠️ Texture not found: {texture_path}")
            self.failed_assets.add(f"texture:{filename}")
            return None
            
        try:
            # Load image using PIL
            image = Image.open(texture_path)
            image = image.convert("RGBA")
            
            # Get image data
            width, height = image.size
            image_data = image.tobytes()
            
            # Generate OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Store texture info
            self.textures[filename] = {
                "id": texture_id,
                "width": width,
                "height": height,
                "path": texture_path
            }
            
            self.loaded_assets.add(f"texture:{filename}")
            print(f"✅ Loaded texture: {filename}")
            
            return self.textures[filename]
            
        except Exception as e:
            print(f"❌ Failed to load texture {filename}: {e}")
            self.failed_assets.add(f"texture:{filename}")
            return None
            
    def load_models(self):
        """Load all model assets."""
        model_path = self.asset_paths["models"]
        
        if not os.path.exists(model_path):
            return
            
        for filename in os.listdir(model_path):
            if filename.lower().endswith(('.obj', '.fbx', '.3ds', '.dae')):
                self.load_model(filename)
                
    def load_model(self, filename):
        """Load a single model."""
        if filename in self.models:
            return self.models[filename]
            
        model_path = os.path.join(self.asset_paths["models"], filename)
        
        if not os.path.exists(model_path):
            print(f"⚠️ Model not found: {model_path}")
            self.failed_assets.add(f"model:{filename}")
            return None
            
        try:
            # For now, create a simple cube model
            # In a real implementation, you'd use a proper model loader like Assimp
            model_data = self.create_cube_model()
            
            self.models[filename] = {
                "vertices": model_data["vertices"],
                "indices": model_data["indices"],
                "normals": model_data["normals"],
                "texcoords": model_data["texcoords"],
                "path": model_path
            }
            
            self.loaded_assets.add(f"model:{filename}")
            print(f"✅ Loaded model: {filename}")
            
            return self.models[filename]
            
        except Exception as e:
            print(f"❌ Failed to load model {filename}: {e}")
            self.failed_assets.add(f"model:{filename}")
            return None
            
    def create_cube_model(self):
        """Create a simple cube model."""
        vertices = [
            # Front face
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,
             0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
            -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  1.0,
            
            # Back face
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  0.0,
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  1.0,
             0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,
            
            # Top face
            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0,
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
             0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0,  1.0,
            
            # Bottom face
            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0,  1.0,
             0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  1.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0,  0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
            
            # Right face
             0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  0.0,
             0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  1.0,
             0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
             0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  0.0,
            
            # Left face
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  0.0,
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  1.0,
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0
        ]
        
        indices = [
            0,  1,  2,    0,  2,  3,   # Front
            4,  5,  6,    4,  6,  7,   # Back
            8,  9,  10,   8,  10, 11,  # Top
            12, 13, 14,   12, 14, 15,  # Bottom
            16, 17, 18,   16, 18, 19,  # Right
            20, 21, 22,   20, 22, 23   # Left
        ]
        
        return {
            "vertices": vertices,
            "indices": indices,
            "normals": [],  # Normals are included in vertices
            "texcoords": []  # Texcoords are included in vertices
        }
        
    def load_sounds(self):
        """Load all sound assets."""
        sound_path = self.asset_paths["sounds"]
        
        if not os.path.exists(sound_path):
            return
            
        for filename in os.listdir(sound_path):
            if filename.lower().endswith(('.wav', '.ogg', '.mp3')):
                self.load_sound(filename)
                
    def load_sound(self, filename):
        """Load a single sound."""
        if filename in self.sounds:
            return self.sounds[filename]
            
        sound_path = os.path.join(self.asset_paths["sounds"], filename)
        
        if not os.path.exists(sound_path):
            print(f"⚠️ Sound not found: {sound_path}")
            self.failed_assets.add(f"sound:{filename}")
            return None
            
        try:
            # Load sound using pygame
            sound = pygame.mixer.Sound(sound_path)
            
            self.sounds[filename] = {
                "sound": sound,
                "path": sound_path
            }
            
            self.loaded_assets.add(f"sound:{filename}")
            print(f"✅ Loaded sound: {filename}")
            
            return self.sounds[filename]
            
        except Exception as e:
            print(f"❌ Failed to load sound {filename}: {e}")
            self.failed_assets.add(f"sound:{filename}")
            return None
            
    def load_music(self):
        """Load all music assets."""
        music_path = self.asset_paths["music"]
        
        if not os.path.exists(music_path):
            return
            
        for filename in os.listdir(music_path):
            if filename.lower().endswith(('.wav', '.ogg', '.mp3')):
                self.load_music_track(filename)
                
    def load_music_track(self, filename):
        """Load a single music track."""
        if filename in self.music:
            return self.music[filename]
            
        music_path = os.path.join(self.asset_paths["music"], filename)
        
        if not os.path.exists(music_path):
            print(f"⚠️ Music not found: {music_path}")
            self.failed_assets.add(f"music:{filename}")
            return None
            
        try:
            self.music[filename] = {
                "path": music_path
            }
            
            self.loaded_assets.add(f"music:{filename}")
            print(f"✅ Loaded music: {filename}")
            
            return self.music[filename]
            
        except Exception as e:
            print(f"❌ Failed to load music {filename}: {e}")
            self.failed_assets.add(f"music:{filename}")
            return None
            
    def load_fonts(self):
        """Load all font assets."""
        font_path = self.asset_paths["fonts"]
        
        if not os.path.exists(font_path):
            return
            
        for filename in os.listdir(font_path):
            if filename.lower().endswith(('.ttf', '.otf')):
                self.load_font(filename)
                
    def load_font(self, filename):
        """Load a single font."""
        if filename in self.fonts:
            return self.fonts[filename]
            
        font_path = os.path.join(self.asset_paths["fonts"], filename)
        
        if not os.path.exists(font_path):
            print(f"⚠️ Font not found: {font_path}")
            self.failed_assets.add(f"font:{filename}")
            return None
            
        try:
            # Load font using pygame
            font = pygame.font.Font(font_path, 16)
            
            self.fonts[filename] = {
                "font": font,
                "path": font_path
            }
            
            self.loaded_assets.add(f"font:{filename}")
            print(f"✅ Loaded font: {filename}")
            
            return self.fonts[filename]
            
        except Exception as e:
            print(f"❌ Failed to load font {filename}: {e}")
            self.failed_assets.add(f"font:{filename}")
            return None
            
    def load_shaders(self):
        """Load all shader assets."""
        shader_path = self.asset_paths["shaders"]
        
        if not os.path.exists(shader_path):
            return
            
        for filename in os.listdir(shader_path):
            if filename.lower().endswith(('.vert', '.frag', '.glsl')):
                self.load_shader(filename)
                
    def load_shader(self, filename):
        """Load a single shader."""
        if filename in self.shaders:
            return self.shaders[filename]
            
        shader_path = os.path.join(self.asset_paths["shaders"], filename)
        
        if not os.path.exists(shader_path):
            print(f"⚠️ Shader not found: {shader_path}")
            self.failed_assets.add(f"shader:{filename}")
            return None
            
        try:
            with open(shader_path, 'r') as f:
                shader_source = f.read()
                
            self.shaders[filename] = {
                "source": shader_source,
                "path": shader_path
            }
            
            self.loaded_assets.add(f"shader:{filename}")
            print(f"✅ Loaded shader: {filename}")
            
            return self.shaders[filename]
            
        except Exception as e:
            print(f"❌ Failed to load shader {filename}: {e}")
            self.failed_assets.add(f"shader:{filename}")
            return None
            
    def get_texture(self, filename):
        """Get a texture by filename."""
        if filename in self.textures:
            return self.textures[filename]
        else:
            # Try to load it
            return self.load_texture(filename)
            
    def get_model(self, filename):
        """Get a model by filename."""
        if filename in self.models:
            return self.models[filename]
        else:
            # Try to load it
            return self.load_model(filename)
            
    def get_sound(self, filename):
        """Get a sound by filename."""
        if filename in self.sounds:
            return self.sounds[filename]
        else:
            # Try to load it
            return self.load_sound(filename)
            
    def get_music(self, filename):
        """Get music by filename."""
        if filename in self.music:
            return self.music[filename]
        else:
            # Try to load it
            return self.load_music_track(filename)
            
    def get_font(self, filename):
        """Get a font by filename."""
        if filename in self.fonts:
            return self.fonts[filename]
        else:
            # Try to load it
            return self.load_font(filename)
            
    def get_shader(self, filename):
        """Get a shader by filename."""
        if filename in self.shaders:
            return self.shaders[filename]
        else:
            # Try to load it
            return self.load_shader(filename)
            
    def bind_texture(self, filename):
        """Bind a texture for rendering."""
        texture = self.get_texture(filename)
        if texture:
            glBindTexture(GL_TEXTURE_2D, texture["id"])
            return True
        return False
        
    def render_model(self, filename):
        """Render a model."""
        model = self.get_model(filename)
        if not model:
            return False
            
        # Enable vertex attributes
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        
        # Set vertex data
        glVertexPointer(3, GL_FLOAT, 32, model["vertices"])
        glNormalPointer(GL_FLOAT, 32, model["vertices"] + 12)
        glTexCoordPointer(2, GL_FLOAT, 32, model["vertices"] + 24)
        
        # Draw model
        glDrawElements(GL_TRIANGLES, len(model["indices"]), GL_UNSIGNED_INT, model["indices"])
        
        # Disable vertex attributes
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        
        return True
        
    def play_sound(self, filename, volume=1.0):
        """Play a sound effect."""
        sound_data = self.get_sound(filename)
        if sound_data:
            sound_data["sound"].set_volume(volume)
            sound_data["sound"].play()
            return True
        return False
        
    def play_music(self, filename, volume=1.0, loop=True):
        """Play background music."""
        music_data = self.get_music(filename)
        if music_data:
            pygame.mixer.music.load(music_data["path"])
            pygame.mixer.music.set_volume(volume)
            if loop:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.play()
            return True
        return False
        
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        
    def is_loading_complete(self):
        """Check if asset loading is complete."""
        return self.loading_complete
        
    def get_loading_progress(self):
        """Get the loading progress as a percentage."""
        if not self.loading_queue:
            return 100.0
            
        total_assets = len(self.loading_queue)
        loaded_assets = len(self.loaded_assets)
        return (loaded_assets / total_assets) * 100.0
        
    def get_asset_count(self):
        """Get the total number of loaded assets."""
        return {
            "textures": len(self.textures),
            "models": len(self.models),
            "sounds": len(self.sounds),
            "music": len(self.music),
            "fonts": len(self.fonts),
            "shaders": len(self.shaders)
        }
        
    def clear_cache(self):
        """Clear asset cache to free memory."""
        # Clear textures
        for texture in self.textures.values():
            glDeleteTextures([texture["id"]])
        self.textures.clear()
        
        # Clear other assets
        self.models.clear()
        self.sounds.clear()
        self.music.clear()
        self.fonts.clear()
        self.shaders.clear()
        
        # Clear loading state
        self.loaded_assets.clear()
        self.failed_assets.clear()
        
    def cleanup(self):
        """Cleanup resources."""
        self.clear_cache()
        self.save_asset_metadata()
