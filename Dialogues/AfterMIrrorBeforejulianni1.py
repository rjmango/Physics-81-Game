import pygame
from utils.spritesheet import SpriteSheet

class MirrorToVineTransitionDialogueState:
    def __init__(self, window, screen_size):
        self.window = window
        self.canvas = pygame.Surface(screen_size)
        self.w, self.h = screen_size

        # Background
        self.background = pygame.image.load("pngs/mirrorbg.jpg").convert()
        self.background = pygame.transform.scale(self.background, screen_size)

        # Sprites
        knight_active = SpriteSheet('spritesheets/knight-idle.png')
        wizard_active = SpriteSheet('spritesheets/Idle.png')

        knight_img = knight_active.get_sprite(0, 128, 128, 9, 'Red')
        wizard_img = wizard_active.get_sprite(0, 128, 128, 11, 'Red')

        self.knight = knight_img
        self.wizard = pygame.transform.flip(wizard_img, True, False)

        # Positions
        self.knight_pos = (-100, 165)
        self.wizard_pos = (890, -90)

        # Dialogue box
        self.dialogue_width = 1800
        self.dialogue_height = 400
        self.dialogue_x = (self.w - self.dialogue_width) // 2
        self.dialogue_y = self.h - self.dialogue_height - 50

        self.dialogue_box = pygame.Surface((self.dialogue_width, self.dialogue_height), pygame.SRCALPHA)
        self.dialogue_box.fill((255, 255, 255, 180))

        self.font = pygame.font.SysFont(None, 36)

        # Dialogue lines
        self.dialogue_lines = [
            "*The knight runs after wizard, following its path*",
            "*The wizard stops*",
            "You really are a persistent one, aren't ya? -wizard",
            "Just stop this! You can still change! -knight",
            "A bit late for that -wizard",
            "*The wizard places his hand on the wall and activates a hidden button*",
            "*The knight is dropped in a secret part of the castle, full of vegetation*",
            "It seems that he has to use these plants in his favor in order to escape",
        ]
        self.current_line = 0
        self.dialogue_finished = False
        self.done = False  # For switching state

        self.click_sound = pygame.mixer.Sound("assets/sfx/dialogue-blip.mp3")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.dialogue_finished:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.current_line += 1
                if self.current_line >= len(self.dialogue_lines):
                    self.dialogue_finished = True
                    self.done = True

    def update(self):
        pass

    def draw(self):
        self.canvas.fill((0, 0, 0) if self.dialogue_finished else (255, 255, 255))

        if not self.dialogue_finished:
            self.canvas.blit(self.background, (0, 0))
            self.canvas.blit(self.wizard, self.wizard_pos)
            self.canvas.blit(self.knight, self.knight_pos)
            self.canvas.blit(self.dialogue_box, (self.dialogue_x, self.dialogue_y))

            text = self.dialogue_lines[self.current_line]
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(
                self.dialogue_x + self.dialogue_width // 2,
                self.dialogue_y + self.dialogue_height // 4
            ))
            self.canvas.blit(text_surface, text_rect)

        self.window.blit(self.canvas, (0, 0))
        pygame.display.update()
