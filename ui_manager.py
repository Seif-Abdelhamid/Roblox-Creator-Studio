"""
UI Manager
Handles user interface, HUD elements, and menu systems.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from vector3 import Vector3

class UIManager:
    """User interface manager for the game."""
    
    def __init__(self):
        """Initialize the UI manager."""
        # UI state
        self.current_menu = "main_menu"
        self.menu_stack = []
        self.ui_elements = {}
        
        # Font and text rendering
        self.fonts = {}
        self.font_sizes = [12, 16, 20, 24, 32, 48]
        self.load_fonts()
        
        # Colors
        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "gray": (128, 128, 128),
            "dark_gray": (64, 64, 64),
            "light_gray": (192, 192, 192),
            "transparent": (0, 0, 0, 0)
        }
        
        # UI elements
        self.buttons = {}
        self.labels = {}
        self.input_fields = {}
        self.sliders = {}
        self.checkboxes = {}
        
        # HUD elements
        self.hud_elements = {
            "health_bar": None,
            "energy_bar": None,
            "crosshair": None,
            "inventory": None,
            "chat": None,
            "minimap": None
        }
        
        # Initialize UI
        self.setup_ui()
        
    def load_fonts(self):
        """Load fonts for text rendering."""
        try:
            for size in self.font_sizes:
                self.fonts[size] = pygame.font.Font(None, size)
        except Exception as e:
            print(f"⚠️ Failed to load fonts: {e}")
            # Use default font
            for size in self.font_sizes:
                self.fonts[size] = pygame.font.SysFont("arial", size)
                
    def setup_ui(self):
        """Setup the user interface."""
        self.setup_main_menu()
        self.setup_hud()
        self.setup_pause_menu()
        self.setup_settings_menu()
        
    def setup_main_menu(self):
        """Setup the main menu."""
        # Title
        self.add_label("title", "Roblox Creator Studio", 640, 200, 48, "white", center=True)
        
        # Buttons
        self.add_button("play_button", "Play Game", 640, 350, 200, 50, self.start_game)
        self.add_button("settings_button", "Settings", 640, 420, 200, 50, self.open_settings)
        self.add_button("quit_button", "Quit", 640, 490, 200, 50, self.quit_game)
        
        # Version info
        self.add_label("version", "v1.0.0 - By Seif Abdelhamid", 640, 700, 16, "gray", center=True)
        
    def setup_hud(self):
        """Setup the heads-up display."""
        # Health bar
        self.add_health_bar("health_bar", 50, 50, 200, 20)
        
        # Energy bar
        self.add_energy_bar("energy_bar", 50, 80, 200, 20)
        
        # Crosshair
        self.add_crosshair("crosshair", 640, 360)
        
        # Chat
        self.add_chat("chat", 50, 600, 400, 100)
        
        # Minimap
        self.add_minimap("minimap", 1100, 50, 150, 150)
        
    def setup_pause_menu(self):
        """Setup the pause menu."""
        # Background overlay
        self.add_overlay("pause_overlay", 0, 0, 1280, 720, (0, 0, 0, 128))
        
        # Title
        self.add_label("pause_title", "Game Paused", 640, 200, 48, "white", center=True)
        
        # Buttons
        self.add_button("resume_button", "Resume", 640, 350, 200, 50, self.resume_game)
        self.add_button("pause_settings_button", "Settings", 640, 420, 200, 50, self.open_settings)
        self.add_button("main_menu_button", "Main Menu", 640, 490, 200, 50, self.return_to_main_menu)
        
    def setup_settings_menu(self):
        """Setup the settings menu."""
        # Title
        self.add_label("settings_title", "Settings", 640, 100, 48, "white", center=True)
        
        # Graphics settings
        self.add_label("graphics_label", "Graphics", 200, 200, 24, "white")
        self.add_slider("render_distance", "Render Distance", 200, 250, 300, 20, 50, 200, 100)
        self.add_checkbox("shadows_enabled", "Enable Shadows", 200, 300, True)
        self.add_checkbox("antialiasing", "Antialiasing", 200, 350, True)
        
        # Audio settings
        self.add_label("audio_label", "Audio", 200, 400, 24, "white")
        self.add_slider("master_volume", "Master Volume", 200, 450, 300, 20, 0, 100, 80)
        self.add_slider("music_volume", "Music Volume", 200, 500, 300, 20, 0, 100, 60)
        self.add_slider("sfx_volume", "SFX Volume", 200, 550, 300, 20, 0, 100, 70)
        
        # Controls
        self.add_label("controls_label", "Controls", 700, 200, 24, "white")
        self.add_button("keybind_button", "Keybindings", 700, 250, 200, 50, self.open_keybindings)
        
        # Buttons
        self.add_button("save_settings", "Save", 640, 600, 200, 50, self.save_settings)
        self.add_button("cancel_settings", "Cancel", 640, 670, 200, 50, self.cancel_settings)
        
    def add_button(self, name, text, x, y, width, height, callback):
        """Add a button to the UI."""
        self.buttons[name] = {
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "callback": callback,
            "hover": False,
            "pressed": False
        }
        
    def add_label(self, name, text, x, y, size, color, center=False):
        """Add a label to the UI."""
        self.labels[name] = {
            "text": text,
            "x": x,
            "y": y,
            "size": size,
            "color": color,
            "center": center
        }
        
    def add_slider(self, name, text, x, y, width, height, min_val, max_val, default):
        """Add a slider to the UI."""
        self.sliders[name] = {
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "min_val": min_val,
            "max_val": max_val,
            "value": default,
            "dragging": False
        }
        
    def add_checkbox(self, name, text, x, y, default):
        """Add a checkbox to the UI."""
        self.checkboxes[name] = {
            "text": text,
            "x": x,
            "y": y,
            "checked": default
        }
        
    def add_health_bar(self, name, x, y, width, height):
        """Add a health bar to the HUD."""
        self.hud_elements["health_bar"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "max_health": 100,
            "current_health": 100
        }
        
    def add_energy_bar(self, name, x, y, width, height):
        """Add an energy bar to the HUD."""
        self.hud_elements["energy_bar"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "max_energy": 100,
            "current_energy": 100
        }
        
    def add_crosshair(self, name, x, y):
        """Add a crosshair to the HUD."""
        self.hud_elements["crosshair"] = {
            "x": x,
            "y": y,
            "size": 20,
            "color": "white"
        }
        
    def add_chat(self, name, x, y, width, height):
        """Add a chat window to the HUD."""
        self.hud_elements["chat"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "messages": [],
            "max_messages": 10,
            "visible": False
        }
        
    def add_minimap(self, name, x, y, width, height):
        """Add a minimap to the HUD."""
        self.hud_elements["minimap"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "scale": 0.1
        }
        
    def add_overlay(self, name, x, y, width, height, color):
        """Add an overlay to the UI."""
        self.ui_elements[name] = {
            "type": "overlay",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "color": color
        }
        
    def handle_event(self, event, game):
        """Handle UI events."""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_mouse_click(event.pos, game)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.handle_mouse_release(event.pos, game)
        elif event.type == MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == KEYDOWN:
            self.handle_key_press(event.key, game)
            
    def handle_mouse_click(self, pos, game):
        """Handle mouse click events."""
        x, y = pos
        
        # Check buttons
        for name, button in self.buttons.items():
            if (x >= button["x"] and x <= button["x"] + button["width"] and
                y >= button["y"] and y <= button["y"] + button["height"]):
                button["pressed"] = True
                if button["callback"]:
                    button["callback"](game)
                return
                
        # Check sliders
        for name, slider in self.sliders.items():
            if (x >= slider["x"] and x <= slider["x"] + slider["width"] and
                y >= slider["y"] and y <= slider["y"] + slider["height"]):
                slider["dragging"] = True
                self.update_slider_value(name, x)
                return
                
        # Check checkboxes
        for name, checkbox in self.checkboxes.items():
            checkbox_x = checkbox["x"]
            checkbox_y = checkbox["y"]
            checkbox_size = 20
            if (x >= checkbox_x and x <= checkbox_x + checkbox_size and
                y >= checkbox_y and y <= checkbox_y + checkbox_size):
                checkbox["checked"] = not checkbox["checked"]
                return
                
    def handle_mouse_release(self, pos, game):
        """Handle mouse release events."""
        # Reset button states
        for button in self.buttons.values():
            button["pressed"] = False
            
        # Reset slider states
        for slider in self.sliders.values():
            slider["dragging"] = False
            
    def handle_mouse_motion(self, pos):
        """Handle mouse motion events."""
        x, y = pos
        
        # Update button hover states
        for button in self.buttons.values():
            button["hover"] = (x >= button["x"] and x <= button["x"] + button["width"] and
                             y >= button["y"] and y <= button["y"] + button["height"])
                             
        # Update slider values if dragging
        for name, slider in self.sliders.items():
            if slider["dragging"]:
                self.update_slider_value(name, x)
                
    def handle_key_press(self, key, game):
        """Handle key press events."""
        if key == K_ESCAPE:
            if game.current_scene == "game":
                game.current_scene = "pause_menu"
            elif game.current_scene == "pause_menu":
                game.current_scene = "game"
        elif key == K_RETURN:
            # Toggle chat
            if game.current_scene == "game":
                chat = self.hud_elements["chat"]
                chat["visible"] = not chat["visible"]
                
    def update_slider_value(self, name, x):
        """Update slider value based on mouse position."""
        slider = self.sliders[name]
        relative_x = x - slider["x"]
        percentage = max(0, min(1, relative_x / slider["width"]))
        slider["value"] = slider["min_val"] + percentage * (slider["max_val"] - slider["min_val"])
        
    def update(self):
        """Update UI logic."""
        # Update HUD elements
        self.update_hud()
        
    def update_hud(self):
        """Update HUD elements."""
        # Update health bar (this would get data from the player)
        # health_bar = self.hud_elements["health_bar"]
        # health_bar["current_health"] = player.health
        
        # Update energy bar (this would get data from the player)
        # energy_bar = self.hud_elements["energy_bar"]
        # energy_bar["current_energy"] = player.energy
        
        pass
        
    def render(self):
        """Render the UI."""
        # Switch to 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1280, 720, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable 3D features for 2D rendering
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Render current menu
        if self.current_menu == "main_menu":
            self.render_main_menu()
        elif self.current_menu == "pause_menu":
            self.render_pause_menu()
        elif self.current_menu == "settings":
            self.render_settings_menu()
        elif self.current_menu == "game":
            self.render_hud()
            
        # Restore 3D settings
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def render_main_menu(self):
        """Render the main menu."""
        # Render labels
        for label in self.labels.values():
            if label["text"] in ["Roblox Creator Studio", "v1.0.0 - By Seif Abdelhamid"]:
                self.render_text(label["text"], label["x"], label["y"], label["size"], label["color"], label["center"])
                
        # Render buttons
        for button in self.buttons.values():
            if button["text"] in ["Play Game", "Settings", "Quit"]:
                self.render_button(button)
                
    def render_pause_menu(self):
        """Render the pause menu."""
        # Render overlay
        self.render_overlay(0, 0, 1280, 720, (0, 0, 0, 128))
        
        # Render labels
        for label in self.labels.values():
            if label["text"] == "Game Paused":
                self.render_text(label["text"], label["x"], label["y"], label["size"], label["color"], label["center"])
                
        # Render buttons
        for button in self.buttons.values():
            if button["text"] in ["Resume", "Settings", "Main Menu"]:
                self.render_button(button)
                
    def render_settings_menu(self):
        """Render the settings menu."""
        # Render labels
        for label in self.labels.values():
            if label["text"] in ["Settings", "Graphics", "Audio", "Controls"]:
                self.render_text(label["text"], label["x"], label["y"], label["size"], label["color"], label["center"])
                
        # Render sliders
        for slider in self.sliders.values():
            self.render_slider(slider)
            
        # Render checkboxes
        for checkbox in self.checkboxes.values():
            self.render_checkbox(checkbox)
            
        # Render buttons
        for button in self.buttons.values():
            if button["text"] in ["Save", "Cancel", "Keybindings"]:
                self.render_button(button)
                
    def render_hud(self):
        """Render the heads-up display."""
        # Render health bar
        health_bar = self.hud_elements["health_bar"]
        if health_bar:
            self.render_health_bar(health_bar)
            
        # Render energy bar
        energy_bar = self.hud_elements["energy_bar"]
        if energy_bar:
            self.render_energy_bar(energy_bar)
            
        # Render crosshair
        crosshair = self.hud_elements["crosshair"]
        if crosshair:
            self.render_crosshair(crosshair)
            
        # Render chat
        chat = self.hud_elements["chat"]
        if chat and chat["visible"]:
            self.render_chat(chat)
            
        # Render minimap
        minimap = self.hud_elements["minimap"]
        if minimap:
            self.render_minimap(minimap)
            
    def render_text(self, text, x, y, size, color, center=False):
        """Render text on screen."""
        if size not in self.fonts:
            return
            
        font = self.fonts[size]
        text_surface = font.render(text, True, self.colors[color])
        
        if center:
            x -= text_surface.get_width() // 2
            
        # Convert to OpenGL texture and render
        # This is a simplified version - in a real implementation you'd use proper text rendering
        glColor3f(*[c/255 for c in self.colors[color]])
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + text_surface.get_width(), y)
        glVertex2f(x + text_surface.get_width(), y + text_surface.get_height())
        glVertex2f(x, y + text_surface.get_height())
        glEnd()
        glColor3f(1.0, 1.0, 1.0)
        
    def render_button(self, button):
        """Render a button."""
        # Button background
        color = "light_gray" if button["hover"] else "gray"
        if button["pressed"]:
            color = "dark_gray"
            
        glColor3f(*[c/255 for c in self.colors[color]])
        glBegin(GL_QUADS)
        glVertex2f(button["x"], button["y"])
        glVertex2f(button["x"] + button["width"], button["y"])
        glVertex2f(button["x"] + button["width"], button["y"] + button["height"])
        glVertex2f(button["x"], button["y"] + button["height"])
        glEnd()
        
        # Button text
        self.render_text(button["text"], button["x"] + button["width"]//2, 
                        button["y"] + button["height"]//2, 20, "black", True)
        
    def render_slider(self, slider):
        """Render a slider."""
        # Slider track
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(slider["x"], slider["y"])
        glVertex2f(slider["x"] + slider["width"], slider["y"])
        glVertex2f(slider["x"] + slider["width"], slider["y"] + slider["height"])
        glVertex2f(slider["x"], slider["y"] + slider["height"])
        glEnd()
        
        # Slider handle
        percentage = (slider["value"] - slider["min_val"]) / (slider["max_val"] - slider["min_val"])
        handle_x = slider["x"] + percentage * slider["width"]
        
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(handle_x - 5, slider["y"] - 5)
        glVertex2f(handle_x + 5, slider["y"] - 5)
        glVertex2f(handle_x + 5, slider["y"] + slider["height"] + 5)
        glVertex2f(handle_x - 5, slider["y"] + slider["height"] + 5)
        glEnd()
        
        # Slider text
        self.render_text(f"{slider['text']}: {int(slider['value'])}", 
                        slider["x"], slider["y"] - 25, 16, "white")
        
    def render_checkbox(self, checkbox):
        """Render a checkbox."""
        # Checkbox box
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(checkbox["x"], checkbox["y"])
        glVertex2f(checkbox["x"] + 20, checkbox["y"])
        glVertex2f(checkbox["x"] + 20, checkbox["y"] + 20)
        glVertex2f(checkbox["x"], checkbox["y"] + 20)
        glEnd()
        
        # Checkbox check
        if checkbox["checked"]:
            glColor3f(0.0, 0.0, 0.0)
            glBegin(GL_QUADS)
            glVertex2f(checkbox["x"] + 5, checkbox["y"] + 5)
            glVertex2f(checkbox["x"] + 15, checkbox["y"] + 5)
            glVertex2f(checkbox["x"] + 15, checkbox["y"] + 15)
            glVertex2f(checkbox["x"] + 5, checkbox["y"] + 15)
            glEnd()
            
        # Checkbox text
        self.render_text(checkbox["text"], checkbox["x"] + 30, checkbox["y"] + 5, 16, "white")
        
    def render_health_bar(self, health_bar):
        """Render the health bar."""
        # Background
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(health_bar["x"], health_bar["y"])
        glVertex2f(health_bar["x"] + health_bar["width"], health_bar["y"])
        glVertex2f(health_bar["x"] + health_bar["width"], health_bar["y"] + health_bar["height"])
        glVertex2f(health_bar["x"], health_bar["y"] + health_bar["height"])
        glEnd()
        
        # Health fill
        health_percentage = health_bar["current_health"] / health_bar["max_health"]
        glColor3f(1.0 - health_percentage, health_percentage, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(health_bar["x"], health_bar["y"])
        glVertex2f(health_bar["x"] + health_bar["width"] * health_percentage, health_bar["y"])
        glVertex2f(health_bar["x"] + health_bar["width"] * health_percentage, health_bar["y"] + health_bar["height"])
        glVertex2f(health_bar["x"], health_bar["y"] + health_bar["height"])
        glEnd()
        
        # Health text
        self.render_text(f"Health: {health_bar['current_health']}/{health_bar['max_health']}", 
                        health_bar["x"], health_bar["y"] - 20, 16, "white")
        
    def render_energy_bar(self, energy_bar):
        """Render the energy bar."""
        # Background
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(energy_bar["x"], energy_bar["y"])
        glVertex2f(energy_bar["x"] + energy_bar["width"], energy_bar["y"])
        glVertex2f(energy_bar["x"] + energy_bar["width"], energy_bar["y"] + energy_bar["height"])
        glVertex2f(energy_bar["x"], energy_bar["y"] + energy_bar["height"])
        glEnd()
        
        # Energy fill
        energy_percentage = energy_bar["current_energy"] / energy_bar["max_energy"]
        glColor3f(0.0, 0.0, energy_percentage)
        glBegin(GL_QUADS)
        glVertex2f(energy_bar["x"], energy_bar["y"])
        glVertex2f(energy_bar["x"] + energy_bar["width"] * energy_percentage, energy_bar["y"])
        glVertex2f(energy_bar["x"] + energy_bar["width"] * energy_percentage, energy_bar["y"] + energy_bar["height"])
        glVertex2f(energy_bar["x"], energy_bar["y"] + energy_bar["height"])
        glEnd()
        
        # Energy text
        self.render_text(f"Energy: {energy_bar['current_energy']}/{energy_bar['max_energy']}", 
                        energy_bar["x"], energy_bar["y"] - 20, 16, "white")
        
    def render_crosshair(self, crosshair):
        """Render the crosshair."""
        glColor3f(1.0, 1.0, 1.0)
        size = crosshair["size"]
        x, y = crosshair["x"], crosshair["y"]
        
        # Horizontal line
        glBegin(GL_LINES)
        glVertex2f(x - size, y)
        glVertex2f(x + size, y)
        glEnd()
        
        # Vertical line
        glBegin(GL_LINES)
        glVertex2f(x, y - size)
        glVertex2f(x, y + size)
        glEnd()
        
    def render_chat(self, chat):
        """Render the chat window."""
        # Chat background
        glColor3f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(chat["x"], chat["y"])
        glVertex2f(chat["x"] + chat["width"], chat["y"])
        glVertex2f(chat["x"] + chat["width"], chat["y"] + chat["height"])
        glVertex2f(chat["x"], chat["y"] + chat["height"])
        glEnd()
        
        # Chat messages
        y_offset = chat["y"] + chat["height"] - 20
        for message in chat["messages"][-chat["max_messages"]:]:
            self.render_text(message, chat["x"] + 10, y_offset, 16, "white")
            y_offset -= 20
            
    def render_minimap(self, minimap):
        """Render the minimap."""
        # Minimap background
        glColor3f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(minimap["x"], minimap["y"])
        glVertex2f(minimap["x"] + minimap["width"], minimap["y"])
        glVertex2f(minimap["x"] + minimap["width"], minimap["y"] + minimap["height"])
        glVertex2f(minimap["x"], minimap["y"] + minimap["height"])
        glEnd()
        
        # Minimap border
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(minimap["x"], minimap["y"])
        glVertex2f(minimap["x"] + minimap["width"], minimap["y"])
        glVertex2f(minimap["x"] + minimap["width"], minimap["y"] + minimap["height"])
        glVertex2f(minimap["x"], minimap["y"] + minimap["height"])
        glEnd()
        
    def render_overlay(self, x, y, width, height, color):
        """Render an overlay."""
        glColor4f(*[c/255 for c in color])
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
    # Menu callback functions
    def start_game(self, game):
        """Start the game."""
        game.current_scene = "game"
        
    def open_settings(self, game):
        """Open settings menu."""
        game.current_scene = "settings"
        
    def quit_game(self, game):
        """Quit the game."""
        game.running = False
        
    def resume_game(self, game):
        """Resume the game."""
        game.current_scene = "game"
        
    def return_to_main_menu(self, game):
        """Return to main menu."""
        game.current_scene = "main_menu"
        
    def save_settings(self, game):
        """Save settings."""
        # Save current settings
        game.current_scene = "game"
        
    def cancel_settings(self, game):
        """Cancel settings changes."""
        game.current_scene = "game"
        
    def open_keybindings(self, game):
        """Open keybindings menu."""
        # This would open a keybindings menu
        pass
