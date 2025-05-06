import pygame

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):

			# dim button
			self.hover = self.image.copy()
			self._apply_hover_tint()  # Apply a visual hover effect
	
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
	
	def _apply_hover_tint(self):
		hover_surface = pygame.Surface(self.hover.get_size(), pygame.SRCALPHA)
		hover_surface.fill((0, 0, 0, 50))  # Black with 50 alpha for dimming
		self.image.blit(hover_surface, (0, 0))