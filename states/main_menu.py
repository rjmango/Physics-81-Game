import pygame
from states.state import State
from states.projectile import Projectile
from utils.button import Button

from .bossDialogue import BossDialogue
from .maze.mazeState import MazeState
from .vinestate import VineState
from IntroSequence.introsequenceclass import IntroSequence
from .introDialogue import IntroDialogue
from .vineDialogue import VineDialogue
from .mirrorDialogue import MirrorDialogue
from .mirrorstate import MirrorState

class MainMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.load_assets()
        # buttons
        scale = 0.5
        self.play_button = Button((self.game.SCREEN_WIDTH - 300)//2, 400, self.play_button_asset, scale)
        self.quit_button = Button((self.game.SCREEN_WIDTH - 300)//2, 520, self.quit_button_asset, scale)
        logo = logo_font = pygame.font.Font('font/LOGO.ttf', 100)
        self.logo_surface = logo_font.render('PHYSMORIA', True, 'Gold')
    
    def update(self, actions):
        pass

    def render(self, display):
        # render background in screen 
        display.blit(self.bg, (0,0))
        display.blit(self.logo_surface, (285, 200))
        

        if self.play_button.draw(display):
            self.game.main_menu_bgm.stop()
            # nextState = BossDialogue(self.game)
            # nextState = EndingDialogue(self.game)
            # nextState = Projectile(self.game)
            # nextState = VineState(self.game)
            # nextState = IntroDialogue(self.game)
            # nextState = VineDialogue(self.game)
            # nextState = MirrorDialogue (self.game)
            # nextState = MazeState(self.game)
            # nextState = MirrorState(self.game)
            nextState = IntroSequence(self.game)
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