import pygame
from sys import exit
import random

# Variables del juego
GAME_WIDTH = 360
GAME_HEIGHT = 640

# Estados del juego
MENU = 0
JUGANDO = 1
PERDIDO = 2
estado = MENU

# Clase pájaro (BORRADOR 1 - Rotación simple)
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird_width = 34
bird_height = 24

class Bird:
    def __init__(self, img, x, y, w, h):
        self.img = img
        self.rect = pygame.Rect(x, y, w, h)
        self.x_float = float(x)
        self.y_float = float(y)
        self.vel_y = 0.0
        self.angle = 0

    def update_rect(self):
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def update_angle(self):
        if self.vel_y < 0:
            self.angle = 25
        else:
            self.angle = -25

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.y_float += self.vel_y
        self.update_angle()
        self.update_rect()

    def jump(self, jump_speed):
        self.vel_y = jump_speed

    def check_boundary(self, height):
        return self.rect.y > height

    def draw(self, surface):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=self.rect.center)
        surface.blit(rotated_img, new_rect)


# Clase tubería
tuberia_x = GAME_WIDTH
tuberia_y = 0
tuberia_width = 64
tuberia_height = 512

class Tuberia(pygame.Rect):
    def __init__(self, img, x, y, w, h):
        pygame.Rect.__init__(self, x, y, w, h)
        self.img = img
        self.passed = False

# Clase Botón 
class Button:
    def __init__(self, x, y, width, height, bg_color="gray", text="", font=None, text_color="white"):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, "black", self.rect, 2)
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                return True
        return False

# Imágenes
background_image = pygame.image.load("sky.png")
bird_image = pygame.image.load("Flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
tuberia_superior_image = pygame.transform.scale(pygame.image.load("tuberia_superior.png"), (tuberia_width, tuberia_height))
tuberia_inferior_image = pygame.transform.scale(pygame.image.load("tuberia_inferior.png"), (tuberia_width, tuberia_height))

# Lógica
bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
tuberias = []
velocidad_x = -2
puntuacion = 0

def reiniciar_juego():
    global bird, tuberias, puntuacion
    bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
    tuberias.clear()
    puntuacion = 0

def draw_menu(window):
    window.blit(background_image, (0,0))
    font_title = pygame.font.SysFont("Comic Sans MS", 40)
    title = font_title.render(" FLAPPY BIRD", True, "white")
    window.blit(title, (40, 100))
    button_play.draw(window)

def draw_game(window):
    window.blit(background_image, (0,0))
    bird.draw(window)
    for tuberia in tuberias:
        window.blit(tuberia.img, tuberia)
    text_font = pygame.font.SysFont("Comic Sans MS", 45)
    window.blit(text_font.render(str(int(puntuacion)), True, "white"), (5, 0))

def draw_game_over(window):
    draw_game(window)
    font_over = pygame.font.SysFont("Comic Sans MS", 45)
    window.blit(font_over.render("¡PERDISTE!", True, "red"), (60, 200))
    button_play.rect.y = 320
    button_play.draw(window)

def move():
    global puntuacion, estado
    bird.apply_gravity(0.4)
    if bird.check_boundary(GAME_HEIGHT):
        estado = PERDIDO
        return
    for tuberia in tuberias:
        tuberia.x += velocidad_x
        if not tuberia.passed and bird.rect.x > tuberia.x + tuberia.width:
            puntuacion += 0.5
            tuberia.passed = True
        if bird.rect.colliderect(tuberia):
            estado = PERDIDO
            return
    while len(tuberias) > 0 and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)

def crear_tuberias():
    random_y = tuberia_y - tuberia_height / 4 - random.random() * (tuberia_height / 2)
    espacio = GAME_HEIGHT / 4
    tuberias.append(Tuberia(tuberia_superior_image, tuberia_x, int(random_y), tuberia_width, tuberia_height))
    tuberias.append(Tuberia(tuberia_inferior_image, tuberia_x, int(random_y + tuberia_height + espacio), tuberia_width, tuberia_height))

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

button_play = Button(GAME_WIDTH//2 - 75, 300, 150, 50, bg_color="orange", text="Jugar", font=pygame.font.SysFont("Comic Sans MS", 25))

temporizador_tuberias = pygame.USEREVENT + 1
pygame.time.set_timer(temporizador_tuberias, 1500)

while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if estado in (MENU, PERDIDO):
            if button_play.is_clicked(mouse_pos, event):
                reiniciar_juego()
                estado = JUGANDO

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                if estado == MENU:
                    reiniciar_juego()
                    estado = JUGANDO
                elif estado == JUGANDO:
                    bird.jump(-6)
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
