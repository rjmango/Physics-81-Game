import pygame
from sys import exit

pygame.init()

screen = pygame.display.set_mode((1920, 1280))
pygame.display.set_caption('Intro')
clock = pygame.time.Clock()

crawl_font = pygame.font.Font('fonts/INTROCRAWL.otf', 100)
crawltext_font = pygame.font.Font('fonts/INTROCRAWL.otf', 35)
logo_font = pygame.font.Font('fonts/LOGO.ttf', 100)
credit_font = pygame.font.Font('fonts/LOGO.ttf', 30)
space_font = pygame.font.Font('fonts/space.otf', 20)

crawlbg_surface = pygame.image.load('pngs/crawlbg.png')
space_surface = space_font.render('Press space to continue', True, 'Black')
logo_surface = logo_font.render('PHYSMORIA', True, 'Gold')
credit_surface = credit_font.render('Made with love by JJ and Friends', True, 'Silver').convert_alpha()
crawlpic1_surface = pygame.image.load('pngs/crawlpic1.png').convert_alpha()
crawlpic2_surface = pygame.image.load('pngs/crawlpic2.jpg').convert_alpha()
crawlpic3_surface = pygame.image.load('pngs/crawlpic3.png').convert_alpha()
crawlpic4_surface = pygame.image.load('pngs/crawlpic4.jpg').convert_alpha()
crawlpic5_surface = pygame.image.load('pngs/crawlpic5.png').convert_alpha()
crawlpic6_surface = pygame.image.load('pngs/crawlpic6.png').convert_alpha()
crawlpic7_surface = pygame.image.load('pngs/crawlpic7.png').convert_alpha()
crawlpic8_surface = pygame.image.load('pngs/crawlpic8.png').convert_alpha()
crawlpic9_surface = pygame.image.load('pngs/crawlpic9.png').convert_alpha()
bigtext1 = crawl_font.render('In a land vastly different from ours', True, 'White')

crawl_lines_raw = [
    'From a distant world unlike our own…',
    'There stood a city, Physmoria — the City of Life.',
    'A haven of beauty, magic, and peace.',
    'Its people, angelic.',
    'Its heart, pure.',
    'A kingdom that welcomed all…',
    'Even those with shadows in their past.',
    "Under the royal family's light, the city prospered.",
    '',
    'But peace does not last forever.',
    '',
    'From the desert came vengeful spirits…',
    'Broken souls seeking only destruction.',
    'Bound by pain, they marched with one goal:',
    'To extinguish Physmoria’s flame of hope.',
    '',
    'Led by a powerful, merciless wizard…',
    'They struck the city with fury.',
    'Day by day, Physmoria crumbled.',
    'Its castle was under siege.',
    'Its people — enslaved, slaughtered, or fleeing.',
    '',
    'On the final day…',
    'The royal family was declared dead.',
    'All… but one.',
    '',
    'The princess lived.',
    'Imprisoned.',
    'A symbol, they said…',
    'That hope itself had been defeated.',
    '',
    'But not all hearts turned to darkness.',
    '',
    'Among the attackers, one man wavered.',
    'Haunted by the eyes of the innocent…',
    'He could not continue.',
    '',
    'In secret, he saved who he could.',
    'One group… then another… then more.',
    'Until only one cry stopped him:',
    'A child, weeping for their princess.',
    '',
    'He hesitated.',
    'But the people spoke:',
    '“What is life without hope?”',
    '',
    'So the nameless turned back.',
    'Not to escape…',
    'But to fight.',
    'To save the last light of Physmoria.',
    '',
    'And bring hope back to a broken world.'
]

crawl_lines = [crawltext_font.render(line, True, 'White') for line in crawl_lines_raw]

intro_sfx = pygame.mixer.Sound('audios/intro.mp3')
pop_sfx = pygame.mixer.Sound('audios/pop.mp3')
sparkle_sfx = pygame.mixer.Sound('audios/sparkle.mp3')
crawl_sfx = pygame.mixer.Sound('audios/crawlsound.mp3')

intro_sfx.set_volume(0.5)
pop_sfx.set_volume(0.5)
crawl_sfx.set_volume(0.5)

logo_y_position = 2000
pop_played = False
sparkle_sfx_played = False
next_step = False
crawl_started = False

start_time = pygame.time.get_ticks()
text1_start_time = None
bgchange = 6416
text1_duration = 5500

alpha = 0
fade_speed = 0.03
fade_speed2 = 1.5

scroll_y = 1280
scroll_speed = 2
fade_margin = 200

blackout = False
blackout_start_time = None

def compute_alpha(y_pos, center_y, margin):
    distance = abs(y_pos - center_y)
    if distance > margin:
        return 0
    return int(255 * (1 - distance / margin))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            next_step = True
            text1_start_time = pygame.time.get_ticks()
            alpha = 0

    if next_step:
        screen.fill((0, 0, 0))
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - text1_start_time

        if elapsed_time < text1_duration:
            if alpha < 255:
                alpha += fade_speed2
                bigtext1.set_alpha(int(min(alpha, 255)))
            screen.blit(bigtext1, (282, logo_y_position))
        elif not blackout:
            screen.blit(crawlbg_surface, (0, 0))
            if not crawl_started:
                crawl_sfx.play()
                crawl_started = True

            scroll_y -= scroll_speed

            for i, line_surface in enumerate(crawl_lines):
                y = scroll_y + i * 50
                if -50 < y < 1280:
                    screen.blit(line_surface, (200, y))

            image_surfaces = [
                crawlpic1_surface, crawlpic2_surface, crawlpic3_surface,
                crawlpic4_surface, crawlpic5_surface, crawlpic6_surface,
                crawlpic7_surface, crawlpic8_surface, crawlpic9_surface
            ]

            image_trigger_lines = [0, 3, 7, 11, 16, 20, 25, 30, 47]

            for img, line_num in zip(image_surfaces, image_trigger_lines):
                line_y = scroll_y + line_num * 50
                alpha_val = compute_alpha(line_y, 300, fade_margin)
                if alpha_val > 0:
                    img_fade = img.copy()
                    img_fade.set_alpha(alpha_val)
                    screen.blit(img_fade, (950, 450))

            if scroll_y + len(crawl_lines) * 50 < 0:
                blackout = True
                blackout_start_time = pygame.time.get_ticks()
                crawl_sfx.stop()
        else:
            if pygame.time.get_ticks() - blackout_start_time < 3000:
                screen.fill((0, 0, 0))
            else:
                screen.fill((0, 0, 0))

    else:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        if alpha < 255:
            alpha += fade_speed
            credit_surface.set_alpha(int(min(alpha, 255)))

        if elapsed_time < bgchange:
            screen.fill((255, 255, 255))
            if not intro_sfx.get_num_channels():
                intro_sfx.play()
        elif elapsed_time < bgchange + 1000:
            screen.fill((0, 0, 255))
            intro_sfx.stop()
            if not pop_played:
                pop_sfx.play()
                pop_played = True
        else:
            screen.blit(credit_surface, (770, logo_y_position + 80))
            if not sparkle_sfx_played:
                sparkle_sfx.play()
                sparkle_sfx_played = True
            if logo_y_position <= 460:
                space_surface.set_alpha(int(alpha))
                screen.blit(space_surface, (870, 800))

        if logo_y_position > 460:
            logo_y_position -= 4
        screen.blit(logo_surface, (740, logo_y_position))

    pygame.display.update()
    clock.tick(60)
