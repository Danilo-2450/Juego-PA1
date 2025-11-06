import pygame 
from sys import exit


#Variables del juego

GAME_WIDTH = 360
GAME_HEIGHT = 640

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH , GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

while True: 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            pygame.quit()
            exit()

    pygame.display.update()
    clock.tick(60)  #60 fps
    