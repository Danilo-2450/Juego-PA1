import pygame
from sys import exit
import random

# Variables del juego
GAME_WIDTH = 360
GAME_HEIGHT = 640

#Estados del juego
MENU = 0
JUGANDO = 1
PERDIDO = 2
estado = MENU

# Clase pájaro
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird_width = 34
bird_height = 24

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img

# Clase tubería
tuberia_x = GAME_WIDTH
tuberia_y = 0
tuberia_width = 64
tuberia_height = 512

class Tuberia(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, tuberia_x, tuberia_y, tuberia_width, tuberia_height)
        self.img = img
        self.passed = False

# Imágenes del juego
background_image = pygame.image.load("sky.png")
bird_image = pygame.image.load("Flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
tuberia_superior_image = pygame.image.load("tuberia_superior.png")
tuberia_superior_image = pygame.transform.scale(tuberia_superior_image, (tuberia_width, tuberia_height))
tuberia_inferior_image = pygame.image.load("tuberia_inferior.png")
tuberia_inferior_image = pygame.transform.scale(tuberia_inferior_image, (tuberia_width, tuberia_height))

# Lógica del juego
bird = Bird(bird_image)
tuberias = []
velocidad_x = -2
velocidad_y = 0
gravedad = 0.4
puntuacion = 0
game_over = False

def reiniciar_juego():
    global bird, tuberias, velocidad_y, puntuacion
    bird.y = bird_y
    tuberias.clear()
    velocidad_y = 0
    puntuacion = 0

def draw_menu(window):
    window.blit(background_image, (0, 0))
    font_title = pygame.font.SysFont("Comic Sans MS", 40)
    font_sub = pygame.font.SysFont("Comic Sans MS", 30)

    title = font_title.render(" FLAPPY BIRD", True, "white")
    start = font_sub.render("Presiona ESPACIO", True, "yellow")

    window.blit(title, (40, 200))
    window.blit(start, (50, 300))

def draw_game(window):
    window.blit(background_image, (0, 0))
    window.blit(bird.img, bird)

    for tuberia in tuberias:
        window.blit(tuberia.img, tuberia)

    text_font = pygame.font.SysFont("Comic Sans MS", 45)
    text_render = text_font.render(str(int(puntuacion)), True, "white")
    window.blit(text_render, (5, 0))

def draw_game_over(window):
    draw_game(window)
    font_over = pygame.font.SysFont("Comic Sans MS", 45)
    font_sub = pygame.font.SysFont("Comic Sans MS", 20)

    text = font_over.render("¡PERDISTE! ", True, "red")
    retry = font_sub.render(" Presiona ESPACIO para reiniciar", True, "yellow")

    window.blit(text, (60, 250))
    window.blit(retry, (20, 320))


def move():
    global velocidad_y, puntuacion, estado
    velocidad_y += gravedad
    bird.y += velocidad_y
    bird.y = max(bird.y, 0)

    if bird.y > GAME_HEIGHT:
        estado = PERDIDO
        return

    for tuberia in tuberias:
        tuberia.x += velocidad_x

        if not tuberia.passed and bird.x > tuberia.x + tuberia.width:
            puntuacion += 0.5
            tuberia.passed = True

        if bird.colliderect(tuberia):
            estado = PERDIDO
            return

    while len(tuberias) > 0 and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)

def crear_tuberias():
    random_y = tuberia_y - tuberia_height / 4 - random.random() * (tuberia_height / 2)
    espacio = GAME_HEIGHT / 4

    tuberia_superior = Tuberia(tuberia_superior_image)
    tuberia_superior.y = random_y
    tuberias.append(tuberia_superior)

    tuberia_inferior = Tuberia(tuberia_inferior_image)
    tuberia_inferior.y = tuberia_superior.y + tuberia_superior.height + espacio
    tuberias.append(tuberia_inferior)

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

temporizador_tuberias = pygame.USEREVENT + 0
pygame.time.set_timer(temporizador_tuberias, 1500)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):

                if estado == MENU:
                    reiniciar_juego()
                    estado = JUGANDO

                elif estado == JUGANDO:
                    velocidad_y = -6

                elif estado == PERDIDO:
                    reiniciar_juego()
                    estado = MENU

        if event.type == temporizador_tuberias and estado == JUGANDO:
            crear_tuberias()
    
    if estado == JUGANDO:
        move()
    if estado == MENU:
        draw_menu(window)
    elif estado == JUGANDO:
        draw_game(window)
    elif estado == PERDIDO:
        draw_game_over(window)
        
    pygame.display.update()
    clock.tick(60)
