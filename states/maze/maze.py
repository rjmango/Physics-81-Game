import pygame as pg
import sys
from tilesheet import Tilesheet
from os import path
from settings import *
from sprites import *
from tilemap import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500,100)
        self.load_data()

        self.tiles = Tilesheet(r'C:\Users\Norvel\Desktop\Code\GithubPhysics\Pygame-learn\maze\tileset\terrain_tiles_v2.png', 32, 32, 16, 10)

    def load_data(self):    
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'tileset')  
        self.map= Map(path.join(game_folder, 'map2.txt'))
        self.player_img = pg.image.load('tileset\kneght.png').convert_alpha()

        
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

    def quit(self):
        pg.quit()
        sys.exit()
    
    def update(self):
        self.all_sprites.update()  # Update all sprites (including player)
        self.camera.update(self.player) 

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, BROWN, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, BROWN, (0, y), (WIDTH, y))
        

    def draw(self):
        self.screen.fill(BGCOLOR)
        #self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
    
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

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
