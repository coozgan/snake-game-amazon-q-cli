import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 200, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        """Initialize the snake with starting position and direction"""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start in center
        self.direction = RIGHT  # Start moving right
        self.grow = False  # Flag to determine if snake should grow
    
    def move(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Add new head to the front
        self.positions.insert(0, new_head)
        
        # Remove tail unless snake should grow
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
    
    def change_direction(self, new_direction):
        """Change snake direction, but prevent reversing into itself"""
        # Prevent snake from reversing into itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def check_collision(self):
        """Check if snake collides with walls or itself"""
        head_x, head_y = self.positions[0]
        
        # Check wall collision
        if (head_x < 0 or head_x >= GRID_WIDTH or 
            head_y < 0 or head_y >= GRID_HEIGHT):
            return True
        
        # Check self collision
        if self.positions[0] in self.positions[1:]:
            return True
        
        return False
    
    def eat_food(self):
        """Make the snake grow on next move"""
        self.grow = True
    
    def draw(self, screen):
        """Draw the snake on the screen"""
        for i, position in enumerate(self.positions):
            x = position[0] * GRID_SIZE
            y = position[1] * GRID_SIZE
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            
            # Draw head in different color
            if i == 0:
                pygame.draw.rect(screen, DARK_GREEN, rect)
            else:
                pygame.draw.rect(screen, GREEN, rect)
            
            # Add border to snake segments
            pygame.draw.rect(screen, BLACK, rect, 1)

class Food:
    def __init__(self):
        """Initialize food at random position"""
        self.position = self.generate_position()
    
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
    
    def draw(self, screen):
        """Draw the food on the screen"""
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

class Game:
    def __init__(self):
        """Initialize the game"""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
    
    def handle_events(self):
        """Handle keyboard input and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    # Restart game on any key press after game over
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    # Handle movement keys
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
            # Move snake
            self.snake.move()
            
            # Check for collisions
            if self.snake.check_collision():
                self.game_over = True
                return
            
            # Check if snake ate food
            if self.snake.positions[0] == self.food.position:
                self.snake.eat_food()
                self.score += 10
                self.food.respawn(self.snake.positions)
    
    def draw(self):
        """Draw everything on the screen"""
        # Clear screen
        self.screen.fill(BLACK)
        
        if not self.game_over:
            # Draw game objects
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
        else:
            # Draw game over screen
            game_over_text = self.font.render("GAME OVER!", True, WHITE)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, WHITE)
            
            # Center the text
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Control game speed (10 FPS)
            self.clock.tick(10)
        
        # Quit
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("Snake Game Controls:")
    print("- Use Arrow Keys or WASD to move")
    print("- Eat red food to grow and increase score")
    print("- Avoid hitting walls or yourself")
    print("- Press ESC to quit")
    print("- After game over: SPACE to restart, ESC to quit")
    print("\nStarting game...")
    
    game = Game()
    game.run()
