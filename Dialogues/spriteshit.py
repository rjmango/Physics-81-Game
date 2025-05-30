import pygame

class SpriteSheet():
    def __init__(self, image_path):
        self.sheet = pygame.image.load(image_path).convert_alpha()  # ✅ Load image from path

    def get_sprite(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
