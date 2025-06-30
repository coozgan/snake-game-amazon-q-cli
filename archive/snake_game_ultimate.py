import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

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

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

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
    def __init__(self, x, y, width, height, text, font, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.animation_scale = 1.0
        self.glow_intensity = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
    
    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Smooth animation
        if self.is_hovered:
            self.animation_scale = min(1.05, self.animation_scale + 0.02)
            self.glow_intensity = min(50, self.glow_intensity + 2)
        else:
            self.animation_scale = max(1.0, self.animation_scale - 0.02)
            self.glow_intensity = max(0, self.glow_intensity - 2)
    
    def draw(self, surface):
        # Calculate animated rect
        scale_offset = (self.rect.width * (self.animation_scale - 1)) / 2
        animated_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            self.rect.width * self.animation_scale,
            self.rect.height * self.animation_scale
        )
        
        # Draw glow effect
        if self.glow_intensity > 0:
            glow_surface = pygame.Surface((animated_rect.width + 20, animated_rect.height + 20), pygame.SRCALPHA)
            glow_color = (*self.hover_color, self.glow_intensity)
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, animated_rect.width, animated_rect.height), border_radius=10)
            surface.blit(glow_surface, (animated_rect.x - 10, animated_rect.y - 10))
        
        # Draw button with gradient
        current_color = self.hover_color if self.is_hovered else self.color
        button_gradient = create_gradient_surface(int(animated_rect.width), int(animated_rect.height), 
                                                current_color, tuple(max(0, c - 30) for c in current_color))
        surface.blit(button_gradient, animated_rect)
        
        # Draw 3D border
        pygame.draw.rect(surface, TEXT_COLOR, animated_rect, 2, border_radius=8)
        
        # Draw text
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=animated_rect.center)
        surface.blit(text_surface, text_rect)

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
        """Add floating background particles for menu"""
        if random.random() < 0.1:  # 10% chance each frame
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
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.animation_offset = 0
        self.segment_animations = [0] * len(self.positions)
    
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
                
                eye_offset = 6
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
        pygame.display.set_caption("Snake Game Ultimate - Modern Edition")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = MENU
        self.snake = None
        self.food = None
        self.score = 0
        self.high_score = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 84)
        self.large_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        # Particles
        self.particles = ParticleSystem()
        
        # Buttons
        self.start_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 50, 200, 60, 
                                 "START GAME", self.font)
        self.play_again_button = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 20, 240, 60, 
                                      "PLAY AGAIN", self.font)
        self.quit_button = Button(WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 + 100, 160, 50, 
                                "QUIT", self.small_font)
        
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
    
    def start_new_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.state = PLAYING
        self.particles = ParticleSystem()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                
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
                
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = MENU
            
            # Handle button clicks
            if self.state == MENU:
                if self.start_button.handle_event(event):
                    self.start_new_game()
                elif self.quit_button.handle_event(event):
                    return False
            
            elif self.state == GAME_OVER:
                if self.play_again_button.handle_event(event):
                    self.start_new_game()
                elif self.quit_button.handle_event(event):
                    self.state = MENU
        
        # Update button hover states
        if self.state == MENU:
            self.start_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
        elif self.state == GAME_OVER:
            self.play_again_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
        
        return True
    
    def update(self):
        # Update animations
        self.title_glow = (self.title_glow + 1) % 120
        self.menu_animation += 1
        
        if self.state == MENU:
            self.particles.add_background_particles()
        
        elif self.state == PLAYING:
            self.snake.move()
            self.food.update()
            
            if self.snake.check_collision():
                self.state = GAME_OVER
                if self.score > self.high_score:
                    self.high_score = self.score
                
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
        # Draw animated title
        title_text = "SNAKE"
        subtitle_text = "ULTIMATE"
        
        # Animated glow effect for title
        glow_intensity = int(50 + 30 * math.sin(self.title_glow * 0.1))
        title_color = (*TITLE_COLOR, glow_intensity)
        
        # Main title with glow
        title_surface = self.title_font.render(title_text, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 150))
        
        # Create glow effect
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        glow_text = self.title_font.render(title_text, True, title_color)
        glow_surface.blit(glow_text, (20, 20))
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_surface = self.large_font.render(subtitle_text, True, ACCENT_COLOR)
        subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 90))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Animated snake decoration
        snake_y = WINDOW_HEIGHT//2 - 30 + int(10 * math.sin(self.menu_animation * 0.05))
        for i in range(5):
            x = WINDOW_WIDTH//2 - 60 + i * 25
            color = SNAKE_HEAD if i == 0 else SNAKE_PRIMARY
            pygame.draw.circle(self.screen, color, (x, snake_y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, snake_y), 10, 2)
        
        # Instructions
        instructions = [
            "Use ARROW KEYS or WASD to move",
            "Eat food to grow and score points",
            "Avoid walls and your own tail"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 180 + i * 30))
            self.screen.blit(text, rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # High score
        if self.high_score > 0:
            high_score_text = self.font.render(f"HIGH SCORE: {self.high_score}", True, ACCENT_COLOR)
            high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH//2, 50))
            self.screen.blit(high_score_text, high_score_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over title with glow
        game_over_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        
        # Glow effect
        glow_surface = pygame.Surface((game_over_rect.width + 20, game_over_rect.height + 20), pygame.SRCALPHA)
        glow_text = self.title_font.render("GAME OVER", True, (255, 100, 100, 100))
        glow_surface.blit(glow_text, (10, 10))
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score display
        score_text = self.large_font.render(f"FINAL SCORE: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        
        # Score background
        score_bg_rect = pygame.Rect(score_rect.x - 20, score_rect.y - 10, 
                                   score_rect.width + 40, score_rect.height + 20)
        score_bg = create_gradient_surface(score_bg_rect.width, score_bg_rect.height, 
                                         ACCENT_COLOR, (ACCENT_COLOR[0]//2, ACCENT_COLOR[1]//2, ACCENT_COLOR[2]//2))
        self.screen.blit(score_bg, score_bg_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, score_bg_rect, 2, border_radius=10)
        self.screen.blit(score_text, score_rect)
        
        # New high score message
        if self.score == self.high_score and self.high_score > 0:
            new_high_text = self.font.render("NEW HIGH SCORE!", True, TITLE_COLOR)
            new_high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 10))
            self.screen.blit(new_high_text, new_high_rect)
        
        # Draw buttons
        self.play_again_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # Instructions
        instruction_text = self.small_font.render("Press SPACE to play again or ESC for menu", True, TEXT_COLOR)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 180))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.state == MENU:
            self.draw_menu()
        
        elif self.state == PLAYING:
            # Draw game objects
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            score_rect = pygame.Rect(20, 20, score_text.get_width() + 20, score_text.get_height() + 10)
            
            score_bg = create_gradient_surface(score_rect.width, score_rect.height, 
                                             ACCENT_COLOR, (ACCENT_COLOR[0]//2, ACCENT_COLOR[1]//2, ACCENT_COLOR[2]//2))
            self.screen.blit(score_bg, score_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, score_rect, 2)
            self.screen.blit(score_text, (score_rect.x + 10, score_rect.y + 5))
        
        elif self.state == GAME_OVER:
            # Still draw the game in background
            if self.snake:
                self.snake.draw(self.screen)
            if self.food:
                self.food.draw(self.screen)
            
            self.draw_game_over()
        
        # Draw particles
        self.particles.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(12)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("🐍 Snake Game Ultimate - Modern Edition")
    print("=" * 50)
    print("✨ NEW FEATURES:")
    print("  • Stylish animated start screen")
    print("  • Professional game over screen")
    print("  • Interactive buttons with hover effects")
    print("  • High score tracking")
    print("  • Floating background particles")
    print("  • Smooth screen transitions")
    print("  • Enhanced visual effects")
    print("\n🎮 Controls:")
    print("  • SPACE/ENTER to start or restart")
    print("  • Arrow Keys or WASD to move")
    print("  • ESC to quit or return to menu")
    print("  • Mouse to interact with buttons")
    print("\nStarting Snake Game Ultimate...")
    
    game = Game()
    game.run()
