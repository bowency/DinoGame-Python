import pygame
import sys

class MainMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.bg_color = (255, 255, 255)  # Белый
        self.difficulty = "normal"  # easy, normal, hard
        
        # Кнопки
        self.buttons = {
            "start": pygame.Rect(250, 200, 300, 50),
            "exit": pygame.Rect(250, 280, 300, 50),
            "bg_white": pygame.Rect(150, 120, 100, 40),
            "bg_black": pygame.Rect(300, 120, 100, 40),
            "easy": pygame.Rect(100, 160, 120, 40),
            "normal": pygame.Rect(240, 160, 120, 40),
            "hard": pygame.Rect(380, 160, 120, 40)
        }
        
        self.selected_bg = "white"
        self.selected_difficulty = "normal"
    
    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)
        return rect
    
    def draw_button(self, rect, text, active=False):
        color = (100, 100, 255) if active else (200, 200, 200)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, (0, 0, 0), 
                      rect.centerx, rect.centery, center=True)
    
    def run(self):
        running = True
        while running:
            self.screen.fill(self.bg_color)
            
            # Заголовок
            self.draw_text("DINO GAME", self.font_large, (0, 0, 0), 
                          400, 40, center=True)
            
            # Выбор фона
            self.draw_text("Background color:", self.font_small, (0, 0, 0), 150, 100)
            self.draw_button(self.buttons["bg_white"], "White", 
                           self.selected_bg == "white")
            self.draw_button(self.buttons["bg_black"], "Black", 
                           self.selected_bg == "black")
            
            # Выбор сложности
            self.draw_text("Difficult:", self.font_small, (0, 0, 0), 100, 140)
            self.draw_button(self.buttons["easy"], "Easy", 
                           self.selected_difficulty == "easy")
            self.draw_button(self.buttons["normal"], "Medium", 
                           self.selected_difficulty == "medium")
            self.draw_button(self.buttons["hard"], "Hard", 
                           self.selected_difficulty == "hard")
            
            # Кнопки начала и выхода
            self.draw_button(self.buttons["start"], "Start Game", True)
            self.draw_button(self.buttons["exit"], "Quit", True)
            
            pygame.display.flip()
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    # Выбор фона
                    if self.buttons["bg_white"].collidepoint(mouse_pos):
                        self.selected_bg = "white"
                        self.bg_color = (255, 255, 255)
                    elif self.buttons["bg_black"].collidepoint(mouse_pos):
                        self.selected_bg = "black"
                        self.bg_color = (0, 0, 0)
                    
                    # Выбор сложности
                    if self.buttons["easy"].collidepoint(mouse_pos):
                        self.selected_difficulty = "easy"
                    elif self.buttons["normal"].collidepoint(mouse_pos):
                        self.selected_difficulty = "normal"
                    elif self.buttons["hard"].collidepoint(mouse_pos):
                        self.selected_difficulty = "hard"
                    
                    # Старт/выход
                    if self.buttons["start"].collidepoint(mouse_pos):
                        return "start"
                    elif self.buttons["exit"].collidepoint(mouse_pos):
                        return "exit"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
            
            self.clock.tick(60)
        
        return "exit"