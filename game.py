import pygame
import random
import os
from player import Player
from zombie import Zombie
from bullet import Bullet
from wallet import Wallet

WHITE = (255, 255, 255)
SCREEN_WIDTH = 1600  # Tamanho da tela
SCREEN_HEIGHT = 1200
MAP_WIDTH = 4000  # Aumentar o tamanho do mapa
MAP_HEIGHT = 3000  # Aumentar o tamanho do mapa
WEAPON_DAMAGE = 40  # Dano da arma do jogador
WEAPON_SPEED = 40  # Velocidade inicial do projétil (mais rápido)
WEAPON_SHOT_INTERVAL = 300  # Intervalo inicial de tiro em milissegundos
ZOMBIE_BASE_SPEED = 2  # Velocidade base dos zumbis

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, effect):
        super().__init__()
        self.image = pygame.image.load(os.path.join('images', image_path))
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.effect = effect

class Game:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Zombie Shooter")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        self.running = True
        self.game_over = False

        self.round_message = ""
        self.round_message_start_time = 0
        self.round_message_duration = 2000  # 2 segundos

        self.weapon_damage = WEAPON_DAMAGE
        self.weapon_speed = WEAPON_SPEED
        self.shot_interval = WEAPON_SHOT_INTERVAL
        self.upgrade_cost = 150
        self.zombie_speed = ZOMBIE_BASE_SPEED  # Velocidade inicial dos zumbis

        # Carregar imagem do botão de upgrade e redimensioná-la
        self.upgrade_button_image = pygame.image.load(os.path.join('images', 'upgrade_button.png'))
        self.upgrade_button_image = pygame.transform.scale(self.upgrade_button_image, (100, 80))  # Ajustar o tamanho
        self.upgrade_button_rect = self.upgrade_button_image.get_rect(center=(self.screen_width // 2, 50))

        # Carregar imagens de fundo
        self.background_images = [
            pygame.image.load(os.path.join('images', 'background1.png')),
            pygame.image.load(os.path.join('images', 'background2.png')),
            pygame.image.load(os.path.join('images', 'background3.png')),
            pygame.image.load(os.path.join('images', 'background4.png'))
        ]
        self.background_images = [pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)) for img in self.background_images]

        self.damage_flash = False
        self.damage_flash_start_time = 0
        self.damage_flash_duration = 100  # 100 ms

        self.insta_kill_active = False
        self.insta_kill_end_time = 0
        self.insta_kill_icon = pygame.image.load(os.path.join('images', 'icon_instaKill.png'))
        self.insta_kill_icon = pygame.transform.scale(self.insta_kill_icon, (50, 50))

        self.drop_images = [
            {'image': 'instaKill.png', 'effect': 'insta_kill'},
            {'image': 'kabum.png', 'effect': 'kabum'}
        ]
        self.drop_list = pygame.sprite.Group()

        # Carregar imagens dos botões de pausa e guia
        self.pause_button_image = pygame.image.load(os.path.join('images', 'pause_button.png'))
        self.pause_button_image = pygame.transform.scale(self.pause_button_image, (50, 50))
        self.pause_button_rect = self.pause_button_image.get_rect(topleft=(10, 10))

        self.guide_button_image = pygame.image.load(os.path.join('images', 'guide_button.png'))
        self.guide_button_image = pygame.transform.scale(self.guide_button_image, (50, 50))
        self.guide_button_rect = self.guide_button_image.get_rect(topleft=(10, 70))

        self.paused = False
        self.guide_open = False

        self.start_new_game()

    def start_new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.zombie_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.player = Player(self)  # Passar o objeto game para Player
        self.all_sprites.add(self.player)

        self.wallet = Wallet()  # Adicionar a carteira
        self.round = 1
        self.zombies_per_round = 10
        self.zombie_damage = 8
        self.zombie_health = 150  # Vida inicial dos zumbis
        self.damage_interval = 1000  # 2000 ms = 2 segundos
        self.kills = 0
        self.shooting = False
        self.last_shot_time = 0
        self.zombies_to_spawn = 0
        self.spawn_delay = 4000  # Delay de 4 segundos em milissegundos
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 1000  # Intervalo de 1 segundo entre spawns de zumbis
        self.create_zombies(self.zombies_per_round)

        # Resetar upgrades da arma
        self.weapon_damage = WEAPON_DAMAGE
        self.weapon_speed = WEAPON_SPEED
        self.shot_interval = WEAPON_SHOT_INTERVAL
        self.upgrade_cost = 150
        self.zombie_speed = ZOMBIE_BASE_SPEED  # Velocidade inicial dos zumbis

    def create_zombies(self, count):
        self.zombies_to_spawn = count
        self.last_spawn_time = pygame.time.get_ticks() + self.spawn_delay

    def spawn_zombie(self):
        if self.zombies_to_spawn > 0:
            x, y = self.get_spawn_position()
            zombie = Zombie(x, y, self.player, self.zombie_damage, self.damage_interval, self.zombie_health, self.zombie_speed, self)  # Passar o objeto game para Zombie
            self.all_sprites.add(zombie)
            self.zombie_list.add(zombie)
            self.zombies_to_spawn -= 1
            self.last_spawn_time = pygame.time.get_ticks()

    def get_spawn_position(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.randint(0, MAP_WIDTH), -50
        elif side == 'bottom':
            return random.randint(0, MAP_WIDTH), MAP_HEIGHT + 50
        elif side == 'left':
            return -50, random.randint(0, MAP_HEIGHT)
        else:  # right
            return MAP_WIDTH + 50, random.randint(0, MAP_HEIGHT)

    def start_new_round(self):
        self.round += 1
        self.zombies_per_round += 5  # Aumentar 5 zumbis a cada round
        self.zombie_damage = int(self.zombie_damage * 1.1)
        self.zombie_health += 20  # Aumentar 20 de vida a cada round
        self.zombie_speed *= 1.1  # Aumentar a velocidade dos zumbis em 10% a cada round
        self.damage_interval = max(500, self.damage_interval - 100)  # Diminuir 0.1 segundos, mas não menos que 0.5 segundos
        self.shot_interval = max(100, self.shot_interval - 20)  # Diminuir o intervalo de tiro, mas não menos que 0.1 segundos
        self.create_zombies(self.zombies_per_round)

        # Exibir mensagem de troca de round
        self.round_message = f"Round {self.round}"
        self.round_message_start_time = pygame.time.get_ticks()

    def run(self):
        while self.running:
            self.handle_events()
            if not self.game_over and not self.paused and not self.guide_open:
                self.update_sprites()
                self.check_collisions()
                self.check_round_completion()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.changespeed(-5, 0)
                elif event.key == pygame.K_d:
                    self.player.changespeed(5, 0)
                elif event.key == pygame.K_w:
                    self.player.changespeed(0, -5)
                elif event.key == pygame.K_s:
                    self.player.changespeed(0, 5)
                elif event.key == pygame.K_SPACE:
                    self.shooting = True
                elif event.key == pygame.K_ESCAPE:
                    self.running = False  # Adicionar ESC para sair do modo tela cheia
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.player.changespeed(5, 0)
                elif event.key == pygame.K_d:
                    self.player.changespeed(-5, 0)
                elif event.key == pygame.K_w:
                    self.player.changespeed(0, 5)
                elif event.key == pygame.K_s:
                    self.player.changespeed(0, -5)
                elif event.key == pygame.K_SPACE:
                    self.shooting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    if self.restart_button.collidepoint(event.pos):
                        self.game_over = False
                        self.start_new_game()
                elif self.guide_open:
                    if self.close_guide_button.collidepoint(event.pos):
                        self.guide_open = False
                    elif self.resume_button.collidepoint(event.pos):
                        self.paused = False
                elif self.paused:
                    if self.guide_button_rect.collidepoint(event.pos):
                        self.guide_open = True
                    elif self.resume_button.collidepoint(event.pos):
                        self.paused = False
                else:
                    if self.upgrade_button_rect.collidepoint(event.pos):
                        self.upgrade_weapon()
                    elif self.pause_button_rect.collidepoint(event.pos):
                        self.paused = True

    def upgrade_weapon(self):
        if self.wallet.get_coins() >= self.upgrade_cost:
            self.wallet.add_coins(-self.upgrade_cost)
            self.weapon_damage *= 1.3
            self.weapon_speed *= 1.3
            self.shot_interval = max(100, int(self.shot_interval / 1.3))
            self.upgrade_cost += 50 * (len(str(self.upgrade_cost)) - 1)

    def update_sprites(self):
        self.all_sprites.update()
        current_time = pygame.time.get_ticks()
        if self.shooting and current_time - self.last_shot_time > self.shot_interval:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            camera_x = max(0, min(self.player.rect.centerx - self.screen_width // 2, MAP_WIDTH - self.screen_width))
            camera_y = max(0, min(self.player.rect.centery - self.screen_height // 2, MAP_HEIGHT - self.screen_height))
            bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, mouse_x + camera_x, mouse_y + camera_y)
            bullet.speed = self.weapon_speed  # Ajustar a velocidade do projétil
            self.all_sprites.add(bullet)
            self.bullet_list.add(bullet)
            self.last_shot_time = current_time

        if self.player.health <= 0:
            self.game_over = True

        if self.zombies_to_spawn > 0 and current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_zombie()

    def check_collisions(self):
        for bullet in self.bullet_list:
            zombie_hit_list = pygame.sprite.spritecollide(bullet, self.zombie_list, False)
            for zombie in zombie_hit_list:
                if self.insta_kill_active:
                    zombie.take_damage(zombie.health)  # Matar zumbi com um tiro
                else:
                    zombie.take_damage(self.weapon_damage)  # Causar dano normal ao zumbi
                print(f"Zombie hit! Health: {zombie.health}")  # Adiciona uma mensagem de depuração para verificar a saúde dos zumbis
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
                if zombie.health <= 0:
                    print("Zombie killed!")
                    self.all_sprites.remove(zombie)
                    self.zombie_list.remove(zombie)
                    self.kills += 1
                    self.wallet.add_coins(2)  # Adicionar 2 moedas por zumbi morto
                    self.maybe_drop_powerup(zombie.rect.centerx, zombie.rect.centery)

        for powerup in self.drop_list:
            if pygame.sprite.collide_rect(self.player, powerup):
                self.apply_powerup(powerup.effect)
                self.drop_list.remove(powerup)
                self.all_sprites.remove(powerup)

    def apply_powerup(self, effect):
        if effect == 'insta_kill':
            self.insta_kill_active = True
            self.insta_kill_end_time = pygame.time.get_ticks() + 10000  # 10 segundos de insta kill
        elif effect == 'kabum':
            for zombie in self.zombie_list:
                self.all_sprites.remove(zombie)
                self.zombie_list.remove(zombie)
            self.start_new_round()

    def maybe_drop_powerup(self, x, y):
        if random.random() < 0.05:  # 5% de chance
            drop_choice = random.choice(self.drop_images)
            drop = PowerUp(drop_choice['image'], x, y, drop_choice['effect'])
            self.all_sprites.add(drop)
            self.drop_list.add(drop)

    def check_round_completion(self):
        if len(self.zombie_list) == 0 and self.zombies_to_spawn == 0:
            self.start_new_round()

    def draw(self):
        # Definir a posição da câmera
        camera_x = max(0, min(self.player.rect.centerx - self.screen_width // 2, MAP_WIDTH - self.screen_width))
        camera_y = max(0, min(self.player.rect.centery - self.screen_height // 2, MAP_HEIGHT - self.screen_height))

        # Desenhar a parte do fundo visível pela câmera
        for i in range(3):
            for j in range(3):
                self.screen.blit(self.background_images[i % 2 + j % 2], (i * SCREEN_WIDTH - camera_x, j * SCREEN_HEIGHT - camera_y))

        # Desenhar todos os sprites com a posição ajustada pela câmera
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))

        for zombie in self.zombie_list:
            zombie.draw_health_bar(self.screen, camera_x, camera_y)  # Desenhar barra de vida dos zumbis

        self.draw_hud()
        self.draw_round_message()
        self.draw_upgrade_button()

        if self.insta_kill_active:
            self.screen.blit(self.insta_kill_icon, (self.screen_width - 100, 100))
            if pygame.time.get_ticks() > self.insta_kill_end_time:
                self.insta_kill_active = False
        
        if self.game_over:
            self.draw_game_over()
        if self.paused:
            self.draw_pause_screen()
        if self.guide_open:
            self.draw_guide_screen()
        
        # Efeito de piscada vermelha
        if self.damage_flash:
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_flash_start_time < self.damage_flash_duration:
                red_overlay = pygame.Surface((self.screen_width, self.screen_height))
                red_overlay.set_alpha(50)  # Transparência do vermelho ajustada
                red_overlay.fill((255, 0, 0))
                self.screen.blit(red_overlay, (0, 0))
            else:
                self.damage_flash = False

        pygame.display.flip()

    def draw_hud(self):
        health_text = self.font.render(f'Health: {self.player.health}', True, (0, 0, 0))
        round_text = self.font.render(f'Round: {self.round}', True, (0, 0, 0))
        kills_text = self.font.render(f'Kills: {self.kills}', True, (0, 0, 0))
        coins_text = self.font.render(f'Coins: {self.wallet.get_coins()}', True, (0, 0, 0))

        self.screen.blit(health_text, (10, 100))
        self.screen.blit(round_text, (10, 130))
        self.screen.blit(kills_text, (10, 160))
        self.screen.blit(coins_text, (self.screen_width - 150, 10))  # Exibir moedas no canto superior direito
        
        # Desenhar o botão de pausa acima do HUD
        self.screen.blit(self.pause_button_image, self.pause_button_rect)

    def draw_game_over(self):
        game_over_text = self.font.render('Game Over', True, (255, 0, 0))
        restart_text = self.font.render('Click to Restart', True, (0, 0, 255))
        
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))

        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(restart_text, restart_rect)
        
        self.restart_button = restart_rect

    def draw_round_message(self):
        if self.round_message:
            current_time = pygame.time.get_ticks()
            if current_time - self.round_message_start_time < self.round_message_duration:
                round_message_text = self.large_font.render(self.round_message, True, (0, 0, 0))
                text_rect = round_message_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(round_message_text, text_rect)
            else:
                self.round_message = ""

    def draw_upgrade_button(self):
        if self.wallet.get_coins() >= self.upgrade_cost:
            self.screen.blit(self.upgrade_button_image, self.upgrade_button_rect)

    def draw_pause_screen(self):
        # Desenhar fundo da janela de pausa
        pause_overlay = pygame.Surface((self.screen_width, self.screen_height))
        pause_overlay.set_alpha(128)  # Transparência do overlay
        pause_overlay.fill((0, 0, 0))
        self.screen.blit(pause_overlay, (0, 0))

        # Desenhar texto de pausa
        pause_text = self.large_font.render('Game Paused', True, WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(pause_text, pause_rect)

        # Desenhar botão de retomar
        resume_text = self.font.render('Resume', True, WHITE, (128, 128, 128))
        resume_rect = resume_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
        self.resume_button = resume_rect

        # Desenhar botão de guia
        guide_text = self.font.render('Guide', True, WHITE, (128, 128, 128))
        guide_rect = guide_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        self.screen.blit(guide_text, guide_rect)
        self.guide_button_rect = guide_rect

    def draw_guide_screen(self):
        # Desenhar fundo da janela de guia
        guide_overlay = pygame.Surface((self.screen_width - 200, self.screen_height - 200))
        guide_overlay.fill((255, 255, 255))
        guide_rect = guide_overlay.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(guide_overlay, guide_rect)

        # Desenhar texto de guia
        guide_text = [
            'Movimentacao:',
            'W - Andar para frente',
            'A - Andar para esquerda',
            'S - Andar para tras',
            'D - Andar para direita',
            'Space - Atirar',
            'Mouse - Guia os tiros de acordo com a direcao do mouse',
            '',
            'Icones:',
            ''
        ]
        y_offset = guide_rect.top + 20
        for line in guide_text:
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surface, (guide_rect.left + 20, y_offset))
            y_offset += 30

        # Desenhar imagens de guia
        icon_images = ['instaKill.png', 'kabum.png', 'upgrade_button.png']
        icon_descriptions = [
            ' - InstaKill: Mata zumbis com um tiro por 10 segundos',
            ' - Kabum: Mata todos os zumbis do round',
            ' - Upgrade: Upa os atributos da sua arma, custa 150 moedas'
        ]
        for icon, desc in zip(icon_images, icon_descriptions):
            icon_image = pygame.image.load(os.path.join('images', icon))
            icon_image = pygame.transform.scale(icon_image, (30, 30))
            self.screen.blit(icon_image, (guide_rect.left + 20, y_offset))
            text_surface = self.font.render(desc, True, (0, 0, 0))
            self.screen.blit(text_surface, (guide_rect.left + 60, y_offset))
            y_offset += 40

        # Desenhar botão de fechar
        close_text = self.font.render('X', True, (0, 0, 0), (255, 0, 0))
        close_rect = close_text.get_rect(topleft=(guide_rect.right - 40, guide_rect.top + 20))
        self.screen.blit(close_text, close_rect)
        self.close_guide_button = close_rect

if __name__ == "__main__":
    game = Game()
    game.run()
