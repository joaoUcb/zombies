import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game  # Adicionar referência ao objeto game
        self.original_image = pygame.image.load(os.path.join('images', 'player.png'))
        self.original_image = pygame.transform.scale(self.original_image, (120, 120))  # Ajustar o tamanho da imagem do jogador
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (pygame.display.Info().current_w // 2, pygame.display.Info().current_h // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.direction = 'RIGHT'
        self.health = 100

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.keep_in_bounds()
        self.update_image()

    def changespeed(self, x, y):
        self.speed_x += x
        self.speed_y += y
        if x > 0:
            self.direction = 'RIGHT'
        elif x < 0:
            self.direction = 'LEFT'

    def update_image(self):
        if self.direction == 'RIGHT':
            self.image = self.original_image
        elif self.direction == 'LEFT':
            self.image = pygame.transform.flip(self.original_image, True, False)
        self.rect = self.image.get_rect(center=self.rect.center)

    def keep_in_bounds(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 4000:
            self.rect.right = 4000
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 3000:
            self.rect.bottom = 3000

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
        else:
            self.game.damage_flash = True
            self.game.damage_flash_start_time = pygame.time.get_ticks()
