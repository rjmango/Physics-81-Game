import pygame as pg
import sys
import os
from os import path
import random
from pygame import mixer

# Initialize pygame and mixer
pg.init()
mixer.init()

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
FPS = 60

# Colors (fallback colors if images don't load)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

# Sound effects
try:
    boulder_release_sound = mixer.Sound(path.join('assets', 'sfx', 'boulder_release.wav'))
    gate_smash_sound = mixer.Sound(path.join('assets', 'sfx', 'gate_smash.wav'))
    object_place_sound = mixer.Sound(path.join('assets', 'sfx', 'object_place.wav'))
    bg_music = mixer.Sound(path.join('assets', 'sfx', 'puzzle_bgm.wav'))
    bg_music.set_volume(0.5)
except Exception as e:
    print(f"Warning: Could not load sound effects - {e}")

# Base asset path: absolute directory of this script file
base_path = path.abspath(path.dirname(__file__))

def load_asset(name, folder='stage 2'):
    """Load an image asset from the specified folder inside 'assets'"""
    try:
        if folder:
            full_path = path.join(base_path, 'assets', folder, name)
        else:
            full_path = path.join(base_path, 'assets', name)
        return pg.image.load(full_path).convert_alpha()
    except Exception as e:
        print(f"Failed to load image: {name} in folder '{folder}' - {e}")
        return None

class InstructionScreen:
    def __init__(self, game):
        self.game = game
        # Load fonts from assets fonts folder (assuming pixeltype.ttf in 'assets' folder)
        try:
            font_path = path.join(base_path, 'assets', 'pixeltype.ttf')
            self.font_large = pg.font.Font(font_path, 72)
            self.font_medium = pg.font.Font(font_path, 48)
            self.font_small = pg.font.Font(font_path, 36)
        except Exception as e:
            print(f"Failed to load font: {e}")
            self.font_large = pg.font.SysFont(None, 72)
            self.font_medium = pg.font.SysFont(None, 48)
            self.font_small = pg.font.SysFont(None, 36)
        
        # Try to load background image for instructions
        self.background = load_asset('rubebg.png', 'stage 2')
        if not self.background:
            self.background = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((20, 20, 40))
        
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
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Create semi-transparent overlay
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw title with fancy effect
        title_shadow = self.font_large.render(self.title, True, (100, 0, 0))
        title_text = self.font_large.render(self.title, True, (200, 160, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        surface.blit(title_shadow, (title_rect.x+3, title_rect.y+3))
        surface.blit(title_text, title_rect)
        
        # Draw description lines
        for i, line in enumerate(self.description):
            if line.startswith("-"):  # Item list
                text = self.font_small.render(line, True, (220, 200, 100))
            elif not line:  # Empty line
                continue
            else:  # Regular text
                text = self.font_small.render(line, True, (220, 220, 220))
            surface.blit(text, (SCREEN_WIDTH//2 - 400, 200 + i * 40))
        
        # Draw controls with pulsing effect
        pulse = int(pg.time.get_ticks() / 200) % 2
        controls_text = self.font_medium.render(self.controls, True, 
            (255, 255, 255) if pulse else (200, 200, 0))
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        surface.blit(controls_text, controls_rect)
    
    def handle_events(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            try:
                bg_music.play(-1)  # Loop background music
            except:
                pass
            return True
        return False

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
        self.highlight = False
        self.highlight_time = 0
        
        # Load image with fallback
        if image_file:
            loaded = load_asset(image_file, 'stage 2')
            if loaded:
                self.original_image = pg.transform.scale(loaded, (width, height))
                self.image = self.original_image.copy()
            else:
                self.create_fallback_image(width, height)
        else:
            self.create_fallback_image(width, height)
    
    def create_fallback_image(self, width, height):
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        color = BROWN if "beam" in self.name.lower() else GRAY
        self.image.fill(color)
        font = pg.font.Font(None, 24)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(width//2, height//2))
        self.image.blit(text, text_rect)
        self.original_image = self.image.copy()
    
    def draw(self, surface):
        # Draw highlight if active
        if self.highlight or (self.highlight_time > 0 and pg.time.get_ticks() % 200 < 100):
            highlight_surf = pg.Surface((self.rect.width+10, self.rect.height+10), pg.SRCALPHA)
            highlight_surf.fill((255, 255, 0, 100))
            surface.blit(highlight_surf, (self.rect.x-5, self.rect.y-5))
            self.highlight_time = max(0, self.highlight_time - 1)
        
        # Draw the object
        surface.blit(self.image, self.rect)
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and not self.placed:
                self.dragging = True
                self.offset_x = self.rect.x - event.pos[0]
                self.offset_y = self.rect.y - event.pos[1]
                try:
                    object_place_sound.play()
                except:
                    pass
        
        elif event.type == pg.MOUSEBUTTONUP:
            if self.dragging:
                try:
                    object_place_sound.play()
                except:
                    pass
            self.dragging = False
        
        elif event.type == pg.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] + self.offset_x
            self.rect.y = event.pos[1] + self.offset_y
    
    def rotate(self):
        if hasattr(self, 'original_image'):
            self.image = pg.transform.rotate(self.original_image, 90)
            self.rect.width, self.rect.height = self.rect.height, self.rect.width
    
    def reset(self):
        self.rect.topleft = self.original_pos
        self.placed = False
        self.dragging = False
        if hasattr(self, 'original_image'):
            self.image = self.original_image.copy()
        self.rect.width, self.rect.height = self.original_size

class BoulderPuzzle:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Boulder Puzzle Challenge")
        self.clock = pg.time.Clock()
        try:
            font_path = path.join(base_path, 'assets', 'pixeltype.ttf')
            self.font = pg.font.Font(font_path, 36)
        except Exception as e:
            print(f"Failed to load font: {e}")
            self.font = pg.font.SysFont(None, 36)
        
        self.showing_instructions = True
        self.playing = False
        self.puzzle_solved = False
        
        self.instruction_screen = InstructionScreen(self)
        
        # Load all assets
        self.load_assets()
        
        # Create draggable objects
        self.objects = [
            DraggableObject(50, 50, 150, 40, "Beam 1", 'woodenbeam.png'),
            DraggableObject(50, 120, 40, 150, "Beam 2", 'woodenbeam.png'),
            DraggableObject(50, 300, 120, 120, "Boulder", 'boulder.png'),
            DraggableObject(50, 450, 120, 30, "Rope", 'rope.png'),
            DraggableObject(50, 500, 60, 90, "Candle", 'candle.png'),
            DraggableObject(50, 600, 80, 60, "Wedge", 'wedge.png')
        ]
        
        # Target positions for solution
        self.target_beam1 = pg.Rect(400, 500, 150, 40)
        self.target_beam2 = pg.Rect(475, 430, 40, 150)
        self.target_rope = pg.Rect(475, 580, 120, 30)
        self.target_wedge = pg.Rect(400, 540, 80, 60)
        self.target_candle = pg.Rect(430, 450, 60, 90)
        
        # Game state variables
        self.boulder_released = False
        self.gate_smashed = False
        self.boulder_rect = pg.Rect(450, 200, 120, 120)
        self.boulder_falling = False
        self.boulder_speed = 0
        self.gate_rect = pg.Rect(900, 300, 80, 500)
        self.gate_damage = 0
        self.gate_shake = 0
        
        # Text messages
        self.instruction = "Arrange the materials to release the boulder and smash the gate!"
        self.success_text = "Success! The gate is smashed. Press R to reset."
        
        # Particles for effects
        self.particles = []
    
    def load_assets(self):
        """Load all game assets with fallbacks"""
        # Background
        bg = load_asset('rubebg.png', 'stage 2')
        if bg:
            self.background = pg.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((50, 50, 50))
        
        # Gate images
        self.gate_image = load_asset('gate.png', 'stage 2')
        if not self.gate_image:
            self.gate_image = pg.Surface((80, 500))
            self.gate_image.fill((100, 100, 100))
        
        self.gate_broken_image = load_asset('gate_broken.png', 'stage 2')
        if not self.gate_broken_image:
            self.gate_broken_image = pg.Surface((80, 500))
            self.gate_broken_image.fill((150, 50, 50))
        
        # Knight character
        knight = load_asset('knight.png', 'stage 2')
        if knight:
            self.knight_img = pg.transform.scale(knight, (150, 200))
        else:
            self.knight_img = pg.Surface((150, 200))
            self.knight_img.fill((200, 200, 200))
    
        def check_solution(self):
            if not self.playing or self.puzzle_solved:
                return

        beam1_placed = beam2_placed = rope_placed = wedge_placed = candle_placed = False

        for obj in self.objects:
            if obj.name == "Beam 1" and obj.rect.colliderect(self.target_beam1):
                beam1_placed = True
                obj.placed = True
                obj.highlight_time = 30
                if obj.rect.height > obj.rect.width:
                    obj.rotate()

            elif obj.name == "Beam 2" and obj.rect.colliderect(self.target_beam2):
                beam2_placed = True
                obj.placed = True
                obj.highlight_time = 30
                if obj.rect.width > obj.rect.height:
                    obj.rotate()

            elif obj.name == "Rope" and obj.rect.colliderect(self.target_rope):
                rope_placed = True
                obj.placed = True
                obj.highlight_time = 30

            elif obj.name == "Wedge" and obj.rect.colliderect(self.target_wedge):
                wedge_placed = True
                obj.placed = True
                obj.highlight_time = 30

            elif obj.name == "Candle" and obj.rect.colliderect(self.target_candle):
                candle_placed = True
                obj.placed = True
                obj.highlight_time = 30

        if beam1_placed and beam2_placed and rope_placed and wedge_placed and candle_placed:
            self.puzzle_solved = True
            self.boulder_falling = True
            try:
                boulder_release_sound.play()
            except:
                pass
    
    def update(self):
        if not self.playing:
            return
        
        # Update boulder physics
        if self.boulder_falling:
            self.boulder_speed += 0.8  # Gravity
            self.boulder_rect.y += self.boulder_speed
            
            # Create dust particles while falling
            if random.random() < 0.3:
                self.particles.append({
                    'x': self.boulder_rect.centerx + random.randint(-20, 20),
                    'y': self.boulder_rect.bottom,
                    'size': random.randint(2, 6),
                    'speed': random.uniform(-1, 1),
                    'life': 30
                })
            
            # Check for collision with gate
            if self.boulder_rect.colliderect(self.gate_rect):
                self.boulder_falling = False
                damage = min(100, int(self.boulder_speed * 2))
                self.gate_damage += damage
                self.gate_shake = 10  # Shake effect duration
                
                # Create impact particles
                for _ in range(20):
                    self.particles.append({
                        'x': self.gate_rect.left + random.randint(0, self.gate_rect.width),
                        'y': self.gate_rect.top + random.randint(0, self.gate_rect.height),
                        'size': random.randint(3, 8),
                        'speed': random.uniform(-3, 3),
                        'life': random.randint(20, 40)
                    })
                
                if self.gate_damage >= 100:
                    self.gate_smashed = True
                    try:
                        gate_smash_sound.play()
                    except:
                        pass
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['speed']
            particle['y'] += 1
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.showing_instructions:
            self.instruction_screen.draw(self.screen)
            return
        
        if not self.playing:
            return
        
        # Draw rope bridge (visual element)
        pg.draw.line(self.screen, BROWN, (300, 550), (900, 550), 5)
        for i in range(300, 900, 50):
            pg.draw.line(self.screen, BROWN, (i, 500), (i, 550), 2)
        
        # Draw gate with shake effect
        gate_pos = self.gate_rect.copy()
        if self.gate_shake > 0:
            gate_pos.x += random.randint(-3, 3)
            self.gate_shake -= 1
        
        if self.gate_smashed:
            self.screen.blit(self.gate_broken_image, gate_pos)
        else:
            # Show damage on gate
            if self.gate_damage > 0:
                damage_surf = pg.Surface((self.gate_rect.width, int(self.gate_rect.height * (1 - self.gate_damage/100))), pg.SRCALPHA)
                damage_surf.fill((255, 0, 0, 100))
                self.screen.blit(damage_surf, (gate_pos.x, gate_pos.y))
            self.screen.blit(self.gate_image, gate_pos)
        
        # Draw boulder
        boulder_img = next((obj.image for obj in self.objects if obj.name == "Boulder"), None)
        if boulder_img and not self.boulder_released:
            self.screen.blit(boulder_img, (450, 200))
        elif self.boulder_falling:
            if boulder_img:
                self.screen.blit(boulder_img, self.boulder_rect)
            else:
                pg.draw.ellipse(self.screen, GRAY, self.boulder_rect)
        
        # Draw particles
        for particle in self.particles:
            pg.draw.circle(self.screen, (200, 200, 200, min(255, particle['life']*5)), 
                          (int(particle['x']), int(particle['y'])), particle['size'])
        
        # Draw draggable objects
        for obj in self.objects:
            if not (obj.name == "Boulder" and self.boulder_released):
                obj.draw(self.screen)
        
        # Draw knight character
        self.screen.blit(self.knight_img, (50, 450))
        
        # Draw instruction text
        text = self.font.render(self.success_text if self.gate_smashed else self.instruction, True, WHITE)
        text_rect = text.get_rect(bottomleft=(50, SCREEN_HEIGHT - 50))
        
        # Text background
        pg.draw.rect(self.screen, (0, 0, 0, 150), 
                     (text_rect.x-10, text_rect.y-10, 
                      text_rect.width+20, text_rect.height+20))
        
        self.screen.blit(text, text_rect)
    
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
        self.particles = []
    
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