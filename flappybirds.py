import pygame
from sys import exit
import random
import os # Importar os para manejo de archivos

# Variables del juego
GAME_WIDTH = 360
GAME_HEIGHT = 640

# Estados del juego
MENU = 0
JUGANDO = 1
PERDIDO = 2

estado = MENU

# =============================
#      CLASE BIRD NUEVA
# =============================
class Bird:
    def __init__(self, img, x, y, w, h):
        self.img = img
        self.rect = pygame.Rect(x, y, w, h)
        self.x_float = float(x)
        self.y_float = float(y)
        self.vel_y = 0.0
        self.angle = 0

        # Límites de ángulos
        self.max_up_angle = 25
        self.max_down_angle = -70

    def update_angle(self):
        if self.vel_y < 0:  
            self.angle = self.max_up_angle
        else:
            self.angle -= 3
            if self.angle < self.max_down_angle:
                self.angle = self.max_down_angle

    def update_rect(self):
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.y_float += self.vel_y

        # No dejar que suba más arriba de la pantalla
        self.y_float = max(self.y_float, 0)

        self.update_angle()
        self.update_rect()

    def jump(self, jump_speed):
        self.vel_y = jump_speed
        self.angle = self.max_up_angle

    def check_boundary(self, height):
        return self.rect.y > height

    def draw(self, surface):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated_img.get_rect(center=self.rect.center)
        surface.blit(rotated_img, new_rect)


# =============================
#         TUBERÍA
# =============================
tuberia_x = GAME_WIDTH
tuberia_width = 64
tuberia_height = 512

class Tuberia(pygame.Rect):
    def __init__(self, img, x, y, w, h, vel_y=0, move_limit=0, is_master=False):
        pygame.Rect.__init__(self, x, y, w, h)
        self.img = img
        self.passed = False
        self.vel_y = vel_y # Velocidad vertical para el movimiento
        self.initial_y = y # Posición Y inicial para el límite de movimiento
        self.move_limit = move_limit # Límite de desplazamiento vertical (ej. 50 pixeles)
        self.is_master = is_master # Indica si esta tubería controla el movimiento

    def move_vertical(self):
        # Solo la tubería "master" (la superior) controla la lógica de inversión
        if self.is_master:
            # Mover la tubería verticalmente
            self.y += self.vel_y

            # Invertir la dirección si alcanza los límites
            # Se usa un margen de 5 píxeles para evitar problemas de flotantes
            if self.vel_y > 0 and self.y > self.initial_y + self.move_limit:
                self.vel_y *= -1
            elif self.vel_y < 0 and self.y < self.initial_y - self.move_limit:
                self.vel_y *= -1
        else:
            # La tubería esclava solo se mueve con su velocidad actual
            self.y += self.vel_y


# =============================
#         BOTÓN
# =============================
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


# =============================
#      CARGA DE IMÁGENES
# =============================
# Asumiendo que las imágenes están en el mismo directorio
background_image = pygame.image.load("sky.png")

bird_width = 34
bird_height = 24

bird_image = pygame.image.load("Flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))

tuberia_superior_image = pygame.image.load("tuberia_superior.png")
tuberia_superior_image = pygame.transform.scale(tuberia_superior_image, (tuberia_width, tuberia_height))

tuberia_inferior_image = pygame.image.load("tuberia_inferior.png")
tuberia_inferior_image = pygame.transform.scale(tuberia_inferior_image, (tuberia_width, tuberia_height))


# =============================
#        LÓGICA DEL JUEGO
# =============================
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2

bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)

tuberias = []
velocidad_x = -2
puntuacion = 0
record = 0
RECORD_FILE = "record.txt"

def cargar_record():
    global record
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            try:
                record = int(f.read())
            except ValueError:
                record = 0
    else:
        record = 0

def guardar_record():
    global record
    with open(RECORD_FILE, "w") as f:
        f.write(str(record))

def reiniciar_juego():
    global bird, tuberias, puntuacion, estado, record
    # Actualizar el récord antes de reiniciar
    if puntuacion > record:
        
        record = int(puntuacion)
        guardar_record()

    bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
    tuberias.clear()
    puntuacion = 0
    estado = MENU # Volver al menú después de perder

# Cargar el récord al inicio
cargar_record()


# =============================
#       DIBUJAR MENÚ
# =============================
def draw_menu(window):
    window.blit(background_image, (0, 0))
    font_title = pygame.font.Font("FlappyBirdy.ttf" , 80)
    title = font_title.render(" FLAPPY BIRD", True, "white")
    window.blit(title, (40, 100))
    
    # Mostrar el récord en el menú
    font_record = pygame.font.SysFont("Comic Sans MS", 30)
    record_text = font_record.render(f"Récord: {record}", True, "black")
    window.blit(record_text, (GAME_WIDTH // 2 - record_text.get_width() // 2, 250))

    button_play.draw(window)


# =============================
#      DIBUJAR JUEGO
# =============================
def draw_game(window):
    window.blit(background_image, (0, 0))
    bird.draw(window)

    for tuberia in tuberias:
        window.blit(tuberia.img, tuberia)

    # --- Puntuación ---
    text_font = pygame.font.SysFont("Comic Sans MS", 60)
    text_render = text_font.render(str(int(puntuacion)), True, "white")
    window.blit(text_render, (20, 20))


def draw_game_over(window):
    draw_game(window)
    font_over = pygame.font.Font("FlappyBirdy.ttf", 80)
    text = font_over.render("GAME OVER", True, "red")
    window.blit(text, (70, 180))

    # --- Puntuación final ---
    font_score = pygame.font.SysFont("Comic Sans MS", 50)
    score_text = font_score.render(f"Puntaje: {int(puntuacion)}", True, "Black")
    window.blit(score_text, (50, 480))
    
    # Mostrar el récord
    font_record = pygame.font.SysFont("Comic Sans MS", 30)
    record_text = font_record.render(f"Récord: {record}", True, "Black")
    window.blit(record_text, (50, 530))

    button_play.rect.y = 360
    button_play.draw(window)


# =============================
#         MOVIMIENTO
# =============================
def move():
    global puntuacion, estado

    bird.apply_gravity(0.4)

    if bird.check_boundary(GAME_HEIGHT):
        estado = PERDIDO
        reiniciar_juego() # Llamar a reiniciar para actualizar el récord
        return

    # Se asume que las tuberías vienen en pares (superior, inferior)
    for i in range(0, len(tuberias), 2):
        superior = tuberias[i]
        inferior = tuberias[i+1]

        # 1. Movimiento vertical (solo la superior es master)
        superior.move_vertical()
        # La inferior sigue el movimiento de la superior para mantener el hueco
        # La diferencia de posición Y entre ellas es constante (espacio + tuberia_height)
        # La inferior solo necesita moverse con la misma velocidad vertical que la superior
        inferior.vel_y = superior.vel_y
        inferior.y += inferior.vel_y

        # 2. Movimiento horizontal
        superior.x += velocidad_x
        inferior.x += velocidad_x

        # 3. Lógica de puntuación y colisión (solo se necesita verificar una vez por par)
        # Usamos la tubería superior para la lógica de puntuación
        if not superior.passed and bird.rect.x > superior.x + superior.width:
            puntuacion += 0.5
            superior.passed = True
            inferior.passed = True # Marcar ambas como pasadas

        if bird.rect.colliderect(superior) or bird.rect.colliderect(inferior):
            estado = PERDIDO
            reiniciar_juego() # Llamar a reiniciar para actualizar el récord
            return

    while len(tuberias) > 0 and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)


# =============================
#   CREACIÓN DE TUBERÍAS
# =============================
def crear_tuberias():
    # Parámetros para el movimiento vertical
    vel_y_tuberia = random.choice([-1, 1]) * 1.5 # Velocidad vertical aumentada para que sea notorio
    move_limit_tuberia = 70 # Límite de movimiento de 70 píxeles

    # Posición vertical inicial aleatoria para el par de tuberías
    # El centro del hueco estará entre 1/4 y 3/4 de la altura de la pantalla
    min_center_y = GAME_HEIGHT * 0.25
    max_center_y = GAME_HEIGHT * 0.75
    center_y = random.uniform(min_center_y, max_center_y)
    
    espacio = GAME_HEIGHT / 4 # Espacio fijo entre tuberías

    # Calcular la posición Y de la tubería superior
    # La parte inferior de la tubería superior debe estar en center_y - espacio/2
    superior_y = center_y - espacio / 2 - tuberia_height
    
    # Calcular la posición Y de la tubería inferior
    # La parte superior de la tubería inferior debe estar en center_y + espacio/2
    inferior_y = center_y + espacio / 2

    # La tubería superior será la "master" que controla la lógica de inversión de movimiento
    superior = Tuberia(
        tuberia_superior_image, 
        tuberia_x, 
        int(superior_y), 
        tuberia_width, 
        tuberia_height,
        vel_y=vel_y_tuberia,
        move_limit=move_limit_tuberia,
        is_master=True # Marcar como master
    )
    
    # La tubería inferior será la "esclava" que sigue el movimiento
    inferior = Tuberia(
        tuberia_inferior_image, 
        tuberia_x, 
        int(inferior_y), 
        tuberia_width, 
        tuberia_height,
        vel_y=vel_y_tuberia, # Misma velocidad vertical inicial
        move_limit=move_limit_tuberia,
        is_master=False # Marcar como esclava
    )

    tuberias.append(superior)
    tuberias.append(inferior)


# =============================
#      INICIO DEL JUEGO
# =============================
pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

button_play = Button(
    GAME_WIDTH//2 - 75, 300,
    150, 50,
    bg_color="orange",
    text="Jugar",
    font=pygame.font.Font("FlappyBirdy.ttf", 25),
    text_color="white"
)

temporizador_tuberias = pygame.USEREVENT + 0
pygame.time.set_timer(temporizador_tuberias, 1500)


# =============================
#           LOOP
# =============================
while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Guardar el récord antes de salir
            if puntuacion > record:
                record = int(puntuacion)
                guardar_record()
            pygame.quit()
            exit()

        if estado == MENU or estado == PERDIDO:
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
                    # Al presionar una tecla en PERDIDO, se vuelve al menú, no se reinicia directamente el juego
                    estado = MENU
                    # No es necesario llamar a reiniciar_juego() aquí porque ya se llamó en move()

        if event.type == temporizador_tuberias and estado == JUGANDO:
            crear_tuberias()

    # Dibujar
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
