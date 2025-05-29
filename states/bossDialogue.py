from .state import State
from .projectile import Projectile
from .endingDialogue import EndingDialogue
from utils.spritesheet import SpriteSheet
import pygame
from pygame import mixer
import time

mixer.init()
blipSound = mixer.Sound('assets/sfx/dialogue-blip.mp3')

class BossDialogue(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.initialize_state()
        self.game.pre_boss_bgm.play(-1)

    def initialize_state(self):
        self.load_assets()
        # Other parts sa code

        self.current_knight_frame = 0
        self.current_wizard_frame = 0
        self.last_time_updated = 0
        self.previous_time = time.time()
        self.knight_turn = True
        self.space_pressed = False

        # Dialogue information
        # self.dialogue_font = pygame.font.SysFont('Arial', 32)
        self.dialogue_font = pygame.font.Font('assets/fonts/MinecraftRegular-Bmg3.otf', 36)  # Custom font
        self.current_dialogue = 0

        if self.game.bossDefeated:
            file = open('assets/dialogues/postBossFight.txt', 'r')
        else:
            file = open('assets/dialogues/preBossFight.txt', 'r')
        self.dialogue = file.readlines()
    
    def update(self, actions):
        if self.game.bossDefeatedChanged:
            self.initialize_state()
            self.game.bossDefeatedChanged = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if not self.space_pressed:  # Only trigger when space was not pressed before
                blip = blipSound
                blip.play()
                self.current_dialogue = (self.current_dialogue+1)
                self.knight_turn = not self.knight_turn
                self.space_pressed = True
        else:
            self.space_pressed = False  # Reset when space is released

        if self.current_dialogue == len(self.dialogue):
            if not self.game.bossDefeated:
                self.game.pre_boss_bgm.stop()
                self.game.bossDefeated = True
                self.initialize_state()
                newState = Projectile(self.game)
                newState.enter_state()
            else:
                self.exit_state()
                self.game.post_boss_bgm.stop()
                newState = EndingDialogue(self.game)
                newState.enter_state()

        # Code for updating values
        now = time.time()
        self.last_time_updated += now - self.previous_time
        self.previous_time = now

        if self.last_time_updated > 0.2:
            self.last_time_updated = 0
            self.current_knight_frame = (self.current_knight_frame+1) % 6
            self.current_wizard_frame = (self.current_wizard_frame+1) % 8

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


        if self.knight_turn:
            knightImage = self.knight_sprites[self.current_knight_frame]
            wizardImage = self.wizard_inactive_sprites[self.current_wizard_frame]
        else:
            knightImage = self.knight_inactive_sprites[self.current_knight_frame]
            wizardImage = self.wizard_sprites[self.current_wizard_frame]


        scaled_knight_width = int(self.game.SCREEN_WIDTH / 1.1428)
        scaled_knight_height = int(self.game.SCREEN_HEIGHT / 0.888)
        
        scaled_wizard_dimensions = int(self.game.SCREEN_WIDTH / 0.6826)

        # knightDisplay = pygame.transform.scale(knightImage, (112*8, 96*8))
        # wizardDisplay = pygame.transform.scale(wizardImage, (1500, 1500))

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

        # # Render text using pre-initialized font
        # wrapped = self.wrap_text(self.dialogue[self.current_dialogue], self.dialogue_font, self.game.SCREEN_WIDTH)
        # text_surface = self.dialogue_font.render(wrapped[0], True, (0, 0, 0))
        # text_rect = text_surface.get_rect(center=(transparent_surface.get_width()//2, 
        #                                 transparent_surface.get_height()//2))
        # transparent_surface.blit(text_surface, text_rect)
        
        # display.blit(transparent_surface, (0, self.game.SCREEN_HEIGHT - 250))
        self.render_dialogue(self.dialogue[self.current_dialogue][8:-1], display)

    def load_assets(self):
        # Load background by changing parameter
        self.bg = self.game.load_background_asset("assets/bg/boss-dialogue.jpg")
        # Example
        # self.bg = self.game.load_background_asset("assets/bg/new-bg.png")

        # load other assets
        self.wizard_sprites, self.knight_sprites = [], []
        self.wizard_inactive_sprites, self.knight_inactive_sprites = [], []

        wizard_idle_sprite_source = pygame.image.load("assets/sprites/wizard/Idle.png").convert_alpha()
        knight_idle_sprite_source = pygame.image.load("assets/sprites/knight-idle.png").convert_alpha()    
        wizard_idle_inactive_sprite_source = pygame.image.load("assets/sprites/wizard/wizard-idle-inactive.png").convert_alpha()
        knight_idle_inactive_sprite_source = pygame.image.load("assets/sprites/knight-idle-inactive.png").convert_alpha()

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


