import pygame
from states.state import State
from states.introDialogue import IntroDialogue
from sys import exit

class IntroSequence(State):
    def __init__(self, game):
        State.__init__(self, game)
        # pygame.init()
        self.game = game
        # self.screen = pygame.display.set_mode((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        # pygame.display.set_caption('Intro')
        self.clock = pygame.time.Clock()
        self.clock.tick(60)

        # Calculate scaling factors
        self.width_scale = self.game.SCREEN_WIDTH / 1920
        self.height_scale = self.game.SCREEN_HEIGHT / 1280
        self.scale = min(self.width_scale, self.height_scale)  # Maintain aspect ratio

        # Scale fonts
        self.crawl_font = pygame.font.Font('font/INTROCRAWL.otf', int(100 * self.scale))
        self.crawltext_font = pygame.font.Font('font/INTROCRAWL.otf', int(35 * self.scale))
        self.logo_font = pygame.font.Font('font/LOGO.ttf', int(150 * self.scale))
        self.credit_font = pygame.font.Font('font/LOGO.ttf', int(40 * self.scale))
        self.space_font = pygame.font.Font('font/space.otf', int(40 * self.scale))

        self.load_assets()
        self.init_states()

    def load_assets(self):
        # Load and scale background images
        self.crawlbg_surface = pygame.transform.scale(
            pygame.image.load('pngs/crawlbg.png').convert_alpha(),
            (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT)
        )
        
        # Scale text surfaces
        self.space_surface = self.space_font.render('Press space to continue', True, 'Black')
        self.logo_surface = self.logo_font.render('PHYSMORIA', True, 'Gold')
        self.credit_surface = self.credit_font.render('Made with love by JJ and Friends', True, 'Silver').convert_alpha()
        self.bigtext1 = self.crawl_font.render('In a land vastly different from ours', True, 'White')

        # Load and scale images
        self.image_surfaces = []
        for i in range(1, 10):
            ext = 'png' if i not in [2, 4] else 'jpg'
            img = pygame.image.load(f'pngs/crawlpic{i}.{ext}').convert_alpha()
            # Scale images while maintaining aspect ratio
            img_width = int(img.get_width() * self.scale)
            img_height = int(img.get_height() * self.scale)
            self.image_surfaces.append(pygame.transform.scale(img, (img_width, img_height)))

        crawl_lines_raw = [
            'From a distant world unlike our own…',
            'There stood a city, Physmoria — the City of Life.',
            'A haven of beauty, magic, and peace.',
            'Its people, angelic.',
            'Its heart, pure.',
            'A kingdom that welcomed all…',
            'Even those with shadows in their past.',
            "Under the royal family's light, the city prospered.",
            '', 'But peace does not last forever.', '',
            'From the desert came vengeful spirits…',
            'Broken souls seeking only destruction.',
            'Bound by pain, they marched with one goal:',
            'To extinguish Physmoria\'s flame of hope.', '',
            'Led by a powerful, merciless wizard…',
            'They struck the city with fury.',
            'Day by day, Physmoria crumbled.',
            'Its castle was under siege.',
            'Its people — enslaved, slaughtered, or fleeing.', '',
            'On the final day…',
            'The royal family was declared dead.',
            'All… but one.', '',
            'The princess lived.',
            'Imprisoned.',
            'A symbol, they said…',
            'That hope itself had been defeated.', '',
            'But not all hearts turned to darkness.', '',
            'Among the attackers, one man wavered.',
            'Haunted by the eyes of the innocent…',
            'He could not continue.', '',
            'In secret, he saved who he could.',
            'One group… then another… then more.',
            'Until only one cry stopped him:',
            'A child, weeping for their princess.', '',
            'He hesitated.',
            'But the people spoke:',
            '“What is life without hope?”', '',
            'So the nameless turned back.',
            'Not to escape…',
            'But to fight.',
            'To save the last light of Physmoria.', '',
            'And bring hope back to a broken world.'
        ]
        self.crawl_lines = [self.crawltext_font.render(line, True, 'White') for line in crawl_lines_raw]

        # Audio setup
        self.intro_sfx = pygame.mixer.Sound('audios/intro.mp3')
        self.pop_sfx = pygame.mixer.Sound('audios/pop.mp3')
        self.sparkle_sfx = pygame.mixer.Sound('audios/sparkle.mp3')
        self.crawl_sfx = pygame.mixer.Sound('audios/crawlsound.mp3')

        self.intro_sfx.set_volume(0.5)
        self.pop_sfx.set_volume(0.5)
        self.crawl_sfx.set_volume(0.5)

    def init_states(self):
        # Initialize all state variables with scaled values
        self.logo_y_position = self.game.SCREEN_HEIGHT * 2  # Start off-screen
        self.pop_played = False
        self.sparkle_sfx_played = False
        self.next_step = False
        self.crawl_started = False

        self.start_time = pygame.time.get_ticks()
        self.text1_start_time = None
        self.bgchange = 6416  # Timing remains the same
        self.text1_duration = 5500  # Timing remains the same
        self.last_frame_time = pygame.time.get_ticks()

        self.alpha = 0
        self.fade_speed = 0.03  # Timing remains the same
        self.fade_speed2 = 1.5  # Timing remains the same

        self.scroll_y = self.game.SCREEN_HEIGHT
        self.fade_margin = 200    # Margin scales with size
        self.scroll_speed = 0.25  # Reduced from 2 to make it slower
        self.line_spacing = 40  # Slightly reduced line spacing
        self.post_logo_scroll_speed = 0.25  # Even slower speed after logo

        self.blackout = False
        self.blackout_start_time = None

    def compute_alpha(self, y_pos, center_y, margin):
        distance = abs(y_pos - center_y)
        if distance > margin:
            return 0
        return int(255 * (1 - distance / margin))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.next_step = True
                self.text1_start_time = pygame.time.get_ticks()
                self.alpha = 0

    def update(self, actions):
        if actions["SPACE"]:
            self.next_step = True
            self.text1_start_time = pygame.time.get_ticks()
            self.alpha = 0
    
    def draw_intro(self, display):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        # Clear the screen appropriately for each phase
        if elapsed_time < self.bgchange:
            display.fill((255, 255, 255))  # White background
            if not self.intro_sfx.get_num_channels():
                self.intro_sfx.play()
        elif elapsed_time < self.bgchange + 1000:
            display.fill((0, 0, 255))  # Blue background
            self.intro_sfx.stop()
            if not self.pop_played:
                self.pop_sfx.play()
                self.pop_played = True
        else:
            # Clear with blue background before drawing anything
            display.fill((0, 0, 255))
            
            # Position credit text below logo with scaled positions
            credit_x = self.game.SCREEN_WIDTH // 2 - self.credit_surface.get_width() // 2
            credit_y = self.logo_y_position + 80 * self.scale
            display.blit(self.credit_surface, (credit_x, credit_y + 20))
            
            if not self.sparkle_sfx_played:
                self.sparkle_sfx.play()
                self.sparkle_sfx_played = True
            
            target_logo_y = self.game.SCREEN_HEIGHT // 2.782608696  # ~460 in original
            print(int(self.logo_y_position) <= int(target_logo_y))
            if int(self.logo_y_position) <= int(target_logo_y):
                self.space_surface.set_alpha(int(self.alpha))
                space_x = self.game.SCREEN_WIDTH // 2 - self.space_surface.get_width() // 2
                space_y = self.game.SCREEN_HEIGHT * 0.625  # ~800 in original
                display.blit(self.space_surface, (space_x, space_y))

        # Handle fade effect (do this before drawing the logo)
        if self.alpha < 255:
            self.alpha += self.fade_speed*5
            self.credit_surface.set_alpha(int(min(self.alpha, 255)))

        # Update logo position
        if self.logo_y_position > self.game.SCREEN_HEIGHT * 0.36:
            self.logo_y_position -= 4 * self.scale  # Movement speed scales with size
        
        # Draw logo (only once per frame)
        logo_x = self.game.SCREEN_WIDTH // 2 - self.logo_surface.get_width() // 2
        display.blit(self.logo_surface, (logo_x, self.logo_y_position))

    def draw_text_and_crawl(self, display):
        display.fill((0, 0, 0))
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.text1_start_time

        if elapsed_time < self.text1_duration:
            if self.alpha < 255:
                self.alpha += self.fade_speed2
                self.bigtext1.set_alpha(int(min(self.alpha, 255)))
            text_x = self.game.SCREEN_WIDTH // 2 - self.bigtext1.get_width() // 2
            display.blit(self.bigtext1, (text_x, self.logo_y_position))
        elif not self.blackout:
            display.blit(self.crawlbg_surface, (0, 0))
            if not self.crawl_started:
                self.crawl_sfx.play()
                self.crawl_started = True

            # Use slower speed after logo is shown
            current_speed = self.post_logo_scroll_speed if self.crawl_started else self.scroll_speed
            self.scroll_y -= current_speed

            for i, line_surface in enumerate(self.crawl_lines):
                y = self.scroll_y + i * self.line_spacing  # Use the defined spacing
                if -self.line_spacing < y < self.game.SCREEN_HEIGHT:
                    line_x = 200 * self.width_scale
                    display.blit(line_surface, (line_x, y))

            image_trigger_lines = [0, 3, 7, 11, 16, 20, 25, 30, 47]
            image_y_pos = self.game.SCREEN_HEIGHT * 0.35

            for img, line_num in zip(self.image_surfaces, image_trigger_lines):
                line_y = self.scroll_y + line_num * self.line_spacing
                alpha_val = self.compute_alpha(line_y, self.game.SCREEN_HEIGHT * 0.23, self.fade_margin)
                if alpha_val > 0:
                    img_fade = img.copy()
                    img_fade.set_alpha(alpha_val)
                    img_x = self.game.SCREEN_WIDTH - img.get_width() - 50 * self.width_scale
                    display.blit(img_fade, (img_x, image_y_pos))

            if self.scroll_y + len(self.crawl_lines) * self.line_spacing < 0:
                self.blackout = True
                self.blackout_start_time = pygame.time.get_ticks()
                self.crawl_sfx.stop()
        else:
            if pygame.time.get_ticks() - self.blackout_start_time < 3000:
                newState = IntroDialogue(self.game)
                self.exit_state()
                newState.enter_state()
            else:
                display.fill((0, 0, 0))

    def render(self, display):
        if self.next_step:
            self.draw_text_and_crawl(display)
        else:
            self.draw_intro(display)

    def run(self):
        while True:
            self.handle_events()
            self.render()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    # Example usage - you'll need to pass a game object with SCREEN_WIDTH and SCREEN_HEIGHT
    class Game:
        def __init__(self):
            self.SCREEN_WIDTH = 1024
            self.SCREEN_HEIGHT = 682
    
    game = Game()
    app = IntroSequence(game)
    app.run()