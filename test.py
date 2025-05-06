import pygame
import sys

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# --- Knight ---
def reset_knight():
    return pygame.Rect(50, 400, 40, 60), 0, False

knight, vel_y, on_ground = reset_knight()
gravity = 800
jump_strength = -400

# --- Platforms ---
platforms = [
    pygame.Rect(100, 450, 150, 10),
    pygame.Rect(300, 380, 200, 10),
    pygame.Rect(550, 300, 170, 10),
    pygame.Rect(750, 400, 150, 10),
    pygame.Rect(900, 320, 120, 10)
]

# --- Colors ---
BLUE = (50, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000  # frame time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        knight.x -= 200 * dt
    if keys[pygame.K_RIGHT]:
        knight.x += 200 * dt

    # --- Jumping ---
    if keys[pygame.K_UP] and on_ground:
        vel_y = jump_strength

    # --- Gravity ---
    vel_y += gravity * dt
    knight.y += vel_y * dt
    on_ground = False

    # --- Platform Collision ---
    for plat in platforms:
        if knight.colliderect(plat) and vel_y > 0:
            knight.bottom = plat.top
            vel_y = 0
            on_ground = True

    # --- Check for failure (falls in water) ---
    if knight.y > 500:
        knight, vel_y, on_ground = reset_knight()

    # --- Drawing ---
    screen.fill((30, 30, 60))

    # Water hazard (blue area)
    pygame.draw.rect(screen, BLUE, (0, 500, 1000, 100))

    # Platforms
    for plat in platforms:
        pygame.draw.rect(screen, GREEN, plat)

    # Knight (red stickman)
    pygame.draw.rect(screen, RED, knight)

    # --- Update Display ---
    pygame.display.flip()

pygame.quit()
sys.exit()

