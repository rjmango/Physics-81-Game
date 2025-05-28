import pygame
import os

from states.main_menu import MainMenu
# check newlymade state


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game")
        
        # Window display information
        self.GAME_W, self.GAME_H = 1920, 1280
        print(f"Game Dimensions: {self.GAME_W} x {self.GAME_H}")
        self.SCREEN_WIDTH = pygame.display.Info().current_w * 6 // 8
        self.SCREEN_HEIGHT = self.SCREEN_WIDTH * 2//3
        print(f"Game Dimensions: {self.SCREEN_WIDTH} x {self.SCREEN_HEIGHT}")
        self.game_canvas = pygame.Surface((self.GAME_W, self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        # Game logic information
        self.running = True
        self.state_stack = []
        self.bossDefeated = False
        self.bossDefeatedChanged = False

        self.actions = {"SPACE": False, "LEFT": False, "RIGHT": False, "UP": False, "DOWN": False, "R": False}

        # initialize dependencies
        self.load_assets()
        self.load_state()
        self.load_sfx()

        # Play background music
        self.main_menu_bgm.play(-1)
        pygame.mixer.music.set_volume(0.8)
    
    def game_loop(self):
        while self.running:
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                if event.key == pygame.K_SPACE:
                    self.actions["SPACE"] = True
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT"] = True
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT"] = True
                if event.key == pygame.K_UP:
                    self.actions["UP"] = True
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN"] = True
                if event.key == pygame.K_r:
                    self.actions["R"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.actions["SPACE"] = False
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT"] = False
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT"] = False
                if event.key == pygame.K_UP:
                    self.actions["UP"] = False
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN"] = False
                if event.key == pygame.K_r:
                    self.actions["R"] = False

    def update(self):
        self.state_stack[-1].update(self.actions)
    
    def render(self):
        self.state_stack[-1].render(self.game_canvas)

        # Render current state to the screen
        # render = pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # print(render.get_width(), render.get_height())
        self.screen.blit(self.game_canvas, (0,0))
        pygame.display.flip()
    
    def load_assets(self):
        # create pointers to directories
        self.assets_dir = os.path.join("assets")
    
    def load_state(self):
        self.main_menu = MainMenu(self)

        # for testing only !!!
        # self.main_menu = <state name>(self)
        self.main_menu = MainMenu(self)
        self.state_stack.append(self.main_menu)
    
    def load_background_asset(self, filepath):
        bg_asset = pygame.image.load(filepath).convert_alpha()
        scaled_asset = pygame.transform.scale(bg_asset, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        return scaled_asset
    
    def load_sfx(self):
        self.main_menu_bgm = pygame.mixer.Sound('assets/sfx/main-menu-bgm.mp3')
        self.projectile_boss_bgm = pygame.mixer.Sound('assets/sfx/projectile-bgm.mp3')
        self.pre_boss_bgm = pygame.mixer.Sound('assets/sfx/pre-boss-fight.mp3')
        self.post_boss_bgm = pygame.mixer.Sound('assets/sfx/post-boss-fight.wav')
    
if __name__ == "__main__":
    game = Game()
    game.game_loop()