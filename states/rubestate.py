import pygame as pg
import sys
import os
from os import path

# Initialize pygame
pg.init()

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

# Base asset path
base_path = path.dirname(__file__)

def load_asset(name):
    try:
        return pg.image.load(path.join(base_path, 'assets', 'stage 2', name)).convert_alpha()
    except Exception as e:
        print(f"Failed to load image: {name} - {e}")
        return None

class InstructionScreen:
    def __init__(self, game):
        self.game = game
        self.font_large = pg.font.SysFont(None, 72)
        self.font_medium = pg.font.SysFont(None, 48)
        self.font_small = pg.font.SysFont(None, 36)
        
        self.title = "BOULDER PUZZLE CHALLENGE"
        self.description = [
            "You stand before an ancient tower, its iron gate sealed shut.",
            "Across a precarious rope bridge, a massive boulder waits -",
            "the key to smashing through the gate.",
            "",
            "You have these materials available:",
            "- Two wooden beams (form a T-shaped lever)",
            "- Rope (to connect the boulder)",
            "- Candle (to burn through the rope)",
            "- Wedge (to act as a fulcrum)",
            "",
            "Arrange them carefully to release the boulder!"
        ]
        
        self.controls = "Press SPACE to begin your attempt"
    
    def draw(self, surface):
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        title_text = self.font_large.render(self.title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        surface.blit(title_text, title_rect)
        
        for i, line in enumerate(self.description):
            text = self.font_small.render(line, True, WHITE)
            surface.blit(text, (SCREEN_WIDTH//2 - 400, 200 + i * 40))
        
        controls_text = self.font_medium.render(self.controls, True, WHITE)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        surface.blit(controls_text, controls_rect)
    
    def handle_events(self, event):
        return event.type == pg.KEYDOWN and event.key == pg.K_SPACE

class DraggableObject:
    def __init__(self, x, y, width, height, name, image_file=None):
        self.rect = pg.Rect(x, y, width, height)
        self.name = name
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.placed = False
        self.original_pos = (x, y)
        self.original_size = (width, height)
        self.image_file = image_file
        
        if image_file:
            loaded = load_asset(image_file)
            if loaded:
                self.image = pg.transform.scale(loaded, (width, height))
            else:
                self.create_fallback_image(width, height)
        else:
            self.create_fallback_image(width, height)
    
    def create_fallback_image(self, width, height):
        self.image = pg.Surface((width, height))
        self.image.fill(BROWN if "beam" in self.name.lower() else GRAY)
        font = pg.font.SysFont(None, 20)
        text = font.render(self.name, True, BLACK)
        self.image.blit(text, (5, 5))
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and not self.placed:
                self.dragging = True
                self.offset_x = self.rect.x - event.pos[0]
                self.offset_y = self.rect.y - event.pos[1]
        
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pg.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] + self.offset_x
            self.rect.y = event.pos[1] + self.offset_y
    
    def reset(self):
        self.rect.topleft = self.original_pos
        self.placed = False
        self.dragging = False
        if self.image_file:
            loaded = load_asset(self.image_file)
            if loaded:
                self.image = pg.transform.scale(loaded, self.original_size)

class BoulderPuzzle:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Boulder Puzzle")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 36)
        
        self.showing_instructions = True
        self.playing = False
        self.puzzle_solved = False
        
        self.instruction_screen = InstructionScreen(self)
        
        # Initialize background
        bg = load_asset('rubebg.png')
        if bg:
            self.background = pg.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((50, 50, 50))
        
        self.objects = [
            DraggableObject(50, 50, 150, 40, "Beam 1", 'woodenbeam.png'),
            DraggableObject(50, 120, 40, 150, "Beam 2", 'woodenbeam.png'),
            DraggableObject(50, 300, 80, 80, "Boulder", 'boulder.png'),
            DraggableObject(50, 400, 120, 30, "Rope", 'rope.png'),
            DraggableObject(50, 450, 40, 60, "Candle", 'candle.png'),
            DraggableObject(50, 530, 60, 40, "Wedge", 'wedge.png')
        ]
        
        knight = load_asset('knight.png')
        self.knight_img = pg.transform.scale(knight, (100, 150)) if knight else None
        
        self.target_beam1 = pg.Rect(400, 500, 150, 40)
        self.target_beam2 = pg.Rect(475, 430, 40, 150)
        self.target_rope = pg.Rect(475, 580, 120, 30)
        self.target_wedge = pg.Rect(400, 540, 60, 40)
        self.target_candle = pg.Rect(430, 450, 40, 60)
        
        self.boulder_released = False
        self.gate_smashed = False
        self.boulder_rect = pg.Rect(450, 200, 80, 80)
        self.boulder_falling = False
        self.boulder_speed = 0
        self.gate_rect = pg.Rect(900, 300, 50, 300)
        self.gate_damage = 0
        
        self.instruction = "Arrange the materials to release the boulder and smash the gate!"
        self.success_text = "Success! The gate is smashed. Press R to reset."
        
        b_img = load_asset('boulder.png')
        self.boulder_img = pg.transform.scale(b_img, (80, 80)) if b_img else None
    
    def check_solution(self):
        if not self.playing or self.puzzle_solved:
            return
        
        beam1_placed = beam2_placed = False
        
        for obj in self.objects:
            if obj.name == "Beam 1" and obj.rect.colliderect(self.target_beam1):
                obj.placed = True
                if obj.rect.height > obj.rect.width:
                    obj.image = pg.transform.rotate(obj.image, 90)
                    obj.rect.width, obj.rect.height = obj.rect.height, obj.rect.width
                beam1_placed = True
            elif obj.name == "Beam 2" and obj.rect.colliderect(self.target_beam2):
                obj.placed = True
                if obj.rect.width > obj.rect.height:
                    obj.image = pg.transform.rotate(obj.image, 90)
                    obj.rect.width, obj.rect.height = obj.rect.height, obj.rect.width
                beam2_placed = True
        
        rope_placed = any(obj.name == "Rope" and obj.rect.colliderect(self.target_rope) for obj in self.objects)
        wedge_placed = any(obj.name == "Wedge" and obj.rect.colliderect(self.target_wedge) for obj in self.objects)
        candle_placed = any(obj.name == "Candle" and obj.rect.colliderect(self.target_candle) for obj in self.objects)
        
        if beam1_placed and beam2_placed and rope_placed and wedge_placed and candle_placed and not self.boulder_released:
            self.boulder_released = True
            self.boulder_falling = True
            self.puzzle_solved = True
    
    def update(self):
        if not self.playing:
            return
        
        if self.boulder_falling:
            self.boulder_speed += 0.5
            self.boulder_rect.y += self.boulder_speed
            
            if self.boulder_rect.colliderect(self.gate_rect):
                self.boulder_falling = False
                self.gate_damage += 50
                if self.gate_damage >= 100:
                    self.gate_smashed = True
    
    def draw(self):
        # Draw background
        if isinstance(self.background, pg.Surface):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
        
        if self.showing_instructions:
            self.instruction_screen.draw(self.screen)
            return
        
        if not self.playing:
            return
        
        # Draw game elements
        pg.draw.rect(self.screen, RED if not self.gate_smashed else GREEN, self.gate_rect)
        
        if self.boulder_img:
            self.screen.blit(self.boulder_img, self.boulder_rect)
        else:
            pg.draw.ellipse(self.screen, GRAY, self.boulder_rect)
        
        for obj in self.objects:
            obj.draw(self.screen)
        
        if self.knight_img:
            self.screen.blit(self.knight_img, (50, 550))
        
        text = self.font.render(self.success_text if self.gate_smashed else self.instruction, True, WHITE)
        self.screen.blit(text, (50, SCREEN_HEIGHT - 50))
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if self.showing_instructions:
                if self.instruction_screen.handle_events(event):
                    self.showing_instructions = False
                    self.playing = True
                continue
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.reset_puzzle()
                elif event.key == pg.K_SPACE and not self.playing:
                    self.playing = True
            
            if self.playing and not self.puzzle_solved:
                for obj in self.objects:
                    if not obj.placed:
                        obj.handle_event(event)
        
        return True
    
    def reset_puzzle(self):
        for obj in self.objects:
            obj.reset()
        self.boulder_released = False
        self.boulder_falling = False
        self.boulder_speed = 0
        self.boulder_rect.y = 200
        self.gate_damage = 0
        self.gate_smashed = False
        self.puzzle_solved = False
    
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.check_solution()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    game = BoulderPuzzle()
    game.run()
    pg.quit()
    sys.exit()