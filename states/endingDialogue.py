from .state import State
from .projectile import Projectile
from utils.spritesheet import SpriteSheet
import pygame
from pygame import mixer
import time

mixer.init()
blipSound = mixer.Sound('assets/sfx/dialogue-blip.mp3')

class EndingDialogue(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.initialize_state()

    def initialize_state(self):
        self.game.ending_dialogue_bgm.play(-1)
        self.load_assets()
        # Other parts sa code

        self.current_knight_frame = 0
        self.current_princess_frame = 0
        self.last_time_updated = 0
        self.previous_time = time.time()
        self.knight_turn = True
        self.both_turn = False
        self.space_pressed = False

        # Dialogue information
        file = open('assets/dialogues/resolution.txt', 'r')
        self.dialogue = file.readlines()
        file.close()

        self.dialogue_font = pygame.font.Font('assets/fonts/MinecraftRegular-Bmg3.otf', 36)  # Custom font
        self.current_dialogue_number = 0
        self.current_dialogue: str = self.dialogue[self.current_dialogue_number]

        
    
    def update(self, actions):
        if self.game.bossDefeatedChanged:
            self.initialize_state()
            self.game.bossDefeatedChanged = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if not self.space_pressed:  # Only trigger when space was not pressed before
                blip = blipSound
                blip.play()
                self.current_dialogue_number = (self.current_dialogue_number+1)
                self.space_pressed = True

                if self.current_dialogue_number == len(self.dialogue):
                    self.exit_state()
                    self.game.ending_dialogue_bgm.stop()
                    return
                
                self.current_dialogue = self.dialogue[self.current_dialogue_number]
                if self.current_dialogue.split(": ")[0] == "Knight":
                    self.knight_turn = True
                    self.both_turn = False
                elif self.current_dialogue.split(": ")[0] == "Princess":
                    self.knight_turn = False
                    self.both_turn = False
                else:
                    self.both_turn = True
        else:
            self.space_pressed = False  # Reset when space is released
        
        # Code for updating values
        now = time.time()
        self.last_time_updated += now - self.previous_time
        self.previous_time = now

        if self.last_time_updated > 0.2:
            self.last_time_updated = 0
            self.current_knight_frame = (self.current_knight_frame+1) % 6
            self.current_princess_frame = (self.current_princess_frame+1) % 5

    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.split(' ')  # Split text into individual words
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])  # Create a test line
            # Check if this line would be too wide
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)  # Keep adding to current line
            else:
                lines.append(' '.join(current_line))  # Finalize current line
                current_line = [word]  # Start new line with current word
        
        # Add the last remaining line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def render_dialogue(self, text, display):
        dialogue_box = pygame.Surface((self.game.SCREEN_WIDTH, 250), pygame.SRCALPHA)
        dialogue_box.fill((255, 255, 255, 200))
        
        wrapped_text = self.wrap_text(text, self.dialogue_font, self.game.SCREEN_WIDTH - 50)
        
        y_pos = 20
        for line in wrapped_text:
            text_surface = self.dialogue_font.render(line, True, (0, 0, 0))
            dialogue_box.blit(text_surface, (20, y_pos))
            y_pos += self.dialogue_font.get_linesize()
        
        prompt_text = self.dialogue_font.render("Press SPACE to continue", True, "black") 
    
        # Position at bottom-right with margin
        prompt_pos = (
            dialogue_box.get_width() - prompt_text.get_width() - 40,  # Right-aligned with 20px margin
            dialogue_box.get_height() - prompt_text.get_height() - 20  # Bottom with 10px margin
        )
        dialogue_box.blit(prompt_text, prompt_pos)
        
        # Draw the complete dialogue box
        display.blit(dialogue_box, (0, self.game.SCREEN_HEIGHT - 250))

    def render(self, display):
        # Code for displaying screens
        # render background in screen
        display.blit(self.bg, (0,0))

        if self.both_turn:
            knightImage = self.knight_sprites[self.current_knight_frame]
            princessImage = self.princess_sprites[self.current_princess_frame]
        else:
            if self.knight_turn:
                knightImage = self.knight_sprites[self.current_knight_frame]
                princessImage = self.princess_inactive_sprites[self.current_princess_frame]
            else:
                knightImage = self.knight_inactive_sprites[self.current_knight_frame]
                princessImage = self.princess_sprites[self.current_princess_frame]

        knightDisplay = pygame.transform.scale(knightImage, (112*8, 96*8))
        princessDisplay = pygame.transform.scale(princessImage, (80*11, 64*11))
        
        left_sprite_x, left_sprite_y = -1 * self.game.SCREEN_WIDTH/4.1, -1 * self.game.SCREEN_HEIGHT/4.55
        right_sprite_x, right_sprite_y = self.game.SCREEN_WIDTH/2.925, -1 * self.game.SCREEN_HEIGHT/6.82
        
        display.blit(knightDisplay, (left_sprite_x, left_sprite_y))
        display.blit(princessDisplay, (right_sprite_x, right_sprite_y))

        # Create transparent surface
        transparent_surface = pygame.Surface((self.game.SCREEN_WIDTH, 250), pygame.SRCALPHA)

        # Draw a semi-transparent rectangle
        pygame.draw.rect(transparent_surface, (255, 255, 255, 200), 
                        (0, 0, self.game.SCREEN_WIDTH, 250))

        if ": " in self.current_dialogue:
            self.current_dialogue = self.current_dialogue.split(": ")[1]
        self.render_dialogue(self.current_dialogue, display)

    def load_assets(self):
        # Load background by changing parameter
        self.bg = self.game.load_background_asset("assets/bg/cellar.jpg")
        # Example
        # self.bg = self.game.load_background_asset("assets/bg/new-bg.png")

        # load other assets
        
        self.princess_sprites,  self.knight_sprites = [], []
        self.princess_inactive_sprites, self.knight_inactive_sprites = [], []

        knight_idle_sprite_source = pygame.image.load("assets/sprites/knight-idle.png").convert_alpha()    
        knight_idle_inactive_sprite_source = pygame.image.load("assets/sprites/knight-idle-inactive.png").convert_alpha()

        princess_idle_sprite_source = pygame.image.load("assets/sprites/princess.png").convert_alpha()
        princess_idle_inactive_sprite_source = pygame.image.load("assets/sprites/princess-inactive.png").convert_alpha()

        knight_spritesheet = SpriteSheet(knight_idle_sprite_source)
        knight_inactive_spritesheet = SpriteSheet(knight_idle_inactive_sprite_source)
        princess_spritesheet = SpriteSheet(princess_idle_sprite_source)
        princess_inactive_spritesheet = SpriteSheet(princess_idle_inactive_sprite_source)

        for i in range(5):
            self.princess_sprites.append(princess_spritesheet.get_image(i, 80, 64, 1, None))
            self.princess_inactive_sprites.append(princess_inactive_spritesheet.get_image(i, 80, 64, 1, None))
        
        for i in range(6):
            self.knight_sprites.append(knight_spritesheet.get_image(i, 112, 96, 1, None))
            self.knight_inactive_sprites.append(knight_inactive_spritesheet.get_image(i, 112, 96, 1, None))
