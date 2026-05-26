import pygame
import sys
from menu import MainMenu
from game import DinoGame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("Dino Game")
    clock = pygame.time.Clock()
    
    # Показываем главное меню
    menu = MainMenu(screen, clock)
    result = menu.run()
    
    if result == "start":
        # Запускаем игру с настройками из меню
        game = DinoGame(screen, clock, menu.bg_color, menu.difficulty)
        game.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()