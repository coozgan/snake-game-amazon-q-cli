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
    # Main rectangle
    pygame.draw.rect(surface, color, rect)
    
    # Highlight (top and left)
    highlight_color = tuple(min(255, c + 40) for c in color)
    pygame.draw.line(surface, highlight_color, 
                    (rect.left, rect.top), (rect.right - 1, rect.top), 2)
    pygame.draw.line(surface, highlight_color, 
                    (rect.left, rect.top), (rect.left, rect.bottom - 1), 2)
    
    # Shadow (bottom and right)
    shadow_color = tuple(max(0, c - 40) for c in color)
    pygame.draw.line(surface, shadow_color, 
                    (rect.left + 1, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 2)
    pygame.draw.line(surface, shadow_color, 
                    (rect.right - 1, rect.top + 1), (rect.right - 1, rect.bottom - 1), 2)

def draw_glowing_circle(surface, color, center, radius, glow_radius=None):
    """Draw a glowing circle effect"""
    if glow_radius is None:
        glow_radius = radius + 10
    
    # Create glow effect
    for i in range(glow_radius, radius, -2):
        alpha = int(255 * (glow_radius - i) / (glow_radius - radius))
        glow_color = (*color, alpha)
        glow_surface = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (i, i), i)
        surface.blit(glow_surface, (center[0] - i, center[1] - i), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Main circle
    pygame.draw.circle(surface, color, center, radius)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color):
        """Add a particle at the given position"""
        particle = {
            'x': x,
            'y': y,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 30,
            'max_life': 30,
            'color': color,
            'size': random.uniform(2, 4)
        }
        self.particles.append(particle)
    
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['size'] *= 0.98
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))

class Snake:
    def __init__(self):
        """Initialize the snake with starting position and direction"""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.animation_offset = 0
        self.segment_animations = [0] * len(self.positions)
    
    def move(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.segment_animations.append(0)
        
        # Update animation
        self.animation_offset = (self.animation_offset + 1) % 60
        for i in range(len(self.segment_animations)):
            self.segment_animations[i] = (self.segment_animations[i] + 1) % 60
    
    def change_direction(self, new_direction):
        """Change snake direction, but prevent reversing into itself"""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def check_collision(self):
        """Check if snake collides with walls or itself"""
        head_x, head_y = self.positions[0]
        
        if (head_x < 0 or head_x >= GRID_WIDTH or 
            head_y < 0 or head_y >= GRID_HEIGHT):
            return True
        
        if self.positions[0] in self.positions[1:]:
            return True
        
        return False
    
    def eat_food(self):
        """Make the snake grow on next move"""
        self.grow = True
    
    def draw(self, screen):
        """Draw the snake with modern 3D effects and animations"""
        for i, position in enumerate(self.positions):
            x = position[0] * GRID_SIZE + 2
            y = position[1] * GRID_SIZE + 2
            size = GRID_SIZE - 4
            
            # Animation pulse effect
            pulse = math.sin(self.segment_animations[i] * 0.2) * 2
            animated_size = size + pulse
            offset = (size - animated_size) / 2
            
            rect = pygame.Rect(x + offset, y + offset, animated_size, animated_size)
            
            if i == 0:  # Head
                # Draw glowing head
                center = (int(rect.centerx), int(rect.centery))
                draw_glowing_circle(screen, SNAKE_HEAD, center, int(animated_size // 2))
                
                # Add eyes
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
                # Gradient body segments
                segment_color = SNAKE_PRIMARY if i % 2 == 0 else SNAKE_SECONDARY
                draw_3d_rect(screen, segment_color, rect, depth=4)
                
                # Add subtle inner glow
                inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
                lighter_color = tuple(min(255, c + 20) for c in segment_color)
                pygame.draw.rect(screen, lighter_color, inner_rect)

class Food:
    def __init__(self):
        """Initialize food at random position"""
        self.position = self.generate_position()
        self.animation = 0
        self.pulse_scale = 1.0
    
    def generate_position(self):
        """Generate random position for food"""
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake_positions):
        """Respawn food at new position, avoiding snake body"""
        while True:
            new_position = self.generate_position()
            if new_position not in snake_positions:
                self.position = new_position
                break
    
    def update(self):
        """Update food animations"""
        self.animation += 1
        self.pulse_scale = 1.0 + math.sin(self.animation * 0.15) * 0.2
    
    def draw(self, screen):
        """Draw the food with glowing 3D effect"""
        x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        
        # Animated size
        base_radius = (GRID_SIZE // 2 - 2)
        radius = int(base_radius * self.pulse_scale)
        
        # Draw glowing food
        draw_glowing_circle(screen, FOOD_PRIMARY, (x, y), radius, radius + 8)
        
        # Add sparkle effect
        sparkle_offset = math.sin(self.animation * 0.3) * 3
        sparkle_pos = (x + int(sparkle_offset), y - int(sparkle_offset))
        pygame.draw.circle(screen, (255, 255, 255), sparkle_pos, 2)

class Game:
    def __init__(self):
        """Initialize the game"""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game Pro - Modern Edition")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.game_over = False
        self.particles = ParticleSystem()
        
        # Create background gradient
        self.background = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT, 
                                                BACKGROUND_DARK, BACKGROUND_LIGHT, True)
        
        # Add subtle grid pattern
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
    
    def handle_events(self):
        """Handle keyboard input and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_ESCAPE:
                        return False
        
        return True
    
    def update(self):
        """Update game state"""
        if not self.game_over:
            self.snake.move()
            self.food.update()
            
            if self.snake.check_collision():
                self.game_over = True
                # Add explosion particles
                head_pos = self.snake.positions[0]
                x = head_pos[0] * GRID_SIZE + GRID_SIZE // 2
                y = head_pos[1] * GRID_SIZE + GRID_SIZE // 2
                for _ in range(20):
                    self.particles.add_particle(x, y, SNAKE_HEAD)
                return
            
            if self.snake.positions[0] == self.food.position:
                self.snake.eat_food()
                self.score += 10
                
                # Add celebration particles
                food_x = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                food_y = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                for _ in range(10):
                    self.particles.add_particle(food_x, food_y, FOOD_PRIMARY)
                
                self.food.respawn(self.snake.positions)
        
        self.particles.update()
    
    def draw(self):
        """Draw everything on the screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if not self.game_over:
            # Draw game objects
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # Draw modern score display
            score_text = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            score_rect = pygame.Rect(20, 20, score_text.get_width() + 20, score_text.get_height() + 10)
            
            # Score background with gradient
            score_bg = create_gradient_surface(score_rect.width, score_rect.height, 
                                             ACCENT_COLOR, (ACCENT_COLOR[0]//2, ACCENT_COLOR[1]//2, ACCENT_COLOR[2]//2))
            self.screen.blit(score_bg, score_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, score_rect, 2)
            self.screen.blit(score_text, (score_rect.x + 10, score_rect.y + 5))
            
        else:
            # Draw modern game over screen
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 100, 100))
            score_text = self.font.render(f"FINAL SCORE: {self.score}", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, TEXT_COLOR)
            
            # Center the text with modern styling
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
            
            # Add background boxes
            for text, rect in [(game_over_text, game_over_rect), (score_text, score_rect), (restart_text, restart_rect)]:
                bg_rect = pygame.Rect(rect.x - 20, rect.y - 10, rect.width + 40, rect.height + 20)
                bg_surface = create_gradient_surface(bg_rect.width, bg_rect.height, 
                                                   (50, 50, 70), (30, 30, 50))
                self.screen.blit(bg_surface, bg_rect)
                pygame.draw.rect(self.screen, ACCENT_COLOR, bg_rect, 2)
                self.screen.blit(text, rect)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.particles = ParticleSystem()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(12)  # Slightly faster for smoother animations
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("🐍 Snake Game Pro - Modern Edition")
    print("=" * 40)
    print("✨ Features:")
    print("  • Modern gradient backgrounds")
    print("  • 3D visual effects and shading")
    print("  • Smooth animations and particle effects")
    print("  • Glowing snake head with animated eyes")
    print("  • Pulsating food with sparkle effects")
    print("  • Professional UI design")
    print("\n🎮 Controls:")
    print("  • Arrow Keys or WASD to move")
    print("  • ESC to quit")
    print("  • SPACE to restart after game over")
    print("\nStarting enhanced Snake game...")
    
    game = Game()
    game.run()
