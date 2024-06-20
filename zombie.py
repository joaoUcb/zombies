import pygame
import random

RED = (255, 0, 0)
ZOMBIE_IMAGES = ['images/zombie.png', 'images/zombie2.png', 'images/zombie3.png']

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, player, damage, damage_interval, health, speed, game):
        super().__init__()
        self.image_path = random.choice(ZOMBIE_IMAGES)
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 138))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.damage = damage
        self.damage_interval = damage_interval
        self.last_damage_time = pygame.time.get_ticks()
        self.health = health
        self.speed = speed
        self.game = game

    def update(self):
        self.move_towards_player()
        self.attack_player()

    def move_towards_player(self):
        direction_x = self.player.rect.x - self.rect.x
        direction_y = self.player.rect.y - self.rect.y
        distance = (direction_x**2 + direction_y**2) ** 0.5
        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        self.rect.x += direction_x * self.speed  # Zombie speed
        self.rect.y += direction_y * self.speed

    def attack_player(self):
        current_time = pygame.time.get_ticks()
        if pygame.sprite.collide_rect(self, self.player) and current_time - self.last_damage_time > self.damage_interval:
            self.player.take_damage(self.damage)
            self.game.damage_flash = True
            self.game.damage_flash_start_time = pygame.time.get_ticks()
            self.last_damage_time = current_time

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen, camera_x, camera_y):
        if self.health > 0:
            health_bar_length = 50
            health_ratio = self.health / 150
            health_bar_width = int(health_bar_length * health_ratio)
            health_bar = pygame.Rect(self.rect.x - camera_x, self.rect.y - camera_y - 10, health_bar_width, 5)
            pygame.draw.rect(screen, RED, health_bar)
