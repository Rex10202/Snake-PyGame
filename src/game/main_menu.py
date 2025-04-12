import pygame
import random
import os
from database.connection import registrar_partida


def iniciar_juego(usuario_actual, game_finished):
    """
    Lógica principal del juego "Culebrita Clásica".

    Args:
        usuario_actual (dict): Información del usuario actual.
        game_finished (function): Función a ejecutar cuando el juego termine.
    """
    print(f"Iniciando juego para el usuario: {usuario_actual['username']}")
    print(f"Nivel del usuario: {usuario_actual['nivel']}")  # Verifica que 'nivel' esté presente

    pygame.init()
    ANCHO, ALTO = 800, 600  # Dimensiones de la ventana Pygame
    TAMANIO_BLOQUE = 20     # Tamaño de cada bloque
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Culebrita Clásica")
    
    # Colores y configuración general
    AMARILLO = (255, 255, 102)
    NEGRO = (0, 0, 0)
    ROJO = (213, 50, 80)
    VERDE = (0, 255, 0)
    AZUL = (50, 153, 213)
    reloj = pygame.time.Clock()
    VELOCIDAD = 8
    VELOCIDAD_MAXIMA = 20  # Velocidad máxima permitida
    estilo_fuente = pygame.font.SysFont("bahnschrift", 25)
    fuente_puntuacion = pygame.font.SysFont("comicsansms", 35)
    
    # Ruta de los sonidos
    ruta_sonidos = os.path.join(os.path.dirname(__file__), "..", "assets", "sonidos")
    pygame.mixer.music.load(os.path.join(ruta_sonidos, "snake.wav"))  # Música de fondo
    sonido_fruta = pygame.mixer.Sound(os.path.join(ruta_sonidos, "score.mp3"))  # Sonido al comer fruta

    # Reproducir música de fondo en bucle
    pygame.mixer.music.play(-1)

    def mostrar_puntuacion(puntuacion, nivel):
        """
        Muestra la puntuación y el nivel actual en la pantalla.

        Args:
            puntuacion (int): Puntuación actual del jugador.
            nivel (int): Nivel actual del jugador.
        """
        valor = fuente_puntuacion.render(f"Puntuación: {puntuacion} | Nivel: {nivel}", True, AMARILLO)
        pantalla.blit(valor, [10, 10])
    
    def mostrar_mensaje(mensaje, color, pos_y):
        """
        Muestra un mensaje en la pantalla.

        Args:
            mensaje (str): Mensaje a mostrar.
            color (tuple): Color del texto.
            pos_y (int): Posición vertical del mensaje.
        """
        texto = estilo_fuente.render(mensaje, True, color)
        pantalla.blit(texto, [ANCHO / 6, pos_y])
    
    def generar_comida(serpiente):
        """
        Genera una nueva posición para la comida, asegurándose de que no esté
        en la posición de la serpiente.

        Args:
            serpiente (list): Lista de posiciones ocupadas por la serpiente.

        Returns:
            tuple: Coordenadas (x, y) de la nueva comida.
        """
        while True:
            comida_x = round(random.randrange(0, ANCHO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE
            comida_y = round(random.randrange(0, ALTO - TAMANIO_BLOQUE) / TAMANIO_BLOQUE) * TAMANIO_BLOQUE
            if [comida_x, comida_y] not in serpiente:
                return comida_x, comida_y

    def bucle_juego():
        """
        Contiene la lógica principal del juego, incluyendo el manejo de eventos,
        la actualización de la posición de la serpiente, la detección de colisiones
        y el registro de la partida.
        """
        try:
            juego_terminado = False
            juego_perdido = False
            partida_registrada = False  # Bandera para evitar registros infinitos

            x1 = ANCHO / 2
            y1 = ALTO / 2
            cambio_x = 0
            cambio_y = 0

            serpiente = []
            longitud_serpiente = 1
            comida_x, comida_y = generar_comida(serpiente)

            puntuacion = 0
            nivel = usuario_actual['nivel']
            velocidad = VELOCIDAD

            while not juego_terminado:
                while juego_perdido:
                    pantalla.fill(NEGRO)
                    mostrar_mensaje("¡Perdiste! Presiona Q para salir o ENTER para continuar", ROJO, ALTO / 2)
                    mostrar_puntuacion(puntuacion, nivel)
                    pygame.display.update()

                    # Registrar la partida solo una vez
                    if not partida_registrada:
                        registrar_partida(usuario_actual['id'], puntuacion, nivel)

                        # Actualizar la puntuación si es necesario
                        if puntuacion > usuario_actual['puntuacion'] or nivel > usuario_actual['nivel']:
                            usuario_actual['puntuacion'] = puntuacion
                            usuario_actual['nivel'] = nivel
                            print("Puntuación actualizada correctamente.")

                        partida_registrada = True  # Evitar registros adicionales

                    # Esperar la decisión del jugador
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            juego_terminado = True
                            return "quit"
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_q:  # Salir del juego
                                juego_terminado = True
                                return "quit"
                            elif evento.key == pygame.K_RETURN:  # Reiniciar el juego
                                return "restart"

                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        juego_terminado = True
                        break
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
                if juego_terminado:
                    break
                x1 += cambio_x
                y1 += cambio_y
                if x1 >= ANCHO or x1 < 0 or y1 >= ALTO or y1 < 0:
                    juego_perdido = True
                pantalla.fill(NEGRO)
                pygame.draw.rect(pantalla, VERDE, [comida_x, comida_y, TAMANIO_BLOQUE, TAMANIO_BLOQUE])
                cabeza = [x1, y1]
                serpiente.append(cabeza)
                if len(serpiente) > longitud_serpiente:
                    del serpiente[0]
                for bloque in serpiente[:-1]:
                    if bloque == cabeza:
                        juego_perdido = True
                for bloque in serpiente:
                    pygame.draw.rect(pantalla, AZUL, [bloque[0], bloque[1], TAMANIO_BLOQUE, TAMANIO_BLOQUE])
                if x1 == comida_x and y1 == comida_y:
                    comida_x, comida_y = generar_comida(serpiente)
                    longitud_serpiente += 1
                    puntuacion += 10
                    sonido_fruta.play()  # Reproducir el sonido al comer fruta
                    if puntuacion // 100 > nivel - 1:
                        nivel += 1
                        velocidad = min(velocidad + 2, VELOCIDAD_MAXIMA)
                mostrar_puntuacion(puntuacion, nivel)
                pygame.display.update()
                reloj.tick(velocidad)

            return "quit"
        except Exception as e:
            print(f"Error en el juego: {e}")
            return "quit"

    while True:
        resultado = bucle_juego()
        if resultado == "restart":
            continue
        else:
            break
    pygame.mixer.music.stop()  # Detener la música al salir
    pygame.quit()
    game_finished()
