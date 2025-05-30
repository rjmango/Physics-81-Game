import pygame
from utils.spritesheet import SpriteSheet

class VineRoomDialogueState:
    def __init__(self, window, screen_size):
        self.window = window
        self.canvas = pygame.Surface(screen_size)
        self.w, self.h = screen_size

        # Background
        self.background = pygame.image.load("pngs/vinebg.jpg").convert()
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
        self.dialogue_box.fill((255, 255, 255, 180))  # Semi-transparent

        self.font = pygame.font.SysFont(None, 36)

        # Dialogue lines
        self.dialogue_lines = [
            "*To escape, knight must still complete another room*",
            "*One whose goals aren't clear yet*",
            "I'm warning you knight! -wizard",
            "As former comrades, I've given you far too many chances -wizard",
            "I do not care! The princess must be saved -knight",
            "When all of this is over, I'll bear witness to Phsymoria's rise. -knight",
            "Very well... You chose this path! -wizard",
            "*The wizard leaves*",
        ]
        self.current_line = 0
        self.dialogue_finished = False
        self.done = False  # Flag for parent game logic

        self.click_sound = pygame.mixer.Sound("assets/sfx/dialogue-blip.mp3")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.dialogue_finished:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.current_line += 1
                if self.current_line >= len(self.dialogue_lines):
                    self.dialogue_finished = True
                    self.done = True  # Let the game know it’s done

    def update(self):
        pass  # Reserved for future use

    def draw(self):
        self.canvas.fill((0, 0, 0) if self.dialogue_finished else (255, 255, 255))

        if not self.dialogue_finished:
            self.canvas.blit(self.background, (0, 0))
            self.canvas.blit(self.wizard, self.wizard_pos)
            self.canvas.blit(self.knight, self.knight_pos)
            self.canvas.blit(self.dialogue_box, (self.dialogue_x, self.dialogue_y))

            text = self.dialogue_lines[self.current_line]
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.dialogue_x + self.dialogue_width // 2,
                                                      self.dialogue_y + self.dialogue_height // 4))
            self.canvas.blit(text_surface, text_rect)

        self.window.blit(self.canvas, (0, 0))
        pygame.display.update()
