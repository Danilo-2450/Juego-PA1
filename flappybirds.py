import pygame
import random
import os
from sys import exit

# -------------------- Inicialización --------------------
pygame.init()
clock = pygame.time.Clock()

# Pantalla
GAME_WIDTH = 360
GAME_HEIGHT = 640
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird - Modo Amarillo/Azul/Intercalado")

# Estados
MENU = 0
JUGANDO = 1
PERDIDO = 2
PAUSA = 3

# Parámetros
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

# -------------------- Clases --------------------
class Bird:
    def __init__(self, img, x, y, w, h):
        self.rect = pygame.Rect(int(x), int(y), w, h)
        self.img = img
        self.x_float = float(x)
        self.y_float = float(y)
        self.vel_y = 0.0

    def update_rect(self):
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.y_float += self.vel_y
        self.y_float = max(self.y_float, 0)
        self.update_rect()

    def jump(self, jump_speed):
        self.vel_y = jump_speed

    def check_boundary(self, height):
        return self.rect.y > height

class Tuberia(pygame.Rect):
    def __init__(self, img, x, y, w, h):
        pygame.Rect.__init__(self, x, y, w, h)
        self.img = img
        self.passed = False

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
            return self.rect.collidepoint(pos)
        return False

# -------------------- Recursos gráficos --------------------
# Cargar imágenes. Si falla, el programa mostrará un error claro.
background_image = pygame.image.load("sky.png").convert()
tuberia_superior_image = pygame.transform.scale(pygame.image.load("tuberia_superior.png").convert_alpha(), (tuberia_width, tuberia_height))
tuberia_inferior_image = pygame.transform.scale(pygame.image.load("tuberia_inferior.png").convert_alpha(), (tuberia_width, tuberia_height))

# Cargar frames por color
frames_yellow = [
    pygame.transform.scale(pygame.image.load("bird_yellow1.png").convert_alpha(), (bird_width, bird_height)),
    pygame.transform.scale(pygame.image.load("bird_yellow2.png").convert_alpha(), (bird_width, bird_height)),
    pygame.transform.scale(pygame.image.load("bird_yellow3.png").convert_alpha(), (bird_width, bird_height))
]

frames_blue = [
    pygame.transform.scale(pygame.image.load("bird_blue1.png").convert_alpha(), (bird_width, bird_height)),
    pygame.transform.scale(pygame.image.load("bird_blue2.png").convert_alpha(), (bird_width, bird_height)),
    pygame.transform.scale(pygame.image.load("bird_blue3.png").convert_alpha(), (bird_width, bird_height))
]

# -------------------- Modos de juego (selección) --------------------
# Modo posible: "yellow" (solo amarillo), "blue" (solo azul), "intercalated" (amarillo-azul alternado)
modo_seleccionado = "intercalated"  # valor por defecto al iniciar

def construir_sprites_para_modo(modo):
    """
    Devuelve la lista sprites_bird (secuencia de frames) según el modo:
    - yellow -> [y1,y2,y3]
    - blue -> [b1,b2,b3]
    - intercalated -> [y1,b1,y2,b2,y3,b3]
    """
    if modo == "yellow":
        return frames_yellow[:]  # copia
    elif modo == "blue":
        return frames_blue[:]
    else:  # intercalated
        seq = []
        for i in range(len(frames_yellow)):
            seq.append(frames_yellow[i])
            seq.append(frames_blue[i])
        return seq

sprites_bird = construir_sprites_para_modo(modo_seleccionado)
indice_sprite = 0

# -------------------- Variables del juego --------------------
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird = Bird(sprites_bird[indice_sprite], bird_x, bird_y, bird_width, bird_height)
tuberias = []
puntuacion = 0.0
estado = MENU
record = cargar_record()

# Timers
temporizador_tuberias = pygame.USEREVENT + 0
pygame.time.set_timer(temporizador_tuberias, 1500)
ANIM_EVENT = pygame.USEREVENT + 5
pygame.time.set_timer(ANIM_EVENT, 150)  # ms por frame de animación

# Fuentes y botones
font_title = pygame.font.SysFont("Comic Sans MS", 40)
font_button = pygame.font.SysFont("Comic Sans MS", 25)
font_score = pygame.font.SysFont("Comic Sans MS", 45)
font_small = pygame.font.SysFont("Comic Sans MS", 24)

button_width = 150
button_height = 50
button_x = GAME_WIDTH // 2 - button_width // 2
button_y = 300
button_play = Button(button_x, button_y, button_width, button_height, "orange", "Jugar", font_button)

# Botones de selección de modo (3 botones)
mode_btn_w = 110
mode_btn_h = 40
mode_btn_y = 200
mode_btn_yellow = Button(20, mode_btn_y, mode_btn_w, mode_btn_h, "gold", "Amarillo", font_small, "black")
mode_btn_blue   = Button(130, mode_btn_y, mode_btn_w, mode_btn_h, "dodgerblue", "Azul", font_small, "white")
mode_btn_inter  = Button(240, mode_btn_y, mode_btn_w, mode_btn_h, "gray", "Intercalado", font_small, "white")

# -------------------- Funciones de lógica --------------------
def reiniciar_juego():
    global bird, tuberias, puntuacion, indice_sprite
    bird = Bird(sprites_bird[indice_sprite], bird_x, bird_y, bird_width, bird_height)
    tuberias.clear()
    puntuacion = 0.0

def crear_tuberias():
    random_y = tuberia_y - tuberia_height / 4 - random.random() * (tuberia_height / 2)
    espacio = GAME_HEIGHT / 4
    tuberia_superior = Tuberia(tuberia_superior_image, tuberia_x, int(random_y), tuberia_width, tuberia_height)
    tuberias.append(tuberia_superior)
    tuberia_inferior = Tuberia(tuberia_inferior_image, tuberia_x, int(tuberia_superior.y + tuberia_superior.height + espacio), tuberia_width, tuberia_height)
    tuberias.append(tuberia_inferior)

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
    title = font_title.render(" FLAPPY BIRD", True, "white")
    window.blit(title, (40, 100))

    # Botón jugar
    button_play.rect.y = button_y
    button_play.draw(window)

    # Texto y botones de modo
    text_select = font_small.render("Modo de juego (elige uno):", True, "white")
    window.blit(text_select, (30, 160))
    mode_btn_yellow.draw(window)
    mode_btn_blue.draw(window)
    mode_btn_inter.draw(window)

    # Mostrar modo actual abajo
    mode_text = font_small.render(f"Modo actual: {modo_seleccionado}", True, "white")
    window.blit(mode_text, (20, 260))

def draw_game(window):
    window.blit(background_image, (0, 0))
    for tuberia in tuberias:
        window.blit(tuberia.img, tuberia)
    window.blit(bird.img, bird.rect)
    text_render = font_score.render(str(int(puntuacion)), True, "white")
    window.blit(text_render, (5, 0))
    record_text = font_small.render(f"Récord: {record}", True, "white")
    window.blit(record_text, (GAME_WIDTH - 120, 8))

def draw_game_over(window):
    draw_game(window)
    font_over = pygame.font.SysFont("Comic Sans MS", 45)
    text = font_over.render("¡PERDISTE!", True, "red")
    window.blit(text, (60, 150))
    font_info = pygame.font.SysFont("Comic Sans MS", 28)
    punt_text = font_info.render(f"Puntuación: {int(puntuacion)}", True, "white")
    window.blit(punt_text, (80, 220))
    rec_text = font_info.render(f"Récord: {record}", True, "white")
    window.blit(rec_text, (80, 260))
    button_play.rect.y = 320
    button_play.draw(window)

def draw_pause(window):
    draw_game(window)
    font_pause = pygame.font.SysFont("Comic Sans MS", 60)
    text = font_pause.render("PAUSA", True, "yellow")
    window.blit(text, (90, 260))
    hint = font_small.render("Presiona P para continuar", True, "white")
    window.blit(hint, (70, 330))

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

        # Temporizador para crear tuberías (solo cuando se juega)
        if event.type == temporizador_tuberias and estado == JUGANDO:
            crear_tuberias()

        # Timer de animación: actualizar índice y la imagen del pájaro
        if event.type == ANIM_EVENT:
            indice_sprite = (indice_sprite + 1) % len(sprites_bird)
            bird.img = sprites_bird[indice_sprite]

        # Clicks en menú y pantalla de perdido
        if estado == MENU or estado == PERDIDO:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Jugar
                if button_play.is_clicked(mouse_pos, event):
                    if estado == MENU:
                        reiniciar_juego()
                        estado = JUGANDO
                    elif estado == PERDIDO:
                        reiniciar_juego()
                        estado = MENU

                # Selección de modo desde el menú
                if estado == MENU:
                    if mode_btn_yellow.is_clicked(mouse_pos, event):
                        modo_seleccionado = "yellow"
                        sprites_bird = construir_sprites_para_modo(modo_seleccionado)
                        indice_sprite = 0
                        bird.img = sprites_bird[indice_sprite]
                    if mode_btn_blue.is_clicked(mouse_pos, event):
                        modo_seleccionado = "blue"
                        sprites_bird = construir_sprites_para_modo(modo_seleccionado)
                        indice_sprite = 0
                        bird.img = sprites_bird[indice_sprite]
                    if mode_btn_inter.is_clicked(mouse_pos, event):
                        modo_seleccionado = "intercalated"
                        sprites_bird = construir_sprites_para_modo(modo_seleccionado)
                        indice_sprite = 0
                        bird.img = sprites_bird[indice_sprite]

        # Teclado: saltar, pausa, volver al menú
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
            if event.key == pygame.K_p:
                if estado == JUGANDO:
                    estado = PAUSA
                elif estado == PAUSA:
                    estado = JUGANDO
            # Tecla C: alternar rápidamente entre modos (opcional)
            if event.key == pygame.K_c:
                if modo_seleccionado == "yellow":
                    modo_seleccionado = "blue"
                elif modo_seleccionado == "blue":
                    modo_seleccionado = "intercalated"
                else:
                    modo_seleccionado = "yellow"
                sprites_bird = construir_sprites_para_modo(modo_seleccionado)
                indice_sprite = 0
                bird.img = sprites_bird[indice_sprite]

    # Lógica solo si está jugando
    if estado == JUGANDO:
        move()

    # Dibujado por estado
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
