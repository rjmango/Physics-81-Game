import pygame
from sys import exit

class IntroSequence:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1280))
        pygame.display.set_caption('Intro')
        self.clock = pygame.time.Clock()

        self.crawl_font = pygame.font.Font('font/INTROCRAWL.otf', 100)
        self.crawltext_font = pygame.font.Font('font/INTROCRAWL.otf', 35)
        self.logo_font = pygame.font.Font('font/LOGO.ttf', 100)
        self.credit_font = pygame.font.Font('font/LOGO.ttf', 30)
        self.space_font = pygame.font.Font('font/space.otf', 20)

        self.load_assets()
        self.init_states()

    def load_assets(self):
        self.crawlbg_surface = pygame.image.load('pngs/crawlbg.png')
        self.space_surface = self.space_font.render('Press space to continue', True, 'Black')
        self.logo_surface = self.logo_font.render('PHYSMORIA', True, 'Gold')
        self.credit_surface = self.credit_font.render('Made with love by JJ and Friends', True, 'Silver').convert_alpha()
        self.bigtext1 = self.crawl_font.render('In a land vastly different from ours', True, 'White')

        self.image_surfaces = [
            pygame.image.load(f'pngs/crawlpic{i}.png' if i not in [2, 4] else f'pngs/crawlpic{i}.jpg').convert_alpha()
            for i in range(1, 10)
        ]

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
            'To extinguish Physmoria’s flame of hope.', '',
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

        self.intro_sfx = pygame.mixer.Sound('audios/intro.mp3')
        self.pop_sfx = pygame.mixer.Sound('audios/pop.mp3')
        self.sparkle_sfx = pygame.mixer.Sound('audios/sparkle.mp3')
        self.crawl_sfx = pygame.mixer.Sound('audios/crawlsound.mp3')

        self.intro_sfx.set_volume(0.5)
        self.pop_sfx.set_volume(0.5)
        self.crawl_sfx.set_volume(0.5)

    def init_states(self):
        self.logo_y_position = 2000
        self.pop_played = False
        self.sparkle_sfx_played = False
        self.next_step = False
        self.crawl_started = False

        self.start_time = pygame.time.get_ticks()
        self.text1_start_time = None
        self.bgchange = 6416
        self.text1_duration = 5500

        self.alpha = 0
        self.fade_speed = 0.03
        self.fade_speed2 = 1.5

        self.scroll_y = 1280
        self.scroll_speed = 2
        self.fade_margin = 200

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

    def draw_intro(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        if self.alpha < 255:
            self.alpha += self.fade_speed
            self.credit_surface.set_alpha(int(min(self.alpha, 255)))

        if elapsed_time < self.bgchange:
            self.screen.fill((255, 255, 255))
            if not self.intro_sfx.get_num_channels():
                self.intro_sfx.play()
        elif elapsed_time < self.bgchange + 1000:
            self.screen.fill((0, 0, 255))
            self.intro_sfx.stop()
            if not self.pop_played:
                self.pop_sfx.play()
                self.pop_played = True
        else:
            self.screen.blit(self.credit_surface, (770, self.logo_y_position + 80))
            if not self.sparkle_sfx_played:
                self.sparkle_sfx.play()
                self.sparkle_sfx_played = True
            if self.logo_y_position <= 460:
                self.space_surface.set_alpha(int(self.alpha))
                self.screen.blit(self.space_surface, (870, 800))

        if self.logo_y_position > 460:
            self.logo_y_position -= 4
        self.screen.blit(self.logo_surface, (740, self.logo_y_position))

    def draw_text_and_crawl(self):
        self.screen.fill((0, 0, 0))
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.text1_start_time

        if elapsed_time < self.text1_duration:
            if self.alpha < 255:
                self.alpha += self.fade_speed2
                self.bigtext1.set_alpha(int(min(self.alpha, 255)))
            self.screen.blit(self.bigtext1, (282, self.logo_y_position))
        elif not self.blackout:
            self.screen.blit(self.crawlbg_surface, (0, 0))
            if not self.crawl_started:
                self.crawl_sfx.play()
                self.crawl_started = True

            self.scroll_y -= self.scroll_speed

            for i, line_surface in enumerate(self.crawl_lines):
                y = self.scroll_y + i * 50
                if -50 < y < 1280:
                    self.screen.blit(line_surface, (200, y))

            image_trigger_lines = [0, 3, 7, 11, 16, 20, 25, 30, 47]

            for img, line_num in zip(self.image_surfaces, image_trigger_lines):
                line_y = self.scroll_y + line_num * 50
                alpha_val = self.compute_alpha(line_y, 300, self.fade_margin)
                if alpha_val > 0:
                    img_fade = img.copy()
                    img_fade.set_alpha(alpha_val)
                    self.screen.blit(img_fade, (950, 450))

            if self.scroll_y + len(self.crawl_lines) * 50 < 0:
                self.blackout = True
                self.blackout_start_time = pygame.time.get_ticks()
                self.crawl_sfx.stop()
        else:
            if pygame.time.get_ticks() - self.blackout_start_time < 3000:
                self.screen.fill((0, 0, 0))
            else:
                self.screen.fill((0, 0, 0))

    def run(self):
        while True:
            self.handle_events()
            if self.next_step:
                self.draw_text_and_crawl()
            else:
                self.draw_intro()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    app = IntroSequence()
    app.run()
