import pygame
from states.state import State
from utils.button import Button

class MainMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_assets()

        # buttons
        scale = 0.5
        self.play_button = Button(200, 200, self.play_button_asset, scale)
        self.quit_button = Button(200, 400, self.quit_button_asset, scale)

    def update(self):
        pass

    def render(self, display):
        # load background
        display.blit(self.bg, (0,0))
        self.play_button.draw(display)
        self.quit_button.draw(display)

    def load_assets(self):
        # bg asset
        self.bg = pygame.image.load("assets/bg/main-menu-bg.png").convert_alpha()

        # button assets
        self.play_button_asset = pygame.image.load("assets/buttons/start-button.png").convert_alpha()
        self.quit_button_asset = pygame.image.load("assets/buttons/quit-button.png").convert_alpha()