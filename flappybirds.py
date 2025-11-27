import pygame
import random
from sys import exit

# ===================== Inicialización =====================
pygame.init()
clock = pygame.time.Clock()

# ===================== Configuración de pantalla =====================
GAME_WIDTH = 360
GAME_HEIGHT = 640
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird Mejorado")

# ===================== Estados =====================
MENU = 0
JUGANDO = 1
PERDIDO = 2
PAUSA = 3
estado = MENU

# ===================== Parámetros =====================
FPS = 60
bird_width = 34
bird_height = 24
tuberia_width = 64
tuberia_height = 512
tuberia_x = GAME_WIDTH
tuberia_y = 0
velocidad_x = -2

# ===================== Archivo de récord =====================
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
    except:
        pass

record = cargar_record()

# ===================== Carga segura de imágenes =====================
def safe_load(path, size=None, alpha=True):
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        surf.fill((200, 0, 200))
        return surf

# Fondo
background_image = safe_load("sky.png", (GAME_WIDTH, GAME_HEIGHT), alpha=False)

# Frames amarillo
frames_yellow = [
    safe_load("bird_yellow1.png", (bird_width, bird_height)),
    safe_load("bird_yellow2.png", (bird_width, bird_height)),
    safe_load("bird_yellow3.png", (bird_width, bird_height))
]

# Frames azul
frames_blue = [
    safe_load("bird_blue1.png", (bird_width, bird_height)),
    safe_load("bird_blue2.png", (bird_width, bird_height)),
    safe_load("bird_blue3.png", (bird_width, bird_height))
]

# Tuberías
tuberia_sup_img = safe_load("tuberia_superior.png", (tuberia_width, tuberia_height))
tuberia_inf_img = safe_load("tuberia_inferior.png", (tuberia_width, tuberia_height))

# ===================== Modos =====================
modo = "intercalated"

def construir_sprites(m):
    if m == "yellow":
        return frames_yellow[:]
    if m == "blue":
        return frames_blue[:]

    seq = []
    for a, b in zip(frames_yellow, frames_blue):
        seq.append(a)
        seq.append(b)
    return seq

sprites_bird = construir_sprites(modo)
frame_index = 0

# ===================== Clases =====================
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
        ang = -self.vel_y * 4
        self.angle = max(-25, min(25, ang))

    def apply_gravity(self, grav):
        self.vel_y += grav
        self.y_float += self.vel_y

        if self.y_float < 0:
            self.y_float = 0
            self.vel_y = 0

        self.update_angle()
        self.update_rect()

    def jump(self, speed):
        self.vel_y = speed

    def check_boundary(self, height):
        return self.rect.y > height - 10

    def draw(self, surf):
        rotated = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        surf.blit(rotated, new_rect)

class Tuberia(pygame.Rect):
    def __init__(self, img, x, y):
        super().__init__(x, y, tuberia_width, tuberia_height)
        self.img = img
        self.passed = False

class Button:
    def __init__(self, x, y, w, h, color, text, font, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        t = self.font.render(self.text, True, self.text_color)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def is_clicked(self, pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(pos)

# ===================== Variables del juego =====================
bird = Bird(sprites_bird[frame_index], GAME_WIDTH/8, GAME_HEIGHT/2, bird_width, bird_height)
tuberias = []
puntuacion = 0.0

# Timers
SPAWN_PIPE = pygame.USEREVENT + 1
ANIM = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_PIPE, 1500)
pygame.time.set_timer(ANIM, 150)

# ===================== Fuentes y botones =====================
font_title = pygame.font.SysFont("Comic Sans MS", 40)
font_button = pygame.font.SysFont("Comic Sans MS", 25)
font_small = pygame.font.SysFont("Comic Sans MS", 22)
font_score = pygame.font.SysFont("Comic Sans MS", 45)

button_play = Button(GAME_WIDTH//2 - 75, 300, 150, 50, (255,165,0), "Jugar", font_button, (0,0,0))

mode_btn_yellow = Button(20, 200, 110, 40, (255,215,0), "Amarillo", font_small, (0,0,0))
mode_btn_blue   = Button(130, 200, 110, 40, (30,144,255), "Azul", font_small, (255,255,255))
mode_btn_inter  = Button(240, 200, 110, 40, (120,120,120), "Intercalado", font_small, (255,255,255))

# ===================== Lógica =====================
def reiniciar():
    global bird, tuberias, puntuacion
    tuberias.clear()
    puntuacion = 0
    frame_index = 0
    return Bird(sprites_bird[0], GAME_WIDTH/8, GAME_HEIGHT/2, bird_width, bird_height)

def crear_tuberias():
    offset = random.randint(-150, 150)
    y_top = -200 + offset
    y_bottom = y_top + tuberia_height + 150

    tuberias.append(Tuberia(tuberia_sup_img, tuberia_x, y_top))
    tuberias.append(Tuberia(tuberia_inf_img, tuberia_x, y_bottom))

def mover():
    global puntuacion, estado, record

    bird.apply_gravity(0.4)

    if bird.check_boundary(GAME_HEIGHT):
        if puntuacion > record:
            guardar_record(int(puntuacion))
        estado = PERDIDO
        return

    for t in tuberias:
        t.x += velocidad_x

        if not t.passed and bird.rect.x > t.x + t.width:
            t.passed = True
            puntuacion += 0.5

        if bird.rect.colliderect(t):
            if puntuacion > record:
                guardar_record(int(puntuacion))
            estado = PERDIDO
            return

    if tuberias and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)

# ===================== Dibujado =====================
def draw_menu():
    window.blit(background_image, (0,0))
    window.blit(font_title.render("FLAPPY BIRD", True, (255,255,255)), (40, 100))

    window.blit(font_small.render("Modo de juego:", True, (255,255,255)), (30, 160))
    mode_btn_yellow.draw(window)
    mode_btn_blue.draw(window)
    mode_btn_inter.draw(window)

    window.blit(font_small.render(f"Modo actual: {modo}", True, (255,255,255)), (20, 260))

    button_play.draw(window)

def draw_game():
    window.blit(background_image, (0,0))

    for t in tuberias:
        window.blit(t.img, (t.x, t.y))

    bird.draw(window)

    window.blit(font_score.render(str(int(puntuacion)), True, (255,255,255)), (5,0))
    window.blit(font_small.render(f"Record: {record}", True, (255,255,255)), (220, 5))

def draw_perdido():
    draw_game()
    window.blit(font_title.render("¡PERDISTE!", True, (255,0,0)), (65, 200))
    button_play.rect.y = 320
    button_play.draw(window)

def draw_pause():
    draw_game()
    window.blit(font_title.render("PAUSA", True, (255,255,0)), (100, 260))

# ===================== Bucle principal =====================
running = True
while running:

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == SPAWN_PIPE and estado == JUGANDO:
            crear_tuberias()

        if event.type == ANIM:
            frame_index = (frame_index + 1) % len(sprites_bird)
            bird.img = sprites_bird[frame_index]

        # -------------------- MENÚ y PERDIDO --------------------
        if estado in (MENU, PERDIDO):
            if button_play.is_clicked(mouse, event):
                bird = reiniciar()
                estado = JUGANDO

            if estado == MENU:
                if mode_btn_yellow.is_clicked(mouse, event):
                    modo = "yellow"
                    sprites_bird = construir_sprites(modo)
                if mode_btn_blue.is_clicked(mouse, event):
                    modo = "blue"
                    sprites_bird = construir_sprites(modo)
                if mode_btn_inter.is_clicked(mouse, event):
                    modo = "intercalated"
                    sprites_bird = construir_sprites(modo)

        # -------------------- TECLAS --------------------
        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if estado == MENU:
                    bird = reiniciar()
                    estado = JUGANDO
                elif estado == JUGANDO:
                    bird.jump(-6)
                elif estado == PERDIDO:
                    estado = MENU

            if event.key == pygame.K_p:
                if estado == JUGANDO:
                    estado = PAUSA
                elif estado == PAUSA:
                    estado = JUGANDO

            if event.key == pygame.K_c:
                if modo == "yellow":
                    modo = "blue"
                elif modo == "blue":
                    modo = "intercalated"
                else:
                    modo = "yellow"
                sprites_bird = construir_sprites(modo)
                frame_index = 0
                bird.img = sprites_bird[frame_index]

    # -------------------- Lógica --------------------
    if estado == JUGANDO:
        mover()

    # -------------------- Dibujado --------------------
    if estado == MENU:
        draw_menu()
    elif estado == JUGANDO:
        draw_game()
    elif estado == PERDIDO:
        draw_perdido()
    elif estado == PAUSA:
        draw_pause()

    pygame.display.update()
    clock.tick(FPS)
