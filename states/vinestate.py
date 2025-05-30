import pygame as pg
import sys
import random
import math
from .state import State
from os import path

class Vine:
    def __init__(self, game, x, y, width=1, height=10, snap_time=2, has_problem=False, swinging=True):
        self.game = game
        # Scale positions based on screen size
        self.original_x = x * self.game.SCREEN_WIDTH / 1920
        self.original_y = y * self.game.SCREEN_HEIGHT / 1280
        self.width = width * self.game.SCREEN_WIDTH / 1920
        self.height = height * self.game.SCREEN_HEIGHT / 1280
        self.rect = pg.Rect(self.original_x - self.width // 2, 
                           self.original_y + 20 * self.game.SCREEN_HEIGHT / 1280, 
                           self.width, 
                           self.height)
        self.angle = random.uniform(-0.5, 0.5)
        self.angular_vel = 0
        self.length = 6
        self.snap_time = snap_time
        self.time_elapsed = 0
        self.snapped = False
        self.has_problem = has_problem
        self.swinging = swinging
        self.knight_attached = False
        self.mass = 56
        self.speed = 5
        self.g = 9.81
        self.correct_answer = 783

    def update(self, dt, knight_on_vine):
        if not self.snapped:
            if self.swinging:
                if not self.knight_attached or not knight_on_vine:
                    angular_accel = (-self.g / self.length) * math.sin(self.angle)
                    self.angular_vel += angular_accel * dt
                    self.angle += self.angular_vel * dt
                    self.angular_vel *= 0.995

                swing_x = math.sin(self.angle) * self.length * 50 * self.game.SCREEN_WIDTH / 1920
                swing_y = (math.cos(self.angle) - 1) * self.length * 50 * self.game.SCREEN_HEIGHT / 1280
            else:
                swing_x = 0
                swing_y = 0

            self.rect.centerx = self.original_x + swing_x
            self.rect.top = self.original_y + swing_y

            if knight_on_vine:
                if not self.knight_attached:
                    self.knight_attached = True
                    self.time_elapsed = 0
                self.time_elapsed += dt
                if self.time_elapsed >= self.snap_time:
                    self.snapped = True
            else:
                self.knight_attached = False

    def draw(self, surface, vine_image):
        if not self.snapped:
            offset_y = -60 * self.game.SCREEN_HEIGHT / 1280
            image_rect = vine_image.get_rect(center=(self.rect.centerx, self.rect.top + offset_y))
            surface.blit(vine_image, image_rect.topleft)

        if self.has_problem:
            font_size = int(40 * min(self.game.SCREEN_WIDTH / 1920, self.game.SCREEN_HEIGHT / 1280))
            font = pg.font.Font(None, font_size)
            problem_text = [
                "There's a restriction on the knight when he's on the vine...",
                "ONLY ONE VINE CAN HOLD YOUR WEIGHT!",
                "What is the minimum tension that the vine",
                "should withstand to avoid snapping?",
                f"Mass: {self.mass}kg | Length of vine: {self.length}m",
                f"Speed: {self.speed}m/s | g: {self.g}m/s²",
                "A) 650N B) 500N C) 450N D) 783N",
                "A) 783N B) 650N C) 450N D) 500N"
            ]
            for i, text in enumerate(problem_text):
                text_surface = font.render(text, True, (255, 255, 255))
                y_pos = 120 * self.game.SCREEN_HEIGHT / 1280 + i * 30 * self.game.SCREEN_HEIGHT / 1280
                surface.blit(text_surface, (20 * self.game.SCREEN_WIDTH / 1920, y_pos))

class VineState(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.ground_position = self.game.SCREEN_HEIGHT // 1.462857143
        self.prev_state = None
        self.load_assets()
        self.init_sound()
        self.current_round = 1
        self.max_rounds = 2
        self.initialize_round()
        self.last_time = pg.time.get_ticks()
        self.knight_speed = 5 * self.game.SCREEN_WIDTH / 1920
        self.knight_gravity = 0
        self.jump_force = -25 * self.game.SCREEN_HEIGHT / 1280
        self.paused = True
        self.finished = False
        self.finishedTimer = 0

    def initialize_round(self):
        self.knight_gravity = 0
        self.on_vine = False
        self.facing_right = True
        self.gravity_enabled = False
        self.reached_final_vine = False
        self.can_jump = True

        if self.current_round == 1:
            self.ground_rect = pg.Rect(-430 * self.game.SCREEN_WIDTH / 1920, 
                                      self.ground_position + self.ground_surface.get_height()//1.5,
                                      self.ground_surface.get_width(),
                                      self.ground_surface.get_height())
            self.initial_vines = [
                Vine(self.game, 550, 850, snap_time=2.0),
                Vine(self.game, 950, 650, snap_time=1.5),
                Vine(self.game, 1300, 520, snap_time=2.0),
                Vine(self.game, 1650, 850, snap_time=999, has_problem=True)
            ]
            knight_start_x = 100 * self.game.SCREEN_WIDTH / 1920
            knight_start_y = 1100 * self.game.SCREEN_HEIGHT / 1280
            self.knight_rect = self.knight_surface.get_rect(bottomleft=(knight_start_x, knight_start_y))
        else:  # Round 2
            self.ground_rect = pg.Rect(1920 * self.game.SCREEN_WIDTH / 1920, 
                                      1090 * self.game.SCREEN_HEIGHT / 1280,
                                      self.ground_surface.get_width(),
                                      self.ground_surface.get_height())
            self.initial_vines = [
                Vine(self.game, 400, 800, snap_time=999, swinging=False),
                Vine(self.game, 700, 600, snap_time=1.5),
                Vine(self.game, 1000, 500, snap_time=1.5),
                Vine(self.game, 1400, 780, snap_time=1.0, has_problem=True, swinging=False)
            ]
            knight_start_x = self.game.SCREEN_WIDTH / 4.8
            knight_start_y = self.game.SCREEN_HEIGHT / 1.6
            self.knight_rect = self.knight_surface.get_rect(bottomleft=(knight_start_x, knight_start_y))

        self.initial_vines[0].length = 7
        self.initial_vines[1].length = 6
        self.initial_vines[3].length = 6
        self.initial_vines[2].length = 5

        self.reset_round()

    def reset_round(self):
        self.vines = [
            Vine(self.game,
                vine.original_x * 1920 / self.game.SCREEN_WIDTH,  # Convert back to original coordinates
                vine.original_y * 1280 / self.game.SCREEN_HEIGHT,  # for the Vine constructor to rescale
                vine.width * 1920 / self.game.SCREEN_WIDTH,
                vine.height * 1280 / self.game.SCREEN_HEIGHT,
                vine.snap_time,
                vine.has_problem,
                vine.swinging)
            for vine in self.initial_vines
        ]
        for i, vine in enumerate(self.vines):
            vine.length = self.initial_vines[i].length

        if self.current_round == 2:
            self.knight_rect.bottomleft = (
                self.vines[0].original_x//2,
                self.vines[0].original_y
            )
        else:
            knight_start_x = 100 * self.game.SCREEN_WIDTH / 1920
            knight_start_y = 1100 * self.game.SCREEN_HEIGHT / 1280
            self.knight_rect.bottomleft = (knight_start_x, knight_start_y)

        self.knight_gravity = 0
        self.on_vine = False
        self.gravity_enabled = False
        self.reached_final_vine = False

    def init_sound(self):
        try:
            base_path = path.dirname(path.dirname(path.abspath(__file__)))
            sound_path = path.join(base_path, 'assets', 'sfx', 'vinebackground_music.mp3')
            pg.mixer.init()
            pg.mixer.music.load(sound_path)
            pg.mixer.music.set_volume(0.5)
            pg.mixer.music.play(-1)
        except Exception as e:
            print(f"SOUND ERROR: Could not load background music - {e}")

    def load_assets(self):
        try:
            base_path = path.dirname(path.dirname(path.abspath(__file__)))
            def load_asset(name):
                img = pg.image.load(path.join(base_path, 'assets', 'stage 1', name)).convert_alpha()
                # Scale images based on screen size
                if name in ['pixelvinebg.png']:
                    return pg.transform.scale(img, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
                elif name == 'vinetop.png':
                    return pg.transform.scale(img, 
                                            (int(1900 * self.game.SCREEN_WIDTH / 1920), 
                                             int(1000 * self.game.SCREEN_HEIGHT / 1280)))
                elif name == 'masgamay.png':
                    return pg.transform.scale(img, 
                                            (int(img.get_width() * self.game.SCREEN_WIDTH / 1920), 
                                             int(img.get_height() * self.game.SCREEN_HEIGHT / 1280)))
                elif name == 'image-removebg-preview.png':
                    return pg.transform.scale(img, 
                                            (int(img.get_width() * self.game.SCREEN_WIDTH / 1920), 
                                             int(img.get_height() * self.game.SCREEN_HEIGHT / 1280)))
                elif name == 'knightpix.png':
                    self.knight_size = (int(img.get_width() * self.game.SCREEN_WIDTH / 1920), 
                                       int(img.get_height() * self.game.SCREEN_HEIGHT / 1280))
                    return pg.transform.scale(img, self.knight_size)
                return pg.transform.scale(img, (int(img.get_width() * self.game.SCREEN_WIDTH / 1920), 
                                       int(img.get_height() * self.game.SCREEN_HEIGHT / 1280)))

            self.background_surface = self.game.load_background_asset('assets/stage 1/pixelvinebg.png')
            self.background_vine = load_asset('vinetop.png')
            self.vine_surface = load_asset('masgamay.png')
            self.water_surface = load_asset('water(resized).png')
            self.ground_surface = load_asset('image-removebg-preview.png')
            self.knight_surface = load_asset('knightpix.png')
            self.knight_surface_left = pg.transform.flip(self.knight_surface, True, False)
            self.knight_surface_right = self.knight_surface

            self.paused_modal = self.game.load_background_asset("assets/popups/vine-start.png")
            self.finished_modal = self.game.load_background_asset("assets/popups/vine-end.png")
            
            # Scale knight rect to match scaled image
            self.knight_rect = self.knight_surface.get_rect()
            
            font_path = path.join(base_path, 'assets', 'stage 1', 'Pixeltype.ttf')
            self.test_font = pg.font.Font(font_path, int(50 * min(self.game.SCREEN_WIDTH / 1920, self.game.SCREEN_HEIGHT / 1280)))
        except Exception as e:
            print(f"ASSET LOADING ERROR: {e}")
            pg.quit()
            sys.exit(1)

    def update(self, actions):

        keys = pg.key.get_pressed()

        if not self.paused:
            if keys[pg.K_TAB]:
                self.game.blip.play()
                self.paused = True
        
        if self.paused:
            if keys[pg.K_RETURN]:
                self.game.blip.play()
                self.paused = False
            return
        
        if self.finished:
            if keys[pg.K_RETURN]:
                self.game.blip.play()
                self.exit_state()
        
        current_time = pg.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time

        moved = False
        if actions.get("LEFT"):
            self.knight_rect.x -= self.knight_speed
            self.facing_right = False
            moved = True
        if actions.get("RIGHT"):
            self.knight_rect.x += self.knight_speed
            self.facing_right = True
            moved = True

        if self.knight_rect.x > 100 * self.game.SCREEN_WIDTH / 1920:
            self.gravity_enabled = True

        if (self.knight_rect.colliderect(self.ground_rect) or self.on_vine):
            self.can_jump = True
        else:
            self.can_jump = False

        if actions.get("SPACE") and self.can_jump:
            self.knight_gravity = self.jump_force
            self.on_vine = False
            self.gravity_enabled = True
            self.can_jump = False

        if moved:
            self.gravity_enabled = True

        if self.gravity_enabled:
            self.knight_gravity += 1 * self.game.SCREEN_HEIGHT / 1280
            self.knight_rect.y += self.knight_gravity

        self.on_vine = False
        current_vine = None

        for vine in self.vines:
            collided = (
                not vine.snapped
                and self.knight_rect.bottom >= vine.rect.top
                and self.knight_rect.top <= vine.rect.bottom
                and self.knight_rect.right >= vine.rect.left
                and self.knight_rect.left <= vine.rect.right
                and self.knight_gravity >= 0
                and abs(self.knight_rect.bottom - vine.rect.top) <= 15 * self.game.SCREEN_HEIGHT / 1280
            )

            if collided:
                self.knight_rect.bottom = vine.rect.top
                self.knight_gravity = 0
                self.on_vine = True
                current_vine = vine
                self.knight_rect.x += vine.angular_vel * 25 * dt * self.game.SCREEN_WIDTH / 1920
                if vine.has_problem:
                    self.reached_final_vine = True
                break

        for vine in self.vines:
            vine.update(dt, vine == current_vine)

        if self.knight_rect.colliderect(self.ground_rect) and self.knight_gravity >= 0:
            self.knight_rect.bottom = self.ground_rect.top
            self.knight_gravity = 0
            self.on_vine = True
            if self.current_round == 2:
                self.finishedTimer += dt
                self.gravity_enabled = False
                self.can_jump = False
                self.knight_speed = 0

        # If the knight falls off the bottom of the screen
        if self.knight_rect.top > self.game.SCREEN_HEIGHT:
            if self.reached_final_vine and self.current_round == 1:
                self.current_round = 2
                self.initialize_round()
            else:
                self.current_round = 1
                self.initialize_round()

        if self.finishedTimer > 3:
            self.finished = True 

    def render(self, display):
        display.blit(self.background_surface, (0, 0))
        display.blit(self.water_surface, (0, self.game.SCREEN_HEIGHT - self.water_surface.get_height()/2))

        if self.current_round == 1:
            display.blit(self.ground_surface, (0, self.ground_position))

        # Position the background vine appropriately
        vine_bg_x = 350 * self.game.SCREEN_WIDTH / 1920
        vine_bg_y = -120 * self.game.SCREEN_HEIGHT / 1280
        display.blit(self.background_vine, (vine_bg_x, vine_bg_y))

        for vine in self.vines:
            vine.draw(display, self.vine_surface)

        if self.current_round == 2:
            ground_x = 1700 * self.game.SCREEN_WIDTH / 1920
            ground_y = 875 * self.game.SCREEN_HEIGHT / 1280
            display.blit(self.ground_surface, (ground_x, ground_y))

        knight_surf = self.knight_surface_right if self.facing_right else self.knight_surface_left
        display.blit(knight_surf, self.knight_rect)

        font_size = int(50 * min(self.game.SCREEN_WIDTH / 1920, self.game.SCREEN_HEIGHT / 1280))
        font = pg.font.Font(None, font_size)
        round_text = font.render(f"Round: {self.current_round}/{self.max_rounds}", True, (255, 255, 255))
        display.blit(round_text, (20 * self.game.SCREEN_WIDTH / 1920, 20 * self.game.SCREEN_HEIGHT / 1280))

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
