import pygame
from sys import exit 

pygame.init()
#sa pygame kay ang origin kay nas top left
screen = pygame.display.set_mode((1920,1280)) #width, height
pygame.display.set_caption('Vine ni juju')
clock = pygame.time.Clock()
test_font = pygame.font.Font(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\Pixeltype.ttf', 50) #font type, font size //ttf file if nahan ka 

vine_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\pixelvinebg.png')
water_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\water(resized).png')
text_surface = test_font.render('Jump and avoid falling on the water!', False, 'Green') #text info, anti-alias, color
ground_surface = pygame.image.load(r'C:\Users\John\Desktop\Physics-81-Game\assets\stage 1\image-removebg-preview.png')

while True:
    #event loop murag for loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() #opposite sa init
            exit()
    #draw all our elements
    #update everything
    #order of code
    
    screen.blit(vine_surface, (0,0)) 
    screen.blit(water_surface, (0,1080))#block image transfer
    screen.blit(text_surface, (50, 150))
    screen.blit(ground_surface, (0, 900))
    
    pygame.display.update()
    clock.tick(60)

#surface kani is display surface ^^
#(regular) surfave single images basically

#creating text (surface with text)
#1 creat an image of the text and place that on a surface 
#2 place that surface on the screen
#create a font(text size and style), write text on a surface, blit the text surface