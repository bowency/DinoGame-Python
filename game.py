import pygame
import random
import numpy as np
from neural_network import DinoAI

class Dino:
    def __init__(self, bg_color):
        self.width = 44
        self.height = 60
        self.x = 50
        self.y = 300
        self.velocity_y = 0
        self.jumping = False
        self.ducking = False
        self.original_height = 47
        self.duck_height = 30
        
        # Загрузка спрайта (если есть)
        try:
            self.image = pygame.image.load("assets/dinosaur.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.use_sprite = True
        except:
            self.use_sprite = False
        
        self.bg_color = bg_color
        self.jump_power = -12
        self.gravity = 0.4
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = self.jump_power
            self.jumping = True
    
    def duck(self, ducking):
        self.ducking = ducking
        if ducking:
            self.height = self.duck_height
        else:
            self.height = self.original_height
    
    def update(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Проверка земли
        if self.y >= 300:
            self.y = 300
            self.jumping = False
            self.velocity_y = 0
    
    def draw(self, screen):
        if self.use_sprite:
            # Масштабируем спрайт при приседании
            img = pygame.transform.scale(self.image, (self.width, self.height))
            screen.blit(img, (self.x, self.y))
        else:
            # Рисуем прямоугольник-заглушку
            color = (0, 0, 0) if self.bg_color == (255, 255, 255) else (255, 255, 255)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_sensor_rect(self):
        # Синий прямоугольник-сенсор перед динозавром
        return pygame.Rect(self.x + self.width, self.y - 20, 150, self.height + 40)


class Obstacle:
    def __init__(self, speed, bg_color):
        self.type = random.choice(["cactus", "bird"])
        self.bg_color = bg_color
        
        if self.type == "cactus":
            self.width = 20
            self.height = random.choice([30, 40, 50])
            self.y = 300
            try:
                self.image = pygame.image.load("assets/cactus.jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.use_sprite = True
            except:
                self.use_sprite = False
        else:  # bird
            self.width = 40
            self.height = 30
            self.y = random.choice([250, 220, 190])  # Разные высоты
            try:
                self.image = pygame.image.load("assets/bird.jpg").convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.use_sprite = True
            except:
                self.use_sprite = False
        
        self.x = 800
        self.speed = speed
        self.passed = False
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        if self.use_sprite:
            screen.blit(self.image, (self.x, self.y))
        else:
            color = (0, 128, 0) if self.type == "cactus" else (255, 0, 0)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def off_screen(self):
        return self.x < -self.width


class DinoGame:
    def __init__(self, screen, clock, bg_color, difficulty):
        self.screen = screen
        self.clock = clock
        self.bg_color = bg_color
        self.difficulty = difficulty
        
        # Настройки сложности
        diff_settings = {
            "easy": {"speed": 5, "spawn_rate": 100},
            "normal": {"speed": 8, "spawn_rate": 75},
            "hard": {"speed": 12, "spawn_rate": 50}
        }
        
        self.speed = diff_settings[difficulty]["speed"]
        self.spawn_rate = diff_settings[difficulty]["spawn_rate"]
        
        self.dino = Dino(bg_color)
        self.obstacles = []
        self.score = 0
        self.high_score = 0
        self.frame_count = 0
        self.game_over = False
        self.auto_play = False
        
        # ИИ для автоигры
        self.ai = DinoAI()
        self.trained = False
        
        # Шрифты
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 74)
        
        # Цвет текста
        self.text_color = (0, 0, 0) if bg_color == (255, 255, 255) else (255, 255, 255)
    
    def spawn_obstacle(self):
        if self.frame_count % self.spawn_rate == 0:
            if random.random() < 0.3:  # 30% шанс птицы
                self.obstacles.append(Obstacle(self.speed, self.bg_color))
            elif len(self.obstacles) == 0 or self.obstacles[-1].x < 600:
                self.obstacles.append(Obstacle(self.speed, self.bg_color))
    
    def check_collision(self):
        dino_rect = self.dino.get_rect()
        for obstacle in self.obstacles:
            if dino_rect.colliderect(obstacle.get_rect()):
                return True
        return False
    
    def draw_sensor(self):
        """Отрисовка синего контура сенсора перед динозавром"""
        sensor_rect = self.dino.get_sensor_rect()
        pygame.draw.rect(self.screen, (0, 0, 255), sensor_rect, 2)
    
    def get_sensor_data(self):
        """
        Собирает данные из зоны сенсора.
        Возвращает словарь с информацией о ближайшем препятствии.
        """
        nearest_obstacle = None
        min_distance = float('inf')
        
        for obstacle in self.obstacles:
            # Расстояние от носа динозавра до препятствия
            distance = obstacle.x - (self.dino.x + self.dino.width)
            # Рассматриваем только препятствия перед нами в пределах видимости
            if 0 < distance < 400:
                if distance < min_distance:
                    min_distance = distance
                    nearest_obstacle = obstacle
        
        return {'obstacle': nearest_obstacle}
    
    def ai_decision(self):
        """Логика принятия решений ИИ на основе предсказаний нейросети"""
        sensor_data = self.get_sensor_data()
        action = self.ai.predict_action(sensor_data)
        
        if action == 1:  # Прыжок
            if not self.dino.jumping:
                self.dino.jump()
            self.dino.duck(False)
        elif action == 2:  # Приседание
            self.dino.duck(True)
        else:  # Ничего не делать
            self.dino.duck(False)
    
    def reset_game(self):
        """Сброс игры в начальное состояние"""
        self.dino = Dino(self.bg_color)
        self.obstacles = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False
    
    def train_ai(self):
        """Запуск обучения нейросети на синтетических данных"""
        print("Training AI...")
        self.ai.train_with_synthetic_data()
        print("AI trained!")
    
    def run(self):
        running = True
        
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.game_over:
                            if not self.auto_play:
                                self.dino.jump()
                        else:
                            # Перезапуск игры
                            self.reset_game()
                    
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        if not self.game_over and not self.auto_play:
                            self.dino.duck(True)
                    
                    if event.key == pygame.K_UP:
                        # Переключение режима автоигры
                        self.auto_play = not self.auto_play
                        if self.auto_play and not self.ai.fitted:
                            print("⚠️ Модель не обучена! Нажмите 'T' для авто-обучения.")
                    
                    if event.key == pygame.K_t:
                        # Обучение ИИ (можно нажимать в любой момент)
                        self.train_ai()
                    
                    if event.key == pygame.K_ESCAPE:
                        return
            
            # Обработка отпускания клавиш (отдельно от KEYDOWN)
            keys = pygame.key.get_pressed()
            if not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                self.dino.duck(False)
            
            if not self.game_over:
                # Автоигра или ручное управление
                if self.auto_play:
                    self.ai_decision()
                
                # Обновление
                self.dino.update()
                self.spawn_obstacle()
                
                for obstacle in self.obstacles:
                    obstacle.update()
                
                # Удаление ушедших препятствий
                self.obstacles = [obs for obs in self.obstacles if not obs.off_screen()]
                
                # Проверка столкновений
                if self.check_collision():
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                
                # Увеличение счета
                self.frame_count += 1
                if self.frame_count % 5 == 0:
                    self.score += 1
                
                # Увеличение сложности
                if self.score % 100 == 0 and self.score > 0:
                    self.speed += 0.5
            
            # Отрисовка
            self.screen.fill(self.bg_color)
            
            # Земля
            ground_color = (0, 0, 0) if self.bg_color == (255, 255, 255) else (255, 255, 255)
            pygame.draw.line(self.screen, ground_color, (0, 347), (800, 347), 2)
            
            # Сенсор (в режиме автоигры)
            if self.auto_play:
                self.draw_sensor()
            
            # Препятствия
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            
            # Динозавр
            self.dino.draw(self.screen)
            
            # Счет
            score_text = f"Score: {self.score}"
            high_score_text = f"HI: {self.high_score}"
            self.screen.blit(self.font.render(score_text, True, self.text_color), (10, 10))
            self.screen.blit(self.font.render(high_score_text, True, self.text_color), (10, 40))
            
            # Режим автоигры
            if self.auto_play:
                ai_text = "AUTO PLAY [UP] | Train AI [T]"
                self.screen.blit(self.font.render(ai_text, True, (0, 0, 255)), (450, 10))
            
            # Game Over
            if self.game_over:
                overlay = pygame.Surface((800, 400))
                overlay.set_alpha(128)
                overlay.fill(self.bg_color)
                self.screen.blit(overlay, (0, 0))
                
                go_text = self.large_font.render("GAME OVER", True, self.text_color)
                restart_text = self.font.render("Press SPACE to restart", True, self.text_color)
                train_text = self.font.render("Press T to train AI", True, self.text_color)
                
                self.screen.blit(go_text, go_text.get_rect(center=(400, 150)))
                self.screen.blit(restart_text, restart_text.get_rect(center=(400, 220)))
                self.screen.blit(train_text, train_text.get_rect(center=(400, 260)))
            
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()
    game = DinoGame(screen, clock, (255, 255, 255), "normal")
    game.run()
    pygame.quit()