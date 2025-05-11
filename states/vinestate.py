import pygame as pg
import sys
from os import path

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

class GameState:
    def __init__(self, game):
        self.game = game 
        self.prev_state = None 
        
        self.load_assets()
        
        self.knight_rect = self.knight_surface.get_rect(bottomleft=(0, 1120))
        self.Angvine_rect = self.Angvine_surface.get_rect(midbottom=(500, 900))
        self.score_rect = self.score_surf.get_rect(center=(990, 150))
        
        self.knight_gravity = 0
        self.on_vine = False

    def load_assets(self):
        """Load all game assets"""
        asset = lambda p: path.join('assets', 'stage 1', p)
        
        self.vine_surface = pg.image.load(asset('pixelvinebg.png')).convert_alpha()
        self.water_surface = pg.image.load(asset('water(resized).png')).convert_alpha()
        self.ground_surface = pg.image.load(asset('image-removebg-preview.png')).convert_alpha()
        self.knight_surface = pg.image.load(asset('knightpix.png')).convert_alpha()
        self.Angvine_surface = pg.image.load(asset('masgamay.png')).convert_alpha()
        
        self.test_font = pg.font.Font(asset('Pixeltype.ttf'), 50)
        self.score_surf = self.test_font.render('Jump and avoid falling on the water!', False, (64, 64, 64))

    def update(self, actions):
        if actions["quit"]:
            pg.quit()
            exit()
            
        # Handle input
        if actions.get("mouse_click") and self.knight_rect.collidepoint(pg.mouse.get_pos()):
            if self.knight_rect.bottom >= 1120 or self.on_vine:
                self.knight_gravity = -25
                
        if actions.get("space") and (self.knight_rect.bottom >= 1120 or self.on_vine):
            self.knight_gravity = -25

        # Update physics
        self.knight_gravity += 1
        self.knight_rect.y += self.knight_gravity
        self.on_vine = False
        
        # Check collisions
        if self.knight_rect.colliderect(self.Angvine_rect) and self.knight_gravity >= 0:
            if self.knight_rect.bottom <= self.Angvine_rect.top + 10:
                self.knight_rect.bottom = self.Angvine_rect.top
                self.knight_gravity = 0
                self.on_vine = True

        if not self.on_vine and self.knight_rect.bottom >= 1120:
            self.knight_rect.bottom = 1120
            self.knight_gravity = 0

        # Move vine
        self.Angvine_rect.x += 3
        if self.Angvine_rect.right > 1000:
            self.Angvine_rect.left = 100

    def render(self, display):
        
        # Draw backgrounds
        display.blit(self.vine_surface, (0, 0))
        display.blit(self.water_surface, (0, 1080))
        display.blit(self.ground_surface, (0, 900))
        
        # Draw UI elements
        display.blit(self.score_surf, self.score_rect)
        pg.draw.rect(display, '#c0e8ec', self.score_rect, 9)
        
        # Draw characters
        display.blit(self.knight_surface, self.knight_rect)
        display.blit(self.Angvine_surface, self.Angvine_rect)
