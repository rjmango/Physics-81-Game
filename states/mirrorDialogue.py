from .state import State
from .projectile import Projectile
from utils.spritesheet import SpriteSheet
from .mirrorstate import MirrorState
import pygame
from pygame import mixer
import time

mixer.init()
blipSound = mixer.Sound('assets/sfx/dialogue-blip.mp3')

class MirrorDialogue(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.initialize_state()

    def initialize_state(self):
        self.game.mirror_dialogue_bgm.play(-1)
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
        file = open('assets/dialogues/mirrorStage.txt', 'r')
        self.dialogue = file.readlines()
        file.close()

        self.dialogue_font = pygame.font.Font('assets/fonts/MinecraftRegular-Bmg3.otf', 36)  # Custom font
        self.current_dialogue_number = 0
        self.current_dialogue: str = self.dialogue[self.current_dialogue_number]

        
    
    def update(self, actions):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if not self.space_pressed:  # Only trigger when space was not pressed before
                blip = blipSound
                blip.play()
                self.current_dialogue_number = (self.current_dialogue_number+1)
                self.space_pressed = True

                if self.current_dialogue_number == len(self.dialogue):
                    newState = MirrorState(self.game)
                    self.exit_state()
                    self.game.mirror_dialogue_bgm.stop()
                    newState.enter_state()
                    return
                
                self.current_dialogue = self.dialogue[self.current_dialogue_number]
                if self.current_dialogue.split(": ")[0] == "Knight":
                    self.knight_turn = True
                    self.both_turn = False
                elif self.current_dialogue.split(": ")[0] == "Wizard":
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
            wizardImage = self.wizard_sprites[self.current_princess_frame]
        else:
            if self.knight_turn:
                knightImage = self.knight_sprites[self.current_knight_frame]
                wizardImage = self.wizard_inactive_sprites[self.current_princess_frame]
            else:
                knightImage = self.knight_inactive_sprites[self.current_knight_frame]
                wizardImage = self.wizard_sprites[self.current_princess_frame]

        scaled_knight_width = int(self.game.SCREEN_WIDTH / 1.1428)
        scaled_knight_height = int(self.game.SCREEN_HEIGHT / 0.888)

        scaled_wizard_dimensions = int(self.game.SCREEN_WIDTH / 0.6826)

        knightDisplay = pygame.transform.scale(knightImage, (scaled_knight_width, scaled_knight_height))
        wizardDisplay = pygame.transform.scale(wizardImage, (scaled_wizard_dimensions, scaled_wizard_dimensions))
        wizardDisplay = pygame.transform.flip(wizardDisplay, 1, 0)        
        
        left_sprite_x, left_sprite_y = -1 * self.game.SCREEN_WIDTH/4.1, -1 * self.game.SCREEN_HEIGHT/4.55
        right_sprite_x, right_sprite_y = self.game.SCREEN_WIDTH/20.48, -1 * self.game.SCREEN_HEIGHT/1.515

        display.blit(knightDisplay, (left_sprite_x, left_sprite_y))
        display.blit(wizardDisplay, (right_sprite_x, right_sprite_y))

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
        self.bg = self.game.load_background_asset("assets/bg/mirror-dialogue-bg.png")
        # Example
        # self.bg = self.game.load_background_asset("assets/bg/new-bg.png")

        # load other assets
        
        self.wizard_sprites, self.knight_sprites = [], []
        self.wizard_inactive_sprites, self.knight_inactive_sprites = [], []

        
        knight_idle_sprite_source = pygame.image.load("assets/sprites/knight-idle.png").convert_alpha()    
        knight_idle_inactive_sprite_source = pygame.image.load("assets/sprites/knight-idle-inactive.png").convert_alpha()

        wizard_idle_sprite_source = pygame.image.load("assets/sprites/wizard/Idle.png").convert_alpha()
        wizard_idle_inactive_sprite_source = pygame.image.load("assets/sprites/wizard/wizard-idle-inactive.png").convert_alpha()

        wizard_spritesheet = SpriteSheet(wizard_idle_sprite_source)
        knight_spritesheet = SpriteSheet(knight_idle_sprite_source)
        wizard_inactive_spritesheet = SpriteSheet(wizard_idle_inactive_sprite_source)
        knight_inactive_spritesheet = SpriteSheet(knight_idle_inactive_sprite_source)

        for i in range(8):
            self.wizard_sprites.append(wizard_spritesheet.get_image(i, 150, 150, 1, None))
            self.wizard_inactive_sprites.append(wizard_inactive_spritesheet.get_image(i, 150, 150, 1, None))
        
        for i in range(6):
            self.knight_sprites.append(knight_spritesheet.get_image(i, 112, 96, 1, None))
            self.knight_inactive_sprites.append(knight_inactive_spritesheet.get_image(i, 112, 96, 1, None))