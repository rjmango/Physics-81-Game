import pygame
import sys
import os
import math
from os import path
from .state import State
from .bossDialogue import BossDialogue

# Constants
ORIGINAL_WIDTH = 1280
ORIGINAL_HEIGHT = 853
FPS = 60
BASE_TILESIZE = 110
BROWN = (181, 151, 108)
SHOW_CONGRATS_EVENT = pygame.USEREVENT + 1

class MirrorState(State):
    def __init__(self, game, screen_width=1280, screen_height=853):
        State.__init__(self, game)
        self.original_width = ORIGINAL_WIDTH
        self.original_height = ORIGINAL_HEIGHT
        self.screen_width = self.game.SCREEN_WIDTH
        self.screen_height = self.game.SCREEN_HEIGHT
        self.game.laser_bgm.play(-1)

        self.paused = True
        self.finished = False
        
        # Calculate scaling factors
        self.width_scale = self.screen_width / self.original_width
        self.height_scale = self.screen_height / self.original_height
        self.scale = min(self.width_scale, self.height_scale)
        
        # Scale tile size
        self.tile_size = int(BASE_TILESIZE * self.scale)
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.light_beam = None
        self.showing_congrats = False
        self.load_data()
        self.load_background()
        self.new()

    def load_data(self):    
        game_folder = path.dirname(__file__)
        self.map = Map(path.join(game_folder, 'mirrortile.txt'), self.tile_size)

    def load_background(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, '..', 'assets', 'stage 2', 'test.png')
        bg_path = os.path.normpath(bg_path)
        self.background = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.paused_modal = self.game.load_background_asset("assets/popups/mirror-start.png")
        self.finished_modal = self.game.load_background_asset("assets/popups/mirror-end.png")

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                x = col * self.tile_size
                y = row * self.tile_size
                if tile == 'M':
                    Mirror(self, x, y, angle=45)
                elif tile == '#':
                    Wall(self, x, y)
                elif tile == 'O':
                    Orb(self, x, y)
        
        self.light_beam = LightBeam(self, (0, self.screen_height // 2 - 30), (1, 0), max_bounces=10)

    def handle_mirror_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for mirror in self.walls:  # Assuming walls is accessible in state
                if isinstance(mirror, Mirror) and mirror.rect.collidepoint(event.pos):
                    mirror.dragging = True
                    return True  # Event consumed
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            for mirror in self.walls:
                if isinstance(mirror, Mirror):
                    mirror.dragging = False
            return True  # Event consumed
        
        elif event.type == SHOW_CONGRATS_EVENT:
            if not self.showing_congrats:
                self.showing_congrats = True
            return True
            
        return False  # Event not consumed by this state
    
    def congratulations(self, display):
        font = pygame.font.SysFont("arial", int(72 * self.scale))
        message = font.render("Congratulations!", True, (255, 255, 0))
        rect = message.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        display.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        # self.screen.blit(message, rect)
        pygame.display.flip()
        pygame.time.wait(3000)


    def update(self, actions):
        keys = pygame.key.get_pressed()

        if not self.paused:
            if keys[pygame.K_TAB]:
                self.game.blip.play()
                self.paused = True
        
        if self.paused:
            if keys[pygame.K_RETURN]:
                self.game.blip.play()
                self.paused = False
            return
        
        if self.showing_congrats:
            if keys[pygame.K_RETURN]:
                self.game.blip.play()
                self.game.laser_bgm.stop()
                newState = BossDialogue(self.game)
                self.exit_state()
                newState.enter_state()
            
        self.all_sprites.update()

    def draw(self, display):
        display.blit(self.background, (0, 0))
        self.all_sprites.draw(display)
        if self.light_beam:
            self.light_beam.draw(display)
        
        if self.showing_congrats:
            self.congratulations(display)

        pygame.display.flip()

    def render(self, display):
        if self.paused:
            image_width, image_height = self.paused_modal.get_size()
            x_centered = self.game.SCREEN_WIDTH // 2 - image_width // 2
            y_centered = self.game.SCREEN_HEIGHT // 2 - image_height // 2
            display.blit(self.paused_modal, (x_centered,y_centered))
            return

        if self.showing_congrats:
            image_width, image_height = self.finished_modal.get_size()
            x_centered = self.game.SCREEN_WIDTH // 2 - image_width // 2
            y_centered = self.game.SCREEN_HEIGHT // 2 - image_height // 2
            display.blit(self.finished_modal, (x_centered,y_centered))
            return
        
        self.draw(display)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

class Map:
    def __init__(self, filename, tile_size):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        self.tile_size = tile_size
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * tile_size
        self.height = self.tileheight * tile_size

class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((game.tile_size, game.tile_size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Orb(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        base_path = os.path.dirname(os.path.abspath(__file__))
        orb_path = os.path.join(base_path, '..', 'assets', 'stage 2', 'orb.png')
        orb_size = int(game.tile_size * 1.45)
        
        if os.path.exists(orb_path):
            self.image = pygame.image.load(orb_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (orb_size, orb_size))
        else:
            self.image = pygame.Surface((orb_size, orb_size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 255, 255), (orb_size//2, orb_size//2), orb_size//3)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x + int(12 * game.scale), y - int(25 * game.scale))
        self.triggered = False
        self.hit_start_time = None

class Mirror(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle=45):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        base_path = os.path.dirname(os.path.abspath(__file__))
        mirror_path = os.path.join(base_path, '..', 'assets', 'stage 2', 'mirror.png')
        
        scale_factor = 2.25 * game.scale
        self.original_image = pygame.image.load(mirror_path).convert_alpha()
        new_size = int(game.tile_size * scale_factor)
        self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))
        
        self.image = self.original_image.copy()
        self.rect = self.original_image.get_rect()
        self.rect.center = (x + game.tile_size//2 - 20, y + game.tile_size//2 - 40)
        self.angle = angle
        self.dragging = False
        self.rotate_to(angle)

    def update(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.rect.centerx
            dy = mouse_y - self.rect.centery
            self.angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
            self.rotate_to(self.angle)

    def rotate_to(self, angle):
        self.angle = angle % 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_surface_line(self):
        length = self.rect.width - int(10 * self.game.scale)
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * length / 2
        dy = math.sin(angle_rad) * length / 2
        x, y = self.rect.center
        return ((x - dx, y - dy), (x + dx, y + dy))

    def get_normal(self, incoming_dir):
        (x1, y1), (x2, y2) = self.get_surface_line()
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        surface_vec = (dx / length, dy / length)
        normal1 = (-surface_vec[1], surface_vec[0])
        normal2 = (surface_vec[1], -surface_vec[0])
        dot1 = incoming_dir[0]*normal1[0] + incoming_dir[1]*normal1[1]
        dot2 = incoming_dir[0]*normal2[0] + incoming_dir[1]*normal2[1]
        return normal1 if dot1 < dot2 else normal2

class LightBeam:
    def __init__(self, game, start_pos, direction, max_bounces=5):
        self.game = game
        self.start_pos = start_pos
        length = math.hypot(direction[0], direction[1])
        self.direction = (direction[0]/length, direction[1]/length)
        self.max_bounces = max_bounces

    def reflect(self, direction, normal):
        dot = direction[0]*normal[0] + direction[1]*normal[1]
        return (
            direction[0] - 2 * dot * normal[0],
            direction[1] - 2 * dot * normal[1]
        )

    def cast(self):
        points = [self.start_pos]
        pos = self.start_pos
        direction = self.direction

        for _ in range(self.max_bounces):
            closest_object = None
            closest_point = None
            is_reflective = False
            min_dist = float("inf")
            ray_end = (pos[0] + direction[0] * 2000, pos[1] + direction[1] * 2000)

            for obj in self.game.walls:
                if isinstance(obj, Mirror):
                    mirror_line = obj.get_surface_line()
                    hit_point = self.line_intersection((pos, ray_end), mirror_line)
                    if hit_point:
                        dist = math.dist(pos, hit_point)
                        if dist < min_dist:
                            min_dist = dist
                            closest_point = hit_point
                            closest_object = obj
                            is_reflective = True

            for obj in self.game.walls:
                if isinstance(obj, Wall):
                    wall_point = self.line_rect_intersect(pos, ray_end, obj.rect)
                    if wall_point:
                        dist = math.dist(pos, wall_point)
                        if dist < min_dist:
                            min_dist = dist
                            closest_point = wall_point
                            closest_object = obj
                            is_reflective = False

            if closest_point:
                points.append(closest_point)
                if is_reflective:
                    normal = closest_object.get_normal(direction)
                    dot = direction[0] * normal[0] + direction[1] * normal[1]
                    if abs(dot) > 0.98:
                        break
                    direction = self.reflect(direction, normal)
                    pos = closest_point
                else:
                    break
            else:
                points.append(ray_end)
                break

        for sprite in self.game.all_sprites:
            if isinstance(sprite, Orb) and not sprite.triggered:
                for i in range(len(points) - 1):
                    beam_segment = (points[i], points[i+1])
                    if self.line_rect_intersect(beam_segment[0], beam_segment[1], sprite.rect):
                        current_time = pygame.time.get_ticks()
                        if sprite.hit_start_time is None:
                            sprite.hit_start_time = current_time
                        elif current_time - sprite.hit_start_time >= 1000 and not sprite.triggered:
                            sprite.triggered = True
                            print("AMEN")
                            pygame.event.post(pygame.event.Event(SHOW_CONGRATS_EVENT))
                        break

        return points

    def draw(self, screen):
        points = self.cast()
        if len(points) > 1:
            pygame.draw.lines(screen, (255, 255, 0), False, points, int(8 * self.game.scale))

    def line_rect_intersect(self, start, end, rect):
        edges = [
            ((rect.left, rect.top), (rect.right, rect.top)),
            ((rect.right, rect.top), (rect.right, rect.bottom)),
            ((rect.right, rect.bottom), (rect.left, rect.bottom)),
            ((rect.left, rect.bottom), (rect.left, rect.top))
        ]
        for edge in edges:
            point = self.line_intersection((start, end), edge)
            if point:
                return point
        return None

    def line_intersection(self, seg1, seg2):
        (x1, y1), (x2, y2) = seg1
        (x3, y3), (x4, y4) = seg2

        denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        if denom == 0:
            return None

        px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

        if (min(x1,x2) <= px <= max(x1,x2) and min(y1,y2) <= py <= max(y1,y2) and
            min(x3,x4) <= px <= max(x3,x4) and min(y3,y4) <= py <= max(y3,y4)):
            return (px, py)
        return None

if __name__ == "__main__":
    # Create game with desired dimensions
    game = MirrorState(1024, 682)  # Original size
    # game = Game(1920, 1080)  # HD
    # game = Game(800, 600)    # Smaller window
    game.run()