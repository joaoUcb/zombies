import pygame

class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
