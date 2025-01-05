import pygame
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla del juego
ANCHO, ALTO = 800, 600  # Dimensiones de la pantalla
TAMANIO_BLOQUE = 20  # Tamaño de cada bloque de la serpiente y la comida
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Culebrita Clásica")  # Título del juego

# Definición de colores
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 102)
NEGRO = (0, 0, 0)
ROJO = (213, 50, 80)
VERDE = (0, 255, 0)
AZUL = (50, 153, 213)

# Configuración del reloj y velocidad
reloj = pygame.time.Clock()
VELOCIDAD = 15

# Configuración de fuentes
estilo_fuente = pygame.font.SysFont("bahnschrift", 25)
fuente_puntuacion = pygame.font.SysFont("comicsansms", 35)

# Cargar sonidos
sonido_comida = pygame.mixer.Sound('Sonidos\score.mp3')
sonido_fondo = pygame.mixer.Sound('Sonidos\snake.wav')
sonido_fondo.play(-1)  # Reproducir en bucle

# Función para mostrar la puntuación en pantalla
def mostrar_puntuacion(puntuacion):
    valor = fuente_puntuacion.render(f"Puntuación: {puntuacion}", True, AMARILLO)
    pantalla.blit(valor, [10, 10])  # Mostrar en la esquina superior izquierda

# Función para mostrar un mensaje de bienvenida en pantalla
def mostrar_mensaje_bienvenida(mensaje, color):
    texto = estilo_fuente.render(mensaje, True, color)
    pantalla.blit(texto, [ANCHO / 6, ALTO / 3])
    
# Función para mostrar un mensaje de menú en pantalla
def mostrar_mensaje_menu(mensaje, color):
    texto = estilo_fuente.render(mensaje, True, color)
    pantalla.blit(texto, [ANCHO / 6, ALTO / 2])

# Función para mostrar el menú inicial
def mostrar_menu():
    pantalla.fill(NEGRO)
    mostrar_mensaje_bienvenida("Bienvenido a Culebrita", AMARILLO)
    mostrar_mensaje_menu("Presiona ENTER para empezar", VERDE)
    pygame.display.update()

    # Esperar hasta que el jugador presione ENTER
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False
                    bucle_juego()

# Función principal del juego
def bucle_juego():
    juego_terminado = False
    juego_perdido = False

    # Posición inicial de la serpiente
    x1 = ANCHO / 2
    y1 = ALTO / 2
    cambio_x = 0
    cambio_y = 0

    # Configuración inicial de la serpiente
    serpiente = []
    longitud_serpiente = 1

    # Posición inicial de la comida
    comida_x = round(random.randrange(0, ANCHO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE
    comida_y = round(random.randrange(0, ALTO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE

    # Puntuación inicial
    puntuacion = 0

    while not juego_terminado:
        while juego_perdido:
            pantalla.fill(NEGRO)  # Fondo negro
            mostrar_mensaje_menu("¡Perdiste! Presiona Q para salir o ENTER para continuar", ROJO)
            mostrar_puntuacion(puntuacion)
            pygame.display.update()

            # Control para reiniciar o salir
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_q:
                        juego_terminado = True
                        juego_perdido = False
                    if evento.key == pygame.K_RETURN:
                        bucle_juego()

        # Manejo de eventos (movimiento de la serpiente)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_terminado = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and cambio_x == 0:
                    cambio_x = -TAMANIO_BLOQUE
                    cambio_y = 0
                elif evento.key == pygame.K_RIGHT and cambio_x == 0:
                    cambio_x = TAMANIO_BLOQUE
                    cambio_y = 0
                elif evento.key == pygame.K_UP and cambio_y == 0:
                    cambio_y = -TAMANIO_BLOQUE
                    cambio_x = 0
                elif evento.key == pygame.K_DOWN and cambio_y == 0:
                    cambio_y = TAMANIO_BLOQUE
                    cambio_x = 0

        # Actualización de la posición de la serpiente
        x1 += cambio_x
        y1 += cambio_y
        if x1 >= ANCHO or x1 < 0 or y1 >= ALTO or y1 < 0:
            juego_perdido = True

        pantalla.fill(NEGRO)  # Fondo negro
        pygame.draw.rect(pantalla, VERDE, [comida_x, comida_y, TAMANIO_BLOQUE, TAMANIO_BLOQUE])  # Dibujar comida

        # Actualización de la serpiente
        cabeza_serpiente = [x1, y1]
        serpiente.append(cabeza_serpiente)
        if len(serpiente) > longitud_serpiente:
            del serpiente[0]

        # Verificar colisión con el cuerpo
        for bloque in serpiente[:-1]:
            if bloque == cabeza_serpiente:
                juego_perdido = True

        # Dibujar la serpiente
        for bloque in serpiente:
            pygame.draw.rect(pantalla, AZUL, [bloque[0], bloque[1], TAMANIO_BLOQUE, TAMANIO_BLOQUE])

        # Verificar si la serpiente come la comida
        if x1 == comida_x and y1 == comida_y:
            comida_x = round(random.randrange(0, ANCHO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE
            comida_y = round(random.randrange(0, ALTO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE
            longitud_serpiente += 1
            puntuacion += 10
            sonido_comida.play()  # Reproducir sonido al comer

        mostrar_puntuacion(puntuacion)
        pygame.display.update()
        reloj.tick(VELOCIDAD)

    pygame.quit()
    quit()

# Ejecutar el menú inicial
mostrar_menu()
