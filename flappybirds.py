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
# RANKING = 3  # Eliminado estado
estado = MENU

# Clase pájaro
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird_width = 34
bird_height = 24

class Bird:
    def __init__(self, img, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h) # El rectángulo para colisiones
        self.img = img
        # Usamos variables flotantes para la posición y velocidad
        self.x_float = float(x)
        self.y_float = float(y)
        self.vel_y = 0.0

    def update_rect(self):
        # Actualiza el rectángulo con las coordenadas enteras
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def apply_gravity(self, gravity):
        self.vel_y += gravity
        self.y_float += self.vel_y
        # Evitar que el pájaro salga por arriba de la pantalla
        self.y_float = max(self.y_float, 0)
        # Actualizar el rectángulo después de moverse
        self.update_rect()

    def jump(self, jump_speed):
        self.vel_y = jump_speed

    def check_boundary(self, height):
        # Devuelve True si el pájaro sale por abajo
        return self.rect.y > height

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

# Clase Botón (Modificada - sin ícono)
class Button:
    def __init__(self, x, y, width, height, bg_color="gray", text="", font=None, text_color="white"):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        # Dibuja el fondo del botón con el color especificado
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, "black", self.rect, 2) # Borde negro

        # Dibujar texto si existe
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Botón izquierdo
            if self.rect.collidepoint(pos):
                return True
        return False

# Imágenes del juego
background_image = pygame.image.load("sky.png")
bird_image = pygame.image.load("Flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
tuberia_superior_image = pygame.image.load("tuberia_superior.png")
tuberia_superior_image = pygame.transform.scale(tuberia_superior_image, (tuberia_width, tuberia_height))
tuberia_inferior_image = pygame.image.load("tuberia_inferior.png")
tuberia_inferior_image = pygame.transform.scale(tuberia_inferior_image, (tuberia_width, tuberia_height))

# Lógica del juego
bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height) # Inicializar con la clase Bird
tuberias = []
velocidad_x = -2
puntuacion = 0
game_over = False

def reiniciar_juego():
    global bird, tuberias, puntuacion
    # Reiniciar la instancia del pájaro
    bird = Bird(bird_image, bird_x, bird_y, bird_width, bird_height)
    tuberias.clear()
    puntuacion = 0

def draw_menu(window):
    window.blit(background_image, (0, 0))
    font_title = pygame.font.SysFont("Comic Sans MS", 40)
    # font_sub = pygame.font.SysFont("Comic Sans MS", 20) # Eliminado: No se usa más

    title = font_title.render(" FLAPPY BIRD", True, "white")
    # subtitle = font_sub.render("¡Presiona ESPACIO o toca el JUGAR!", True, "yellow") # Eliminado: No se dibuja más

    window.blit(title, (40, 100)) # Ajusté la posición
    # window.blit(subtitle, (30, 160)) # Eliminado: No se dibuja más

    # Dibujar botón
    button_play.draw(window)


def draw_game(window):
    window.blit(background_image, (0, 0))
    # Dibujar usando la imagen en la posición del rectángulo del pájaro
    window.blit(bird.img, bird.rect)

    for tuberia in tuberias:
        window.blit(tuberia.img, tuberia)

    text_font = pygame.font.SysFont("Comic Sans MS", 45)
    text_render = text_font.render(str(int(puntuacion)), True, "white")
    window.blit(text_render, (5, 0))

def draw_game_over(window):
    draw_game(window) # Dibuja el fondo y los elementos del juego
    font_over = pygame.font.SysFont("Comic Sans MS", 45)

    text = font_over.render("¡PERDISTE! ", True, "red")

    # Ajustar la posición Y del texto "¡PERDISTE!" para que esté más arriba
    text_y_position = 200 # Subí la posición de 250 a 200 (o el valor que prefieras)
    window.blit(text, (60, text_y_position)) # Posición del texto "¡PERDISTE!"

    # Dibujar botón en la pantalla de game over también
    # Ajustar la posición Y del botón para que esté más abajo, dejando espacio
    button_play_y_position = 320 # Bajé la posición del botón de 300 a 320 (o el valor que prefieras)
    button_play.rect.y = button_play_y_position # Actualizar la posición del rectángulo del botón
    button_play.draw(window) # Dibujar el botón en la nueva posición


def move():
    global puntuacion, estado
    # Aplicar gravedad a la instancia del pájaro
    bird.apply_gravity(0.4) # Pasamos la gravedad directamente

    # Verificar límites
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

    # Limpiar tuberías fuera de la pantalla
    while len(tuberias) > 0 and tuberias[0].x < -tuberia_width:
        tuberias.pop(0)

def crear_tuberias():
    random_y = tuberia_y - tuberia_height / 4 - random.random() * (tuberia_height / 2)
    espacio = GAME_HEIGHT / 4

    tuberia_superior = Tuberia(tuberia_superior_image, tuberia_x, int(random_y), tuberia_width, tuberia_height)
    tuberias.append(tuberia_superior)

    tuberia_inferior = Tuberia(tuberia_inferior_image, tuberia_x, int(tuberia_superior.y + tuberia_superior.height + espacio), tuberia_width, tuberia_height)
    tuberias.append(tuberia_inferior)

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# --- Crear Botón ---
button_width = 150
button_height = 50
button_x = GAME_WIDTH // 2 - button_width // 2 # Centrado horizontalmente
button_y = 300 # Posición inicial (se usará solo para el menú)
button_y_game_over = 320 # Nueva variable para la posición Y en game over

# Botón de Jugar (Color naranja, texto "Jugar", sin ícono)
button_play = Button(
    button_x,
    button_y, # Se usará esta posición para el menú
    button_width,
    button_height,
    bg_color="orange",  # Color naranja
    text="Jugar",
    font=pygame.font.SysFont("Comic Sans MS", 25),
    text_color="white"
)

# --- Fin Crear Botón ---

temporizador_tuberias = pygame.USEREVENT + 0
pygame.time.set_timer(temporizador_tuberias, 1500)

while True:
    mouse_pos = pygame.mouse.get_pos() # Obtener posición del mouse

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if estado == MENU or estado == PERDIDO: # Manejar clics en menú y game over
            # Manejar clics en el menú principal y en game over
            if button_play.is_clicked(mouse_pos, event):
                reiniciar_juego()
                estado = JUGANDO
            # if button_ranking.is_clicked(mouse_pos, event): # Eliminado
            #     estado = RANKING

        if event.type == pygame.KEYDOWN:
            # Espacio para navegar entre menús o jugar
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                if estado == MENU:
                    reiniciar_juego()
                    estado = JUGANDO
                elif estado == JUGANDO:
                    # Hacer saltar a la instancia del pájaro
                    bird.jump(-6)
                elif estado == PERDIDO:
                    reiniciar_juego()
                    estado = MENU
                # elif estado == RANKING: # Eliminado
                #     estado = MENU

        if event.type == temporizador_tuberias and estado == JUGANDO:
            crear_tuberias()

    # --- Dibujar Pantalla ---
    if estado == JUGANDO:
        move() # Llamar a move() para actualizar la física
    if estado == MENU:
        draw_menu(window)
    elif estado == JUGANDO:
        draw_game(window)
    elif estado == PERDIDO:
        draw_game_over(window)
    # elif estado == RANKING: # Eliminado
    #     draw_ranking(window)
    # --- Fin Dibujar ---

    pygame.display.update()
    clock.tick(60)