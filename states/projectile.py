from states.state import State
from utils.spritesheet import SpriteSheet
from pygame import mixer
import pygame
import math
import time
import random


# Initialize the mixer
mixer.init()

hit_sound_effect = mixer.Sound('assets/sfx/hit.mp3')
cannon_sound_effect = mixer.Sound('assets/sfx/cannon.mp3')
death1 = mixer.Sound('assets/sfx/death1.mp3')
death2 = mixer.Sound('assets/sfx/death2.mp3')
death3 = mixer.Sound('assets/sfx/death3.mp3')
blipSound = mixer.Sound('assets/sfx/dialogue-blip.mp3')

class Ball:
    def __init__(self, x, y, radius, color, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.3 * 682/screen_height
        self.elasticity = 0.7
        self.friction = 0.99
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
        if self.launched:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
    
    def launch(self, angle, power):
        cannon_sound = cannon_sound_effect
        cannon_sound.play()
        angle_rad = math.radians(angle)
        self.velocity_x = math.cos(angle_rad) * power
        self.velocity_y = -math.sin(angle_rad) * power
        print(self.velocity_x, self.velocity_y)
        self.launched = True
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class Platform:
    def __init__(self, x, y, width):
        self.x, self.y = x, y
        self.width = width
        self.load_assets()
        self.rect = pygame.Rect(x, y, width*32, 32)
        self.elasticity = 0.8
    
    def load_assets(self):
        self.TILE_SIZE = 32
        tilesheet = pygame.image.load("assets/tilesheets/tilesheet.png").convert_alpha()
        rect = pygame.Rect(1 * self.TILE_SIZE, 0 * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
        self.platform_tile = tilesheet.subsurface(rect)

    def draw(self, surface):
        for i in range(self.width):
            surface.blit(self.platform_tile, (self.x +(32*i), self.y))
    
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
            return True
        return False

class Cannon:
    def __init__(self, x, y, length=80, width=20, game=None):
        self.x = x
        self.y = y
        self.game = game
        self.base_length = length
        self.width = width
        self.angle = 0
        self.power = 10
        self.color = (150, 150, 150)
        self.load_assets()
    
    def draw(self, surface):
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * self.base_length
        end_y = self.y - math.sin(angle_rad) * self.base_length

        surface.blit(self.cannon_base_sprite, (0, self.game.SCREEN_HEIGHT * (9/10) - 32))
        
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.width)
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), (end_x, end_y), self.width)
        
        # surface.blit(rotated, (0, 550))
        
        power_indicator_length = self.power * 3
        pygame.draw.line(surface, (255, 0, 0), 
                        (self.x - 30, self.y + 40), 
                        (self.x - 30 + power_indicator_length, self.y + 40), 
                        5)
    
    def load_assets(self):
        # Load cannon image
        self.cannon_head_sprite = pygame.image.load("assets/sprites/cannon-head.png").convert_alpha()
        self.cannon_head_sprite = pygame.transform.scale(self.cannon_head_sprite, (self.game.SCREEN_WIDTH/10, self.game.SCREEN_HEIGHT/10))
        # self.cannon_head_sprite = pygame.transform.flip(self.cannon_head_sprite, True, False)

        self.cannon_base_sprite = pygame.image.load("assets/sprites/cannon-base.png").convert_alpha()
        self.cannon_base_sprite = pygame.transform.scale(self.cannon_base_sprite, (self.game.SCREEN_WIDTH//15, self.game.SCREEN_HEIGHT//10))

class Wizard:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game
        self.width = 150*3
        self.height = 150*3
        self.rect_width = 80
        self.rect_height = 155
        self.rect_x, self.rect_y = x+200, y+160
        self.health = 2000
        self.max_health = 2000
        self.hit_cooldown = 0
        self.defeated = False
        self.load_assets()

        self.current_frame: int = 0
        self.last_time_updated: int = 0
        self.previous_time: int = time.time()
        self.time_count: int = 0

    def load_assets(self):
        self.hit_sprites, self.idle_sprites, self.death_sprites = [], [], []
        SPRITE_SIZE = 150

        # Load wizard sprites
        self.idle_sprite_source = pygame.image.load("assets/sprites/wizard/Idle.png").convert_alpha()
        self.hit_sprite_source = pygame.image.load("assets/sprites/wizard/Take Hit.png").convert_alpha()    
        self.death_sprite_source = pygame.image.load("assets/sprites/wizard/Death.png").convert_alpha()    

        self.idle_spritesheet = SpriteSheet(self.idle_sprite_source)
        self.hit_spritesheet = SpriteSheet(self.hit_sprite_source)
        self.death_spritesheet = SpriteSheet(self.death_sprite_source)

        for i in range(4):
            self.hit_sprites.append(self.hit_spritesheet.get_image(i, SPRITE_SIZE, SPRITE_SIZE, 1, None))

        for i in range(8):
            self.idle_sprites.append(self.idle_spritesheet.get_image(i, SPRITE_SIZE, SPRITE_SIZE, 1, None))

        for i in range (5):
            self.death_sprites.append(self.death_spritesheet.get_image(i, SPRITE_SIZE, SPRITE_SIZE, 1, None))

        self.current_sprite = self.idle_sprites
        self.curr_image = self.current_sprite[0]
    
    def update(self):
        now = time.time()
        self.last_time_updated += now - self.previous_time
        self.previous_time = now

        if self.last_time_updated > 0.2:
            self.last_time_updated = 0
            self.current_frame = (self.current_frame +1)
            if self.current_frame >= len(self.current_sprite):
                if self.defeated:
                    self.current_frame = len(self.current_sprite) - 1
                else:
                    self.current_frame = 0
            self.curr_image = self.current_sprite[self.current_frame]

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            if self.hit_cooldown == 0:
                if not self.defeated:
                    self.relocate()
                    self.current_sprite = self.idle_sprites

    def draw(self, surface):
        # Draw wizard
        toDisplay = pygame.transform.scale(self.current_sprite[self.current_frame], (self.width, self.height))
        toDisplay = pygame.transform.flip(toDisplay, True, False)
        surface.blit(toDisplay, (self.x, self.y))
        # Draw health bar
        health_bar_width = 100
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), (self.rect_x-15, self.rect_y-45, health_bar_width, 10))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect_x-15, self.rect_y-45, health_bar_width * health_ratio, 10))
    
    def get_rect(self):
        return pygame.Rect(self.rect_x, self.rect_y, self.rect_width, self.rect_height)
    
    def check_hit(self, ball):
        hit_sound = hit_sound_effect
        if self.hit_cooldown > 0:
            return False
            
        wizard_rect = self.get_rect()
        ball_rect = ball.get_rect()
        
        if wizard_rect.colliderect(ball_rect):
            hit_sound.play()
            # Calculate damage based on ball velocity
            damage = math.sqrt(ball.velocity_x**2 + ball.velocity_y**2) * 4
            self.health -= damage

            self.hit_cooldown = 50 # Cooldown frames
            self.current_frame = 0
            if self.is_defeated():
                death = death3
                death.set_volume(100)
                death.play()
                self.defeated = True
                self.current_sprite = self.death_sprites
            else:
                self.current_sprite = self.hit_sprites
            
            # Bounce the ball away
            ball.velocity_x *= -0.8
            ball.velocity_y *= -0.8
            
            return True
        return False
    
    def is_defeated(self):
        return self.health <= 0
    
    def relocate(self):
        self.x, self.y = random.randint(0, self.game.SCREEN_WIDTH - 300), random.randint(0, self.game.SCREEN_HEIGHT - 300)
        print(self.x,self.y)
        self.rect_x, self.rect_y = self.x+200, self.y+160

class Projectile(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_assets()
        self.paused = True
        self.finished = False
        self.start_countdown = False
        self.GAME_W, self.GAME_H = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT
        self.game.projectile_boss_bgm.play(-1)
        
        self.wizard = Wizard(
            x=self.GAME_W//2, 
            y=self.GAME_H//2,  # On top of ground
            game=self.game
        )
        
        self.cannon = Cannon(
            x= (0 + self.game.SCREEN_WIDTH // 30),
            y=self.game.SCREEN_HEIGHT * (9/10) - 32 + self.game.SCREEN_HEIGHT/10 * 0.28,
            length=50,
            width=25,
            game=self.game
        )
        
        self.ball = Ball(
            x=self.cannon.x,
            y=self.cannon.y,
            radius=15,
            color=(255, 0, 0),
            screen_height=self.game.SCREEN_HEIGHT
        )
        
        # Create platforms
        self.platforms = [
            Platform(200, 200, 3),
            Platform(500, 500, 5),
            Platform(700, 200, 6),
            # Platform(400, 300, 150, 20),
            # Platform(600, 500, 250, 20),
            # Platform(800, 200, 200, 20),
        ]
        
        self.charging = False
        self.font = pygame.font.SysFont('Arial', 20)
    
    def update(self, actions):
            
    # Calculate elapsed time
        if self.start_countdown:
            self.elapsed = pygame.time.get_ticks() - self.start_time
            print(self.elapsed)
            if self.elapsed > 7000:
                self.start_countdown = False
                self.finished = True
        self.get_events(actions)
        self.ball.update()

        self.wizard.update()
        self.wizard.check_hit(self.ball)

        if self.wizard.is_defeated():
            self.wizard.defeated = True
            if not self.start_countdown:
                self.start_time = pygame.time.get_ticks()  # Get current time in milliseconds
                self.elapsed_time = 0
                self.start_countdown = True

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
            elif self.ball.x >= self.GAME_W - self.ball.radius:
                self.ball.x = self.GAME_W - self.ball.radius
                
            if self.ball.y >= self.GAME_H - self.ball.radius - 32:
                self.ball.y = self.GAME_H - self.ball.radius - 32
                self.ball.velocity_y *= -self.ball.elasticity
                self.ball.velocity_x *= 0.9
                
                if abs(self.ball.velocity_x) < 0.5 and abs(self.ball.velocity_y) < 0.5:
                    self.reset_ball()
            elif self.ball.y <= self.ball.radius:
                self.ball.y = self.ball.radius
                self.ball.velocity_y *= -self.ball.elasticity

    def render(self, display):
        # render background in screen
        display.blit(self.bg, (0,0))
        
        # draw ground
        for i in range(self.game.SCREEN_WIDTH // 32):
            display.blit(self.ground_tile, (i*32, self.game.SCREEN_HEIGHT - 32))
        
        # display.blit(self.platform_tile, (100, 400))
        # Draw platforms
        for platform in self.platforms:
            platform.draw(display)
        
        self.cannon.draw(display)
        self.ball.draw(display)

        self.wizard.draw(display)
        
        instructions = [
            f"Press TAB to see goal",
            f"Angle: {self.cannon.angle:.0f}°",
            f"Power: {self.cannon.power:.1f}"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (255, 255, 255))
            display.blit(text_surface, (10, 10 + i * 25))
        
        if self.paused:
            image_width, image_height = self.paused_modal.get_size()
            x_centered = self.game.SCREEN_WIDTH // 2 - image_width // 2
            y_centered = self.game.SCREEN_HEIGHT // 2 - image_height // 2
            display.blit(self.paused_modal, (x_centered,y_centered))

        if self.finished:
            image_width, image_height = self.finished_modal.get_size()
            x_centered = self.game.SCREEN_WIDTH // 2 - image_width // 2
            y_centered = self.game.SCREEN_HEIGHT // 2 - image_height // 2
            display.blit(self.finished_modal, (x_centered,y_centered))
        pygame.display.flip()
        # Code for displaying screens

    def get_events(self, action):
        blip = blipSound

        keys = pygame.key.get_pressed()
        if not self.paused:
            if keys[pygame.K_TAB]:
                blip.play()
                self.paused = True
        
        if self.paused:
            if keys[pygame.K_RETURN]:
                blip.play()
                self.paused = False
            return
        
        if self.finished:
            if keys[pygame.K_RETURN]:
                self.game.projectile_boss_bgm.stop()
                self.game.post_boss_bgm.play(-1)
                self.game.bossDefeated = True
                self.game.bossDefeatedChanged = True
                self.exit_state()

        if action["R"]:
            self.reset_ball()
        if action["SPACE"] and not self.ball.launched and not self.wizard.defeated:
            self.charging = True
        if action["SPACE"] == False and self.charging and not self.wizard.defeated:
            self.charging = False
            scaled_cannon_power = (self.game.SCREEN_WIDTH/41) * (self.cannon.power/25) * (self.game.SCREEN_WIDTH/1024)
            self.ball.launch(self.cannon.angle, scaled_cannon_power)
            self.cannon.power = 2.5

        keys = pygame.key.get_pressed()
        if not self.ball.launched:
            if keys[pygame.K_UP] and self.cannon.angle < 90:
                self.cannon.angle += 0.5
            if keys[pygame.K_DOWN] and self.cannon.angle > -90:
                self.cannon.angle -= 0.5
        
        if self.charging and self.cannon.power < 25:
            self.cannon.power += 0.2
    
    def reset_ball(self):
        self.ball.launched = False
        self.ball.velocity_x = 0
        self.ball.velocity_y = 0

    def load_assets(self):
        # Load background by changing parameter
        self.bg = self.game.load_background_asset("assets/bg/projectile-bg.jpg")
        
        self.paused_modal = self.game.load_background_asset("assets/popups/boss-start.jpg")
        self.paused_modal = pygame.transform.scale_by(self.paused_modal, 0.8)
        
        self.finished_modal = self.game.load_background_asset("assets/popups/boss-end.jpg")
        self.finished_modal = pygame.transform.scale_by(self.finished_modal, 0.8)
        
        tilesheet = pygame.image.load("assets/tilesheets/tilesheet.png").convert_alpha()
        TILE_SIZE = 32

        rect = pygame.Rect(1 * TILE_SIZE, 1 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.ground_tile = tilesheet.subsurface(rect)

        # load other assets
        # self.asset_name = pygame.image.load("Enter filepath here").convert_alpha()