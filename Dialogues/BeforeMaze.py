import pygame
from utils.spritesheet import SpriteSheet
from states.state import State

class MazeDialogueState(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.w, self.h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT

        # Background
        self.background = pygame.image.load("pngs/mazebg.png").convert()
        self.background = pygame.transform.scale(self.background, (self.w, self.h))

        # Sprites
        knight_inactive = SpriteSheet('spritesheets/knight-idle-inactive.png')
        knight_active = SpriteSheet('spritesheets/knight-idle.png')
        wizard_inactive = SpriteSheet('spritesheets/wizard-idle-inactive.png')
        wizard_active = SpriteSheet('spritesheets/Idle.png')

        knight_img = knight_active.get_sprite(0, 128, 128, 9, 'Red')
        wizard_img = wizard_active.get_sprite(0, 128, 128, 11, 'Red')
        self.knight = knight_img
        self.wizard = pygame.transform.flip(wizard_img, True, False)

        self.knight_pos = (-100, 165)
        self.wizard_pos = (890, -90)

        # Dialogue Box
        self.dialogue_width = 1800
        self.dialogue_height = 400
        self.dialogue_x = (self.w - self.dialogue_width) // 2
        self.dialogue_y = self.h - self.dialogue_height - 50

        self.dialogue_box = pygame.Surface((self.dialogue_width, self.dialogue_height), pygame.SRCALPHA)
        self.dialogue_box.fill((255, 255, 255, 180))

        self.font = pygame.font.SysFont(None, 36)
        self.click_sound = pygame.mixer.Sound("assets/sfx/dialogue-blip.mp3")

        self.dialogue_lines = [
            "*The knight confronts the wizard in the castle garden*",
            "So you want to save the princess, huh? -wizard",
            "LET HER OUT! -knight",
            "Not so easy! -wizard",
            "I'll consider the offer once you're out of THIS! -wizard",
            "*Huge walls form around the knight.*",
            "*It seemed like the wizard trapped him in a maze.*"
        ]
        self.current_line = 0
        self.dialogue_finished = False
        self.done = False  # Flag to tell external systems to transition state

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.dialogue_finished:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.current_line += 1
                if self.current_line >= len(self.dialogue_lines):
                    self.dialogue_finished = True
                    self.done = True  # Let the game know this state is complete

    def update(self):
        pass  # Not used in this static dialogue, but useful if you animate text

    def draw(self):
        self.canvas.fill((0, 0, 0) if self.dialogue_finished else (255, 255, 255))
        if not self.dialogue_finished:
            self.canvas.blit(self.background, (0, 0))
            self.canvas.blit(self.wizard, self.wizard_pos)
            self.canvas.blit(self.knight, self.knight_pos)
            self.canvas.blit(self.dialogue_box, (self.dialogue_x, self.dialogue_y))

            # Draw text
            text = self.dialogue_lines[self.current_line]
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.dialogue_x + self.dialogue_width // 2,
                                                      self.dialogue_y + self.dialogue_height // 4))
            self.canvas.blit(text_surface, text_rect)

        self.window.blit(self.canvas, (0, 0))
        pygame.display.update()
