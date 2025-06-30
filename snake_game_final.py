"""
Snake Game Final - Ultimate Edition
A complete, professional Snake game with advanced features and visual effects.

Features:
- Multiple difficulty levels with score multipliers
- Persistent high-score leaderboard system
- Professional UI with smooth animations
- Advanced particle effects and visual polish
- Comprehensive audio system with fallbacks
- Proper game area separation from UI elements
"""

import pygame
import random
import sys
import math
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
class GameConfig:
    """Game configuration constants"""
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    
    # Game area (separate from UI)
    GAME_AREA_X = 150
    GAME_AREA_Y = 80
    GAME_AREA_WIDTH = 700
    GAME_AREA_HEIGHT = 540
    
    GRID_SIZE = 20
    GRID_WIDTH = GAME_AREA_WIDTH // GRID_SIZE
    GRID_HEIGHT = GAME_AREA_HEIGHT // GRID_SIZE

class Colors:
    """Color palette for consistent theming"""
    BACKGROUND_DARK = (10, 10, 20)
    BACKGROUND_LIGHT = (20, 20, 35)
    GAME_AREA_BG = (15, 15, 25)
    
    SNAKE_PRIMARY = (50, 255, 50)
    SNAKE_SECONDARY = (34, 200, 34)
    SNAKE_HEAD = (100, 255, 150)
    SNAKE_GLOW = (50, 255, 50, 80)
    
    FOOD_PRIMARY = (255, 100, 50)
    FOOD_SECONDARY = (255, 150, 100)
    FOOD_GLOW = (255, 100, 50, 120)
    
    TEXT_PRIMARY = (240, 240, 240)
    TEXT_SECONDARY = (180, 180, 180)
    ACCENT_BLUE = (100, 149, 237)
    ACCENT_GREEN = (50, 255, 127)
    
    GRID_LINE = (30, 30, 45)
    UI_BORDER = (60, 60, 80)
    
    # Difficulty colors
    EASY_COLOR = (50, 255, 50)
    MEDIUM_COLOR = (255, 200, 50)
    HARD_COLOR = (255, 80, 80)

class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    DIFFICULTY_SELECT = "difficulty_select"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    LEADERBOARD = "leaderboard"

@dataclass
class DifficultyConfig:
    """Configuration for difficulty levels"""
    name: str
    speed: int
    multiplier: float
    color: Tuple[int, int, int]

class DifficultyManager:
    """Manages difficulty settings and configurations"""
    
    DIFFICULTIES = {
        'EASY': DifficultyConfig('EASY', 8, 1.0, Colors.EASY_COLOR),
        'MEDIUM': DifficultyConfig('MEDIUM', 12, 1.5, Colors.MEDIUM_COLOR),
        'HARD': DifficultyConfig('HARD', 18, 2.0, Colors.HARD_COLOR)
    }
    
    @classmethod
    def get_config(cls, difficulty: str) -> DifficultyConfig:
        """Get configuration for a difficulty level"""
        return cls.DIFFICULTIES.get(difficulty, cls.DIFFICULTIES['MEDIUM'])

class ScoreManager:
    """Handles persistent high score management"""
    
    def __init__(self, filename: str = "high_scores.json"):
        self.filename = filename
        self.scores = self._load_scores()
    
    def _load_scores(self) -> Dict[str, List[Dict]]:
        """Load scores from file with error handling"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load scores - {e}")
        
        return {'EASY': [], 'MEDIUM': [], 'HARD': []}
    
    def _save_scores(self) -> None:
        """Save scores to file with error handling"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save scores - {e}")
    
    def add_score(self, difficulty: str, score: int, player: str = "Player") -> int:
        """Add a new score and return its rank"""
        entry = {
            'score': score,
            'player': player,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        if difficulty not in self.scores:
            self.scores[difficulty] = []
        
        self.scores[difficulty].append(entry)
        self.scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
        self.scores[difficulty] = self.scores[difficulty][:10]  # Keep top 10
        
        self._save_scores()
        
        # Return rank (1-based)
        for i, score_entry in enumerate(self.scores[difficulty]):
            if score_entry == entry:
                return i + 1
        return len(self.scores[difficulty])
    
    def get_high_score(self, difficulty: str) -> int:
        """Get highest score for difficulty"""
        scores = self.scores.get(difficulty, [])
        return scores[0]['score'] if scores else 0
    
    def get_top_scores(self, difficulty: str, count: int = 10) -> List[Dict]:
        """Get top scores for difficulty"""
        return self.scores.get(difficulty, [])[:count]
    
    def is_high_score(self, difficulty: str, score: int) -> bool:
        """Check if score qualifies for leaderboard"""
        scores = self.scores.get(difficulty, [])
        return len(scores) < 10 or (scores and score > scores[-1]['score'])

class AudioManager:
    """Manages all audio functionality with fallbacks"""
    
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.3
        self.sfx_volume = 0.7
        self.enabled = True
        self.audio_dir = "audio"
        
        self._ensure_audio_dir()
        self._load_sounds()
        self._start_background_music()
    
    def _ensure_audio_dir(self) -> None:
        """Create audio directory if it doesn't exist"""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def _load_sounds(self) -> None:
        """Load all sound effects with fallbacks"""
        sound_files = {
            'eat': 'eat_food.wav',
            'turn': 'turn.wav',
            'game_over': 'game_over.wav',
            'button_hover': 'button_hover.wav',
            'button_click': 'button_click.wav',
            'game_start': 'game_start.wav',
            'high_score': 'high_score.wav'
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(self.audio_dir, filename)
            try:
                if os.path.exists(filepath):
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                else:
                    self.sounds[sound_name] = None
            except pygame.error:
                self.sounds[sound_name] = None
    
    def _start_background_music(self) -> None:
        """Start background music if available"""
        music_file = os.path.join(self.audio_dir, "background_music.ogg")
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass  # Silently fail if music can't load
    
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect if available and enabled"""
        if not self.enabled:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except pygame.error:
                pass  # Silently fail if sound can't play
    
    def toggle(self) -> None:
        """Toggle audio on/off"""
        self.enabled = not self.enabled
        if self.enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

class GraphicsUtils:
    """Utility functions for graphics and visual effects"""
    
    @staticmethod
    def create_gradient_surface(width: int, height: int, 
                              color1: Tuple[int, int, int], 
                              color2: Tuple[int, int, int], 
                              vertical: bool = True) -> pygame.Surface:
        """Create a gradient surface between two colors"""
        surface = pygame.Surface((width, height))
        
        if vertical:
            for y in range(height):
                ratio = y / height
                color = tuple(int(color1[i] * (1 - ratio) + color2[i] * ratio) for i in range(3))
                pygame.draw.line(surface, color, (0, y), (width, y))
        else:
            for x in range(width):
                ratio = x / width
                color = tuple(int(color1[i] * (1 - ratio) + color2[i] * ratio) for i in range(3))
                pygame.draw.line(surface, color, (x, 0), (x, height))
        
        return surface
    
    @staticmethod
    def draw_glowing_rect(surface: pygame.Surface, color: Tuple[int, int, int], 
                         rect: pygame.Rect, glow_size: int = 5) -> None:
        """Draw a rectangle with a glowing border effect"""
        # Draw glow layers
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (glow_size - i) / glow_size * 0.3)
            glow_color = (*color, alpha)
            glow_surface = pygame.Surface((rect.width + i*2, rect.height + i*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, 
                           (0, 0, rect.width + i*2, rect.height + i*2), border_radius=5)
            surface.blit(glow_surface, (rect.x - i, rect.y - i))
        
        # Draw main rectangle
        pygame.draw.rect(surface, color, rect, border_radius=3)
    
    @staticmethod
    def draw_glowing_circle(surface: pygame.Surface, color: Tuple[int, int, int], 
                          center: Tuple[int, int], radius: int, glow_size: int = 8) -> None:
        """Draw a circle with a glowing effect"""
        # Draw glow layers
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (glow_size - i) / glow_size * 0.4)
            glow_color = (*color, alpha)
            glow_surface = pygame.Surface(((radius + i) * 2, (radius + i) * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (radius + i, radius + i), radius + i)
            surface.blit(glow_surface, (center[0] - radius - i, center[1] - radius - i))
        
        # Draw main circle
        pygame.draw.circle(surface, color, center, radius)

class Particle:
    """Individual particle for effects"""
    
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 color: Tuple[int, int, int], life: int = 60, size: float = 3.0):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.initial_size = size
    
    def update(self) -> bool:
        """Update particle and return True if still alive"""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        # Fade and shrink over time
        life_ratio = self.life / self.max_life
        self.size = self.initial_size * life_ratio
        
        # Add gravity to some particles
        self.vy += 0.1
        
        return self.life > 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the particle with alpha blending"""
        if self.life <= 0 or self.size <= 0:
            return
        
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (self.size, self.size), self.size)
        surface.blit(particle_surface, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    """Manages particle effects throughout the game"""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 20) -> None:
        """Add explosion effect at position"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            life = random.randint(30, 60)
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, velocity, color, life, size))
    
    def add_food_effect(self, x: float, y: float) -> None:
        """Add sparkle effect when food is eaten"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice([Colors.FOOD_PRIMARY, Colors.FOOD_SECONDARY, (255, 255, 255)])
            life = random.randint(20, 40)
            size = random.uniform(1, 3)
            self.particles.append(Particle(x, y, velocity, color, life, size))
    
    def add_background_particles(self) -> None:
        """Add floating background particles for ambiance"""
        if random.random() < 0.05:  # 5% chance each frame
            x = random.randint(0, GameConfig.WINDOW_WIDTH)
            y = GameConfig.WINDOW_HEIGHT + 10
            velocity = (random.uniform(-0.5, 0.5), random.uniform(-1, -0.3))
            color = random.choice([Colors.SNAKE_PRIMARY, Colors.FOOD_PRIMARY, Colors.ACCENT_BLUE])
            life = random.randint(120, 180)
            size = random.uniform(1, 2)
            self.particles.append(Particle(x, y, velocity, color, life, size))
    
    def update(self) -> None:
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()

class Button:
    """Interactive button with hover effects and animations"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 font: pygame.font.Font, audio_manager: AudioManager,
                 color: Tuple[int, int, int] = Colors.ACCENT_BLUE,
                 hover_color: Optional[Tuple[int, int, int]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color or tuple(min(255, c + 30) for c in color)
        self.audio_manager = audio_manager
        
        self.is_hovered = False
        self.was_hovered = False
        self.selected = False
        self.animation_scale = 1.0
        self.glow_intensity = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events and return True if clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.audio_manager.play_sound('button_click')
                return True
        return False
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update button state and animations"""
        self.was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Play hover sound
        if self.is_hovered and not self.was_hovered:
            self.audio_manager.play_sound('button_hover')
        
        # Smooth animations
        target_scale = 1.05 if (self.is_hovered or self.selected) else 1.0
        target_glow = 50 if (self.is_hovered or self.selected) else 0
        
        self.animation_scale += (target_scale - self.animation_scale) * 0.15
        self.glow_intensity += (target_glow - self.glow_intensity) * 0.15
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button with all effects"""
        # Calculate animated rect
        scale_offset = (self.rect.width * (self.animation_scale - 1)) / 2
        animated_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            self.rect.width * self.animation_scale,
            self.rect.height * self.animation_scale
        )
        
        # Draw glow effect
        if self.glow_intensity > 5:
            glow_color = (*self.hover_color, int(self.glow_intensity))
            glow_surface = pygame.Surface((animated_rect.width + 20, animated_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, animated_rect.width, animated_rect.height), border_radius=10)
            surface.blit(glow_surface, (animated_rect.x - 10, animated_rect.y - 10))
        
        # Draw button background
        current_color = self.hover_color if (self.is_hovered or self.selected) else self.color
        button_gradient = GraphicsUtils.create_gradient_surface(
            int(animated_rect.width), int(animated_rect.height),
            current_color, tuple(max(0, c - 30) for c in current_color)
        )
        surface.blit(button_gradient, animated_rect)
        
        # Draw border
        pygame.draw.rect(surface, Colors.TEXT_PRIMARY, animated_rect, 2, border_radius=8)
        
        # Draw text
        text_surface = self.font.render(self.text, True, Colors.TEXT_PRIMARY)
        text_rect = text_surface.get_rect(center=animated_rect.center)
        surface.blit(text_surface, text_rect)

class DifficultyButton(Button):
    """Specialized button for difficulty selection with additional info"""
    
    def __init__(self, x: int, y: int, width: int, height: int, difficulty: str, 
                 font: pygame.font.Font, audio_manager: AudioManager):
        config = DifficultyManager.get_config(difficulty)
        super().__init__(x, y, width, height, difficulty, font, audio_manager, 
                        config.color, tuple(min(255, c + 30) for c in config.color))
        self.difficulty = difficulty
        self.config = config
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw difficulty button with additional stats"""
        super().draw(surface)
        
        # Draw difficulty stats below button
        info_font = pygame.font.Font(None, 24)
        speed_text = f"Speed: {self.config.speed} FPS"
        multiplier_text = f"Score: x{self.config.multiplier}"
        
        speed_surface = info_font.render(speed_text, True, Colors.TEXT_SECONDARY)
        multiplier_surface = info_font.render(multiplier_text, True, Colors.TEXT_SECONDARY)
        
        speed_rect = speed_surface.get_rect(centerx=self.rect.centerx, y=self.rect.bottom + 8)
        multiplier_rect = multiplier_surface.get_rect(centerx=self.rect.centerx, y=self.rect.bottom + 28)
        
        surface.blit(speed_surface, speed_rect)
        surface.blit(multiplier_surface, multiplier_rect)

class Snake:
    """Enhanced snake with visual effects and smooth animations"""
    
    def __init__(self, audio_manager: AudioManager):
        start_x = GameConfig.GRID_WIDTH // 2
        start_y = GameConfig.GRID_HEIGHT // 2
        self.positions = [(start_x, start_y)]
        self.direction = (1, 0)  # Moving right
        self.grow_pending = False
        self.audio_manager = audio_manager
        
        # Animation properties
        self.segment_animations = [0]
        self.head_glow_intensity = 0
        self.body_pulse_offset = 0
    
    def move(self) -> None:
        """Move the snake forward"""
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        self.positions.insert(0, new_head)
        
        if not self.grow_pending:
            self.positions.pop()
        else:
            self.grow_pending = False
            self.segment_animations.append(0)
        
        # Update animations
        self.body_pulse_offset = (self.body_pulse_offset + 1) % 120
        for i in range(len(self.segment_animations)):
            self.segment_animations[i] = (self.segment_animations[i] + 1) % 60
        
        self.head_glow_intensity = (self.head_glow_intensity + 1) % 60
    
    def change_direction(self, new_direction: Tuple[int, int]) -> None:
        """Change direction if valid (no reversing)"""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            if new_direction != self.direction:
                self.audio_manager.play_sound('turn')
            self.direction = new_direction
    
    def check_collision(self) -> bool:
        """Check for wall or self collision"""
        head_x, head_y = self.positions[0]
        
        # Wall collision
        if (head_x < 0 or head_x >= GameConfig.GRID_WIDTH or 
            head_y < 0 or head_y >= GameConfig.GRID_HEIGHT):
            return True
        
        # Self collision
        return self.positions[0] in self.positions[1:]
    
    def eat_food(self) -> None:
        """Grow the snake and play sound"""
        self.grow_pending = True
        self.audio_manager.play_sound('eat')
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw snake with advanced visual effects"""
        for i, (grid_x, grid_y) in enumerate(self.positions):
            # Convert grid position to screen position
            screen_x = GameConfig.GAME_AREA_X + grid_x * GameConfig.GRID_SIZE
            screen_y = GameConfig.GAME_AREA_Y + grid_y * GameConfig.GRID_SIZE
            
            # Animation effects
            pulse = math.sin((self.segment_animations[i] + self.body_pulse_offset) * 0.1) * 2
            size = GameConfig.GRID_SIZE - 4 + pulse
            offset = (GameConfig.GRID_SIZE - size) / 2
            
            rect = pygame.Rect(screen_x + offset, screen_y + offset, size, size)
            
            if i == 0:  # Snake head
                # Glowing head with pulsing effect
                head_glow = 50 + 30 * math.sin(self.head_glow_intensity * 0.2)
                center = (int(rect.centerx), int(rect.centery))
                
                # Draw glow effect
                GraphicsUtils.draw_glowing_circle(surface, Colors.SNAKE_HEAD, center, 
                                                int(size // 2), int(head_glow // 10))
                
                # Draw eyes based on direction
                eye_offset = 4
                if self.direction == (1, 0):  # Right
                    eye1 = (center[0] + eye_offset, center[1] - 3)
                    eye2 = (center[0] + eye_offset, center[1] + 3)
                elif self.direction == (-1, 0):  # Left
                    eye1 = (center[0] - eye_offset, center[1] - 3)
                    eye2 = (center[0] - eye_offset, center[1] + 3)
                elif self.direction == (0, -1):  # Up
                    eye1 = (center[0] - 3, center[1] - eye_offset)
                    eye2 = (center[0] + 3, center[1] - eye_offset)
                else:  # Down
                    eye1 = (center[0] - 3, center[1] + eye_offset)
                    eye2 = (center[0] + 3, center[1] + eye_offset)
                
                # Draw eyes with glow
                for eye_pos in [eye1, eye2]:
                    pygame.draw.circle(surface, (255, 255, 255), eye_pos, 3)
                    pygame.draw.circle(surface, (100, 255, 150), eye_pos, 2)
                    pygame.draw.circle(surface, (0, 0, 0), eye_pos, 1)
                
            else:  # Snake body
                # Alternating body colors with glow
                segment_color = Colors.SNAKE_PRIMARY if i % 2 == 0 else Colors.SNAKE_SECONDARY
                
                # Draw glowing body segment
                GraphicsUtils.draw_glowing_rect(surface, segment_color, rect, 3)
                
                # Inner highlight
                inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
                inner_color = tuple(min(255, c + 20) for c in segment_color)
                pygame.draw.rect(surface, inner_color, inner_rect, border_radius=2)

class Food:
    """Enhanced food with particle effects and animations"""
    
    def __init__(self):
        self.position = self._generate_position()
        self.animation_frame = 0
        self.pulse_intensity = 0
        self.sparkle_particles = []
    
    def _generate_position(self) -> Tuple[int, int]:
        """Generate random position within game grid"""
        return (random.randint(0, GameConfig.GRID_WIDTH - 1),
                random.randint(0, GameConfig.GRID_HEIGHT - 1))
    
    def respawn(self, snake_positions: List[Tuple[int, int]]) -> None:
        """Respawn food avoiding snake body"""
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            new_position = self._generate_position()
            if new_position not in snake_positions:
                self.position = new_position
                break
            attempts += 1
    
    def update(self) -> None:
        """Update food animations and effects"""
        self.animation_frame += 1
        self.pulse_intensity = math.sin(self.animation_frame * 0.15) * 0.3 + 1.0
        
        # Add occasional sparkle particles
        if random.random() < 0.1:
            screen_x = GameConfig.GAME_AREA_X + self.position[0] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            screen_y = GameConfig.GAME_AREA_Y + self.position[1] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            
            particle = Particle(
                screen_x + offset_x, screen_y + offset_y,
                (random.uniform(-0.5, 0.5), random.uniform(-1, 0)),
                (255, 255, 255), 20, 1
            )
            self.sparkle_particles.append(particle)
        
        # Update sparkle particles
        self.sparkle_particles = [p for p in self.sparkle_particles if p.update()]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw food with glowing effects and sparkles"""
        screen_x = GameConfig.GAME_AREA_X + self.position[0] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        screen_y = GameConfig.GAME_AREA_Y + self.position[1] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        
        # Pulsing radius
        base_radius = GameConfig.GRID_SIZE // 2 - 3
        radius = int(base_radius * self.pulse_intensity)
        
        # Draw glowing food
        GraphicsUtils.draw_glowing_circle(surface, Colors.FOOD_PRIMARY, 
                                        (screen_x, screen_y), radius, 12)
        
        # Draw inner core
        inner_radius = max(1, radius - 3)
        pygame.draw.circle(surface, Colors.FOOD_SECONDARY, (screen_x, screen_y), inner_radius)
        
        # Draw moving sparkle
        sparkle_offset = math.sin(self.animation_frame * 0.3) * 4
        sparkle_pos = (screen_x + int(sparkle_offset), screen_y - int(sparkle_offset))
        pygame.draw.circle(surface, (255, 255, 255), sparkle_pos, 2)
        
        # Draw sparkle particles
        for particle in self.sparkle_particles:
            particle.draw(surface)

class GameUI:
    """Handles all UI rendering and layout"""
    
    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        self.title_glow = 0
        self.menu_animation = 0
    
    def update_animations(self) -> None:
        """Update UI animations"""
        self.title_glow = (self.title_glow + 1) % 120
        self.menu_animation += 1
    
    def draw_game_area_border(self, surface: pygame.Surface) -> None:
        """Draw the game area with a professional border"""
        # Game area background
        game_area_rect = pygame.Rect(GameConfig.GAME_AREA_X - 5, GameConfig.GAME_AREA_Y - 5,
                                   GameConfig.GAME_AREA_WIDTH + 10, GameConfig.GAME_AREA_HEIGHT + 10)
        
        # Draw gradient background
        bg_gradient = GraphicsUtils.create_gradient_surface(
            game_area_rect.width, game_area_rect.height,
            Colors.GAME_AREA_BG, Colors.BACKGROUND_DARK
        )
        surface.blit(bg_gradient, game_area_rect)
        
        # Draw glowing border
        GraphicsUtils.draw_glowing_rect(surface, Colors.UI_BORDER, game_area_rect, 3)
        
        # Draw grid lines
        for x in range(0, GameConfig.GRID_WIDTH + 1):
            line_x = GameConfig.GAME_AREA_X + x * GameConfig.GRID_SIZE
            pygame.draw.line(surface, Colors.GRID_LINE,
                           (line_x, GameConfig.GAME_AREA_Y),
                           (line_x, GameConfig.GAME_AREA_Y + GameConfig.GAME_AREA_HEIGHT))
        
        for y in range(0, GameConfig.GRID_HEIGHT + 1):
            line_y = GameConfig.GAME_AREA_Y + y * GameConfig.GRID_SIZE
            pygame.draw.line(surface, Colors.GRID_LINE,
                           (GameConfig.GAME_AREA_X, line_y),
                           (GameConfig.GAME_AREA_X + GameConfig.GAME_AREA_WIDTH, line_y))
    
    def draw_score_panel(self, surface: pygame.Surface, score: int, difficulty: str, multiplier: float) -> None:
        """Draw the score panel outside game area"""
        panel_x = 20
        panel_y = 100
        panel_width = 120
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, 150)
        panel_bg = GraphicsUtils.create_gradient_surface(
            panel_width, 150, Colors.ACCENT_BLUE, 
            tuple(c // 2 for c in Colors.ACCENT_BLUE)
        )
        surface.blit(panel_bg, panel_rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, panel_rect, 2, border_radius=8)
        
        # Score text
        score_text = self.fonts['medium'].render("SCORE", True, Colors.TEXT_PRIMARY)
        score_value = self.fonts['large'].render(str(score), True, Colors.ACCENT_GREEN)
        
        # Difficulty text
        diff_text = self.fonts['small'].render("DIFFICULTY", True, Colors.TEXT_SECONDARY)
        diff_color = DifficultyManager.get_config(difficulty).color
        diff_value = self.fonts['medium'].render(difficulty, True, diff_color)
        
        # Multiplier text
        mult_text = self.fonts['small'].render("MULTIPLIER", True, Colors.TEXT_SECONDARY)
        mult_value = self.fonts['medium'].render(f"x{multiplier}", True, Colors.ACCENT_BLUE)
        
        # Position text elements
        y_offset = panel_y + 10
        surface.blit(score_text, (panel_x + 10, y_offset))
        surface.blit(score_value, (panel_x + 10, y_offset + 25))
        
        y_offset += 60
        surface.blit(diff_text, (panel_x + 10, y_offset))
        surface.blit(diff_value, (panel_x + 10, y_offset + 20))
        
        y_offset += 50
        surface.blit(mult_text, (panel_x + 10, y_offset))
        surface.blit(mult_value, (panel_x + 10, y_offset + 20))
    
    def draw_high_score_panel(self, surface: pygame.Surface, score_manager: ScoreManager) -> None:
        """Draw high scores panel"""
        panel_x = GameConfig.WINDOW_WIDTH - 140
        panel_y = 100
        panel_width = 120
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, 200)
        panel_bg = GraphicsUtils.create_gradient_surface(
            panel_width, 200, Colors.ACCENT_GREEN,
            tuple(c // 2 for c in Colors.ACCENT_GREEN)
        )
        surface.blit(panel_bg, panel_rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, panel_rect, 2, border_radius=8)
        
        # Title
        title_text = self.fonts['medium'].render("HIGH SCORES", True, Colors.TEXT_PRIMARY)
        surface.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # High scores for each difficulty
        y_offset = panel_y + 40
        for difficulty in ['EASY', 'MEDIUM', 'HARD']:
            config = DifficultyManager.get_config(difficulty)
            high_score = score_manager.get_high_score(difficulty)
            
            diff_text = self.fonts['small'].render(difficulty, True, config.color)
            score_text = self.fonts['small'].render(str(high_score), True, Colors.TEXT_PRIMARY)
            
            surface.blit(diff_text, (panel_x + 10, y_offset))
            surface.blit(score_text, (panel_x + 10, y_offset + 15))
            y_offset += 40

class SnakeGame:
    """Main game class orchestrating all components"""
    
    def __init__(self):
        # Initialize display
        self.screen = pygame.display.set_mode((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game Final - Ultimate Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize managers
        self.audio_manager = AudioManager()
        self.score_manager = ScoreManager()
        self.particle_system = ParticleSystem()
        
        # Initialize fonts
        self.fonts = {
            'title': pygame.font.Font(None, 84),
            'large': pygame.font.Font(None, 56),
            'medium': pygame.font.Font(None, 42),
            'small': pygame.font.Font(None, 32),
            'tiny': pygame.font.Font(None, 24)
        }
        
        # Initialize UI
        self.ui = GameUI(self.fonts)
        
        # Game state
        self.state = GameState.MENU
        self.current_difficulty = 'MEDIUM'
        self.snake = None
        self.food = None
        self.score = 0
        
        # Create buttons
        self._create_buttons()
        
        # Create background
        self.background = GraphicsUtils.create_gradient_surface(
            GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT,
            Colors.BACKGROUND_DARK, Colors.BACKGROUND_LIGHT
        )
        
        # Leaderboard state
        self.leaderboard_difficulty = 'MEDIUM'
    
    def _create_buttons(self) -> None:
        """Create all game buttons"""
        center_x = GameConfig.WINDOW_WIDTH // 2
        
        # Main menu buttons
        self.start_button = Button(center_x - 100, 350, 200, 60, "START GAME", 
                                 self.fonts['medium'], self.audio_manager)
        self.leaderboard_button = Button(center_x - 120, 420, 240, 50, "LEADERBOARD", 
                                       self.fonts['small'], self.audio_manager)
        self.quit_button = Button(center_x - 80, 480, 160, 50, "QUIT", 
                                self.fonts['small'], self.audio_manager)
        
        # Difficulty buttons
        self.easy_button = DifficultyButton(center_x - 280, 300, 160, 80, 'EASY', 
                                          self.fonts['medium'], self.audio_manager)
        self.medium_button = DifficultyButton(center_x - 80, 300, 160, 80, 'MEDIUM', 
                                            self.fonts['medium'], self.audio_manager)
        self.hard_button = DifficultyButton(center_x + 120, 300, 160, 80, 'HARD', 
                                          self.fonts['medium'], self.audio_manager)
        
        # Set default selection
        self.medium_button.selected = True
        
        # Game over buttons
        self.play_again_button = Button(center_x - 120, 400, 240, 60, "PLAY AGAIN", 
                                      self.fonts['medium'], self.audio_manager)
        self.change_difficulty_button = Button(center_x - 140, 470, 280, 50, "CHANGE DIFFICULTY", 
                                             self.fonts['small'], self.audio_manager)
        
        # Universal buttons
        self.back_button = Button(50, GameConfig.WINDOW_HEIGHT - 80, 120, 50, "BACK", 
                                self.fonts['small'], self.audio_manager)
        self.audio_button = Button(GameConfig.WINDOW_WIDTH - 170, GameConfig.WINDOW_HEIGHT - 80, 
                                 120, 50, "AUDIO: ON", self.fonts['small'], self.audio_manager)
    
    def _start_new_game(self) -> None:
        """Initialize a new game"""
        self.snake = Snake(self.audio_manager)
        self.food = Food()
        self.score = 0
        self.state = GameState.PLAYING
        self.particle_system.clear()
        self.audio_manager.play_sound('game_start')
    
    def _select_difficulty(self, difficulty: str) -> None:
        """Select difficulty and update UI"""
        self.current_difficulty = difficulty
        
        # Update button selections
        self.easy_button.selected = (difficulty == 'EASY')
        self.medium_button.selected = (difficulty == 'MEDIUM')
        self.hard_button.selected = (difficulty == 'HARD')
    
    def _handle_events(self) -> bool:
        """Handle all input events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if not self._handle_keyboard_input(event.key):
                    return False
            
            # Handle button clicks
            if not self._handle_button_clicks(event):
                return False
        
        # Update button hover states
        self._update_button_hovers(mouse_pos)
        
        return True
    
    def _handle_keyboard_input(self, key: int) -> bool:
        """Handle keyboard input based on current state"""
        if self.state == GameState.MENU:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.state = GameState.DIFFICULTY_SELECT
            elif key == pygame.K_l:
                self.state = GameState.LEADERBOARD
            elif key == pygame.K_ESCAPE:
                return False
            elif key == pygame.K_m:
                self._toggle_audio()
        
        elif self.state == GameState.DIFFICULTY_SELECT:
            if key == pygame.K_1:
                self._select_difficulty('EASY')
            elif key == pygame.K_2:
                self._select_difficulty('MEDIUM')
            elif key == pygame.K_3:
                self._select_difficulty('HARD')
            elif key == pygame.K_SPACE or key == pygame.K_RETURN:
                self._start_new_game()
            elif key == pygame.K_ESCAPE:
                self.state = GameState.MENU
        
        elif self.state == GameState.PLAYING:
            if key in [pygame.K_UP, pygame.K_w]:
                self.snake.change_direction((0, -1))
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.snake.change_direction((0, 1))
            elif key in [pygame.K_LEFT, pygame.K_a]:
                self.snake.change_direction((-1, 0))
            elif key in [pygame.K_RIGHT, pygame.K_d]:
                self.snake.change_direction((1, 0))
            elif key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif key == pygame.K_m:
                self._toggle_audio()
        
        elif self.state == GameState.GAME_OVER:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self._start_new_game()
            elif key == pygame.K_d:
                self.state = GameState.DIFFICULTY_SELECT
            elif key == pygame.K_l:
                self.state = GameState.LEADERBOARD
            elif key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif key == pygame.K_m:
                self._toggle_audio()
        
        elif self.state == GameState.LEADERBOARD:
            if key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif key == pygame.K_1:
                self.leaderboard_difficulty = 'EASY'
            elif key == pygame.K_2:
                self.leaderboard_difficulty = 'MEDIUM'
            elif key == pygame.K_3:
                self.leaderboard_difficulty = 'HARD'
        
        return True
    
    def _handle_button_clicks(self, event: pygame.event.Event) -> bool:
        """Handle button click events"""
        if self.state == GameState.MENU:
            if self.start_button.handle_event(event):
                self.state = GameState.DIFFICULTY_SELECT
            elif self.leaderboard_button.handle_event(event):
                self.state = GameState.LEADERBOARD
            elif self.quit_button.handle_event(event):
                return False
            elif self.audio_button.handle_event(event):
                self._toggle_audio()
        
        elif self.state == GameState.DIFFICULTY_SELECT:
            if self.easy_button.handle_event(event):
                self._select_difficulty('EASY')
                self._start_new_game()
            elif self.medium_button.handle_event(event):
                self._select_difficulty('MEDIUM')
                self._start_new_game()
            elif self.hard_button.handle_event(event):
                self._select_difficulty('HARD')
                self._start_new_game()
            elif self.back_button.handle_event(event):
                self.state = GameState.MENU
            elif self.audio_button.handle_event(event):
                self._toggle_audio()
        
        elif self.state == GameState.GAME_OVER:
            if self.play_again_button.handle_event(event):
                self._start_new_game()
            elif self.change_difficulty_button.handle_event(event):
                self.state = GameState.DIFFICULTY_SELECT
            elif self.back_button.handle_event(event):
                self.state = GameState.MENU
            elif self.audio_button.handle_event(event):
                self._toggle_audio()
        
        elif self.state == GameState.LEADERBOARD:
            if self.back_button.handle_event(event):
                self.state = GameState.MENU
            elif self.audio_button.handle_event(event):
                self._toggle_audio()
        
        return True
    
    def _update_button_hovers(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover states for all relevant buttons"""
        buttons_by_state = {
            GameState.MENU: [self.start_button, self.leaderboard_button, self.quit_button, self.audio_button],
            GameState.DIFFICULTY_SELECT: [self.easy_button, self.medium_button, self.hard_button, 
                                        self.back_button, self.audio_button],
            GameState.GAME_OVER: [self.play_again_button, self.change_difficulty_button, 
                                self.back_button, self.audio_button],
            GameState.LEADERBOARD: [self.back_button, self.audio_button]
        }
        
        for button in buttons_by_state.get(self.state, []):
            button.update(mouse_pos)
    
    def _toggle_audio(self) -> None:
        """Toggle audio and update button text"""
        self.audio_manager.toggle()
        self.audio_button.text = "AUDIO: ON" if self.audio_manager.enabled else "AUDIO: OFF"
    
    def _update_game_logic(self) -> None:
        """Update game logic and state"""
        if self.state == GameState.PLAYING:
            # Move snake
            self.snake.move()
            self.food.update()
            
            # Check collision
            if self.snake.check_collision():
                self._handle_game_over()
                return
            
            # Check food consumption
            if self.snake.positions[0] == self.food.position:
                self._handle_food_eaten()
        
        # Update animations and particles
        self.ui.update_animations()
        self.particle_system.update()
        
        # Add background particles for menu states
        if self.state in [GameState.MENU, GameState.DIFFICULTY_SELECT, GameState.LEADERBOARD]:
            self.particle_system.add_background_particles()
    
    def _handle_game_over(self) -> None:
        """Handle game over logic"""
        self.state = GameState.GAME_OVER
        
        # Calculate final score
        config = DifficultyManager.get_config(self.current_difficulty)
        final_score = int(self.score * config.multiplier)
        
        # Check for high score
        if self.score_manager.is_high_score(self.current_difficulty, final_score):
            self.score_manager.add_score(self.current_difficulty, final_score)
            self.audio_manager.play_sound('high_score')
        else:
            self.audio_manager.play_sound('game_over')
        
        # Add explosion effect
        if self.snake and self.snake.positions:
            head_pos = self.snake.positions[0]
            screen_x = GameConfig.GAME_AREA_X + head_pos[0] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            screen_y = GameConfig.GAME_AREA_Y + head_pos[1] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
            self.particle_system.add_explosion(screen_x, screen_y, Colors.SNAKE_HEAD, 25)
    
    def _handle_food_eaten(self) -> None:
        """Handle food consumption"""
        self.snake.eat_food()
        self.score += 10
        
        # Add particle effect
        food_screen_x = GameConfig.GAME_AREA_X + self.food.position[0] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        food_screen_y = GameConfig.GAME_AREA_Y + self.food.position[1] * GameConfig.GRID_SIZE + GameConfig.GRID_SIZE // 2
        self.particle_system.add_food_effect(food_screen_x, food_screen_y)
        
        # Respawn food
        self.food.respawn(self.snake.positions)
    
    def _draw_menu(self) -> None:
        """Draw the main menu screen"""
        # Animated title
        title_text = "SNAKE ULTIMATE"
        glow_intensity = int(50 + 30 * math.sin(self.ui.title_glow * 0.1))
        
        # Main title
        title_surface = self.fonts['title'].render(title_text, True, Colors.ACCENT_GREEN)
        title_rect = title_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 200))
        
        # Glow effect
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        glow_color = (*Colors.ACCENT_GREEN, glow_intensity)
        glow_text = self.fonts['title'].render(title_text, True, glow_color)
        glow_surface.blit(glow_text, (20, 20))
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle = "FINAL EDITION"
        subtitle_surface = self.fonts['large'].render(subtitle, True, Colors.ACCENT_BLUE)
        subtitle_rect = subtitle_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 260))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Animated snake decoration
        snake_y = 300 + int(10 * math.sin(self.ui.menu_animation * 0.05))
        for i in range(6):
            x = GameConfig.WINDOW_WIDTH // 2 - 75 + i * 25
            color = Colors.SNAKE_HEAD if i == 0 else Colors.SNAKE_PRIMARY
            GraphicsUtils.draw_glowing_circle(self.screen, color, (x, snake_y), 8, 4)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.audio_button.draw(self.screen)
        
        # Instructions
        instructions = [
            "SPACE - Start Game  |  L - Leaderboard  |  M - Audio Toggle  |  ESC - Quit"
        ]
        for instruction in instructions:
            text = self.fonts['tiny'].render(instruction, True, Colors.TEXT_SECONDARY)
            rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT - 50))
            self.screen.blit(text, rect)
    
    def _draw_difficulty_select(self) -> None:
        """Draw difficulty selection screen"""
        # Title
        title = "SELECT DIFFICULTY"
        title_surface = self.fonts['large'].render(title, True, Colors.ACCENT_GREEN)
        title_rect = title_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle = "Choose your challenge level"
        subtitle_surface = self.fonts['medium'].render(subtitle, True, Colors.TEXT_SECONDARY)
        subtitle_rect = subtitle_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Difficulty buttons
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        
        # Current selection
        config = DifficultyManager.get_config(self.current_difficulty)
        selected_text = f"Selected: {self.current_difficulty}"
        selected_surface = self.fonts['medium'].render(selected_text, True, config.color)
        selected_rect = selected_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 450))
        self.screen.blit(selected_surface, selected_rect)
        
        # Instructions
        instructions = [
            "Click difficulty or press 1/2/3  |  SPACE - Start  |  ESC - Back"
        ]
        for instruction in instructions:
            text = self.fonts['small'].render(instruction, True, Colors.TEXT_SECONDARY)
            rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 500))
            self.screen.blit(text, rect)
        
        # Draw universal buttons
        self.back_button.draw(self.screen)
        self.audio_button.draw(self.screen)
    
    def _draw_leaderboard(self) -> None:
        """Draw leaderboard screen"""
        # Title
        title = "LEADERBOARD"
        title_surface = self.fonts['large'].render(title, True, Colors.ACCENT_GREEN)
        title_rect = title_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Difficulty tabs
        tab_width = 200
        tab_height = 50
        tab_y = 130
        
        difficulties = ['EASY', 'MEDIUM', 'HARD']
        for i, difficulty in enumerate(difficulties):
            x = GameConfig.WINDOW_WIDTH // 2 - 300 + i * 200
            config = DifficultyManager.get_config(difficulty)
            
            tab_rect = pygame.Rect(x, tab_y, tab_width, tab_height)
            
            # Tab appearance
            if difficulty == self.leaderboard_difficulty:
                tab_bg = GraphicsUtils.create_gradient_surface(tab_width, tab_height, 
                                                             config.color, tuple(max(0, c - 30) for c in config.color))
                self.screen.blit(tab_bg, tab_rect)
                pygame.draw.rect(self.screen, Colors.TEXT_PRIMARY, tab_rect, 3, border_radius=8)
            else:
                darker_color = tuple(c // 2 for c in config.color)
                tab_bg = GraphicsUtils.create_gradient_surface(tab_width, tab_height, 
                                                             darker_color, tuple(max(0, c - 30) for c in darker_color))
                self.screen.blit(tab_bg, tab_rect)
                pygame.draw.rect(self.screen, Colors.TEXT_SECONDARY, tab_rect, 1, border_radius=8)
            
            # Tab text
            tab_text = self.fonts['medium'].render(difficulty, True, Colors.TEXT_PRIMARY)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text, tab_text_rect)
            
            # Handle tab clicks
            mouse_pos = pygame.mouse.get_pos()
            if tab_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.leaderboard_difficulty = difficulty
        
        # Show scores
        scores = self.score_manager.get_top_scores(self.leaderboard_difficulty, 10)
        
        if scores:
            # Headers
            headers_y = 220
            headers = [("RANK", 200), ("SCORE", 400), ("DATE", 600)]
            for header, x in headers:
                header_text = self.fonts['medium'].render(header, True, Colors.TEXT_PRIMARY)
                self.screen.blit(header_text, (x, headers_y))
            
            # Scores
            for i, score_entry in enumerate(scores):
                y = 260 + i * 35
                rank_color = Colors.ACCENT_GREEN if i < 3 else Colors.TEXT_PRIMARY
                
                # Rank
                rank_text = self.fonts['small'].render(f"#{i+1}", True, rank_color)
                self.screen.blit(rank_text, (200, y))
                
                # Score
                score_text = self.fonts['small'].render(str(score_entry['score']), True, Colors.TEXT_PRIMARY)
                self.screen.blit(score_text, (400, y))
                
                # Date
                date_text = self.fonts['small'].render(score_entry['date'], True, Colors.TEXT_SECONDARY)
                self.screen.blit(date_text, (600, y))
                
                # Highlight top 3
                if i < 3:
                    highlight_rect = pygame.Rect(190, y - 5, GameConfig.WINDOW_WIDTH - 380, 30)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    highlight_surface.fill((*rank_color, 20))
                    self.screen.blit(highlight_surface, highlight_rect)
        else:
            no_scores_text = self.fonts['medium'].render("No scores yet! Start playing to set records!", 
                                                       True, Colors.TEXT_SECONDARY)
            no_scores_rect = no_scores_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 350))
            self.screen.blit(no_scores_text, no_scores_rect)
        
        # Instructions
        instructions = [
            "Click tabs or press 1/2/3 to switch difficulties  |  ESC - Back to menu"
        ]
        for instruction in instructions:
            text = self.fonts['small'].render(instruction, True, Colors.TEXT_SECONDARY)
            rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT - 50))
            self.screen.blit(text, rect)
        
        # Draw universal buttons
        self.back_button.draw(self.screen)
        self.audio_button.draw(self.screen)
    
    def _draw_game_over(self) -> None:
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over title
        game_over_text = self.fonts['title'].render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 200))
        
        # Glow effect
        glow_surface = pygame.Surface((game_over_rect.width + 20, game_over_rect.height + 20), pygame.SRCALPHA)
        glow_text = self.fonts['title'].render("GAME OVER", True, (255, 100, 100, 100))
        glow_surface.blit(glow_text, (10, 10))
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score breakdown
        config = DifficultyManager.get_config(self.current_difficulty)
        final_score = int(self.score * config.multiplier)
        
        score_info = [
            f"Difficulty: {self.current_difficulty}",
            f"Base Score: {self.score}",
            f"Multiplier: x{config.multiplier}",
            f"Final Score: {final_score}"
        ]
        
        y_offset = 280
        for i, info in enumerate(score_info):
            color = config.color if i == 0 else Colors.ACCENT_GREEN if i == 3 else Colors.TEXT_PRIMARY
            font = self.fonts['large'] if i == 3 else self.fonts['medium']
            
            text_surface = font.render(info, True, color)
            text_rect = text_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, y_offset))
            
            if i == 3:  # Final score background
                bg_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, 
                                    text_rect.width + 40, text_rect.height + 20)
                bg_surface = GraphicsUtils.create_gradient_surface(bg_rect.width, bg_rect.height,
                                                                 Colors.ACCENT_BLUE, tuple(c // 2 for c in Colors.ACCENT_BLUE))
                self.screen.blit(bg_surface, bg_rect)
                pygame.draw.rect(self.screen, Colors.TEXT_PRIMARY, bg_rect, 2, border_radius=10)
            
            self.screen.blit(text_surface, text_rect)
            y_offset += 40
        
        # High score notification
        if self.score_manager.is_high_score(self.current_difficulty, final_score):
            pulse = math.sin(self.ui.menu_animation * 0.2) * 0.1 + 1.0
            high_score_text = self.fonts['large'].render("NEW HIGH SCORE!", True, Colors.ACCENT_GREEN)
            scaled_surface = pygame.transform.scale(high_score_text, 
                                                  (int(high_score_text.get_width() * pulse), 
                                                   int(high_score_text.get_height() * pulse)))
            scaled_rect = scaled_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, y_offset + 20))
            self.screen.blit(scaled_surface, scaled_rect)
        
        # Draw buttons
        self.play_again_button.draw(self.screen)
        self.change_difficulty_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.audio_button.draw(self.screen)
        
        # Instructions
        instructions = [
            "SPACE - Play Again  |  D - Change Difficulty  |  L - Leaderboard  |  ESC - Menu"
        ]
        for instruction in instructions:
            text = self.fonts['tiny'].render(instruction, True, Colors.TEXT_SECONDARY)
            rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT - 30))
            self.screen.blit(text, rect)
    
    def _draw_game(self) -> None:
        """Draw the main game screen"""
        # Draw game area border and grid
        self.ui.draw_game_area_border(self.screen)
        
        # Draw game objects
        if self.snake:
            self.snake.draw(self.screen)
        if self.food:
            self.food.draw(self.screen)
        
        # Draw UI panels
        config = DifficultyManager.get_config(self.current_difficulty)
        self.ui.draw_score_panel(self.screen, self.score, self.current_difficulty, config.multiplier)
        self.ui.draw_high_score_panel(self.screen, self.score_manager)
        
        # Draw audio button
        self.audio_button.draw(self.screen)
        
        # Game title at top
        title_text = f"Snake Ultimate - {self.current_difficulty} Mode"
        title_surface = self.fonts['medium'].render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 30))
        self.screen.blit(title_surface, title_rect)
    
    def draw(self) -> None:
        """Main drawing method"""
        # Clear screen with background
        self.screen.blit(self.background, (0, 0))
        
        # Draw based on current state
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self._draw_difficulty_select()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.GAME_OVER:
            self._draw_game()  # Draw game in background
            self._draw_game_over()  # Draw overlay
        elif self.state == GameState.LEADERBOARD:
            self._draw_leaderboard()
        
        # Draw particles on top of everything
        self.particle_system.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        print("🐍 Snake Game Final - Ultimate Edition")
        print("=" * 60)
        print("🎯 FEATURES:")
        print("  • Professional visual effects and animations")
        print("  • Separated game area from UI elements")
        print("  • Advanced particle systems")
        print("  • Glowing snake with animated eyes")
        print("  • Sparkling food with effects")
        print("  • Three difficulty levels with score multipliers")
        print("  • Persistent high-score leaderboard")
        print("  • Professional UI with smooth transitions")
        print("  • Comprehensive audio system")
        print("\n🎮 CONTROLS:")
        print("  • Arrow Keys/WASD - Move snake")
        print("  • SPACE/ENTER - Start/Confirm")
        print("  • 1/2/3 - Quick difficulty selection")
        print("  • L - Leaderboard")
        print("  • M - Toggle audio")
        print("  • ESC - Back/Menu")
        print("\nStarting game...")
        
        running = True
        while running:
            # Handle events
            running = self._handle_events()
            
            # Update game logic
            self._update_game_logic()
            
            # Draw everything
            self.draw()
            
            # Control frame rate based on difficulty
            if self.state == GameState.PLAYING:
                config = DifficultyManager.get_config(self.current_difficulty)
                self.clock.tick(config.speed)
            else:
                self.clock.tick(60)  # 60 FPS for menus
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
