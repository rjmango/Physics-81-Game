import pygame as pg
from ..state import State
import sys
import os
from .tilesheet import Tilesheet
from .settings import *
from .sprites import *
from .tilemap import *

WIDTH = 960
HEIGHT = 640

class MazeState(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500,100)
        self.load_assets()
        self.load_data()

       # Get path to terrain_tiles_v2.png relative to this file
        current_dir = os.path.dirname(__file__)  # .../game/states/maze
        tilesheet_path = os.path.abspath(
            os.path.join(current_dir, '..', '..', 'assets', 'stage 2', 'terrain_tiles_v2.png')
        )

        self.tiles = Tilesheet(tilesheet_path, 32, 32, 16, 10)
        self.paused = True
        self.finished = False

        self.new()

    def load_assets(self):
        self.paused_modal = self.game.load_background_asset("assets/popups/maze-start.png")

        self.finished_modal = self.game.load_background_asset("assets/popups/maze-end.png")

    def load_data(self):    
        game_folder = os.path.dirname(__file__)
        img_folder = os.path.join(game_folder, '..', '..', 'assets', 'stage 2')  # Adjust to correct folder
        map_path = os.path.join(game_folder, 'map2.txt')

        # Assuming Map is a class defined elsewhere
        self.map = Map(map_path)

        # Properly join the path to the image
        self.player_img = pg.image.load(os.path.join(img_folder, 'knight.png')).convert_alpha()
        
    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                #1 horizontal wall
                #2 horizontal wall left end
                #3 horizontal wall right end
                #4 vertical wall
                #5 vertical wall top end
                #6 vertical wall bottom end
                if tile == '1':
                    Horizontal_Wall(self, col, row)
                if tile == '2':
                    Horizontal_Left_End(self, col, row)
                if tile == '3':
                    Horizontal_Right_End(self, col, row)
                if tile == '4':
                    Vertical_Wall(self, col, row)
                if tile == '5':
                    Vertical_Top_Wall(self, col, row)
                if tile == '6':
                    Vertical_Bottom_Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'G':
                    Goal(self, col, row)
                #elif tile == '.':
                    #Floor(self, col, row)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    def show_congrats_screen(self):
        self.screen.fill(BLACK)
        font = pg.font.SysFont('Arial', 48)
        text_surface = font.render("Congratulations! You reached the end!", True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pg.display.flip()
        pg.time.wait(3000)  # Show for 3 seconds before continuing

    def quit(self):
        pg.quit()
        sys.exit()
    
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
        
        if self.finished:
            if keys[pygame.K_RETURN]:
                self.exit_state()

        self.dt = self.clock.tick(FPS) / 1000
        self.all_sprites.update()  # Update all sprites (including player)
        self.camera.update(self.player)
        goal_hit = pg.sprite.spritecollideany(self.player, [s for s in self.all_sprites if isinstance(s, Goal)])
        if goal_hit:
            self.finished = True
            self.playing = False  # End the current game loop
            
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, BROWN, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, BROWN, (0, y), (WIDTH, y))
        
    def render(self, display):
        self.draw(display)
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

    def draw(self, display):
        display.fill(BGCOLOR)
        #self.draw_grid()
        for sprite in self.all_sprites:
            display.blit(sprite.image, self.camera.apply(sprite))
    
        #self.screen.blit(self.tiles.get_tile(3,5), (72, 72))
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
    
    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

if __name__ == "__main__":
    # create the game object
    g = MazeState()
    g.show_start_screen()
    while True:
        g.new()
        g.run()
        g.show_go_screen()
