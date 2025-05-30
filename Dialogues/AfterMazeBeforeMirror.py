import pygame
from spriteshit import SpriteSheet

class MirrorRoomDialogueState:
    def __init__(self, window, screen_size):
        self.window = window
        self.canvas = pygame.Surface(screen_size)
        self.w, self.h = screen_size

        # Background: mirror room
        self.background = pygame.image.load("pngs/mirrorbg.jpg").convert()
        self.background = pygame.transform.scale(self.background, screen_size)

        # Sprites
        knight_active = SpriteSheet('spritesheets/knight-idle.png')
        wizard_active = SpriteSheet('spritesheets/Idle.png')

        knight_img = knight_active.get_sprite(0, 128, 128, 9, 'Red')
        wizard_img = wizard_active.get_sprite(0, 128, 128, 11, 'Red')
        self.knight = knight_img
        self.wizard = pygame.transform.flip(wizard_img, True, False)

        # Sprite positions
        self.knight_pos = (-100, 165)
        self.wizard_pos = (890, -90)

        # Dialogue box
        self.dialogue_width = 1800
        self.dialogue_height = 400
        self.dialogue_x = (self.w - self.dialogue_width) // 2
        self.dialogue_y = self.h - self.dialogue_height - 50

        self.dialogue_box = pygame.Surface((self.dialogue_width, self.dialogue_height), pygame.SRCALPHA)
        self.dialogue_box.fill((255, 255, 255, 180))  # Semi-transparent white

        # Font
        self.font = pygame.font.SysFont(None, 36)

        # Dialogue lines
        self.dialogue_lines = [
            "*The knight enters the castle*",
            "Very well! It seems that I may have underestimated you. -wizard",
            "I wouldn't celebrate that easily though... -wizard",
            "This is still extremely far from over -wizard",
            "WHY DO YOU DO THIS!? JUST WHY -knight",
            "These poor souls suffering all because of your doing! -knight",
            "Woah! I sure hope you didn't forget -wizard",
            "You are part of this too. -wizard",
            "Why you! -knight",
            "*The wizard escapes from a door, leaving the knight behind with... mirrors?*",
            "*What can these possibly do?*",
        ]
        self.current_line = 0
        self.dialogue_finished = False
        self.done = False  # Flag to signal state transition

        # Sound
        self.click_sound = pygame.mixer.Sound("assets/sfx/dialogue-blip.mp3")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.dialogue_finished:
            if event.key == pygame.K_SPACE:
                self.click_sound.play()
                self.current_line += 1
                if self.current_line >= len(self.dialogue_lines):
                    self.dialogue_finished = True
                    self.done = True  # Let parent game know to move to next scene

    def update(self):
        pass  # Placeholder for animation or timed effects

    def draw(self):
        self.canvas.fill((0, 0, 0) if self.dialogue_finished else (255, 255, 255))

        if not self.dialogue_finished:
            self.canvas.blit(self.background, (0, 0))
            self.canvas.blit(self.wizard, self.wizard_pos)
            self.canvas.blit(self.knight, self.knight_pos)
            self.canvas.blit(self.dialogue_box, (self.dialogue_x, self.dialogue_y))

            # Render dialogue line
            text = self.dialogue_lines[self.current_line]
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.dialogue_x + self.dialogue_width // 2,
                                                      self.dialogue_y + self.dialogue_height // 4))
            self.canvas.blit(text_surface, text_rect)

        self.window.blit(self.canvas, (0, 0))
        pygame.display.update()
