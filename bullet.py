import pygame

YELLOW = (255, 255, 0)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 20  # Bullet speed

        # Calculate direction to target
        direction_x = target_x - x
        direction_y = target_y - y
        distance = (direction_x**2 + direction_y**2) ** 0.5
        if distance != 0:
            self.direction_x = direction_x / distance
            self.direction_y = direction_y / distance

    def update(self):
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        if (self.rect.right < 0 or self.rect.left > 4000 or
                self.rect.bottom < 0 or self.rect.top > 3000):
            self.kill()
