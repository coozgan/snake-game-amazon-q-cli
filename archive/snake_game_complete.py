import pygame
import random
import sys
import math
import os
import json
from datetime import datetime

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
GRID_SIZE = 25
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Modern color palette
BACKGROUND_DARK = (15, 15, 25)
BACKGROUND_LIGHT = (25, 25, 40)
SNAKE_PRIMARY = (50, 205, 50)
SNAKE_SECONDARY = (34, 139, 34)
SNAKE_HEAD = (0, 255, 127)
FOOD_PRIMARY = (255, 69, 0)
FOOD_SECONDARY = (255, 140, 0)
TEXT_COLOR = (220, 220, 220)
ACCENT_COLOR = (100, 149, 237)
GRID_COLOR = (40, 40, 55)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 149, 237)
TITLE_COLOR = (0, 255, 127)
DIFFICULTY_EASY = (50, 205, 50)
DIFFICULTY_MEDIUM = (255, 165, 0)
DIFFICULTY_HARD = (255, 69, 0)

# Game states
MENU = 0
DIFFICULTY_SELECT = 1
PLAYING = 2
GAME_OVER = 3
LEADERBOARD = 4

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'EASY': {'speed': 8, 'color': DIFFICULTY_EASY, 'multiplier': 1.0},
    'MEDIUM': {'speed': 12, 'color': DIFFICULTY_MEDIUM, 'multiplier': 1.5},
    'HARD': {'speed': 18, 'color': DIFFICULTY_HARD, 'multiplier': 2.0}
}

class ScoreManager:
    def __init__(self):
        self.scores_file = "high_scores.json"
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            else:
                return {'EASY': [], 'MEDIUM': [], 'HARD': []}
        except Exception as e:
            print(f"Error loading scores: {e}")
            return {'EASY': [], 'MEDIUM': [], 'HARD': []}
    
    def save_scores(self):
        """Save high scores to file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, difficulty, score, player_name="Player"):
        """Add a new score to the leaderboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        score_entry = {
            'score': score,
            'player': player_name,
            'date': timestamp
        }
        
        if difficulty not in self.scores:
            self.scores[difficulty] = []
        
        self.scores[difficulty].append(score_entry)
        self.scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 10 scores per difficulty
        self.scores[difficulty] = self.scores[difficulty][:10]
        
        self.save_scores()
        
        # Return rank (1-based)
        for i, entry in enumerate(self.scores[difficulty]):
            if entry == score_entry:
                return i + 1
        return len(self.scores[difficulty])
    
    def get_high_score(self, difficulty):
        """Get the highest score for a difficulty"""
        if difficulty in self.scores and self.scores[difficulty]:
            return self.scores[difficulty][0]['score']
        return 0
    
    def get_top_scores(self, difficulty, count=10):
        """Get top scores for a difficulty"""
        if difficulty in self.scores:
            return self.scores[difficulty][:count]
        return []
    
    def is_high_score(self, difficulty, score):
        """Check if score qualifies for leaderboard"""
        if difficulty not in self.scores:
            return True
        
        if len(self.scores[difficulty]) < 10:
            return True
        
        return score > self.scores[difficulty][-1]['score']

class AudioManager:
    def __init__(self):
        """Initialize audio manager with sound effects and music"""
        self.sounds = {}
        self.music_volume = 0.3
        self.sfx_volume = 0.7
        self.audio_enabled = True
        
        # Create audio directory if it doesn't exist
        self.audio_dir = "audio"
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        
        # Load sounds
        self.load_sounds()
        
        # Start background music
        self.start_background_music()
    
    def load_sounds(self):
        """Load all sound effects"""
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
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                except pygame.error as e:
                    print(f"✗ Could not load {filename}: {e}")
                    self.sounds[sound_name] = None
            else:
                self.sounds[sound_name] = None
    
    def start_background_music(self):
        """Start background music"""
        music_file = os.path.join(self.audio_dir, "background_music.ogg")
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"✗ Could not load background music: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.audio_enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def toggle_audio(self):
        """Toggle audio on/off"""
        self.audio_enabled = not self.audio_enabled
        if self.audio_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Create a gradient surface between two colors"""
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
    
    return surface

def draw_3d_rect(surface, color, rect, depth=3):
    """Draw a 3D-looking rectangle with shading"""
    pygame.draw.rect(surface, color, rect)
    
    highlight_color = tuple(min(255, c + 40) for c in color)
    pygame.draw.line(surface, highlight_color, 
                    (rect.left, rect.top), (rect.right - 1, rect.top), 2)
    pygame.draw.line(surface, highlight_color, 
                    (rect.left, rect.top), (rect.left, rect.bottom - 1), 2)
    
    shadow_color = tuple(max(0, c - 40) for c in color)
    pygame.draw.line(surface, shadow_color, 
                    (rect.left + 1, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
    pygame.draw.line(surface, shadow_color, 
                    (rect.right - 1, rect.top + 1), (rect.right - 1, rect.bottom - 1), 2)

def draw_glowing_circle(surface, color, center, radius, glow_radius=None):
    """Draw a glowing circle effect"""
    if glow_radius is None:
        glow_radius = radius + 10
    
    for i in range(glow_radius, radius, -2):
        alpha = int(255 * (glow_radius - i) / (glow_radius - radius))
        glow_color = (*color, alpha)
        glow_surface = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (i, i), i)
        surface.blit(glow_surface, (center[0] - i, center[1] - i), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    pygame.draw.circle(surface, color, center, radius)

class Button:
    def __init__(self, x, y, width, height, text, font, audio_manager, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.was_hovered = False
        self.animation_scale = 1.0
        self.glow_intensity = 0
        self.audio_manager = audio_manager
        self.selected = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.audio_manager.play_sound('button_click')
                return True
        return False
    
    def update(self, mouse_pos):
        self.was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and not self.was_hovered:
            self.audio_manager.play_sound('button_hover')
        
        if self.is_hovered or self.selected:
            self.animation_scale = min(1.05, self.animation_scale + 0.02)
            self.glow_intensity = min(50, self.glow_intensity + 2)
        else:
            self.animation_scale = max(1.0, self.animation_scale - 0.02)
            self.glow_intensity = max(0, self.glow_intensity - 2)
    
    def draw(self, surface):
        scale_offset = (self.rect.width * (self.animation_scale - 1)) / 2
        animated_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            self.rect.width * self.animation_scale,
            self.rect.height * self.animation_scale
        )
        
        if self.glow_intensity > 0:
            glow_surface = pygame.Surface((animated_rect.width + 20, animated_rect.height + 20), pygame.SRCALPHA)
            glow_color = (*self.hover_color, self.glow_intensity)
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, animated_rect.width, animated_rect.height), border_radius=10)
            surface.blit(glow_surface, (animated_rect.x - 10, animated_rect.y - 10))
        
        current_color = self.hover_color if (self.is_hovered or self.selected) else self.color
        button_gradient = create_gradient_surface(int(animated_rect.width), int(animated_rect.height), 
                                                current_color, tuple(max(0, c - 30) for c in current_color))
        surface.blit(button_gradient, animated_rect)
        
        pygame.draw.rect(surface, TEXT_COLOR, animated_rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=animated_rect.center)
        surface.blit(text_surface, text_rect)

class DifficultyButton(Button):
    def __init__(self, x, y, width, height, difficulty, font, audio_manager):
        color = DIFFICULTY_SETTINGS[difficulty]['color']
        hover_color = tuple(min(255, c + 30) for c in color)
        super().__init__(x, y, width, height, difficulty, font, audio_manager, color, hover_color)
        self.difficulty = difficulty
        self.speed = DIFFICULTY_SETTINGS[difficulty]['speed']
        self.multiplier = DIFFICULTY_SETTINGS[difficulty]['multiplier']
    
    def draw(self, surface):
        super().draw(surface)
        
        # Add difficulty indicator
        speed_text = f"Speed: {self.speed} FPS"
        multiplier_text = f"Score: x{self.multiplier}"
        
        speed_surface = pygame.font.Font(None, 24).render(speed_text, True, TEXT_COLOR)
        multiplier_surface = pygame.font.Font(None, 24).render(multiplier_text, True, TEXT_COLOR)
        
        speed_rect = speed_surface.get_rect(centerx=self.rect.centerx, y=self.rect.bottom + 5)
        multiplier_rect = multiplier_surface.get_rect(centerx=self.rect.centerx, y=self.rect.bottom + 25)
        
        surface.blit(speed_surface, speed_rect)
        surface.blit(multiplier_surface, multiplier_rect)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color, velocity=None):
        if velocity is None:
            velocity = (random.uniform(-2, 2), random.uniform(-2, 2))
        
        particle = {
            'x': x,
            'y': y,
            'vx': velocity[0],
            'vy': velocity[1],
            'life': 60,
            'max_life': 60,
            'color': color,
            'size': random.uniform(2, 5)
        }
        self.particles.append(particle)
    
    def add_background_particles(self):
        if random.random() < 0.1:
            x = random.randint(0, WINDOW_WIDTH)
            y = WINDOW_HEIGHT + 10
            color = random.choice([SNAKE_PRIMARY, FOOD_PRIMARY, ACCENT_COLOR])
            velocity = (random.uniform(-0.5, 0.5), random.uniform(-1, -0.3))
            self.add_particle(x, y, color, velocity)
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['size'] *= 0.99
            
            if particle['life'] <= 0 or particle['y'] < -10:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))

class Snake:
    def __init__(self, audio_manager):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.animation_offset = 0
        self.segment_animations = [0] * len(self.positions)
        self.audio_manager = audio_manager
    
    def move(self):
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.segment_animations.append(0)
        
        self.animation_offset = (self.animation_offset + 1) % 60
        for i in range(len(self.segment_animations)):
            self.segment_animations[i] = (self.segment_animations[i] + 1) % 60
    
    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            if new_direction != self.direction:
                self.audio_manager.play_sound('turn')
            self.direction = new_direction
    
    def check_collision(self):
        head_x, head_y = self.positions[0]
        
        if (head_x < 0 or head_x >= GRID_WIDTH or 
            head_y < 0 or head_y >= GRID_HEIGHT):
            return True
        
        if self.positions[0] in self.positions[1:]:
            return True
        
        return False
    
    def eat_food(self):
        self.grow = True
        self.audio_manager.play_sound('eat')
    
    def draw(self, screen):
        for i, position in enumerate(self.positions):
            x = position[0] * GRID_SIZE + 2
            y = position[1] * GRID_SIZE + 2
            size = GRID_SIZE - 4
            
            pulse = math.sin(self.segment_animations[i] * 0.2) * 2
            animated_size = size + pulse
            offset = (size - animated_size) / 2
            
            rect = pygame.Rect(x + offset, y + offset, animated_size, animated_size)
            
            if i == 0:  # Head
                center = (int(rect.centerx), int(rect.centery))
                draw_glowing_circle(screen, SNAKE_HEAD, center, int(animated_size // 2))
                
                if self.direction == RIGHT:
                    eye1 = (center[0] + 3, center[1] - 3)
                    eye2 = (center[0] + 3, center[1] + 3)
                elif self.direction == LEFT:
                    eye1 = (center[0] - 3, center[1] - 3)
                    eye2 = (center[0] - 3, center[1] + 3)
                elif self.direction == UP:
                    eye1 = (center[0] - 3, center[1] - 3)
                    eye2 = (center[0] + 3, center[1] - 3)
                else:  # DOWN
                    eye1 = (center[0] - 3, center[1] + 3)
                    eye2 = (center[0] + 3, center[1] + 3)
                
                pygame.draw.circle(screen, (255, 255, 255), eye1, 2)
                pygame.draw.circle(screen, (255, 255, 255), eye2, 2)
                pygame.draw.circle(screen, (0, 0, 0), eye1, 1)
                pygame.draw.circle(screen, (0, 0, 0), eye2, 1)
            else:  # Body
                segment_color = SNAKE_PRIMARY if i % 2 == 0 else SNAKE_SECONDARY
                draw_3d_rect(screen, segment_color, rect, depth=4)
                
                inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
                lighter_color = tuple(min(255, c + 20) for c in segment_color)
                pygame.draw.rect(screen, lighter_color, inner_rect)

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.animation = 0
        self.pulse_scale = 1.0
    
    def generate_position(self):
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake_positions):
        while True:
            new_position = self.generate_position()
            if new_position not in snake_positions:
                self.position = new_position
                break
    
    def update(self):
        self.animation += 1
        self.pulse_scale = 1.0 + math.sin(self.animation * 0.15) * 0.2
    
    def draw(self, screen):
        x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        
        base_radius = (GRID_SIZE // 2 - 2)
        radius = int(base_radius * self.pulse_scale)
        
        draw_glowing_circle(screen, FOOD_PRIMARY, (x, y), radius, radius + 8)
        
        sparkle_offset = math.sin(self.animation * 0.3) * 3
        sparkle_pos = (x + int(sparkle_offset), y - int(sparkle_offset))
        pygame.draw.circle(screen, (255, 255, 255), sparkle_pos, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game Complete - Ultimate Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize managers
        self.audio_manager = AudioManager()
        self.score_manager = ScoreManager()
        
        # Game state
        self.state = MENU
        self.snake = None
        self.food = None
        self.score = 0
        self.current_difficulty = 'MEDIUM'
        self.game_speed = DIFFICULTY_SETTINGS[self.current_difficulty]['speed']
        self.score_multiplier = DIFFICULTY_SETTINGS[self.current_difficulty]['multiplier']
        
        # Fonts
        self.title_font = pygame.font.Font(None, 84)
        self.large_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        
        # Particles
        self.particles = ParticleSystem()
        
        # Create buttons
        self.create_buttons()
        
        # Background
        self.background = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT, 
                                                BACKGROUND_DARK, BACKGROUND_LIGHT, True)
        
        # Add grid pattern
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Animation variables
        self.title_glow = 0
        self.menu_animation = 0
        self.leaderboard_scroll = 0
    
    def create_buttons(self):
        """Create all game buttons"""
        # Main menu buttons
        self.start_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30, 200, 60, 
                                 "START GAME", self.font, self.audio_manager)
        self.leaderboard_button = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 100, 240, 50, 
                                       "LEADERBOARD", self.medium_font, self.audio_manager)
        self.quit_button = Button(WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 + 160, 160, 50, 
                                "QUIT", self.medium_font, self.audio_manager)
        
        # Difficulty selection buttons
        self.easy_button = DifficultyButton(WINDOW_WIDTH//2 - 300, WINDOW_HEIGHT//2 - 50, 180, 80, 
                                          'EASY', self.font, self.audio_manager)
        self.medium_button = DifficultyButton(WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 50, 180, 80, 
                                            'MEDIUM', self.font, self.audio_manager)
        self.hard_button = DifficultyButton(WINDOW_WIDTH//2 + 120, WINDOW_HEIGHT//2 - 50, 180, 80, 
                                          'HARD', self.font, self.audio_manager)
        
        # Set default selection
        self.medium_button.selected = True
        
        # Game over buttons
        self.play_again_button = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 20, 240, 60, 
                                      "PLAY AGAIN", self.font, self.audio_manager)
        self.change_difficulty_button = Button(WINDOW_WIDTH//2 - 140, WINDOW_HEIGHT//2 + 90, 280, 50, 
                                             "CHANGE DIFFICULTY", self.medium_font, self.audio_manager)
        
        # Universal buttons
        self.back_button = Button(50, WINDOW_HEIGHT - 80, 120, 50, 
                                "BACK", self.medium_font, self.audio_manager)
        self.audio_button = Button(WINDOW_WIDTH - 170, WINDOW_HEIGHT - 80, 120, 50, 
                                 "AUDIO: ON", self.medium_font, self.audio_manager)
    
    def start_new_game(self):
        """Start a new game with current difficulty"""
        self.snake = Snake(self.audio_manager)
        self.food = Food()
        self.score = 0
        self.state = PLAYING
        self.particles = ParticleSystem()
        self.audio_manager.play_sound('game_start')
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = DIFFICULTY_SELECT
                    elif event.key == pygame.K_l:
                        self.state = LEADERBOARD
                    elif event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_m:
                        self.toggle_audio()
                
                elif self.state == DIFFICULTY_SELECT:
                    if event.key == pygame.K_1:
                        self.select_difficulty('EASY')
                    elif event.key == pygame.K_2:
                        self.select_difficulty('MEDIUM')
                    elif event.key == pygame.K_3:
                        self.select_difficulty('HARD')
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
                
                elif self.state == PLAYING:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
                    elif event.key == pygame.K_m:
                        self.toggle_audio()
                
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif event.key == pygame.K_d:
                        self.state = DIFFICULTY_SELECT
                    elif event.key == pygame.K_l:
                        self.state = LEADERBOARD
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
                    elif event.key == pygame.K_m:
                        self.toggle_audio()
                
                elif self.state == LEADERBOARD:
                    if event.key == pygame.K_ESCAPE:
                        self.state = MENU
                    elif event.key == pygame.K_UP:
                        self.leaderboard_scroll = max(0, self.leaderboard_scroll - 1)
                    elif event.key == pygame.K_DOWN:
                        self.leaderboard_scroll = min(9, self.leaderboard_scroll + 1)
            
            # Handle button clicks
            self.handle_button_clicks(event)
        
        # Update button hover states
        self.update_button_hovers(mouse_pos)
        
        return True
    
    def handle_button_clicks(self, event):
        """Handle all button click events"""
        if self.state == MENU:
            if self.start_button.handle_event(event):
                self.state = DIFFICULTY_SELECT
            elif self.leaderboard_button.handle_event(event):
                self.state = LEADERBOARD
            elif self.quit_button.handle_event(event):
                return False
            elif self.audio_button.handle_event(event):
                self.toggle_audio()
        
        elif self.state == DIFFICULTY_SELECT:
            if self.easy_button.handle_event(event):
                self.select_difficulty('EASY')
                self.start_new_game()
            elif self.medium_button.handle_event(event):
                self.select_difficulty('MEDIUM')
                self.start_new_game()
            elif self.hard_button.handle_event(event):
                self.select_difficulty('HARD')
                self.start_new_game()
            elif self.back_button.handle_event(event):
                self.state = MENU
            elif self.audio_button.handle_event(event):
                self.toggle_audio()
        
        elif self.state == GAME_OVER:
            if self.play_again_button.handle_event(event):
                self.start_new_game()
            elif self.change_difficulty_button.handle_event(event):
                self.state = DIFFICULTY_SELECT
            elif self.back_button.handle_event(event):
                self.state = MENU
            elif self.audio_button.handle_event(event):
                self.toggle_audio()
        
        elif self.state == LEADERBOARD:
            if self.back_button.handle_event(event):
                self.state = MENU
            elif self.audio_button.handle_event(event):
                self.toggle_audio()
    
    def update_button_hovers(self, mouse_pos):
        """Update hover states for all buttons"""
        if self.state == MENU:
            self.start_button.update(mouse_pos)
            self.leaderboard_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
            self.audio_button.update(mouse_pos)
        
        elif self.state == DIFFICULTY_SELECT:
            self.easy_button.update(mouse_pos)
            self.medium_button.update(mouse_pos)
            self.hard_button.update(mouse_pos)
            self.back_button.update(mouse_pos)
            self.audio_button.update(mouse_pos)
        
        elif self.state == GAME_OVER:
            self.play_again_button.update(mouse_pos)
            self.change_difficulty_button.update(mouse_pos)
            self.back_button.update(mouse_pos)
            self.audio_button.update(mouse_pos)
        
        elif self.state == LEADERBOARD:
            self.back_button.update(mouse_pos)
            self.audio_button.update(mouse_pos)
    
    def select_difficulty(self, difficulty):
        """Select a difficulty level"""
        self.current_difficulty = difficulty
        self.game_speed = DIFFICULTY_SETTINGS[difficulty]['speed']
        self.score_multiplier = DIFFICULTY_SETTINGS[difficulty]['multiplier']
        
        # Update button selections
        self.easy_button.selected = (difficulty == 'EASY')
        self.medium_button.selected = (difficulty == 'MEDIUM')
        self.hard_button.selected = (difficulty == 'HARD')
    
    def toggle_audio(self):
        """Toggle audio on/off"""
        self.audio_manager.toggle_audio()
        self.audio_button.text = "AUDIO: ON" if self.audio_manager.audio_enabled else "AUDIO: OFF"
    
    def update(self):
        """Update game state"""
        self.title_glow = (self.title_glow + 1) % 120
        self.menu_animation += 1
        
        if self.state == MENU or self.state == DIFFICULTY_SELECT or self.state == LEADERBOARD:
            self.particles.add_background_particles()
        
        elif self.state == PLAYING:
            self.snake.move()
            self.food.update()
            
            if self.snake.check_collision():
                self.state = GAME_OVER
                
                # Calculate final score with multiplier
                final_score = int(self.score * self.score_multiplier)
                
                # Check if it's a high score
                if self.score_manager.is_high_score(self.current_difficulty, final_score):
                    rank = self.score_manager.add_score(self.current_difficulty, final_score)
                    self.audio_manager.play_sound('high_score')
                else:
                    self.audio_manager.play_sound('game_over')
                
                # Add explosion particles
                head_pos = self.snake.positions[0]
                x = head_pos[0] * GRID_SIZE + GRID_SIZE // 2
                y = head_pos[1] * GRID_SIZE + GRID_SIZE // 2
                for _ in range(30):
                    self.particles.add_particle(x, y, SNAKE_HEAD)
                return
            
            if self.snake.positions[0] == self.food.position:
                self.snake.eat_food()
                self.score += 10
                
                # Add celebration particles
                food_x = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                food_y = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                for _ in range(15):
                    self.particles.add_particle(food_x, food_y, FOOD_PRIMARY)
                
                self.food.respawn(self.snake.positions)
        
        self.particles.update()
    
    def draw_menu(self):
        """Draw the main menu"""
        # Animated title
        title_text = "SNAKE"
        subtitle_text = "COMPLETE"
        
        glow_intensity = int(50 + 30 * math.sin(self.title_glow * 0.1))
        title_color = (*TITLE_COLOR, glow_intensity)
        
        title_surface = self.title_font.render(title_text, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 180))
        
        # Glow effect
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        glow_text = self.title_font.render(title_text, True, title_color)
        glow_surface.blit(glow_text, (20, 20))
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_surface = self.large_font.render(subtitle_text, True, ACCENT_COLOR)
        subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Animated snake decoration
        snake_y = WINDOW_HEIGHT//2 - 60 + int(10 * math.sin(self.menu_animation * 0.05))
        for i in range(5):
            x = WINDOW_WIDTH//2 - 60 + i * 25
            color = SNAKE_HEAD if i == 0 else SNAKE_PRIMARY
            pygame.draw.circle(self.screen, color, (x, snake_y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, snake_y), 10, 2)
        
        # High scores preview
        high_score_easy = self.score_manager.get_high_score('EASY')
        high_score_medium = self.score_manager.get_high_score('MEDIUM')
        high_score_hard = self.score_manager.get_high_score('HARD')
        
        if any([high_score_easy, high_score_medium, high_score_hard]):
            high_scores_text = self.medium_font.render("HIGH SCORES", True, ACCENT_COLOR)
            high_scores_rect = high_scores_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
            self.screen.blit(high_scores_text, high_scores_rect)
            
            y_offset = 10
            for difficulty, score in [('EASY', high_score_easy), ('MEDIUM', high_score_medium), ('HARD', high_score_hard)]:
                if score > 0:
                    color = DIFFICULTY_SETTINGS[difficulty]['color']
                    score_text = self.small_font.render(f"{difficulty}: {int(score)}", True, color)
                    score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + y_offset))
                    self.screen.blit(score_text, score_rect)
                    y_offset += 25
        
        # Instructions
        instructions = [
            "SPACE - Start Game  |  L - Leaderboard  |  M - Audio Toggle"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 120))
            self.screen.blit(text, rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.audio_button.draw(self.screen)
    
    def draw_difficulty_select(self):
        """Draw the difficulty selection screen"""
        # Title
        title_text = "SELECT DIFFICULTY"
        title_surface = self.large_font.render(title_text, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 200))
        self.screen.blit(title_surface, title_rect)
        
        # Difficulty buttons
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        
        # Instructions
        instructions = [
            "Click a difficulty or press 1/2/3",
            "SPACE - Start with selected difficulty",
            "ESC - Back to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 120 + i * 30))
            self.screen.blit(text, rect)
        
        # Current selection indicator
        selected_text = f"Selected: {self.current_difficulty}"
        selected_surface = self.medium_font.render(selected_text, True, DIFFICULTY_SETTINGS[self.current_difficulty]['color'])
        selected_rect = selected_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
        self.screen.blit(selected_surface, selected_rect)
        
        # Draw universal buttons
        self.back_button.draw(self.screen)
        self.audio_button.draw(self.screen)
    
    def draw_leaderboard(self):
        """Draw the leaderboard screen"""
        # Title
        title_text = "LEADERBOARD"
        title_surface = self.large_font.render(title_text, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Difficulty tabs
        tab_width = 200
        tab_height = 50
        tab_y = 130
        
        difficulties = ['EASY', 'MEDIUM', 'HARD']
        selected_difficulty = difficulties[self.leaderboard_scroll % 3] if hasattr(self, 'leaderboard_difficulty') else 'MEDIUM'
        
        for i, difficulty in enumerate(difficulties):
            x = WINDOW_WIDTH//2 - 300 + i * 200
            color = DIFFICULTY_SETTINGS[difficulty]['color']
            
            tab_rect = pygame.Rect(x, tab_y, tab_width, tab_height)
            
            if difficulty == selected_difficulty:
                # Selected tab
                tab_gradient = create_gradient_surface(tab_width, tab_height, color, tuple(max(0, c - 30) for c in color))
                self.screen.blit(tab_gradient, tab_rect)
                pygame.draw.rect(self.screen, TEXT_COLOR, tab_rect, 3, border_radius=8)
            else:
                # Unselected tab
                darker_color = tuple(c // 2 for c in color)
                tab_gradient = create_gradient_surface(tab_width, tab_height, darker_color, tuple(max(0, c - 30) for c in darker_color))
                self.screen.blit(tab_gradient, tab_rect)
                pygame.draw.rect(self.screen, TEXT_COLOR, tab_rect, 1, border_radius=8)
            
            # Tab text
            tab_text = self.medium_font.render(difficulty, True, TEXT_COLOR)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text, tab_text_rect)
        
        # Show scores for selected difficulty
        if not hasattr(self, 'leaderboard_difficulty'):
            self.leaderboard_difficulty = 'MEDIUM'
        
        scores = self.score_manager.get_top_scores(self.leaderboard_difficulty, 10)
        
        if scores:
            # Headers
            headers_y = 220
            rank_text = self.medium_font.render("RANK", True, TEXT_COLOR)
            score_text = self.medium_font.render("SCORE", True, TEXT_COLOR)
            date_text = self.medium_font.render("DATE", True, TEXT_COLOR)
            
            self.screen.blit(rank_text, (150, headers_y))
            self.screen.blit(score_text, (300, headers_y))
            self.screen.blit(date_text, (500, headers_y))
            
            # Scores
            for i, score_entry in enumerate(scores):
                y = 260 + i * 35
                rank_color = TITLE_COLOR if i < 3 else TEXT_COLOR
                
                rank_surface = self.small_font.render(f"#{i+1}", True, rank_color)
                score_surface = self.small_font.render(str(score_entry['score']), True, TEXT_COLOR)
                date_surface = self.small_font.render(score_entry['date'], True, TEXT_COLOR)
                
                self.screen.blit(rank_surface, (150, y))
                self.screen.blit(score_surface, (300, y))
                self.screen.blit(date_surface, (500, y))
                
                # Highlight top 3
                if i < 3:
                    highlight_rect = pygame.Rect(140, y - 5, WINDOW_WIDTH - 280, 30)
                    highlight_color = (*rank_color, 30)
                    highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                    highlight_surface.fill(highlight_color)
                    self.screen.blit(highlight_surface, highlight_rect)
        else:
            no_scores_text = self.medium_font.render("No scores yet! Start playing to set records!", True, TEXT_COLOR)
            no_scores_rect = no_scores_text.get_rect(center=(WINDOW_WIDTH//2, 350))
            self.screen.blit(no_scores_text, no_scores_rect)
        
        # Instructions
        instructions = [
            "Click tabs or use arrow keys to switch difficulties",
            "ESC - Back to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100 + i * 25))
            self.screen.blit(text, rect)
        
        # Handle tab clicks
        mouse_pos = pygame.mouse.get_pos()
        for i, difficulty in enumerate(difficulties):
            x = WINDOW_WIDTH//2 - 300 + i * 200
            tab_rect = pygame.Rect(x, tab_y, tab_width, tab_height)
            if tab_rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    self.leaderboard_difficulty = difficulty
        
        # Draw universal buttons
        self.back_button.draw(self.screen)
        self.audio_button.draw(self.screen)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over title
        game_over_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 150))
        
        # Glow effect
        glow_surface = pygame.Surface((game_over_rect.width + 20, game_over_rect.height + 20), pygame.SRCALPHA)
        glow_text = self.title_font.render("GAME OVER", True, (255, 100, 100, 100))
        glow_surface.blit(glow_text, (10, 10))
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        self.screen.blit(game_over_text, game_over_rect)
        
        # Difficulty and score display
        difficulty_text = f"Difficulty: {self.current_difficulty}"
        base_score_text = f"Base Score: {self.score}"
        multiplier_text = f"Multiplier: x{self.score_multiplier}"
        final_score = int(self.score * self.score_multiplier)
        final_score_text = f"Final Score: {final_score}"
        
        difficulty_surface = self.medium_font.render(difficulty_text, True, DIFFICULTY_SETTINGS[self.current_difficulty]['color'])
        base_score_surface = self.medium_font.render(base_score_text, True, TEXT_COLOR)
        multiplier_surface = self.medium_font.render(multiplier_text, True, ACCENT_COLOR)
        final_score_surface = self.large_font.render(final_score_text, True, TITLE_COLOR)
        
        difficulty_rect = difficulty_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80))
        base_score_rect = base_score_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        multiplier_rect = multiplier_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
        final_score_rect = final_score_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        
        # Score background
        score_bg_rect = pygame.Rect(final_score_rect.x - 20, final_score_rect.y - 10, 
                                   final_score_rect.width + 40, final_score_rect.height + 20)
        score_bg = create_gradient_surface(score_bg_rect.width, score_bg_rect.height, 
                                         ACCENT_COLOR, (ACCENT_COLOR[0]//2, ACCENT_COLOR[1]//2, ACCENT_COLOR[2]//2))
        self.screen.blit(score_bg, score_bg_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, score_bg_rect, 2, border_radius=10)
        
        self.screen.blit(difficulty_surface, difficulty_rect)
        self.screen.blit(base_score_surface, base_score_rect)
        self.screen.blit(multiplier_surface, multiplier_rect)
        self.screen.blit(final_score_surface, final_score_rect)
        
        # High score check
        if self.score_manager.is_high_score(self.current_difficulty, final_score):
            new_high_text = self.font.render("NEW HIGH SCORE!", True, TITLE_COLOR)
            new_high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
            
            # Pulsing effect
            pulse = math.sin(self.menu_animation * 0.2) * 0.1 + 1.0
            scaled_surface = pygame.transform.scale(new_high_text, 
                                                  (int(new_high_text.get_width() * pulse), 
                                                   int(new_high_text.get_height() * pulse)))
            scaled_rect = scaled_surface.get_rect(center=new_high_rect.center)
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
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
            self.screen.blit(text, rect)
    
    def draw(self):
        """Main draw method"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.state == MENU:
            self.draw_menu()
        
        elif self.state == DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        
        elif self.state == PLAYING:
            # Draw game objects
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # Draw HUD
            score_text = f"SCORE: {self.score}"
            difficulty_text = f"DIFFICULTY: {self.current_difficulty}"
            multiplier_text = f"MULTIPLIER: x{self.score_multiplier}"
            
            score_surface = self.font.render(score_text, True, TEXT_COLOR)
            difficulty_surface = self.small_font.render(difficulty_text, True, DIFFICULTY_SETTINGS[self.current_difficulty]['color'])
            multiplier_surface = self.small_font.render(multiplier_text, True, ACCENT_COLOR)
            
            # Score background
            score_rect = pygame.Rect(20, 20, score_surface.get_width() + 20, score_surface.get_height() + 10)
            score_bg = create_gradient_surface(score_rect.width, score_rect.height, 
                                             ACCENT_COLOR, (ACCENT_COLOR[0]//2, ACCENT_COLOR[1]//2, ACCENT_COLOR[2]//2))
            self.screen.blit(score_bg, score_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, score_rect, 2)
            self.screen.blit(score_surface, (score_rect.x + 10, score_rect.y + 5))
            
            # Difficulty and multiplier info
            self.screen.blit(difficulty_surface, (20, 70))
            self.screen.blit(multiplier_surface, (20, 95))
            
            # Audio button
            self.audio_button.draw(self.screen)
        
        elif self.state == GAME_OVER:
            # Still draw the game in background
            if self.snake:
                self.snake.draw(self.screen)
            if self.food:
                self.food.draw(self.screen)
            
            self.draw_game_over()
        
        elif self.state == LEADERBOARD:
            self.draw_leaderboard()
        
        # Draw particles
        self.particles.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.game_speed)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("🐍 Snake Game Complete - Ultimate Edition")
    print("=" * 60)
    print("🎯 NEW FEATURES:")
    print("  • Three difficulty levels (Easy/Medium/Hard)")
    print("  • Persistent high-score leaderboard")
    print("  • Score multipliers based on difficulty")
    print("  • Professional difficulty selection UI")
    print("  • Comprehensive leaderboard with rankings")
    print("  • Session-persistent score tracking")
    print("\n🎮 Controls:")
    print("  • SPACE/ENTER - Start game or confirm")
    print("  • Arrow Keys/WASD - Move snake")
    print("  • 1/2/3 - Quick difficulty selection")
    print("  • L - View leaderboard")
    print("  • M - Toggle audio")
    print("  • ESC - Back/Menu")
    print("\n🏆 Difficulty Levels:")
    print("  • EASY: 8 FPS, x1.0 score multiplier")
    print("  • MEDIUM: 12 FPS, x1.5 score multiplier")
    print("  • HARD: 18 FPS, x2.0 score multiplier")
    print("\n📊 High Scores:")
    print("  • Top 10 scores saved per difficulty")
    print("  • Automatic score tracking")
    print("  • Persistent between sessions")
    print("  • Professional leaderboard display")
    print("\nStarting Snake Game Complete...")
    
    game = Game()
    game.run()
