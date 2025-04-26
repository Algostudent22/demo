import pygame
import random
import os
# ! jhdakjfhkjsafks
# TODO djisadjis
# Инициализация pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 700, 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Космический шутер')

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Загрузка изображений
def load_image(name, size):
    try:
        image = pygame.image.load(name)
        return pygame.transform.scale(image, size)
    except:
        surface = pygame.Surface(size)
        surface.fill(RED if "heart" in name else WHITE)
        return surface

# Класс спрайта
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, speed, x, y, width, height):
        super().__init__()
        self.image = load_image(image, (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Игрок
class Player(GameSprite):
    def __init__(self, image, speed, x, y, width, height):
        super().__init__(image, speed, x, y, width, height)
        self.lives = 2
        self.reloading = False
        self.last_shot = 0
        self.shots_fired = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.x > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed
    
    def fire(self):
        now = pygame.time.get_ticks()
        if not self.reloading and now - self.last_shot > 200:  # 200ms задержка
            if self.shots_fired < 5:
                bullet = Bullet("bullet.png", 10, self.rect.centerx-7, self.rect.top, 15, 20)
                bullets.add(bullet)
                self.shots_fired += 1
                self.last_shot = now
            else:
                self.start_reload()
    
    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_start = pygame.time.get_ticks()
    
    def update_reload(self):
        if self.reloading:
            if pygame.time.get_ticks() - self.reload_start >= 3000:  # 3 секунды
                self.reloading = False
                self.shots_fired = 0

# Враги
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.reset_pos()
            global lose
            lose += 1
    
    def reset_pos(self):
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(2, 5)

# Астероиды
class Asteroid(GameSprite):
    def __init__(self, image, speed, x, y, width, height):
        super().__init__(image, speed, x, y, width, height)
        self.speed = random.randint(1, 3)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.reset_pos()
    
    def reset_pos(self):
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

# Пули
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

# Инициализация
hero = Player("rocket.png", 5, WIDTH//2, HEIGHT-100, 65, 80)
bullets = pygame.sprite.Group()
monsters = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Создание врагов
for _ in range(4):
    monster = Enemy("ufo.png", random.randint(2, 5), random.randint(0, WIDTH-60), -60, 60, 50)
    monsters.add(monster)

# Создание астероидов
for _ in range(3):  # Установлено 3 астероида
    asteroid = Asteroid("asteroid.png", random.randint(1, 3), random.randint(0, WIDTH-50), -50, 50, 50)
    asteroids.add(asteroid)

# Загрузка фона и сердец
background = load_image("galaxy.jpg", (WIDTH, HEIGHT))
heart_img = load_image("pngwing.com.png", (30, 30))  # Ваше сердце из pngwing.com.png

# Шрифты
font_small = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 70)

# Игровые переменные
score = 0
lose = 0
goal = 30
game_over = False
clock = pygame.time.Clock()

# Главный цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                hero.fire()
            if event.key == pygame.K_r and game_over:
                # Рестарт игры
                game_over = False
                score = 0
                lose = 0
                hero.lives = 2
                for m in monsters:
                    m.reset_pos()
                for a in asteroids:
                    a.reset_pos()
                bullets.empty()
                hero.shots_fired = 0
                hero.reloading = False
    
    if not game_over:
        # Обновление объектов
        hero.update()
        hero.update_reload()
        monsters.update()
        asteroids.update()
        bullets.update()
        
        # Проверка столкновений
        # Пули с врагами
        hits = pygame.sprite.groupcollide(monsters, bullets, True, True)
        for hit in hits:
            score += 1
            monster = Enemy("ufo.png", random.randint(2, 5),
                          random.randint(0, WIDTH-60), -60, 60, 50)
            monsters.add(monster)
        
        # Игрок с астероидами
        asteroid_hits = pygame.sprite.spritecollide(hero, asteroids, False)
        for asteroid in asteroid_hits:
            hero.lives -= 1
            asteroid.reset_pos()
            if hero.lives <= 0:
                game_over = True
        
        # Проверка условий окончания игры
        if lose >= 20 or score >= goal:
            game_over = True
    
    # Отрисовка
    window.blit(background, (0, 0))
    
    # Отрисовка спрайтов
    hero.reset()
    monsters.draw(window)
    asteroids.draw(window)
    bullets.draw(window)
    
    # Отрисовка интерфейса
    # Счетчики
    score_text = font_small.render(f"Убито: {score}/{goal}", True, WHITE)
    miss_text = font_small.render(f"Пропущено: {lose}/10", True, WHITE)
    ammo_text = font_small.render(f"Патроны: {5 - hero.shots_fired}/5", True, WHITE)
    reload_text = font_small.render("ПЕРЕЗАРЯДКА!", True, RED) if hero.reloading else font_small.render("", True, WHITE)
    
    window.blit(score_text, (10, 10))
    window.blit(miss_text, (10, 50))
    window.blit(ammo_text, (10, 90))
    window.blit(reload_text, (WIDTH//2 - 100, 10))
    
    # Жизни (сердечки)
    for i in range(hero.lives):
        window.blit(heart_img, (WIDTH - 40 - i*35, 10))
    
    # Сообщение о конце игры
    if game_over:
        if score >= goal:
            result = font_large.render("ПОБЕДА!", True, GREEN)
        else:
            result = font_large.render("ПОРАЖЕНИЕ!", True, RED)
        restart = font_small.render("Нажми R для рестарта", True, WHITE)
        
        window.blit(result, (WIDTH//2 - 100, HEIGHT//2 - 50))
        window.blit(restart, (WIDTH//2 - 120, HEIGHT//2 + 20))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
