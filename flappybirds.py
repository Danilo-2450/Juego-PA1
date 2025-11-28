import pygame
import random
import os
from sys import exit

# -------------------- Inicialización --------------------
pygame.init()
clock = pygame.time.Clock()

# -------------------- Pantalla --------------------
GAME_WIDTH = 360
GAME_HEIGHT = 640
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird - Modo Amarillo")

# -------------------- Estados --------------------
MENU = 0
JUGANDO = 1
PERDIDO = 2
PAUSA = 3
estado = MENU

# -------------------- Parámetros --------------------
FPS = 60
bird_width = 34
bird_height = 24
tuberia_width = 64
tuberia_height = 512
tuberia_x = GAME_WIDTH
tuberia_y = 0
velocidad_x = -2

# -------------------- Récord --------------------
RECORD_FILE = "record.txt"

def cargar_record():
    try:
        with open(RECORD_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def guardar_record(score):
    try:
        with open(RECORD_FILE, "w") as f:
            f.write(str(int(score)))
    except Exception as e:
        print("Error guardando récord:", e)

record = cargar_record()

# -------------------- Clases --------------------
class Bird:
    def __init__(self, img, x, y, w, h):
        self.img = img
        self.rect = pygame.Rect(int(x), int(y), w, h)
        self.x_float = float(x)
        self.y_float = float(y)
        self.vel_y = 0.0
        self.angle = 0

    def update_rect(self):
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def update_angle(self):
        ang = -self.vel_y * 4
        if ang > 25: ang = 25
        if ang < -25: ang = -25
        self.angle = ang

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.y_float += self.vel_y
        if self.y_float < 0:
            self.y_float = 0
            self.vel_y = 0
        self.update_angle()
        self.update_rect()

    def jump(self, jump_speed):
        self.vel_y = jump_speed

    def check_boundary(self, height):
        return self.rect.y > height - 10

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, new_rect)

class Tuberia(pygame.Rect):
    def __init__(self, img, x, y, w, h):
        super().__init__(int(x), int(y), int(w), int(h))
        self.img = img
        self.passed = False

class Button:
    def __init__(self, x, y, width, height, bg_color=(150,150,150), text="", font=None, text_color=(255,255,255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# -------------------- Carga de imágenes --------------------
def safe_load_image(path, size=None, alpha=True):
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 0))
        return surf

background_image = safe_load_image("sky.png", (GAME_WIDTH, GAME_HEIGHT), alpha=False)

# --- EL ÚNICO PÁJARO ---
bird_image = safe_load_image("flappybirds.png", (bird_width, bird_height))

tuberia_superior_image = safe_load_image("tuberia_superior.png", (tuberia_width, tuberia_height))
tuberia_inferior_image = safe_load_image("tuberia_inferior.png", (tuberia_width, tuberia_height))

# -------------------- Variables del juego --------------------
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
tuberias = []
puntuacion = 0.0

temporizador_tuberias = pygame.USEREVENT + 0
pygame.time.set_timer(temporizador_tuberias, 1500)

# -------------------- Fuentes y botones --------------------
font_title = pygame.font.SysFont("Comic Sans MS", 40)
font_button = pygame.font.SysFont("Comic Sans MS", 25)
font_score = pygame.font.SysFont("Comic Sans MS", 45)
font_small = pygame.font.SysFont("Comic Sans MS", 24)

button_width = 150
button_height = 50
button_x = GAME_WIDTH // 2 - button_width // 2
button_y = 300
button_play = Button(button_x, button_y, button_width, button_height, (255,165,0), "Jugar", font_button, (0,0,0))

# -------------------- Funciones --------------------
def reiniciar_juego():
    global bird, tuberias, puntuacion
    bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
    tuberias.clear()
    puntuacion = 0.0

def crear_tuberias():
    random_y = tuberia_y - tuberia_height / 4 - random.random() * (tuberia_height / 2)
    espacio = GAME_HEIGHT / 4
    superior = Tuberia(tuberia_superior_image, tuberia_x, int(random_y), tuberia_width, tuberia_height)
    inferior = Tuberia(tuberia_inferior_image, tuberia_x, int(random_y + tuberia_height + espacio), tuberia_width, tuberia_height)
    tuberias.append(superior)
    tuberias.append(inferior)

def move():
    global puntuacion, estado, record
    bird.apply_gravity(0.4)

    if bird.check_boundary(GAME_HEIGHT):
        if puntuacion > record:
            record = int(puntuacion)
            guardar_record(record)
        estado = PERDIDO
        return

    for tuberia in tuberias:
        tuberia.x += velocidad_x

        if not tuberia.passed and bird.rect.x > tuberia.x + tuberia.width:
            puntuacion += 0.5
            tuberia.passed = True

        if bird.rect.colliderect(tuberia):
            if puntuacion > record:
                record = int(puntuacion)
                guardar_record(record)
            estado = PERDIDO
            return

    while len(tuberias) > 0 and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)

# -------------------- Dibujado --------------------
def draw_menu(window):
    window.blit(background_image, (0, 0))
    title = font_title.render(" FLAPPY BIRD", True, (255,255,255))
    window.blit(title, (40, 120))
    button_play.draw(window)
    rec_text = font_small.render(f"Récord: {record}", True, (255,255,255))
    window.blit(rec_text, (10, 10))

def draw_game(window):
    window.blit(background_image, (0, 0))
    for tuberia in tuberias:
        window.blit(tuberia.img, (tuberia.x, tuberia.y))
    bird.draw(window)
    window.blit(font_score.render(str(int(puntuacion)), True, (255,255,255)), (5, 0))
    window.blit(font_small.render(f"Récord: {record}", True, (255,255,255)), (GAME_WIDTH - 120, 8))

def draw_game_over(window):
    draw_game(window)
    text = pygame.font.SysFont("Comic Sans MS", 45).render("¡PERDISTE!", True, (255,0,0))
    window.blit(text, (60, 150))
    info = pygame.font.SysFont("Comic Sans MS", 28)
    window.blit(info.render(f"Puntuación: {int(puntuacion)}", True, (255,255,255)), (80, 220))
    window.blit(info.render(f"Récord: {record}", True, (255,255,255)), (80, 260))
    button_play.rect.y = 320
    button_play.draw(window)

def draw_pause(window):
    draw_game(window)
    text = pygame.font.SysFont("Comic Sans MS", 60).render("PAUSA", True, (255,255,0))
    window.blit(text, (90, 260))

# -------------------- Loop principal --------------------
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if puntuacion > record:
                guardar_record(int(puntuacion))
            pygame.quit()
            exit()

        if event.type == temporizador_tuberias and estado == JUGANDO:
            crear_tuberias()

        if estado in (MENU, PERDIDO):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.is_clicked(mouse_pos, event):
                    if estado == MENU:
                        reiniciar_juego()
                        estado = JUGANDO
                    else:
                        reiniciar_juego()
                        estado = MENU

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if estado == MENU:
                    reiniciar_juego()
                    estado = JUGANDO
                elif estado == JUGANDO:
                    bird.jump(-6)
                elif estado == PERDIDO:
                    reiniciar_juego()
                    estado = MENU

            if event.key == pygame.K_p:
                if estado == JUGANDO:
                    estado = PAUSA
                elif estado == PAUSA:
                    estado = JUGANDO

    if estado == JUGANDO:
        move()

    if estado == MENU:
        draw_menu(window)
    elif estado == JUGANDO:
        draw_game(window)
    elif estado == PERDIDO:
        draw_game_over(window)
    elif estado == PAUSA:
        draw_pause(window)

    pygame.display.update()
    clock.tick(FPS)
