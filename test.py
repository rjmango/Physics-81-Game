import pygame
from sys import exit 

pygame.init()
#sa pygame kay ang origin kay nas top left
screen = pygame.display.set_mode((1920,1280)) #width, height
pygame.display.set_caption('Vine ni juju')
clock = pygame.time.Clock()
test_font = pygame.font.Font(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\Pixeltype.ttf', 50) #font type, font size //ttf file if nahan ka 

vine_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\pixelvinebg.png').convert_alpha()
water_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\water(resized).png').convert_alpha()

score_surf = test_font.render('Jump and avoid falling on the water!', False, (64,64,64)) #text info, anti-alias, color
score_rect = score_surf.get_rect(center = (990, 150))

ground_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\image-removebg-preview.png').convert_alpha()

#animation
#knight_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\knightpix.png').convert_alpha()
#knightxpos = 0

#playerknight = pygame.image.load()
knight_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\knightpix.png').convert_alpha()
knight_rect = knight_surface.get_rect(bottomleft = (0,1120))
#later sprite class combines a surface and a rectangle and places them in one class 

Angvine_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\masgamay.png').convert_alpha()
Angvine_rect = Angvine_surface.get_rect(midbottom = (500,900))

while True:
    #event loop murag for loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() #opposite sa init
            exit()

            #if event.type == pygame.MOUSEMOTION: #.MOUSEBUTTONUP .MOUSEBUTTONDOWN
               # print(event.pos) #would also give us the mouse position
            
            #to get mouse position mag mouse motion ka
            #if event.type == pygame.MOUSEMOTION:
                # if knight.knight_rect.collidepoint(event.pos): print('collision') 
             
            if event.type == pygame.KEYDOWN: 
                 if event.key == pygame.K_SPACE:
                     print('jump')





    #draw all our elements
    #update everything
    #order of code
    
    screen.blit(vine_surface, (0,0)) 
    screen.blit(water_surface, (0,1080))#block image transfer
    screen.blit(score_surf, score_rect)
    screen.blit(ground_surface, (0, 900))#we are placing them in the same position but we can do more than that char
    pygame.draw.rect(screen, '#c0e8ec', score_rect, 9) #adding bg color sa text aye
    #pygame.draw.rect(screen, '#c0e8ec', score_rect)
    

    #pygame.draw.line(screen, 'Gold',(0,0),pygame.mouse.get_pos(), 10)
    
    #knightxpos += 8  #everytime our while loop is running we want to increase knight pos by 1?
    #screen.blit(knight_surface, (knightxpos,730))
    #knight_rect.left +=1
    screen.blit(knight_surface, knight_rect)
    knight_rect.x += 8
    if knight_rect.right > 2000: knight_rect.left = 0
    #print(player_surf,player_rect) useful niya lang basin to measure posi
    #if our knight pos is too low, we want to put our snail pos on a higher number 
    #if knightxpos > 2000: knightxpos = 0
    screen.blit(Angvine_surface, Angvine_rect)
    Angvine_rect.x += 3
    if Angvine_rect.right > 1000: Angvine_rect.left = 100

    #if knight_rect.colliderect(Angvine_rect):
      #  print('collision')
    
    #PLAYER CHARACTER (we want to use a sub mod keys)
    #keys = pygame.key.get_pressed() #we can use this like a dictionary
    #if keys[pygame.K_SPACE]: print('jump') #can return either 0 or 1 so you know wat dat mean maka if statement u ughh
    
    
    #mouse_pos = pygame.mouse.get_pos()
    #if knight_rect.collidepoint(mouse_pos):
       # print(pygame.mouse.get_pressed()) #shows which mouse button you are pressing 

    pygame.display.update()
    clock.tick(60)

#surface kani is display surface ^^
#(regular) surfave single images basically

#creating text (surface with text)
#1 creat an image of the text and place that on a surface 
#2 place that surface on the screen
#create a font(text size and style), write text on a surface, blit the text surface

#how to make the player character work
#RECTANGLES   two core func in the basic sense 
#1 help place a surface much more efficiently (precise posi of surface)
#2 basic collisions 