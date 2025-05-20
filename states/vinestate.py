import pygame as pg
import sys
import random
import math
from os import path

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
FPS = 60

class Vine:
    def __init__(self, x, y, width=200, height=20, snap_time=3, has_problem=False):
        self.original_x = x  # Anchor point x
        self.original_y = y  # Anchor point y
        self.rect = pg.Rect(x, y, width, height)
        self.angle = random.uniform(-0.5, 0.5)  # Random starting angle
        self.angular_vel = 0
        self.length = 6  # Length of the vine in meters (converted to pixels)
        self.snap_time = snap_time
        self.time_elapsed = 0
        self.snapped = False
        self.has_problem = has_problem
        self.knight_attached = False  # Initialize the attribute here

        # Physics properties from the problem
        self.mass = 56
        self.speed = 5
        self.g = 9.81
        self.correct_answer = 783

    def update(self, dt, knight_on_vine):
        if not self.snapped:
            # Only update physics if no knight is attached (or it's the first frame)
            if not self.knight_attached or not knight_on_vine:
                angular_accel = (-self.g / self.length) * math.sin(self.angle)
                self.angular_vel += angular_accel * dt
                self.angle += self.angular_vel * dt
                self.angular_vel *= 0.995  # damping
            
            swing_x = math.sin(self.angle) * self.length * 50
            swing_y = (math.cos(self.angle) - 1) * self.length * 50
            
            self.rect.x = self.original_x + swing_x
            self.rect.y = self.original_y + swing_y

            if knight_on_vine:
                if not self.knight_attached:
                    # When first landing, match the vine's angle
                    self.knight_attached = True
                    self.time_elapsed = 0
                self.time_elapsed += dt
                if self.time_elapsed >= self.snap_time:
                    self.snapped = True
            else:
                self.knight_attached = False

    def draw(self, surface, vine_image):
        if not self.snapped:
            surface.blit(vine_image, self.rect.topleft)

        if self.has_problem:
            font = pg.font.Font(None, 40)
            problem_text = [
                f"Mass: {self.mass}kg | Length: {self.length}m",
                f"Speed: {self.speed}m/s | g: {self.g}m/s²",
                "Minimum tension to avoid snapping:",
                f"A) 650N B) {self.correct_answer}N C) 450N D) 500N"
            ]

            for i, text in enumerate(problem_text):
                text_surface = font.render(text, True, (255, 255, 255))
                surface.blit(text_surface, (20, 120 + i * 30))

class GameState:
    def __init__(self, game):
        self.game = game
        self.prev_state = None
        self.load_assets()

        self.knight_rect = self.knight_surface.get_rect(bottomleft=(100, 1100))
        self.knight_gravity = 0
        self.knight_speed = 5
        self.on_vine = False
        self.facing_right = True
        self.gravity_enabled = False

        # Ground collision rect
        self.ground_rect = pg.Rect(-430, 1090, self.ground_surface.get_width(), self.ground_surface.get_height())

        # Initialize vines with different pendulum lengths based on height
        self.vines = [
            Vine(300, 700, snap_time=5),            # Vine A - higher position = longer swing
            Vine(650, 750, snap_time=5),            # Vine B
            Vine(1000, 800, snap_time=5),           # Vine C - lower position = shorter swing
            Vine(1350, 750, snap_time=5, has_problem=True)  # Vine D
        ]
        
        # Adjust pendulum lengths based on height (higher vines swing more)
        self.vines[0].length = 7  # Vine A - longest
        self.vines[1].length = 6   # Vine B
        self.vines[3].length = 6   # Vine D
        self.vines[2].length = 5   # Vine C - shortest

    def load_assets(self):
        try:
            base_path = path.dirname(path.dirname(path.abspath(__file__)))

            def load_asset(name):
                return pg.image.load(
                    path.join(base_path, 'assets', 'stage 1', name)
                ).convert_alpha()

            self.background_surface = load_asset('pixelvinebg.png')
            self.vine_surface = load_asset('masgamay.png')
            self.water_surface = load_asset('water(resized).png')
            self.ground_surface = load_asset('image-removebg-preview.png')

            self.knight_surface = load_asset('knightpix.png')
            self.knight_surface_left = pg.transform.flip(self.knight_surface, True, False)
            self.knight_surface_right = self.knight_surface

            font_path = path.join(base_path, 'assets', 'stage 1', 'Pixeltype.ttf')
            self.test_font = pg.font.Font(font_path, 50)
        except Exception as e:
            print(f"ASSET LOADING ERROR: {e}")
            pg.quit()
            sys.exit(1)

    def update(self, actions, dt):
        if actions.get("quit"):
            pg.quit()
            sys.exit()

        moved = False

        if actions.get("left"):
            self.knight_rect.x -= self.knight_speed
            self.facing_right = False
            moved = True
        if actions.get("right"):
            self.knight_rect.x += self.knight_speed
            self.facing_right = True
            moved = True

        # Only enable gravity if knight is beyond x=100
        if self.knight_rect.x > 100:
            self.gravity_enabled = True

        if actions.get("jump") and (self.knight_rect.colliderect(self.ground_rect) or self.on_vine):
            self.knight_gravity = -25
            self.on_vine = False
            self.gravity_enabled = True

        if moved:
            self.gravity_enabled = True

        if self.gravity_enabled:
            self.knight_gravity += 1
            self.knight_rect.y += self.knight_gravity

        self.on_vine = False
        for vine in self.vines:
            vine.update(dt, False)  # Update vine physics first
    
            collided = (
                not vine.snapped and
                self.knight_rect.bottom >= vine.rect.top and
                self.knight_rect.top <= vine.rect.bottom and
                self.knight_rect.right >= vine.rect.left and
                self.knight_rect.left <= vine.rect.right and
                self.knight_gravity >= 0 and
                abs(self.knight_rect.bottom - vine.rect.top) <= 20  # More lenient margin
            )

            if collided:
                # Stick firmly to the vine
                self.knight_rect.bottom = vine.rect.top
                self.knight_gravity = 0
                self.on_vine = True
                # Move horizontally with the vine
                self.knight_rect.x += vine.angular_vel * 25 * dt
        
                # Only start snap timer when actually standing on vine
                vine.update(dt, True)  # Pass True to indicate knight is on vine

        # Check ground collision
        if self.knight_rect.colliderect(self.ground_rect) and self.knight_gravity >= 0:
            self.knight_rect.bottom = self.ground_rect.top
            self.knight_gravity = 0
            self.on_vine = True

        # Reset if knight falls out of screen
        if self.knight_rect.top > SCREEN_HEIGHT:
            self.knight_rect.bottomleft = (100, 1100)
            self.knight_gravity = 0
            self.gravity_enabled = False

    def render(self, display):
        display.blit(self.background_surface, (0, 0))
        display.blit(self.water_surface, (0, 1100))
        display.blit(self.ground_surface, (0, 875))

        for vine in self.vines:
            vine.draw(display, self.vine_surface)

        knight_surf = (
            self.knight_surface_right if self.facing_right 
            else self.knight_surface_left
        )
        display.blit(knight_surf, self.knight_rect)

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption('Vine Physics Challenge')
        self.clock = pg.time.Clock()
        self.state = GameState(self)
        self.last_time = pg.time.get_ticks()

    def run(self):
        while True:
            current_time = pg.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
            self.last_time = current_time

            actions = {
                "quit": False,
                "left": False,
                "right": False,
                "jump": False
            }

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    actions["quit"] = True

            keys = pg.key.get_pressed()
            actions["left"] = keys[pg.K_LEFT]
            actions["right"] = keys[pg.K_RIGHT]
            actions["jump"] = keys[pg.K_SPACE] or keys[pg.K_UP]

            self.state.update(actions, dt)
            self.screen.fill((0, 0, 0))
            self.state.render(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()