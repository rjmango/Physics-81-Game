import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((1920, 1280))
pygame.display.set_caption('Vine ni juju')
clock = pygame.time.Clock()
test_font = pygame.font.Font(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\Pixeltype.ttf', 50)

game_active = True 

vine_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\pixelvinebg.png').convert_alpha()
water_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\water(resized).png').convert_alpha()
ground_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\image-removebg-preview.png').convert_alpha()
knight_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\knightpix.png').convert_alpha()
Angvine_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\masgamay.png').convert_alpha()

score_surf = test_font.render('Jump and avoid falling on the water!', False, (64, 64, 64))
score_rect = score_surf.get_rect(center=(990, 150))
knight_rect = knight_surface.get_rect(bottomleft=(0, 1120))
Angvine_rect = Angvine_surface.get_rect(midbottom=(500, 900))

knight_gravity = 0
on_vine = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if knight_rect.collidepoint(event.pos) and (knight_rect.bottom >= 1120 or on_vine):
                knight_gravity = -25
             
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (knight_rect.bottom >= 1120 or on_vine):
                knight_gravity = -25

    knight_gravity += 1
    knight_rect.y += knight_gravity
    on_vine = False
    
    if knight_rect.colliderect(Angvine_rect) and knight_gravity >= 0:
        if knight_rect.bottom <= Angvine_rect.top + 10:
            knight_rect.bottom = Angvine_rect.top
            knight_gravity = 0
            on_vine = True

    if not on_vine and knight_rect.bottom >= 1120:
        knight_rect.bottom = 1120
        knight_gravity = 0

    Angvine_rect.x += 3
    if Angvine_rect.right > 1000:
        Angvine_rect.left = 100

    

    screen.blit(vine_surface, (0, 0))
    screen.blit(water_surface, (0, 1080))
    screen.blit(score_surf, score_rect)
    screen.blit(ground_surface, (0, 900))
    pygame.draw.rect(screen, '#c0e8ec', score_rect, 9)
    screen.blit(knight_surface, knight_rect)
    screen.blit(Angvine_surface, Angvine_rect)

    pygame.display.update()
    clock.tick(60)