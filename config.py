"""
Game Configuration
Contains all game settings, constants, and configuration options.
"""

import os

class GameConfig:
    """Game configuration class containing all settings."""
    
    def __init__(self):
        # Window settings
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.FPS = 60
        self.FULLSCREEN = False
        
        # Game settings
        self.GAME_TITLE = "Roblox Creator Studio"
        self.VERSION = "1.0.0"
        self.DEBUG_MODE = False
        
        # Network settings
        self.SERVER_HOST = "localhost"
        self.SERVER_PORT = 8080
        self.MAX_PLAYERS = 50
        self.TICK_RATE = 20
        
        # Graphics settings
        self.RENDER_DISTANCE = 100.0
        self.SHADOW_QUALITY = "medium"  # low, medium, high
        self.TEXTURE_QUALITY = "high"   # low, medium, high
        self.ANTIALIASING = True
        
        # Audio settings
        self.MASTER_VOLUME = 0.8
        self.MUSIC_VOLUME = 0.6
        self.SFX_VOLUME = 0.7
        self.VOICE_VOLUME = 0.9
        
        # Physics settings
        self.GRAVITY = -9.81
        self.PHYSICS_TICK_RATE = 60
        self.COLLISION_DETECTION = True
        
        # Player settings
        self.PLAYER_SPEED = 5.0
        self.PLAYER_JUMP_FORCE = 8.0
        self.PLAYER_HEALTH = 100
        self.PLAYER_MAX_HEALTH = 100
        
        # World settings
        self.WORLD_SIZE = 1000.0
        self.CHUNK_SIZE = 16
        self.MAX_BUILD_HEIGHT = 256
        
        # UI settings
        self.UI_SCALE = 1.0
        self.FONT_SIZE = 16
        self.CROSSHAIR_ENABLED = True
        
        # File paths
        self.ASSETS_PATH = "assets"
        self.SAVES_PATH = "saves"
        self.LOGS_PATH = "logs"
        self.CONFIG_PATH = "config"
        
        # Create necessary directories
        self.create_directories()
        
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.ASSETS_PATH,
            self.SAVES_PATH,
            self.LOGS_PATH,
            self.CONFIG_PATH,
            os.path.join(self.ASSETS_PATH, "textures"),
            os.path.join(self.ASSETS_PATH, "models"),
            os.path.join(self.ASSETS_PATH, "sounds"),
            os.path.join(self.ASSETS_PATH, "music"),
            os.path.join(self.ASSETS_PATH, "fonts"),
            os.path.join(self.ASSETS_PATH, "shaders")
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
    def save_config(self):
        """Save current configuration to file."""
        config_data = {
            "window": {
                "width": self.WINDOW_WIDTH,
                "height": self.WINDOW_HEIGHT,
                "fps": self.FPS,
                "fullscreen": self.FULLSCREEN
            },
            "graphics": {
                "render_distance": self.RENDER_DISTANCE,
                "shadow_quality": self.SHADOW_QUALITY,
                "texture_quality": self.TEXTURE_QUALITY,
                "antialiasing": self.ANTIALIASING
            },
            "audio": {
                "master_volume": self.MASTER_VOLUME,
                "music_volume": self.MUSIC_VOLUME,
                "sfx_volume": self.SFX_VOLUME,
                "voice_volume": self.VOICE_VOLUME
            },
            "gameplay": {
                "player_speed": self.PLAYER_SPEED,
                "player_jump_force": self.PLAYER_JUMP_FORCE,
                "physics_tick_rate": self.PHYSICS_TICK_RATE
            }
        }
        
        import json
        config_file = os.path.join(self.CONFIG_PATH, "settings.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
            
    def load_config(self):
        """Load configuration from file."""
        config_file = os.path.join(self.CONFIG_PATH, "settings.json")
        if os.path.exists(config_file):
            import json
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                
            # Apply loaded settings
            if "window" in config_data:
                window = config_data["window"]
                self.WINDOW_WIDTH = window.get("width", self.WINDOW_WIDTH)
                self.WINDOW_HEIGHT = window.get("height", self.WINDOW_HEIGHT)
                self.FPS = window.get("fps", self.FPS)
                self.FULLSCREEN = window.get("fullscreen", self.FULLSCREEN)
                
            if "graphics" in config_data:
                graphics = config_data["graphics"]
                self.RENDER_DISTANCE = graphics.get("render_distance", self.RENDER_DISTANCE)
                self.SHADOW_QUALITY = graphics.get("shadow_quality", self.SHADOW_QUALITY)
                self.TEXTURE_QUALITY = graphics.get("texture_quality", self.TEXTURE_QUALITY)
                self.ANTIALIASING = graphics.get("antialiasing", self.ANTIALIASING)
                
            if "audio" in config_data:
                audio = config_data["audio"]
                self.MASTER_VOLUME = audio.get("master_volume", self.MASTER_VOLUME)
                self.MUSIC_VOLUME = audio.get("music_volume", self.MUSIC_VOLUME)
                self.SFX_VOLUME = audio.get("sfx_volume", self.SFX_VOLUME)
                self.VOICE_VOLUME = audio.get("voice_volume", self.VOICE_VOLUME)
                
            if "gameplay" in config_data:
                gameplay = config_data["gameplay"]
                self.PLAYER_SPEED = gameplay.get("player_speed", self.PLAYER_SPEED)
                self.PLAYER_JUMP_FORCE = gameplay.get("player_jump_force", self.PLAYER_JUMP_FORCE)
                self.PHYSICS_TICK_RATE = gameplay.get("physics_tick_rate", self.PHYSICS_TICK_RATE)
