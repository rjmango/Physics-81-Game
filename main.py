import pygame
import os

from states.main_menu import MainMenu

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game")
        
        # Window display information
        self.GAME_W, self.GAME_H = 1920/2, 1280/2
        self.SCREEN_WIDTH = pygame.display.Info().current_w * 6 // 8
        self.SCREEN_HEIGHT = self.SCREEN_WIDTH * 2//3
        self.game_canvas = pygame.Surface((self.GAME_W, self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        # Game logic information
        self.running = True
        self.state_stack = []

        # initialize dependencies
        self.load_assets()
        self.load_state()
    
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

    def update(self):
        self.state_stack[-1].update()
    
    def render(self):
        self.state_stack[-1].render(self.game_canvas)

        # Render current state to the screen
        render = pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.blit(render, (0,0))
        pygame.display.flip()
    
    def load_assets(self):
        # create pointers to directories
        self.assets_dir = os.path.join("assets")
    
    def load_state(self):
        self.main_menu = MainMenu(self)
        self.state_stack.append(self.main_menu)
    
if __name__ == "__main__":
    game = Game()
    game.game_loop()