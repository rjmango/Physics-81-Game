import pygame
import sys
import os
import math

from os import path

# Constants
SCREEN_WIDTH = 1280 #1920 1280 720
SCREEN_HEIGHT = 853 #1280 853 480
FPS = 60
TILESIZE = 110
BROWN = (181, 151, 108)
SHOW_CONGRATS_EVENT = pygame.USEREVENT + 1 

import pygame
import math

class LightBeam:
    def __init__(self, game, start_pos, direction, max_bounces=5):
        self.game = game
        self.start_pos = start_pos
        length = math.hypot(direction[0], direction[1])
        self.direction = (direction[0]/length, direction[1]/length)
        self.max_bounces = max_bounces

    def reflect(self, direction, normal):
        # Reflect direction over normal
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

            # Create a long ray
            ray_end = (pos[0] + direction[0] * 2000, pos[1] + direction[1] * 2000)

            # Check mirrors (reflective)
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

            # Check walls (non-reflective)
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
                    if abs(dot) > 0.98:  # if almost parallel, don't reflect again
                        break
                    direction = self.reflect(direction, normal)
                    pos = closest_point
                else:
                    break  # hit a wall, stop
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
                            pygame.event.post(pygame.event.Event(SHOW_CONGRATS_EVENT))
                        break

        return points


    def draw(self, screen):
        points = self.cast()
        if len(points) > 1:
            pygame.draw.lines(screen, (255, 255, 0), False, points, 8)

    def line_rect_intersect(self, start, end, rect):
        # Basic 2D line intersection with rectangle sides
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

    def check_collision(self, ray, target_rect):
        # Simple side-based collision (treat as axis-aligned)
        lines = [
            ((target_rect.left, target_rect.top), (target_rect.right, target_rect.top), (0, -1)),
            ((target_rect.right, target_rect.top), (target_rect.right, target_rect.bottom), (1, 0)),
            ((target_rect.right, target_rect.bottom), (target_rect.left, target_rect.bottom), (0, 1)),
            ((target_rect.left, target_rect.bottom), (target_rect.left, target_rect.top), (-1, 0)),
        ]
        closest_point = None
        normal = (0, 0)
        min_dist = float("inf")

        for (p1, p2, n) in lines:
            point = self.line_intersection((ray.topleft, (ray.right, ray.bottom)), (p1, p2))
            if point:
                dist = math.dist(ray.topleft, point)
                if dist < min_dist:
                    closest_point = point
                    normal = n
                    min_dist = dist

        return closest_point is not None, normal, closest_point
    
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)  # Enable per-pixel alpha
        self.image.fill((0, 0, 0, 0))  # Fully transparent
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)

class Orb(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        base_path = os.path.dirname(os.path.abspath(__file__))
        orb_path = os.path.join(base_path, '..', 'assets', 'stage 2', 'orb.png')
        if os.path.exists(orb_path):
            self.image = pygame.image.load(orb_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE+50, TILESIZE+50))
        else:
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 255, 255), (TILESIZE // 2, TILESIZE // 2), TILESIZE // 3)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE + 12, y * TILESIZE - 25)

        # ✅ This line is required:
        self.triggered = False
        self.hit_start_time = None

class Mirror(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle=45):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.original_image = pygame.image.load(os.path.join(base_path, '..', 'assets', 'stage 2', 'mirror.png')).convert_alpha()

        scale_factor = 2.0  # adjust this as you like (e.g., 1.2, 1.5, 2.0)
        new_size = int(TILESIZE * scale_factor)
        self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))


        self.image = self.original_image.copy()
        self.rect = self.original_image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (x * TILESIZE, y * TILESIZE)

        self.angle = angle
        self.dragging = False

    def update(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.rect.centerx
            dy = mouse_y - self.rect.centery
            self.angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360  # Clockwise
            self.rotate_to(self.angle)

    def rotate_to(self, angle):
        self.angle = angle % 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_surface_line(self):
        length = self.rect.width - 10  # Add buffer to extend the line slightly
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

        # Get both possible normals (perpendiculars)
        normal1 = (-surface_vec[1], surface_vec[0])
        normal2 = (surface_vec[1], -surface_vec[0])

        # Pick the normal that faces against the incoming direction
        dot1 = incoming_dir[0]*normal1[0] + incoming_dir[1]*normal1[1]
        dot2 = incoming_dir[0]*normal2[0] + incoming_dir[1]*normal2[1]

        return normal1 if dot1 < dot2 else normal2

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Background with Class")
        self.clock = pygame.time.Clock()
        self.running = True
        self.light_beam = LightBeam(self, (0, SCREEN_HEIGHT // 2), (1, 0), max_bounces=10)
        # Construct the correct path to the background image
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, '..', 'assets', 'stage 2', 'test.png')
        bg_path = os.path.normpath(bg_path)
        self.background = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.showing_congrats = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for mirror in self.walls:
                    if mirror.rect.collidepoint(event.pos):
                        mirror.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                for mirror in self.walls:
                    mirror.dragging = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == SHOW_CONGRATS_EVENT:
                if not self.showing_congrats:
                    self.showing_congrats = True
                    self.congratulations()
                    pygame.time.set_timer(SHOW_CONGRATS_EVENT, 0)  # stop the timer

    def load_data(self):    
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'tileset')  
        self.map= Map(path.join(game_folder, 'mirrortile.txt'))

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'M':
                    Mirror(self, col, row, angle=45)  # Default diagonal
                elif tile == '#':
                    Wall(self, col, row)
                elif tile == 'O':  # <- add this!
                    Orb(self, col, row)

    def congratulations(self):
        font = pygame.font.SysFont("arial", 72)
        message = font.render("Congratulations!", True, (255, 255, 0))
        rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.screen.blit(message, rect)
        pygame.display.flip()
        
        pygame.time.wait(3000)

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.light_beam.draw(self.screen)
        #self.draw_grid()
        pygame.display.flip()

    def draw_grid(self):
        # Create a transparent surface the size of the screen
        grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        transparent_brown = (181, 151, 108, 60)  # RGBA - the last number is alpha (0-255)

        for x in range(0, SCREEN_WIDTH, TILESIZE):
            pygame.draw.line(grid_surface, transparent_brown, (x, 0), (x, SCREEN_HEIGHT))

        for y in range(0, SCREEN_HEIGHT, TILESIZE):
            pygame.draw.line(grid_surface, transparent_brown, (0, y), (SCREEN_WIDTH, y))

        # Blit the grid onto the main screen
        self.screen.blit(grid_surface, (0, 0))
        

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.load_data()
    game.new()
    game.run()

