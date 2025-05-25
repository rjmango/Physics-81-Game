import pygame
from states.state import State
from states.projectile import Projectile
from utils.button import Button

from states.bossDialogue import BossDialogue

class MainMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_assets()
        # buttons
        scale = 0.5
        self.play_button = Button((self.game.SCREEN_WIDTH - 300)//2, 400, self.play_button_asset, scale)
        self.quit_button = Button((self.game.SCREEN_WIDTH - 300)//2, 520, self.quit_button_asset, scale)
    
    def update(self, actions):
        pass

    def render(self, display):
        # render background in screen 
        display.blit(self.bg, (0,0))

        if self.play_button.draw(display):
            self.game.main_menu_bgm.stop()
            nextState = BossDialogue(self.game)
            # projectileState = Projectile(self.game)
            # projectileState = Game(self.game)
            nextState.enter_state()
        if self.quit_button.draw(display):
            print("quit")
            self.game.running = False

    def load_assets(self):
        # bg asset
        self.bg = self.game.load_background_asset("assets/bg/main-menu-bg.png")

        # button assets
        self.play_button_asset = pygame.image.load("assets/buttons/start-button.png").convert_alpha()
        self.quit_button_asset = pygame.image.load("assets/buttons/quit-button.png").convert_alpha()