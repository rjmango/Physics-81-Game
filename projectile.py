import pygame
import sys
import math
import os

WINDOW_WIDTH = 1920/2
WINDOW_HEIGHT = 1280/2

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.elasticity = 0.7
        self.friction = 0.98
        self.launched = False
    
    def update(self):
        if not self.launched:
            return
            
        self.velocity_y += self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply friction to horizontal movement
        self.velocity_x *= self.friction
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
    
    def launch(self, angle, power):
        angle_rad = math.radians(angle)
        self.velocity_x = math.cos(angle_rad) * power
        self.velocity_y = -math.sin(angle_rad) * power
        self.launched = True
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class Platform:
    def __init__(self, x, y, width, height, color=(100, 200, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.elasticity = 0.8
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
    
    def check_collision(self, ball):
        # Simple circle-rectangle collision detection
        closest_x = max(self.rect.left, min(ball.x, self.rect.right))
        closest_y = max(self.rect.top, min(ball.y, self.rect.bottom))
        
        distance_x = ball.x - closest_x
        distance_y = ball.y - closest_y
        
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        if distance < ball.radius:
            # Determine collision side
            if abs(closest_y - self.rect.top) < abs(closest_y - self.rect.bottom):
                # Top collision
                ball.y = self.rect.top - ball.radius
                ball.velocity_y *= -ball.elasticity * self.elasticity
                print("top collision")
            elif abs(closest_y - self.rect.top) > abs(closest_y - self.rect.bottom):
                # Bottom collision
                ball.y = self.rect.bottom + ball.radius
                ball.velocity_y *= -ball.elasticity * self.elasticity
                print("bottom collision")
            
            elif abs(closest_x - self.rect.left) < abs(closest_x - self.rect.right):
                # Left collision
                ball.x = self.rect.left - ball.radius
                ball.velocity_x *= -ball.elasticity * self.elasticity
                print("left collision")
            else:
                # Right collision
                ball.x = self.rect.right + ball.radius
                ball.velocity_x *= -ball.elasticity * self.elasticity
                print("right collision")
            print(ball.velocity_x, ball.velocity_y)
            return True
        return False

class Cannon:
    def __init__(self, x, y, length=80, width=20):
        self.x = x
        self.y = y
        self.base_length = length
        self.width = width
        self.angle = 0
        self.power = 10
        self.color = (150, 150, 150)
    
    def draw(self, surface):
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * self.base_length
        end_y = self.y - math.sin(angle_rad) * self.base_length
        
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.width)
        pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), self.width//2)
        
        power_indicator_length = self.power * 3
        pygame.draw.line(surface, (255, 0, 0), 
                        (self.x - 30, self.y + 40), 
                        (self.x - 30 + power_indicator_length, self.y + 40), 
                        5)

class Game():
    def __init__(self):
        pygame.init()
        self.GAME_W, self.GAME_H = 1920/2, 1280/2
        self.SCREEN_WIDTH = pygame.display.Info().current_w * 6 // 8
        self.SCREEN_HEIGHT = self.SCREEN_WIDTH * 2//3
        self.game_canvas = pygame.Surface((self.GAME_W,self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))
        pygame.display.set_caption("Cannon Platform Game")
        self.running = True
        self.clock = pygame.time.Clock()
        self.load_assets()
        
        self.cannon = Cannon(
            x=25, 
            y=self.GAME_H - 50,
            length=100,
            width=25
        )
        
        self.ball = Ball(
            x=self.cannon.x,
            y=self.cannon.y,
            radius=15,
            color=(255, 0, 0)
        )
        
        # Create platforms
        self.platforms = [
            Platform(100, 400, 200, 20),
            Platform(400, 300, 150, 20),
            Platform(600, 500, 250, 20),
            Platform(800, 200, 200, 20),
        ]
        
        self.charging = False
        self.font = pygame.font.SysFont('Arial', 20)

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE and not self.ball.launched:
                    self.charging = True
                if event.key == pygame.K_r:
                    self.reset_ball()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.charging:
                    self.charging = False
                    self.ball.launch(self.cannon.angle, self.cannon.power)
                    self.cannon.power = 10
        
        keys = pygame.key.get_pressed()
        if not self.ball.launched:
            if keys[pygame.K_UP] and self.cannon.angle < 90:
                self.cannon.angle += 2
            if keys[pygame.K_DOWN] and self.cannon.angle > -90:
                self.cannon.angle -= 2
        
        if self.charging and self.cannon.power < 40:
            self.cannon.power += 0.2

    def game_loop(self):
        while self.running:
            self.get_events()
            self.update()
            self.render()
            self.clock.tick(60)
    
    def update(self):
        self.ball.update()
        
        if not self.ball.launched:
            angle_rad = math.radians(self.cannon.angle)
            self.ball.x = self.cannon.x + math.cos(angle_rad) * (self.cannon.base_length + self.ball.radius)
            self.ball.y = self.cannon.y - math.sin(angle_rad) * (self.cannon.base_length + self.ball.radius)
        
        # Check collisions with platforms
        for platform in self.platforms:
            platform.check_collision(self.ball)
        
        # Boundary checking
        if self.ball.launched:
            if self.ball.x <= self.ball.radius:
                self.ball.x = self.ball.radius
                self.ball.velocity_x *= -self.ball.elasticity
            elif self.ball.x >= self.GAME_W - self.ball.radius:
                self.ball.x = self.GAME_W - self.ball.radius
                self.ball.velocity_x *= -self.ball.elasticity
                
            if self.ball.y >= self.GAME_H - self.ball.radius:
                self.ball.y = self.GAME_H - self.ball.radius
                self.ball.velocity_y *= -self.ball.elasticity
                self.ball.velocity_x *= 0.9
                
                print(abs(self.ball.velocity_x), abs(self.ball.velocity_y))
                if abs(self.ball.velocity_x) < 0.5 and abs(self.ball.velocity_y) < 0.5:
                    self.reset_ball()
            elif self.ball.y <= self.ball.radius:
                self.ball.y = self.ball.radius
                self.ball.velocity_y *= -self.ball.elasticity
    
    def reset_ball(self):
        self.ball.launched = False
        self.ball.velocity_x = 0
        self.ball.velocity_y = 0

    def render(self):
        self.game_canvas.blit(self.bg, (0,0))
        
        # Draw ground
        pygame.draw.rect(self.game_canvas, (100, 100, 100), 
                        (0, self.GAME_H - 20, self.GAME_W, 20))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.game_canvas)
        
        self.cannon.draw(self.game_canvas)
        self.ball.draw(self.game_canvas)
        
        instructions = [
            "UP/DOWN: Adjust angle",
            "SPACE: Charge and launch",
            "R: Reset ball",
            f"Angle: {self.cannon.angle:.0f}°",
            f"Power: {self.cannon.power:.1f}"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.game_canvas.blit(text_surface, (10, 10 + i * 25))
        
        scaled_canvas = pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.blit(scaled_canvas, (0, 0))
        
        pygame.display.flip()

    def load_assets(self):
        self.assets_dir = os.path.join("assets")

        self.bg = pygame.image.load("assets/Projectile-background.jpg").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (self.GAME_W, self.GAME_H))

if __name__ == "__main__":
    game = Game()
    game.game_loop()
    pygame.quit()
    sys.exit()