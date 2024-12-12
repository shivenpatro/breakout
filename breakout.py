import pygame
import random
import math
from pygame import mixer

# Initialize pygame and mixer
pygame.init()
mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLUE = (65, 105, 225)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
BACKGROUND = (25, 25, 25)

# Game elements
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_COLOR = (200, 200, 200)
PADDLE_SPEED = 8

BALL_RADIUS = 8
BALL_COLOR = (255, 255, 255)
INITIAL_BALL_SPEED = 6

BRICK_WIDTH = 80
BRICK_HEIGHT = 30

# Load sounds (comment these out if you don't have sound files)
try:
    hit_sound = mixer.Sound('hit.wav')
    brick_sound = mixer.Sound('brick.wav')
    powerup_sound = mixer.Sound('powerup.wav')
except:
    print("Sound files not found. Game will run without sound.")

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.life = 255
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 5)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 10
        return self.life > 0

    def draw(self, screen):
        alpha = max(0, min(255, self.life))
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        particle_color = (*self.color, alpha)
        pygame.draw.circle(particle_surface, particle_color, (self.size//2, self.size//2), self.size//2)
        screen.blit(particle_surface, (int(self.x), int(self.y)))

class Ball:
    def __init__(self, x, y):
        self.reset(x, y)
        self.piercing = False
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        angle = random.uniform(-math.pi/4, math.pi/4)
        self.speed = INITIAL_BALL_SPEED
        self.dx = math.sin(angle) * self.speed
        self.dy = -math.cos(angle) * self.speed
        self.piercing = False
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # Wall collisions
        if self.x <= self.radius:
            self.x = self.radius
            self.dx = abs(self.dx)
        elif self.x >= SCREEN_WIDTH - self.radius:
            self.x = SCREEN_WIDTH - self.radius
            self.dx = -abs(self.dx)
            
        if self.y <= self.radius:
            self.y = self.radius
            self.dy = abs(self.dy)
            
    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius)

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = PADDLE_SPEED
        self.color = PADDLE_COLOR
        
    def move(self, direction):
        self.x += direction * self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, self.width, self.height])

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 3
        self.type = random.choice(['W', 'S', 'M', 'L', 'F', 'P'])
        self.colors = {
            'W': GREEN,  # Wider paddle
            'S': BLUE,   # Slower ball
            'M': YELLOW, # Multi-ball
            'L': RED,    # Extra life
            'F': ORANGE, # Faster ball
            'P': PURPLE  # Piercing ball
        }
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.colors[self.type], [self.x, self.y, self.width, self.height])
        font = pygame.font.Font(None, 20)
        text = font.render(self.type, True, WHITE)
        screen.blit(text, (self.x + 5, self.y + 2))

class Brick:
    def __init__(self, x, y, color, hits_required=1):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.hits_required = hits_required
        self.hits = 0
        self.visible = True
        self.points = hits_required * 10

    def hit(self):
        self.hits += 1
        if self.hits >= self.hits_required:
            self.visible = False
            return True
        self.color = (max(self.color[0] - 50, 0), 
                     max(self.color[1] - 50, 0), 
                     max(self.color[2] - 50, 0))
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)]
        self.bricks = self.create_bricks()
        self.particles = []
        self.powerups = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        self.screen_shake = 0
        self.power_up_timer = 0

    def create_bricks(self):
        bricks = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        pattern = random.choice(['normal', 'pyramid', 'scattered', 'diagonal'])
        
        if pattern == 'normal':
            for row in range(6):
                for col in range(8):
                    x = col * (BRICK_WIDTH + 2) + 45
                    y = row * (BRICK_HEIGHT + 2) + 50
                    hits_required = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                    bricks.append(Brick(x, y, colors[row], hits_required))
        elif pattern == 'pyramid':
            for row in range(6):
                for col in range(row, 8 - row):
                    x = col * (BRICK_WIDTH + 2) + 45
                    y = row * (BRICK_HEIGHT + 2) + 50
                    hits_required = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                    bricks.append(Brick(x, y, colors[row], hits_required))
        elif pattern == 'scattered':
            positions = [(col, row) for row in range(6) for col in range(8)]
            selected = random.sample(positions, 30)  # Select 30 random positions
            for row, col in selected:
                x = col * (BRICK_WIDTH + 2) + 45
                y = row * (BRICK_HEIGHT + 2) + 50
                hits_required = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                bricks.append(Brick(x, y, random.choice(colors), hits_required))
        elif pattern == 'diagonal':
            for i in range(12):
                for j in range(min(i + 1, 6)):
                    if i - j < 8:
                        x = (i - j) * (BRICK_WIDTH + 2) + 45
                        y = j * (BRICK_HEIGHT + 2) + 50
                        hits_required = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                        bricks.append(Brick(x, y, colors[j], hits_required))
        return bricks

    def handle_collisions(self, ball):
        # Paddle collision
        if (ball.y + ball.radius >= self.paddle.y and 
            ball.x >= self.paddle.x and 
            ball.x <= self.paddle.x + self.paddle.width):
            ball.dy = -abs(ball.dy)
            ball.y = self.paddle.y - ball.radius
            relative_intersect_x = (self.paddle.x + self.paddle.width/2) - ball.x
            normalized_intersect = relative_intersect_x / (self.paddle.width/2)
            bounce_angle = normalized_intersect * math.pi/3
            ball.dx = -ball.speed * math.sin(bounce_angle)
            ball.dy = -ball.speed * math.cos(bounce_angle)
            try:
                hit_sound.play()
            except:
                pass

        # Brick collision
        for brick in self.bricks:
            if brick.visible:
                if (ball.x + ball.radius > brick.x and 
                    ball.x - ball.radius < brick.x + brick.width and
                    ball.y + ball.radius > brick.y and 
                    ball.y - ball.radius < brick.y + brick.height):
                    
                    if ball.piercing:
                        brick.visible = False
                        self.score += brick.points
                    elif brick.hit():
                        self.score += brick.points
                        
                    # Create particles
                    for _ in range(10):
                        self.particles.append(Particle(brick.x + brick.width/2, 
                                                    brick.y + brick.height/2, 
                                                    brick.color))
                    # Chance to spawn power-up
                    if random.random() < 0.2:  # 20% chance
                        self.powerups.append(PowerUp(brick.x + brick.width/2, brick.y))
                    try:
                        brick_sound.play()
                    except:
                        pass
                    
                    if not ball.piercing:
                        if abs(ball.x - brick.x) < 5 or abs(ball.x - (brick.x + brick.width)) < 5:
                            ball.dx *= -1
                        else:
                            ball.dy *= -1
                        break

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        running = False

            if not self.game_over and not self.won:
                # Paddle movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.paddle.move(-1)
                if keys[pygame.K_RIGHT]:
                    self.paddle.move(1)

                # Update balls
                for ball in self.balls[:]:
                    ball.move()
                    self.handle_collisions(ball)
                    if ball.y > SCREEN_HEIGHT:
                        self.balls.remove(ball)
                
                if not self.balls:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.balls.append(Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))

                # Check if all bricks are broken
                if all(not brick.visible for brick in self.bricks):
                    self.won = True

                # Update particles
                self.particles = [p for p in self.particles if p.update()]

                # Update power-ups
                for powerup in self.powerups[:]:
                    powerup.update()
                    if not powerup.active:
                        self.powerups.remove(powerup)
                    elif (powerup.y + powerup.height > self.paddle.y and
                          powerup.x < self.paddle.x + self.paddle.width and
                          powerup.x + powerup.width > self.paddle.x):
                        self.apply_powerup(powerup.type)
                        self.powerups.remove(powerup)
                        try:
                            powerup_sound.play()
                        except:
                            pass

                # Update screen shake
                if self.screen_shake > 0:
                    self.screen_shake -= 1

                # Update power-up timer
                if self.power_up_timer > 0:
                    self.power_up_timer -= 1
                    if self.power_up_timer == 0:
                        self.paddle.width = PADDLE_WIDTH

            # Drawing
            shake_offset = random.randint(-self.screen_shake, self.screen_shake)
            self.screen.fill(BACKGROUND)
            
            # Draw game elements
            for brick in self.bricks:
                if brick.visible:
                    pygame.draw.rect(self.screen, brick.color, 
                                   [brick.x, brick.y + shake_offset, brick.width, brick.height])
            
            for particle in self.particles:
                particle.draw(self.screen)
            
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            for ball in self.balls:
                ball.draw(self.screen)
            
            self.paddle.draw(self.screen)

            # Draw UI
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, WHITE)
            lives_text = font.render(f'Lives: {self.lives}', True, WHITE)
            
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))

            if self.game_over:
                game_over_text = font.render('Game Over! Press R to restart or Q to quit', True, WHITE)
                self.screen.blit(game_over_text, 
                               (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                                SCREEN_HEIGHT//2))
            
            if self.won:
                win_text = font.render('You Win! Press R to restart or Q to quit', True, WHITE)
                self.screen.blit(win_text, 
                               (SCREEN_WIDTH//2 - win_text.get_width()//2, 
                                SCREEN_HEIGHT//2))

            pygame.display.flip()
            self.clock.tick(60)

    def apply_powerup(self, powerup_type):
        if powerup_type == 'W':  # Wider paddle
            self.paddle.width = min(200, self.paddle.width * 1.5)
            self.power_up_timer = 300
        elif powerup_type == 'S':  # Slower ball
            for ball in self.balls:
                ball.speed = max(3, ball.speed * 0.7)
        elif powerup_type == 'F':  # Faster ball
            for ball in self.balls:
                ball.speed = min(12, ball.speed * 1.3)
        elif powerup_type == 'M':  # Multi-ball
            current_balls = len(self.balls)
            for _ in range(current_balls):
                new_ball = Ball(self.balls[0].x, self.balls[0].y)
                self.balls.append(new_ball)
        elif powerup_type == 'L':  # Extra life
            self.lives += 1
        elif powerup_type == 'P':  # Piercing ball
            for ball in self.balls:
                ball.piercing = True
            self.power_up_timer = 300

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
