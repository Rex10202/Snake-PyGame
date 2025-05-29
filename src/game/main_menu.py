import pygame
import random
import os
import time
import math
import json
from database.connection import registrar_partida, actualizar_nivel_maximo, obtener_niveles_maximos


class PaimonSnake:
    def __init__(self):
        pygame.init()
        self.ANCHO, self.ALTO = 800, 600
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Paimon Snake")
        
        # Estados del juego
        self.estado = "menu_principal"  # "menu_principal", "selector_niveles", "opciones", "jugando", "pausado"
        
        # Colores
        self.AMARILLO = (255, 255, 102)
        self.NEGRO = (0, 0, 0)
        self.ROJO = (213, 50, 80)
        self.VERDE = (0, 255, 0)
        self.VERDE_OSCURO = (0, 180, 0)
        self.AZUL = (50, 153, 213)
        self.MARRON = (139, 69, 19)
        self.DORADO = (255, 215, 0)
        self.NARANJA = (255, 165, 0)
        self.MORADO = (128, 0, 128)
        self.ROSA = (255, 20, 147)
        self.BLANCO = (255, 255, 255)
        self.GRIS = (128, 128, 128)
        self.GRIS_CLARO = (200, 200, 200)
        self.GRIS_OSCURO = (64, 64, 64)
        
        # Colores específicos para niveles
        self.VERDE_SELVA = (34, 139, 34)
        self.ROJO_LAVA = (255, 69, 0)
        self.AMARILLO_DESIERTO = (238, 203, 173)
        self.MARRON_DESIERTO = (160, 82, 45)
        self.ARENA_COLOR = (194, 178, 128)
        
        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("arial", 48, bold=True)
        self.fuente_boton = pygame.font.SysFont("arial", 24, bold=True)
        self.fuente_texto = pygame.font.SysFont("arial", 20)
        self.fuente_pequena = pygame.font.SysFont("arial", 16)
        self.fuente_puntuacion = pygame.font.SysFont("comicsansms", 35)
        self.fuente_estado = pygame.font.SysFont("comicsansms", 20)
        self.fuente_categoria = pygame.font.SysFont("arial", 16)
        self.fuente_timer = pygame.font.SysFont("arial", 14)
        self.fuente_pausa = pygame.font.SysFont("arial", 72, bold=True)
        self.fuente_advertencia = pygame.font.SysFont("arial", 20, bold=True)
        
        # Configuración
        self.configuracion = self.cargar_configuracion()
        
        # Sonidos
        self.cargar_sonidos()
        self.aplicar_configuracion_audio()
        
        # Variables del juego
        self.reloj = pygame.time.Clock()
        self.usuario_actual = None
        self.nivel_seleccionado = 1
        
        # Variables para vibración
        self.vibracion_activa = False
        self.tiempo_vibracion = 0
        self.intensidad_vibracion = 5
        
        # Cooldown para controles
        self.ultimo_cambio_vibracion = 0
        self.ultimo_click_boton = 0
        self.cooldown_vibracion = 0.5  # 500ms de cooldown
        self.cooldown_boton = 0.3  # 300ms de cooldown para botones
        
        # Variables para pausa
        self.juego_pausado = False
        self.tiempo_pausa_inicio = 0
        
        # Configuración del juego Snake
        self.TAMANIO_BLOQUE = 20
        self.VELOCIDAD_BASE = 8
        self.VELOCIDAD_MAXIMA = 20
        self.DURACION_POWERUP_MAPA = 10.0
        self.TIEMPO_ESPERA_POWERUP = 5.0
        
        # Configuración de niveles especiales - LAVA MEJORADA
        self.TIEMPO_LAVA_BASE = 8.0  # Tiempo inicial entre gotas de lava
        self.TIEMPO_LAVA_MINIMO = 3.0  # Tiempo mínimo entre gotas de lava
        self.DURACION_LAVA = 5.0  # Duración del área de lava (aumentado a 5 segundos)
        self.DURACION_ADVERTENCIA_LAVA = 2.0  # Tiempo de advertencia antes de que aparezca la lava
        self.TAMANIO_LAVA = 3  # Área de lava 3x3
        
        self.TIEMPO_TORMENTA = 10.0  # Tiempo entre tormentas de arena
        self.DURACION_TORMENTA = 5.0  # Duración de la tormenta
        
        # Variables para efecto de arena
        self.particulas_arena = []
        
        # Variables para música
        self.musica_actual = None
        
        # Definición de consumibles
        self.COMIDA = {
            "manzana": {
                "color": self.VERDE,
                "probabilidad": 80,
                "puntos": 10,
                "crecimiento": 1,
                "descripcion": "Comida básica"
            },
            "carne": {
                "color": self.MARRON,
                "probabilidad": 20,
                "puntos": 20,
                "crecimiento": 2,
                "descripcion": "Comida nutritiva"
            }
        }

        self.POWER_UPS = {
            "escudo": {
                "color": self.DORADO,
                "probabilidad": 30,
                "puntos": 5,
                "crecimiento": 1,
                "descripcion": "Invulnerabilidad temporal",
                "duracion_efecto": 10
            },
            "acelerador": {
                "color": self.NARANJA,
                "probabilidad": 25,
                "puntos": 5,
                "crecimiento": 1,
                "descripcion": "Velocidad x2, Puntos x3",
                "duracion_efecto": 10
            },
            "ralentizador": {
                "color": self.MORADO,
                "probabilidad": 25,
                "puntos": 5,
                "crecimiento": 1,
                "descripcion": "Velocidad x0.5, Puntos x0.5",
                "duracion_efecto": 10
            },
            "reductor": {
                "color": self.ROSA,
                "probabilidad": 20,
                "puntos": 15,
                "crecimiento": 0,
                "descripcion": "Reduce tamaño en 1/4",
                "duracion_efecto": 0
            }
        }
    
    def cargar_configuracion(self):
        """Carga la configuración desde un archivo o usa valores por defecto."""
        configuracion_default = {
            "volumen_general": 0.7,
            "volumen_efectos": 0.8,
            "volumen_musica": 0.6,
            "vibracion_pantalla": True
        }
        
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                for clave, valor in configuracion_default.items():
                    if clave not in config:
                        config[clave] = valor
                return config
        except:
            return configuracion_default
    
    def guardar_configuracion(self):
        """Guarda la configuración actual en un archivo."""
        try:
            with open("config.json", "w") as f:
                json.dump(self.configuracion, f, indent=2)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
    
    def cargar_sonidos(self):
        """Carga todos los sonidos del juego."""
        ruta_sonidos = os.path.join(os.path.dirname(__file__), "..", "assets", "sonidos")
        
        try:
            # Sonidos de efectos
            self.sonido_comer = pygame.mixer.Sound(os.path.join(ruta_sonidos, "Comer.wav"))
            self.sonido_escudo = pygame.mixer.Sound(os.path.join(ruta_sonidos, "EscudoActivado.wav"))
            self.sonido_acelerar = pygame.mixer.Sound(os.path.join(ruta_sonidos, "Acelerar.wav"))
            self.sonido_descelerar = pygame.mixer.Sound(os.path.join(ruta_sonidos, "Descelerar.wav"))
            self.sonido_reducir = pygame.mixer.Sound(os.path.join(ruta_sonidos, "ReducirTamanio.wav"))
            self.sonido_muerte = pygame.mixer.Sound(os.path.join(ruta_sonidos, "Morir.wav"))
            
            # Música de ambiente por contexto
            self.musica_menu = os.path.join(ruta_sonidos, "Menu.wav")
            self.musica_selva = os.path.join(ruta_sonidos, "Ambiente1.wav")
            self.musica_volcan = os.path.join(ruta_sonidos, "Ambiente2.wav")
            self.musica_desierto = os.path.join(ruta_sonidos, "Ambiente3.wav")
            
        except Exception as e:
            print(f"Error al cargar sonidos: {e}")
    
    def cargar_musica(self, tipo_musica):
        """Carga la música específica según el contexto."""
        try:
            if tipo_musica == "menu":
                if self.musica_actual != "menu":
                    pygame.mixer.music.load(self.musica_menu)
                    self.musica_actual = "menu"
            elif tipo_musica == "selva":
                if self.musica_actual != "selva":
                    pygame.mixer.music.load(self.musica_selva)
                    self.musica_actual = "selva"
            elif tipo_musica == "volcan":
                if self.musica_actual != "volcan":
                    pygame.mixer.music.load(self.musica_volcan)
                    self.musica_actual = "volcan"
            elif tipo_musica == "desierto":
                if self.musica_actual != "desierto":
                    pygame.mixer.music.load(self.musica_desierto)
                    self.musica_actual = "desierto"
        except Exception as e:
            print(f"Error al cargar música {tipo_musica}: {e}")
    
    def cargar_musica_nivel(self, nivel_mundo):
        """Carga la música específica para cada nivel."""
        if nivel_mundo == 1:
            self.cargar_musica("selva")
        elif nivel_mundo == 2:
            self.cargar_musica("volcan")
        elif nivel_mundo == 3:
            self.cargar_musica("desierto")
        else:
            self.cargar_musica("selva")  # Por defecto
    
    def aplicar_configuracion_audio(self):
        """Aplica la configuración de audio actual."""
        try:
            pygame.mixer.music.set_volume(
                self.configuracion["volumen_musica"] * self.configuracion["volumen_general"]
            )
            
            volumen_efectos = self.configuracion["volumen_efectos"] * self.configuracion["volumen_general"]
            self.sonido_comer.set_volume(volumen_efectos)
            self.sonido_escudo.set_volume(volumen_efectos)
            self.sonido_acelerar.set_volume(volumen_efectos)
            self.sonido_descelerar.set_volume(volumen_efectos)
            self.sonido_reducir.set_volume(volumen_efectos)
            self.sonido_muerte.set_volume(volumen_efectos)
        except Exception as e:
            print(f"Error al aplicar configuración de audio: {e}")
    
    def iniciar_vibracion(self, duracion=0.5, intensidad=5):
        """Inicia el efecto de vibración de pantalla."""
        if self.configuracion["vibracion_pantalla"]:
            self.vibracion_activa = True
            self.tiempo_vibracion = duracion
            self.intensidad_vibracion = intensidad
    
    def actualizar_vibracion(self, dt):
        """Actualiza el efecto de vibración."""
        if self.vibracion_activa:
            self.tiempo_vibracion -= dt
            if self.tiempo_vibracion <= 0:
                self.vibracion_activa = False
                self.intensidad_vibracion = 5
    
    def obtener_offset_vibracion(self):
        """Obtiene el offset de vibración para la pantalla."""
        if self.vibracion_activa:
            return (
                random.randint(-self.intensidad_vibracion, self.intensidad_vibracion),
                random.randint(-self.intensidad_vibracion, self.intensidad_vibracion)
            )
        return (0, 0)
    
    def pausar_juego(self):
        """Pausa o despausa el juego."""
        if self.estado == "jugando":
            self.juego_pausado = not self.juego_pausado
            if self.juego_pausado:
                self.tiempo_pausa_inicio = time.time()
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
    
    def dibujar_pantalla_pausa(self, offset_x=0, offset_y=0):
        """Dibuja la pantalla de pausa."""
        # Crear superficie semi-transparente
        superficie_pausa = pygame.Surface((self.ANCHO, self.ALTO))
        superficie_pausa.set_alpha(128)
        superficie_pausa.fill(self.NEGRO)
        self.pantalla.blit(superficie_pausa, (0, 0))
        
        # Texto principal de pausa
        texto_pausa = self.fuente_pausa.render("PAUSA", True, self.AMARILLO)
        rect_pausa = texto_pausa.get_rect(center=(self.ANCHO//2 + offset_x, self.ALTO//2 - 50 + offset_y))
        self.pantalla.blit(texto_pausa, rect_pausa)
        
        # Instrucciones
        instrucciones = [
            "Presiona 'P' para continuar",
            "Presiona 'ESC' para volver al menú"
        ]
        
        for i, instruccion in enumerate(instrucciones):
            texto_inst = self.fuente_texto.render(instruccion, True, self.BLANCO)
            rect_inst = texto_inst.get_rect(center=(self.ANCHO//2 + offset_x, self.ALTO//2 + 20 + i*30 + offset_y))
            self.pantalla.blit(texto_inst, rect_inst)
    
    def verificar_nivel_desbloqueado(self, nivel_mundo):
        """Verifica si un nivel está desbloqueado basado en el progreso del usuario."""
        if nivel_mundo == 1:
            return True  # Nivel 1 siempre disponible
        elif nivel_mundo == 2:
            # Nivel 2 se desbloquea al superar nivel 5 en mundo 1
            return self.usuario_actual.get('nivel_mundo_1', 0) >= 5
        elif nivel_mundo == 3:
            # Nivel 3 se desbloquea al superar nivel 5 en mundo 2
            return self.usuario_actual.get('nivel_mundo_2', 0) >= 5
        return False
    
    def obtener_descripcion_nivel(self, nivel_mundo):
        """Obtiene la descripción de cada nivel."""
        descripciones = {
            1: "Selva - Clásico",
            2: "Volcán - Gotas de lava",
            3: "Desierto - Tormentas de arena"
        }
        return descripciones.get(nivel_mundo, "Desconocido")
    
    def obtener_requisito_desbloqueo(self, nivel_mundo):
        """Obtiene el texto del requisito para desbloquear un nivel."""
        if nivel_mundo == 2:
            nivel_actual = self.usuario_actual.get('nivel_mundo_1', 0)
            return f"Requiere nivel 5 en Selva (actual: {nivel_actual})"
        elif nivel_mundo == 3:
            nivel_actual = self.usuario_actual.get('nivel_mundo_2', 0)
            return f"Requiere nivel 5 en Volcán (actual: {nivel_actual})"
        return ""
    
    def puede_hacer_click_boton(self):
        """Verifica si se puede hacer click en un botón (cooldown)."""
        tiempo_actual = time.time()
        return tiempo_actual - self.ultimo_click_boton >= self.cooldown_boton
    
    def registrar_click_boton(self):
        """Registra que se hizo click en un botón."""
        self.ultimo_click_boton = time.time()
    
    def dibujar_boton(self, texto, x, y, ancho, alto, color_fondo, color_texto, activo=True):
        """Dibuja un botón con cooldown y retorna si fue clickeado."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        puede_click = self.puede_hacer_click_boton()
        
        if not activo or not puede_click:
            color_fondo = self.GRIS
            color_texto = self.GRIS_OSCURO
        elif x <= mouse_pos[0] <= x + ancho and y <= mouse_pos[1] <= y + alto:
            color_fondo = tuple(min(255, c + 30) for c in color_fondo)
        
        pygame.draw.rect(self.pantalla, color_fondo, [x, y, ancho, alto])
        pygame.draw.rect(self.pantalla, self.BLANCO, [x, y, ancho, alto], 2)
        
        texto_surface = self.fuente_boton.render(texto, True, color_texto)
        texto_rect = texto_surface.get_rect(center=(x + ancho//2, y + alto//2))
        self.pantalla.blit(texto_surface, texto_rect)
        
        # Mostrar cooldown si está activo
        if not puede_click:
            tiempo_restante = self.cooldown_boton - (time.time() - self.ultimo_click_boton)
            cooldown_texto = f"{tiempo_restante:.1f}s"
            cooldown_surface = self.fuente_pequena.render(cooldown_texto, True, self.AMARILLO)
            cooldown_rect = cooldown_surface.get_rect(center=(x + ancho//2, y + alto + 15))
            self.pantalla.blit(cooldown_surface, cooldown_rect)
        
        if (activo and puede_click and x <= mouse_pos[0] <= x + ancho and y <= mouse_pos[1] <= y + alto and 
            mouse_click and not hasattr(self, '_ultimo_click')):
            self._ultimo_click = True
            self.registrar_click_boton()
            return True
        
        return False
    
    def dibujar_barra_volumen(self, texto, x, y, ancho, valor, callback):
        """Dibuja una barra de volumen y maneja la interacción."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        texto_surface = self.fuente_texto.render(texto, True, self.BLANCO)
        self.pantalla.blit(texto_surface, (x, y - 25))
        
        pygame.draw.rect(self.pantalla, self.GRIS_OSCURO, [x, y, ancho, 20])
        pygame.draw.rect(self.pantalla, self.BLANCO, [x, y, ancho, 20], 2)
        
        progreso_ancho = int(ancho * valor)
        pygame.draw.rect(self.pantalla, self.AZUL, [x, y, progreso_ancho, 20])
        
        indicador_x = x + progreso_ancho - 5
        pygame.draw.rect(self.pantalla, self.BLANCO, [indicador_x, y - 2, 10, 24])
        
        valor_texto = f"{int(valor * 100)}%"
        valor_surface = self.fuente_pequena.render(valor_texto, True, self.BLANCO)
        self.pantalla.blit(valor_surface, (x + ancho + 10, y))
        
        if (x <= mouse_pos[0] <= x + ancho and y <= mouse_pos[1] <= y + 20 and mouse_click):
            nuevo_valor = (mouse_pos[0] - x) / ancho
            nuevo_valor = max(0, min(1, nuevo_valor))
            callback(nuevo_valor)
    
    def dibujar_switch(self, texto, x, y, valor, callback):
        """Dibuja un switch (toggle) con cooldown y maneja la interacción."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        tiempo_actual = time.time()
        
        # Verificar cooldown
        puede_cambiar = tiempo_actual - self.ultimo_cambio_vibracion >= self.cooldown_vibracion
        
        # Dimensiones del switch
        switch_width = 60
        switch_height = 30
        circle_radius = switch_height - 6
        
        # Dibujar fondo del switch
        if valor:
            color_fondo = self.VERDE_OSCURO if puede_cambiar else self.GRIS
            circle_pos = x + switch_width - circle_radius - 3
        else:
            color_fondo = self.GRIS
            circle_pos = x + circle_radius + 3
        
        # Dibujar el switch
        pygame.draw.rect(self.pantalla, color_fondo, [x, y, switch_width, switch_height], border_radius=15)
        pygame.draw.rect(self.pantalla, self.BLANCO, [x, y, switch_width, switch_height], 2, border_radius=15)
        
        # Dibujar el círculo del switch
        color_circulo = self.BLANCO if puede_cambiar else self.GRIS_CLARO
        pygame.draw.circle(self.pantalla, color_circulo, (circle_pos, y + switch_height//2), circle_radius//2)
        
        # Dibujar texto
        texto_surface = self.fuente_texto.render(texto, True, self.BLANCO)
        self.pantalla.blit(texto_surface, (x + switch_width + 15, y + switch_height//2 - 10))
        
        # Dibujar estado actual
        if puede_cambiar:
            estado_texto = "Activado" if valor else "Desactivado"
            estado_color = self.VERDE if valor else self.GRIS_CLARO
        else:
            tiempo_restante = self.cooldown_vibracion - (tiempo_actual - self.ultimo_cambio_vibracion)
            estado_texto = f"Espera {tiempo_restante:.1f}s"
            estado_color = self.AMARILLO
        
        estado_surface = self.fuente_pequena.render(estado_texto, True, estado_color)
        self.pantalla.blit(estado_surface, (x + switch_width + 15, y + switch_height//2 + 10))
        
        # Manejar click solo si puede cambiar
        if (puede_cambiar and x <= mouse_pos[0] <= x + switch_width and y <= mouse_pos[1] <= y + switch_height and 
            mouse_click and not hasattr(self, '_ultimo_click_switch')):
            self._ultimo_click_switch = True
            self.ultimo_cambio_vibracion = tiempo_actual
            callback(not valor)
            
            # Probar vibración si se activa
            if not valor:  # Si estaba desactivado y ahora se activa
                self.iniciar_vibracion(0.3, 3)
            
            return True
        
        return False
    
    def dibujar_fondo_nivel(self, nivel_mundo, offset_x=0, offset_y=0):
        """Dibuja el fondo específico para cada nivel."""
        if nivel_mundo == 1:  # Selva
            self.pantalla.fill(self.VERDE_SELVA)
            # Añadir algunos elementos decorativos de selva
            for i in range(0, self.ANCHO, 40):
                for j in range(0, self.ALTO, 40):
                    if random.randint(1, 10) == 1:  # 10% de probabilidad
                        pygame.draw.circle(self.pantalla, self.VERDE_OSCURO, 
                                         (i + offset_x, j + offset_y), 3)
        
        elif nivel_mundo == 2:  # Volcán
            self.pantalla.fill(self.GRIS_OSCURO)
            # Añadir elementos volcánicos
            for i in range(0, self.ANCHO, 30):
                for j in range(0, self.ALTO, 30):
                    if random.randint(1, 15) == 1:  # Rocas volcánicas
                        pygame.draw.circle(self.pantalla, self.MARRON, 
                                         (i + offset_x, j + offset_y), 2)
        
        elif nivel_mundo == 3:  # Desierto
            self.pantalla.fill(self.AMARILLO_DESIERTO)
            # Añadir elementos del desierto
            for i in range(0, self.ANCHO, 25):
                for j in range(0, self.ALTO, 25):
                    if random.randint(1, 20) == 1:  # Dunas de arena
                        pygame.draw.circle(self.pantalla, self.MARRON_DESIERTO, 
                                         (i + offset_x, j + offset_y), 1)
    
    def inicializar_particulas_arena(self):
        """Inicializa las partículas de arena para el efecto de tormenta."""
        self.particulas_arena = []
        for _ in range(150):  # Número de partículas
            particula = {
                'x': random.randint(0, self.ANCHO),
                'y': random.randint(-50, self.ALTO),
                'velocidad_y': random.uniform(2, 6),
                'velocidad_x': random.uniform(-1, 1),
                'tamanio': random.randint(1, 3),
                'opacidad': random.randint(100, 200)
            }
            self.particulas_arena.append(particula)
    
    def actualizar_particulas_arena(self, dt):
        """Actualiza las partículas de arena."""
        for particula in self.particulas_arena:
            particula['y'] += particula['velocidad_y']
            particula['x'] += particula['velocidad_x']
            
            # Reiniciar partícula si sale de la pantalla
            if particula['y'] > self.ALTO:
                particula['y'] = random.randint(-20, -5)
                particula['x'] = random.randint(0, self.ANCHO)
            
            if particula['x'] < 0 or particula['x'] > self.ANCHO:
                particula['x'] = random.randint(0, self.ANCHO)
    
    def dibujar_efecto_arena_cayendo(self, intensidad=1.0, offset_x=0, offset_y=0):
        """Dibuja el efecto de arena cayendo con opacidad del 70%."""
        if not self.particulas_arena:
            self.inicializar_particulas_arena()
        
        # Crear superficie para las partículas con transparencia
        superficie_arena = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        
        for particula in self.particulas_arena:
            # Calcular opacidad basada en la intensidad (70% máximo)
            opacidad = int(particula['opacidad'] * intensidad * 0.7)
            color_arena = (*self.ARENA_COLOR, opacidad)
            
            # Dibujar partícula
            x = int(particula['x'] + offset_x)
            y = int(particula['y'] + offset_y)
            tamanio = particula['tamanio']
            
            if tamanio == 1:
                pygame.draw.circle(superficie_arena, color_arena, (x, y), 1)
            elif tamanio == 2:
                pygame.draw.circle(superficie_arena, color_arena, (x, y), 2)
            else:
                pygame.draw.rect(superficie_arena, color_arena, (x, y, 3, 3))
        
        # Dibujar la superficie con las partículas sobre la pantalla
        self.pantalla.blit(superficie_arena, (0, 0))
    
    def menu_principal(self):
        """Dibuja y maneja el menú principal."""
        # Cargar música del menú si no está ya cargada
        if self.musica_actual != "menu":
            self.cargar_musica("menu")
            pygame.mixer.music.play(-1)
        
        self.pantalla.fill(self.NEGRO)
        
        titulo = self.fuente_titulo.render("Paimon Snake", True, self.DORADO)
        titulo_rect = titulo.get_rect(center=(self.ANCHO//2, 150))
        self.pantalla.blit(titulo, titulo_rect)
        
        boton_ancho, boton_alto = 200, 50
        boton_x = self.ANCHO//2 - boton_ancho//2
        
        if self.dibujar_boton("Jugar", boton_x, 250, boton_ancho, boton_alto, self.VERDE, self.NEGRO):
            self.estado = "selector_niveles"
        
        if self.dibujar_boton("Opciones", boton_x, 320, boton_ancho, boton_alto, self.AZUL, self.BLANCO):
            self.estado = "opciones"
        
        if self.dibujar_boton("Salir", boton_x, 390, boton_ancho, boton_alto, self.ROJO, self.BLANCO):
            return False
        
        return True
    
    def selector_niveles(self):
        """Dibuja y maneja el selector de niveles."""
        self.pantalla.fill(self.NEGRO)
        
        titulo = self.fuente_titulo.render("Seleccionar Nivel", True, self.BLANCO)
        titulo_rect = titulo.get_rect(center=(self.ANCHO//2, 80))
        self.pantalla.blit(titulo, titulo_rect)
        
        nivel_ancho, nivel_alto = 180, 120
        espaciado = 220
        inicio_x = self.ANCHO//2 - (3 * espaciado)//2
        
        for i in range(1, 4):
            x = inicio_x + (i-1) * espaciado
            y = 200
            
            disponible = self.verificar_nivel_desbloqueado(i)
            
            if disponible:
                if i == 1:
                    color = self.VERDE_SELVA
                elif i == 2:
                    color = self.ROJO_LAVA
                else:
                    color = self.AMARILLO_DESIERTO
            else:
                color = self.GRIS
            
            if self.dibujar_boton(f"Nivel {i}", x, y, nivel_ancho, nivel_alto, color, self.NEGRO, disponible):
                if disponible:
                    self.nivel_seleccionado = i
                    self.estado = "jugando"
            
            # Descripción del nivel
            desc = self.obtener_descripcion_nivel(i)
            desc_surface = self.fuente_pequena.render(desc, True, self.BLANCO if disponible else self.GRIS)
            desc_rect = desc_surface.get_rect(center=(x + nivel_ancho//2, y + nivel_alto + 15))
            self.pantalla.blit(desc_surface, desc_rect)
            
            # Mostrar requisitos si no está disponible
            if not disponible:
                req = self.obtener_requisito_desbloqueo(i)
                req_surface = self.fuente_pequena.render(req, True, self.ROJO)
                req_rect = req_surface.get_rect(center=(x + nivel_ancho//2, y + nivel_alto + 35))
                self.pantalla.blit(req_surface, req_rect)
            else:
                # Mostrar progreso actual
                if i == 1:
                    progreso = self.usuario_actual.get('nivel_mundo_1', 1)
                elif i == 2:
                    progreso = self.usuario_actual.get('nivel_mundo_2', 1)
                else:
                    progreso = self.usuario_actual.get('nivel_mundo_3', 1)
                
                prog_text = f"Mejor nivel: {progreso}"
                prog_surface = self.fuente_pequena.render(prog_text, True, self.AMARILLO)
                prog_rect = prog_surface.get_rect(center=(x + nivel_ancho//2, y + nivel_alto + 35))
                self.pantalla.blit(prog_surface, prog_rect)
        
        if self.dibujar_boton("Volver", 50, 500, 100, 40, self.GRIS_OSCURO, self.BLANCO):
            self.estado = "menu_principal"
        
        return True
    
    def menu_opciones(self):
        """Dibuja y maneja el menú de opciones."""
        self.pantalla.fill(self.NEGRO)
        
        titulo = self.fuente_titulo.render("Opciones", True, self.BLANCO)
        titulo_rect = titulo.get_rect(center=(self.ANCHO//2, 80))
        self.pantalla.blit(titulo, titulo_rect)
        
        barra_ancho = 300
        barra_x = self.ANCHO//2 - barra_ancho//2
        
        self.dibujar_barra_volumen(
            "Volumen General", barra_x, 150, barra_ancho,
            self.configuracion["volumen_general"],
            lambda v: self.actualizar_volumen("volumen_general", v)
        )
        
        self.dibujar_barra_volumen(
            "Volumen de Efectos", barra_x, 220, barra_ancho,
            self.configuracion["volumen_efectos"],
            lambda v: self.actualizar_volumen("volumen_efectos", v)
        )
        
        self.dibujar_barra_volumen(
            "Volumen de Música", barra_x, 290, barra_ancho,
            self.configuracion["volumen_musica"],
            lambda v: self.actualizar_volumen("volumen_musica", v)
        )
        
        # Switch con cooldown
        self.dibujar_switch(
            "Vibración de Pantalla", barra_x, 360,
            self.configuracion["vibracion_pantalla"],
            lambda v: self.actualizar_configuracion("vibracion_pantalla", v)
        )
        
        if self.dibujar_boton("Guardar", barra_x, 450, 100, 40, self.VERDE, self.NEGRO):
            self.guardar_configuracion()
        
        if self.dibujar_boton("Volver", barra_x + 200, 450, 100, 40, self.GRIS_OSCURO, self.BLANCO):
            self.estado = "menu_principal"
        
        return True
    
    def actualizar_volumen(self, tipo, valor):
        """Actualiza un valor de volumen específico."""
        self.configuracion[tipo] = valor
        self.aplicar_configuracion_audio()
    
    def actualizar_configuracion(self, clave, valor):
        """Actualiza un valor de configuración."""
        self.configuracion[clave] = valor
    
    # ==================== FUNCIONES DEL JUEGO SNAKE ====================
    
    def mostrar_puntuacion(self, puntuacion, nivel, nivel_mundo, offset_x=0, offset_y=0):
        """Muestra la puntuación, nivel y mundo actual en la pantalla."""
        nombres_mundo = {1: "Selva", 2: "Volcán", 3: "Desierto"}
        nombre_mundo = nombres_mundo.get(nivel_mundo, "Desconocido")
        valor = self.fuente_puntuacion.render(f"Puntuación: {puntuacion} | {nombre_mundo} Nivel: {nivel}", True, self.AMARILLO)
        self.pantalla.blit(valor, [10 + offset_x, 10 + offset_y])
    
    def mostrar_estado_efectos(self, efectos_activos, offset_x=0, offset_y=0):
        """Muestra los efectos activos y su tiempo restante."""
        y_pos = 50
        for efecto, datos in efectos_activos.items():
            if datos["tiempo_restante"] > 0:
                tiempo = round(datos["tiempo_restante"])
                if efecto == "escudo":
                    texto = self.fuente_estado.render(f"🛡️ Escudo: {tiempo}s", True, self.DORADO)
                elif efecto == "acelerador":
                    texto = self.fuente_estado.render(f"⚡ Acelerador: {tiempo}s", True, self.NARANJA)
                elif efecto == "ralentizador":
                    texto = self.fuente_estado.render(f"🐌 Ralentizador: {tiempo}s", True, self.MORADO)
                self.pantalla.blit(texto, [10 + offset_x, y_pos + offset_y])
                y_pos += 30
    
    def mostrar_eventos_especiales(self, nivel_mundo, eventos_activos, offset_x=0, offset_y=0):
        """Muestra información sobre eventos especiales del nivel."""
        y_pos = self.ALTO - 160
        
        if nivel_mundo == 2:  # Volcán
            if "lava" in eventos_activos:
                tiempo_restante = round(eventos_activos["lava"]["tiempo_siguiente"])
                areas_activas = len([a for a in eventos_activos["lava"]["areas_activas"] if a["activa"]])
                advertencias = len([a for a in eventos_activos["lava"]["areas_activas"] if a["estado"] == "advertencia"])
                
                if tiempo_restante <= 3:
                    color = self.ROJO
                    texto = self.fuente_timer.render(f"🌋 ¡LAVA EN {tiempo_restante}s!", True, color)
                else:
                    color = self.NARANJA
                    texto = self.fuente_timer.render(f"🌋 Próxima lava: {tiempo_restante}s", True, color)
                self.pantalla.blit(texto, [10 + offset_x, y_pos + offset_y])
                
                # Mostrar contador de áreas activas
                if areas_activas > 0 or advertencias > 0:
                    contador_texto = f"Lava activa: {areas_activas} | Advertencias: {advertencias}"
                    contador_surface = self.fuente_pequena.render(contador_texto, True, self.ROJO)
                    self.pantalla.blit(contador_surface, [10 + offset_x, y_pos + 20 + offset_y])
        
        elif nivel_mundo == 3:  # Desierto
            if "tormenta" in eventos_activos:
                if eventos_activos["tormenta"]["activa"]:
                    tiempo_restante = round(eventos_activos["tormenta"]["tiempo_restante"])
                    color = self.AMARILLO
                    texto = self.fuente_timer.render(f"🌪️ Tormenta: {tiempo_restante}s", True, color)
                else:
                    tiempo_siguiente = round(eventos_activos["tormenta"]["tiempo_siguiente"])
                    if tiempo_siguiente <= 3:
                        color = self.AMARILLO
                        texto = self.fuente_timer.render(f"🌪️ ¡TORMENTA EN {tiempo_siguiente}s!", True, color)
                    else:
                        color = self.MARRON_DESIERTO
                        texto = self.fuente_timer.render(f"🌪️ Próxima tormenta: {tiempo_siguiente}s", True, color)
                self.pantalla.blit(texto, [10 + offset_x, y_pos + offset_y])
    
    def mostrar_estado_powerup(self, estado_powerup, offset_x=0, offset_y=0):
        """Muestra el estado actual del sistema de power-ups."""
        y_pos = self.ALTO - 120
        
        if estado_powerup["estado"] == "activo":
            tiempo_restante = round(estado_powerup["tiempo_restante"])
            if tiempo_restante <= 3:
                color = self.ROJO
                texto = self.fuente_timer.render(f"⚠️ Power-up desaparece en: {tiempo_restante}s", True, color)
            else:
                color = self.BLANCO
                texto = self.fuente_timer.render(f"Power-up disponible: {tiempo_restante}s", True, color)
        elif estado_powerup["estado"] == "esperando":
            tiempo_restante = round(estado_powerup["tiempo_restante"])
            color = self.AMARILLO
            texto = self.fuente_timer.render(f"Próximo power-up en: {tiempo_restante}s", True, color)
        else:
            color = self.GRIS
            texto = self.fuente_timer.render("Generando power-up...", True, color)
            
        self.pantalla.blit(texto, [10 + offset_x, y_pos + offset_y])
    
    def mostrar_estadisticas_consumibles(self, comida_consumida, powerups_consumidos, offset_x=0, offset_y=0):
        """Muestra estadísticas de consumibles en la esquina inferior derecha."""
        y_pos = self.ALTO - 80
        
        texto_comida = self.fuente_categoria.render(f"Comida: {comida_consumida}", True, self.VERDE)
        self.pantalla.blit(texto_comida, [self.ANCHO - 150 + offset_x, y_pos + offset_y])
        
        texto_powerups = self.fuente_categoria.render(f"Power-ups: {powerups_consumidos}", True, self.DORADO)
        self.pantalla.blit(texto_powerups, [self.ANCHO - 150 + offset_x, y_pos + 20 + offset_y])
    
    def mostrar_mensaje(self, mensaje, color, pos_y, offset_x=0, offset_y=0):
        """Muestra un mensaje en la pantalla."""
        texto = self.fuente_boton.render(mensaje, True, color)
        self.pantalla.blit(texto, [self.ANCHO / 6 + offset_x, pos_y + offset_y])
    
    def calcular_max_charcos_lava(self, nivel_juego):
        """Calcula el número máximo de charcos de lava simultáneos basado en el nivel."""
        # Empezar con 1 charco, añadir 1 cada 3 niveles, máximo 5 charcos
        return min(5, 1 + (nivel_juego - 1) // 3)
    
    def generar_comida(self, serpiente, comida_existente=None, areas_lava=None):
        """Genera una nueva comida en una posición aleatoria, evitando áreas de lava."""
        rand = random.randint(1, 100)
        acumulado = 0
        tipo_elegido = "manzana"
        
        for tipo, datos in self.COMIDA.items():
            acumulado += datos["probabilidad"]
            if rand <= acumulado:
                tipo_elegido = tipo
                break
        
        intentos = 0
        while intentos < 100:  # Evitar bucle infinito
            x = round(random.randrange(0, self.ANCHO - self.TAMANIO_BLOQUE) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            y = round(random.randrange(0, self.ALTO - self.TAMANIO_BLOQUE) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            posicion = [x, y]
            
            # Verificar que no esté en la serpiente
            if posicion in serpiente:
                intentos += 1
                continue
            
            # Verificar que no esté en la comida existente
            if comida_existente is not None and posicion == list(comida_existente[:2]):
                intentos += 1
                continue
            
            # Verificar que no esté en áreas de lava (activas o en advertencia)
            if areas_lava:
                en_lava = False
                for area_lava in areas_lava:
                    if self.posicion_en_area_lava(x, y, area_lava):
                        en_lava = True
                        break
                if en_lava:
                    intentos += 1
                    continue
            
            return x, y, tipo_elegido
        
        # Si no se puede encontrar una posición válida, usar una posición por defecto
        return 100, 100, tipo_elegido

    def generar_powerup(self, serpiente, comida_pos, powerup_existente=None, areas_lava=None):
        """Genera un nuevo power-up en una posición aleatoria, evitando áreas de lava."""
        rand = random.randint(1, 100)
        acumulado = 0
        tipo_elegido = "escudo"
        
        for tipo, datos in self.POWER_UPS.items():
            acumulado += datos["probabilidad"]
            if rand <= acumulado:
                tipo_elegido = tipo
                break
        
        intentos = 0
        while intentos < 100:
            x = round(random.randrange(0, self.ANCHO - self.TAMANIO_BLOQUE) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            y = round(random.randrange(0, self.ALTO - self.TAMANIO_BLOQUE) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            posicion = [x, y]
            
            if (posicion not in serpiente and 
                posicion != list(comida_pos[:2]) and
                (powerup_existente is None or posicion != list(powerup_existente[:2]))):
                
                # Verificar que no esté en áreas de lava
                if areas_lava:
                    en_lava = False
                    for area_lava in areas_lava:
                        if self.posicion_en_area_lava(x, y, area_lava):
                            en_lava = True
                            break
                    if en_lava:
                        intentos += 1
                        continue
                
                return x, y, tipo_elegido
            
            intentos += 1
        
        return 100, 120, tipo_elegido

    def generar_gota_lava(self, serpiente, comida_pos, powerup_pos=None, areas_existentes=None):
        """Genera una gota de lava en una posición aleatoria."""
        intentos = 0
        while intentos < 50:
            # Generar posición en múltiplos del tamaño de bloque
            x = round(random.randrange(0, self.ANCHO - self.TAMANIO_BLOQUE * self.TAMANIO_LAVA) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            y = round(random.randrange(0, self.ALTO - self.TAMANIO_BLOQUE * self.TAMANIO_LAVA) / self.TAMANIO_BLOQUE) * self.TAMANIO_BLOQUE
            
            # Verificar que no interfiera con elementos importantes
            area_ocupada = False
            for i in range(self.TAMANIO_LAVA):
                for j in range(self.TAMANIO_LAVA):
                    pos_x = x + i * self.TAMANIO_BLOQUE
                    pos_y = y + j * self.TAMANIO_BLOQUE
                    posicion = [pos_x, pos_y]
                    
                    if (posicion in serpiente or 
                        posicion == list(comida_pos[:2]) or
                        (powerup_pos and posicion == list(powerup_pos[:2]))):
                        area_ocupada = True
                        break
                if area_ocupada:
                    break
            
            # Verificar que no se superponga con otras áreas de lava
            if areas_existentes and not area_ocupada:
                for area_existente in areas_existentes:
                    if (abs(x - area_existente["x"]) < self.TAMANIO_LAVA * self.TAMANIO_BLOQUE and
                        abs(y - area_existente["y"]) < self.TAMANIO_LAVA * self.TAMANIO_BLOQUE):
                        area_ocupada = True
                        break
            
            if not area_ocupada:
                return {
                    "x": x,
                    "y": y,
                    "estado": "advertencia",  # Nuevo estado: advertencia -> activa
                    "tiempo_advertencia": self.DURACION_ADVERTENCIA_LAVA,
                    "tiempo_restante": self.DURACION_LAVA,
                    "activa": False
                }
            
            intentos += 1
        
        # Posición por defecto si no se encuentra una válida
        return {
            "x": 200,
            "y": 200,
            "estado": "advertencia",
            "tiempo_advertencia": self.DURACION_ADVERTENCIA_LAVA,
            "tiempo_restante": self.DURACION_LAVA,
            "activa": False
        }

    def posicion_en_area_lava(self, x, y, area_lava):
        """Verifica si una posición está dentro de un área de lava (activa o en advertencia)."""
        if area_lava["estado"] == "inactiva":
            return False
        
        return (area_lava["x"] <= x < area_lava["x"] + self.TAMANIO_LAVA * self.TAMANIO_BLOQUE and
                area_lava["y"] <= y < area_lava["y"] + self.TAMANIO_LAVA * self.TAMANIO_BLOQUE)

    def dibujar_comida(self, x, y, tipo, offset_x=0, offset_y=0):
        """Dibuja comida en la pantalla."""
        color = self.COMIDA[tipo]["color"]
        pygame.draw.rect(self.pantalla, color, [x + offset_x, y + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
        
        if tipo == "manzana":
            pygame.draw.rect(self.pantalla, self.MARRON, [x + 8 + offset_x, y - 5 + offset_y, 4, 5])
        elif tipo == "carne":
            pygame.draw.line(self.pantalla, self.ROJO, [x + 5 + offset_x, y + 5 + offset_y], [x + 15 + offset_x, y + 15 + offset_y], 2)
            pygame.draw.line(self.pantalla, self.ROJO, [x + 15 + offset_x, y + 5 + offset_y], [x + 5 + offset_x, y + 15 + offset_y], 2)

    def dibujar_powerup(self, x, y, tipo, tiempo_restante, offset_x=0, offset_y=0):
        """Dibuja power-up en la pantalla con efectos visuales según el tiempo restante."""
        color = self.POWER_UPS[tipo]["color"]
        
        if tiempo_restante <= 3:
            frecuencia_parpadeo = max(0.2, tiempo_restante / 10)
            if int(time.time() / frecuencia_parpadeo) % 2 == 0:
                color = tuple(max(0, c - 50) for c in color)
        
        pygame.draw.rect(self.pantalla, self.BLANCO, [x-2 + offset_x, y-2 + offset_y, self.TAMANIO_BLOQUE+4, self.TAMANIO_BLOQUE+4])
        pygame.draw.rect(self.pantalla, color, [x + offset_x, y + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
        
        if tipo == "escudo":
            pygame.draw.circle(self.pantalla, self.AMARILLO, [x + 10 + offset_x, y + 10 + offset_y], 7, 2)
        elif tipo == "acelerador":
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 5 + offset_x, y + 10 + offset_y], [x + 15 + offset_x, y + 10 + offset_y], 2)
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 15 + offset_x, y + 10 + offset_y], [x + 10 + offset_x, y + 5 + offset_y], 2)
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 15 + offset_x, y + 10 + offset_y], [x + 10 + offset_x, y + 15 + offset_y], 2)
        elif tipo == "ralentizador":
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 15 + offset_x, y + 10 + offset_y], [x + 5 + offset_x, y + 10 + offset_y], 2)
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 5 + offset_x, y + 10 + offset_y], [x + 10 + offset_x, y + 5 + offset_y], 2)
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 5 + offset_x, y + 10 + offset_y], [x + 10 + offset_x, y + 15 + offset_y], 2)
        elif tipo == "reductor":
            pygame.draw.line(self.pantalla, self.AMARILLO, [x + 5 + offset_x, y + 10 + offset_y], [x + 15 + offset_x, y + 10 + offset_y], 3)

    def dibujar_advertencia_lava(self, area_lava, offset_x=0, offset_y=0):
        """Dibuja la advertencia de donde va a caer la lava."""
        if area_lava["estado"] != "advertencia":
            return
        
        # Calcular el centro del área
        centro_x = area_lava["x"] + (self.TAMANIO_LAVA * self.TAMANIO_BLOQUE) // 2
        centro_y = area_lava["y"] + (self.TAMANIO_LAVA * self.TAMANIO_BLOQUE) // 2
        
        # Efecto de parpadeo basado en el tiempo restante
        tiempo_restante = area_lava["tiempo_advertencia"]
        if tiempo_restante <= 1.0:
            frecuencia = 0.1  # Parpadeo rápido
        else:
            frecuencia = 0.3  # Parpadeo normal
        
        if int(time.time() / frecuencia) % 2 == 0:
            # Dibujar área de advertencia con borde rojo
            for i in range(self.TAMANIO_LAVA):
                for j in range(self.TAMANIO_LAVA):
                    x = area_lava["x"] + i * self.TAMANIO_BLOQUE
                    y = area_lava["y"] + j * self.TAMANIO_BLOQUE
                    pygame.draw.rect(self.pantalla, self.ROJO, 
                                   [x + offset_x, y + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE], 3)
            
            # Dibujar símbolo de advertencia "!" en el centro
            texto_advertencia = self.fuente_advertencia.render("!", True, self.ROJO)
            rect_advertencia = texto_advertencia.get_rect(center=(centro_x + offset_x, centro_y + offset_y))
            
            # Fondo blanco para el símbolo
            pygame.draw.circle(self.pantalla, self.BLANCO, 
                             (centro_x + offset_x, centro_y + offset_y), 12)
            pygame.draw.circle(self.pantalla, self.ROJO, 
                             (centro_x + offset_x, centro_y + offset_y), 12, 2)
            
            self.pantalla.blit(texto_advertencia, rect_advertencia)

    def dibujar_area_lava(self, area_lava, offset_x=0, offset_y=0):
        """Dibuja un área de lava en la pantalla."""
        if area_lava["estado"] == "advertencia":
            self.dibujar_advertencia_lava(area_lava, offset_x, offset_y)
            return
        
        if not area_lava["activa"]:
            return
        
        # Efecto de desvanecimiento gradual
        tiempo_restante = area_lava["tiempo_restante"]
        intensidad = 1.0
        if tiempo_restante < 1.0:
            intensidad = tiempo_restante  # Desvanecimiento gradual
        
        # Dibujar área de lava
        for i in range(self.TAMANIO_LAVA):
            for j in range(self.TAMANIO_LAVA):
                x = area_lava["x"] + i * self.TAMANIO_BLOQUE
                y = area_lava["y"] + j * self.TAMANIO_BLOQUE
                
                # Color base de lava
                color_lava = tuple(int(c * intensidad) for c in self.ROJO_LAVA)
                pygame.draw.rect(self.pantalla, color_lava, 
                               [x + offset_x, y + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                
                # Efecto de burbujeo
                if random.randint(1, 10) == 1:
                    pygame.draw.circle(self.pantalla, self.AMARILLO, 
                                     (x + self.TAMANIO_BLOQUE//2 + offset_x, 
                                      y + self.TAMANIO_BLOQUE//2 + offset_y), 3)

    def aplicar_efecto_powerup(self, tipo, efectos_activos):
        """Aplica el efecto del power-up recogido."""
        duracion = self.POWER_UPS[tipo]["duracion_efecto"]
        
        if tipo == "escudo":
            efectos_activos["escudo"] = {
                "activo": True,
                "tiempo_restante": duracion
            }
        elif tipo == "acelerador":
            efectos_activos["acelerador"] = {
                "activo": True,
                "tiempo_restante": duracion,
                "multiplicador_velocidad": 2.0,
                "multiplicador_puntos": 3.0
            }
            if "ralentizador" in efectos_activos:
                efectos_activos["ralentizador"]["activo"] = False
                efectos_activos["ralentizador"]["tiempo_restante"] = 0
        elif tipo == "ralentizador":
            efectos_activos["ralentizador"] = {
                "activo": True,
                "tiempo_restante": duracion,
                "multiplicador_velocidad": 0.5,
                "multiplicador_puntos": 0.5
            }
            if "acelerador" in efectos_activos:
                efectos_activos["acelerador"]["activo"] = False
                efectos_activos["acelerador"]["tiempo_restante"] = 0
                
        return efectos_activos

    def aplicar_reductor_tamanio(self, serpiente, longitud_serpiente):
        """Aplica el efecto del reductor de tamaño."""
        if longitud_serpiente >= 4:
            reduccion = max(1, longitud_serpiente // 4)
            nueva_longitud = longitud_serpiente - reduccion
            
            if len(serpiente) > nueva_longitud:
                nueva_serpiente = serpiente[-nueva_longitud:]
            else:
                nueva_serpiente = serpiente.copy()
                
            return nueva_serpiente, nueva_longitud
        else:
            return serpiente, longitud_serpiente

    def actualizar_efectos(self, efectos_activos, tiempo_transcurrido):
        """Actualiza el tiempo restante de los efectos activos."""
        for efecto in efectos_activos:
            if efectos_activos[efecto]["activo"]:
                efectos_activos[efecto]["tiempo_restante"] -= tiempo_transcurrido
                if efectos_activos[efecto]["tiempo_restante"] <= 0:
                    efectos_activos[efecto]["activo"] = False
                    efectos_activos[efecto]["tiempo_restante"] = 0
        
        return efectos_activos

    def actualizar_eventos_especiales(self, nivel_mundo, eventos_activos, tiempo_transcurrido, nivel_juego, serpiente, comida_pos, powerup_pos=None):
        """Actualiza los eventos especiales según el nivel."""
        if nivel_mundo == 2:  # Volcán - Gotas de lava mejoradas
            if "lava" not in eventos_activos:
                eventos_activos["lava"] = {
                    "tiempo_siguiente": self.TIEMPO_LAVA_BASE,
                    "areas_activas": []
                }
            
            # Actualizar tiempo para próxima gota
            eventos_activos["lava"]["tiempo_siguiente"] -= tiempo_transcurrido
            
            # Generar nueva gota de lava
            if eventos_activos["lava"]["tiempo_siguiente"] <= 0:
                max_charcos = self.calcular_max_charcos_lava(nivel_juego)
                areas_activas_count = len([a for a in eventos_activos["lava"]["areas_activas"] 
                                         if a["estado"] != "inactiva"])
                
                # Solo generar si no hemos alcanzado el máximo
                if areas_activas_count < max_charcos:
                    nueva_area = self.generar_gota_lava(serpiente, comida_pos, powerup_pos, 
                                                      eventos_activos["lava"]["areas_activas"])
                    eventos_activos["lava"]["areas_activas"].append(nueva_area)
                
                # Calcular próximo tiempo basado en el nivel
                tiempo_base = max(self.TIEMPO_LAVA_MINIMO, self.TIEMPO_LAVA_BASE - (nivel_juego - 1) * 0.3)
                eventos_activos["lava"]["tiempo_siguiente"] = tiempo_base
            
            # Actualizar áreas de lava existentes
            areas_a_remover = []
            for i, area in enumerate(eventos_activos["lava"]["areas_activas"]):
                if area["estado"] == "advertencia":
                    area["tiempo_advertencia"] -= tiempo_transcurrido
                    if area["tiempo_advertencia"] <= 0:
                        # Cambiar de advertencia a activa
                        area["estado"] = "activa"
                        area["activa"] = True
                elif area["estado"] == "activa":
                    area["tiempo_restante"] -= tiempo_transcurrido
                    if area["tiempo_restante"] <= 0:
                        area["estado"] = "inactiva"
                        area["activa"] = False
                        areas_a_remover.append(i)
            
            # Remover áreas expiradas
            for i in reversed(areas_a_remover):
                del eventos_activos["lava"]["areas_activas"][i]
        
        elif nivel_mundo == 3:  # Desierto - Tormenta de arena
            if "tormenta" not in eventos_activos:
                eventos_activos["tormenta"] = {
                    "activa": False,
                    "tiempo_restante": 0,
                    "tiempo_siguiente": self.TIEMPO_TORMENTA
                }
            
            if eventos_activos["tormenta"]["activa"]:
                # Actualizar tormenta activa
                eventos_activos["tormenta"]["tiempo_restante"] -= tiempo_transcurrido
                # Actualizar partículas de arena
                self.actualizar_particulas_arena(tiempo_transcurrido)
                
                if eventos_activos["tormenta"]["tiempo_restante"] <= 0:
                    eventos_activos["tormenta"]["activa"] = False
                    eventos_activos["tormenta"]["tiempo_siguiente"] = self.TIEMPO_TORMENTA
            else:
                # Actualizar tiempo para próxima tormenta
                eventos_activos["tormenta"]["tiempo_siguiente"] -= tiempo_transcurrido
                if eventos_activos["tormenta"]["tiempo_siguiente"] <= 0:
                    eventos_activos["tormenta"]["activa"] = True
                    eventos_activos["tormenta"]["tiempo_restante"] = self.DURACION_TORMENTA
                    # Reinicializar partículas para la nueva tormenta
                    self.inicializar_particulas_arena()
        
        return eventos_activos

    def verificar_colision_lava(self, x, y, areas_lava):
        """Verifica si la serpiente colisiona con algún área de lava activa."""
        for area_lava in areas_lava:
            if area_lava["estado"] == "activa" and self.posicion_en_area_lava(x, y, area_lava):
                return True
        return False

    def actualizar_estado_powerup(self, estado_powerup, tiempo_transcurrido, serpiente, comida_pos, areas_lava=None):
        """Actualiza el estado del sistema de power-ups."""
        estado_powerup["tiempo_restante"] -= tiempo_transcurrido
        
        if estado_powerup["estado"] == "activo":
            if estado_powerup["tiempo_restante"] <= 0:
                estado_powerup["estado"] = "esperando"
                estado_powerup["tiempo_restante"] = self.TIEMPO_ESPERA_POWERUP
                estado_powerup["x"] = None
                estado_powerup["y"] = None
                estado_powerup["tipo"] = None
                
        elif estado_powerup["estado"] == "esperando":
            if estado_powerup["tiempo_restante"] <= 0:
                x, y, tipo = self.generar_powerup(serpiente, comida_pos, None, areas_lava)
                estado_powerup["estado"] = "activo"
                estado_powerup["tiempo_restante"] = self.DURACION_POWERUP_MAPA
                estado_powerup["x"] = x
                estado_powerup["y"] = y
                estado_powerup["tipo"] = tipo
                
        return estado_powerup

    def calcular_velocidad_actual(self, velocidad_base, nivel, efectos_activos):
        """Calcula la velocidad actual basada en el nivel y los efectos activos."""
        velocidad = velocidad_base + (nivel - 1) * 2
        velocidad = min(velocidad, self.VELOCIDAD_MAXIMA)
        
        if "acelerador" in efectos_activos and efectos_activos["acelerador"]["activo"]:
            velocidad *= efectos_activos["acelerador"]["multiplicador_velocidad"]
        elif "ralentizador" in efectos_activos and efectos_activos["ralentizador"]["activo"]:
            velocidad *= efectos_activos["ralentizador"]["multiplicador_velocidad"]
            
        return velocidad

    def calcular_puntos(self, tipo, categoria, efectos_activos):
        """Calcula los puntos ganados por un consumible teniendo en cuenta los efectos activos."""
        if categoria == "comida":
            puntos_base = self.COMIDA[tipo]["puntos"]
        else:
            puntos_base = self.POWER_UPS[tipo]["puntos"]
        
        if "acelerador" in efectos_activos and efectos_activos["acelerador"]["activo"]:
            puntos_base *= efectos_activos["acelerador"]["multiplicador_puntos"]
        elif "ralentizador" in efectos_activos and efectos_activos["ralentizador"]["activo"]:
            puntos_base *= efectos_activos["ralentizador"]["multiplicador_puntos"]
            
        return int(puntos_base)

    def reproducir_sonido_consumible(self, tipo, categoria):
        """Reproduce el sonido correspondiente al tipo de consumible."""
        if categoria == "comida":
            self.sonido_comer.play()
        else:
            if tipo == "escudo":
                self.sonido_escudo.play()
            elif tipo == "acelerador":
                self.sonido_acelerar.play()
            elif tipo == "ralentizador":
                self.sonido_descelerar.play()
            elif tipo == "reductor":
                self.sonido_reducir.play()
    
    def actualizar_progreso_usuario(self, nivel_mundo, nivel_alcanzado):
        """Actualiza el progreso del usuario en el mundo específico."""
        clave_progreso = f"nivel_mundo_{nivel_mundo}"
        if clave_progreso not in self.usuario_actual:
            self.usuario_actual[clave_progreso] = 1
        if nivel_alcanzado > self.usuario_actual[clave_progreso]:
            self.usuario_actual[clave_progreso] = nivel_alcanzado
            # Actualizar también en la base de datos
            actualizar_nivel_maximo(self.usuario_actual["id"], nivel_mundo, nivel_alcanzado)
    
    def iniciar_juego_nivel(self, nivel_mundo):
        """Inicia el juego en el nivel/mundo especificado."""
        try:
            # Cargar música específica del nivel
            self.cargar_musica_nivel(nivel_mundo)
            pygame.mixer.music.play(-1)
            
            juego_terminado = False
            juego_perdido = False
            partida_registrada = False
            sonido_muerte_reproducido = False
            
            # Resetear estado de pausa
            self.juego_pausado = False
            
            # Inicializar posición de la serpiente
            x1 = self.ANCHO / 2
            y1 = self.ALTO / 2
            cambio_x = 0
            cambio_y = 0

            serpiente = []
            longitud_serpiente = 1
            
            # Estadísticas de consumibles
            comida_consumida = 0
            powerups_consumidos = 0
            
            # Inicializar eventos especiales
            eventos_activos = {}
            
            # Inicializar partículas de arena para el desierto
            if nivel_mundo == 3:
                self.inicializar_particulas_arena()
            
            # Generar comida inicial
            areas_lava = eventos_activos.get("lava", {}).get("areas_activas", []) if nivel_mundo == 2 else None
            comida_x, comida_y, tipo_comida = self.generar_comida(serpiente, None, areas_lava)
            
            # Inicializar sistema de power-ups
            estado_powerup = {
                "estado": "esperando",
                "tiempo_restante": 3.0,
                "x": None,
                "y": None,
                "tipo": None
            }

            puntuacion = 0
            nivel = 1
            
            # Inicializar efectos
            efectos_activos = {
                "escudo": {"activo": False, "tiempo_restante": 0},
                "acelerador": {"activo": False, "tiempo_restante": 0, "multiplicador_velocidad": 1.0, "multiplicador_puntos": 1.0},
                "ralentizador": {"activo": False, "tiempo_restante": 0, "multiplicador_velocidad": 1.0, "multiplicador_puntos": 1.0}
            }
            
            # Control de tiempo
            ultimo_tiempo = time.time()

            while not juego_terminado:
                # Calcular tiempo transcurrido
                tiempo_actual = time.time()
                tiempo_transcurrido = tiempo_actual - ultimo_tiempo
                ultimo_tiempo = tiempo_actual
                
                # Actualizar vibración
                self.actualizar_vibracion(tiempo_transcurrido)
                offset_x, offset_y = self.obtener_offset_vibracion()
                
                # Manejar eventos
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        return False
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            self.estado = "menu_principal"
                            pygame.mixer.music.stop()
                            return True
                        elif evento.key == pygame.K_p:  # Tecla de pausa
                            self.pausar_juego()
                        elif not self.juego_pausado:  # Solo procesar movimiento si no está pausado
                            if evento.key == pygame.K_LEFT and cambio_x == 0:
                                cambio_x = -self.TAMANIO_BLOQUE
                                cambio_y = 0
                            elif evento.key == pygame.K_RIGHT and cambio_x == 0:
                                cambio_x = self.TAMANIO_BLOQUE
                                cambio_y = 0
                            elif evento.key == pygame.K_UP and cambio_y == 0:
                                cambio_y = -self.TAMANIO_BLOQUE
                                cambio_x = 0
                            elif evento.key == pygame.K_DOWN and cambio_y == 0:
                                cambio_y = self.TAMANIO_BLOQUE
                                cambio_x = 0
                
                # Si el juego está pausado, solo dibujar la pantalla de pausa
                if self.juego_pausado:
                    # Dibujar fondo del nivel
                    self.dibujar_fondo_nivel(nivel_mundo, offset_x, offset_y)
                    
                    # Dibujar todos los elementos del juego
                    if nivel_mundo == 2 and "lava" in eventos_activos:
                        for area_lava in eventos_activos["lava"]["areas_activas"]:
                            self.dibujar_area_lava(area_lava, offset_x, offset_y)
                    
                    self.dibujar_comida(comida_x, comida_y, tipo_comida, offset_x, offset_y)
                    
                    if estado_powerup["estado"] == "activo":
                        self.dibujar_powerup(estado_powerup["x"], estado_powerup["y"], 
                                          estado_powerup["tipo"], estado_powerup["tiempo_restante"], offset_x, offset_y)
                    
                    # Dibujar la serpiente
                    for bloque in serpiente:
                        if efectos_activos["escudo"]["activo"]:
                            pygame.draw.rect(self.pantalla, self.DORADO, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                            pygame.draw.rect(self.pantalla, self.AZUL, [bloque[0]+2 + offset_x, bloque[1]+2 + offset_y, self.TAMANIO_BLOQUE-4, self.TAMANIO_BLOQUE-4])
                        elif efectos_activos["acelerador"]["activo"]:
                            pygame.draw.rect(self.pantalla, self.NARANJA, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                        elif efectos_activos["ralentizador"]["activo"]:
                            pygame.draw.rect(self.pantalla, self.MORADO, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                        else:
                            pygame.draw.rect(self.pantalla, self.AZUL, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                    
                    # Dibujar UI
                    self.mostrar_puntuacion(puntuacion, nivel, nivel_mundo, offset_x, offset_y)
                    self.mostrar_estado_efectos(efectos_activos, offset_x, offset_y)
                    self.mostrar_eventos_especiales(nivel_mundo, eventos_activos, offset_x, offset_y)
                    self.mostrar_estado_powerup(estado_powerup, offset_x, offset_y)
                    self.mostrar_estadisticas_consumibles(comida_consumida, powerups_consumidos, offset_x, offset_y)
                    
                    # Dibujar pantalla de pausa encima
                    self.dibujar_pantalla_pausa(offset_x, offset_y)
                    
                    pygame.display.update()
                    self.reloj.tick(60)
                    continue
                
                # Actualizar efectos activos solo si no está pausado
                efectos_activos = self.actualizar_efectos(efectos_activos, tiempo_transcurrido)
                
                # Actualizar eventos especiales del nivel
                powerup_pos = (estado_powerup["x"], estado_powerup["y"]) if estado_powerup["estado"] == "activo" else None
                eventos_activos = self.actualizar_eventos_especiales(
                    nivel_mundo, eventos_activos, tiempo_transcurrido, nivel, 
                    serpiente, (comida_x, comida_y), powerup_pos
                )
                
                # Actualizar estado de power-ups
                areas_lava = eventos_activos.get("lava", {}).get("areas_activas", []) if nivel_mundo == 2 else None
                estado_powerup = self.actualizar_estado_powerup(estado_powerup, tiempo_transcurrido, serpiente, (comida_x, comida_y), areas_lava)
                
                # Calcular velocidad actual
                velocidad = self.calcular_velocidad_actual(self.VELOCIDAD_BASE, nivel, efectos_activos)
                
                while juego_perdido:
                    # Reproducir sonido de muerte y activar vibración solo una vez
                    if not sonido_muerte_reproducido:
                        pygame.mixer.music.stop()
                        self.sonido_muerte.play()
                        # Activar vibración fuerte al perder
                        self.iniciar_vibracion(1.5, 10)
                        sonido_muerte_reproducido = True

                    # Actualizar vibración durante la pantalla de game over
                    self.actualizar_vibracion(1/60)
                    offset_x, offset_y = self.obtener_offset_vibracion()

                    # Dibujar fondo del nivel
                    self.dibujar_fondo_nivel(nivel_mundo, offset_x, offset_y)
                    
                    self.mostrar_mensaje("¡Perdiste! Presiona ESC para volver al menú o ENTER para reintentar", self.ROJO, self.ALTO / 2, offset_x, offset_y)
                    self.mostrar_puntuacion(puntuacion, nivel, nivel_mundo, offset_x, offset_y)
                    self.mostrar_estadisticas_consumibles(comida_consumida, powerups_consumidos, offset_x, offset_y)
                    pygame.display.update()

                    # Registrar la partida solo una vez
                    if not partida_registrada:
                        try:
                            registrar_partida(self.usuario_actual['id'], puntuacion, nivel)
                            self.actualizar_progreso_usuario(nivel_mundo, nivel)
                            print("Puntuación actualizada correctamente.")
                        except Exception as e:
                            print(f"Error al registrar partida: {e}")
                        partida_registrada = True

                    # Esperar la decisión del jugador
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            return False
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_ESCAPE:
                                self.estado = "menu_principal"
                                pygame.mixer.music.stop()
                                return True
                            elif evento.key == pygame.K_RETURN:
                                return self.iniciar_juego_nivel(nivel_mundo)  # Reiniciar

                if juego_terminado:
                    break

                x1 += cambio_x
                y1 += cambio_y

                # Detectar colisión con bordes
                if x1 >= self.ANCHO or x1 < 0 or y1 >= self.ALTO or y1 < 0:
                    if efectos_activos["escudo"]["activo"]:
                        if x1 >= self.ANCHO:
                            x1 = 0
                        elif x1 < 0:
                            x1 = self.ANCHO - self.TAMANIO_BLOQUE
                        elif y1 >= self.ALTO:
                            y1 = 0
                        elif y1 < 0:
                            y1 = self.ALTO - self.TAMANIO_BLOQUE
                    else:
                        juego_perdido = True

                # Verificar colisión con lava (solo en nivel volcán)
                if nivel_mundo == 2 and "lava" in eventos_activos:
                    if self.verificar_colision_lava(x1, y1, eventos_activos["lava"]["areas_activas"]):
                        if not efectos_activos["escudo"]["activo"]:
                            juego_perdido = True

                # Dibujar fondo del nivel
                self.dibujar_fondo_nivel(nivel_mundo, offset_x, offset_y)
                
                # Dibujar áreas de lava (solo en nivel volcán)
                if nivel_mundo == 2 and "lava" in eventos_activos:
                    for area_lava in eventos_activos["lava"]["areas_activas"]:
                        self.dibujar_area_lava(area_lava, offset_x, offset_y)
                
                # Dibujar comida (siempre presente)
                self.dibujar_comida(comida_x, comida_y, tipo_comida, offset_x, offset_y)
                
                # Dibujar power-up si está activo
                if estado_powerup["estado"] == "activo":
                    self.dibujar_powerup(estado_powerup["x"], estado_powerup["y"], 
                                      estado_powerup["tipo"], estado_powerup["tiempo_restante"], offset_x, offset_y)
                
                cabeza = [x1, y1]
                serpiente.append(cabeza)
                
                if len(serpiente) > longitud_serpiente:
                    del serpiente[0]

                # Detectar colisión consigo misma
                for bloque in serpiente[:-1]:
                    if bloque == cabeza:
                        if not efectos_activos["escudo"]["activo"]:
                            juego_perdido = True

                # Dibujar la serpiente
                for bloque in serpiente:
                    if efectos_activos["escudo"]["activo"]:
                        pygame.draw.rect(self.pantalla, self.DORADO, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                        pygame.draw.rect(self.pantalla, self.AZUL, [bloque[0]+2 + offset_x, bloque[1]+2 + offset_y, self.TAMANIO_BLOQUE-4, self.TAMANIO_BLOQUE-4])
                    elif efectos_activos["acelerador"]["activo"]:
                        pygame.draw.rect(self.pantalla, self.NARANJA, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                    elif efectos_activos["ralentizador"]["activo"]:
                        pygame.draw.rect(self.pantalla, self.MORADO, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])
                    else:
                        pygame.draw.rect(self.pantalla, self.AZUL, [bloque[0] + offset_x, bloque[1] + offset_y, self.TAMANIO_BLOQUE, self.TAMANIO_BLOQUE])

                # Aplicar efecto de arena cayendo (solo en nivel desierto durante tormenta)
                if nivel_mundo == 3 and "tormenta" in eventos_activos and eventos_activos["tormenta"]["activa"]:
                    intensidad_tormenta = eventos_activos["tormenta"]["tiempo_restante"] / self.DURACION_TORMENTA
                    self.dibujar_efecto_arena_cayendo(intensidad_tormenta, offset_x, offset_y)

                # Detectar si come comida
                if x1 == comida_x and y1 == comida_y:
                    self.reproducir_sonido_consumible(tipo_comida, "comida")
                    comida_consumida += 1
                    longitud_serpiente += self.COMIDA[tipo_comida]["crecimiento"]
                    puntos_ganados = self.calcular_puntos(tipo_comida, "comida", efectos_activos)
                    puntuacion += puntos_ganados
                    
                    # Regenerar comida evitando áreas de lava
                    areas_lava = eventos_activos.get("lava", {}).get("areas_activas", []) if nivel_mundo == 2 else None
                    powerup_pos = (estado_powerup["x"], estado_powerup["y"]) if estado_powerup["estado"] == "activo" else None
                    comida_x, comida_y, tipo_comida = self.generar_comida(serpiente, powerup_pos, areas_lava)
                    
                    if puntuacion // 100 > nivel - 1:
                        nivel += 1

                # Detectar si come power-up
                if (estado_powerup["estado"] == "activo" and 
                    x1 == estado_powerup["x"] and y1 == estado_powerup["y"]):
                    
                    self.reproducir_sonido_consumible(estado_powerup["tipo"], "powerup")
                    powerups_consumidos += 1
                    
                    if estado_powerup["tipo"] == "reductor":
                        serpiente, longitud_serpiente = self.aplicar_reductor_tamanio(serpiente, longitud_serpiente)
                    else:
                        efectos_activos = self.aplicar_efecto_powerup(estado_powerup["tipo"], efectos_activos)
                        longitud_serpiente += self.POWER_UPS[estado_powerup["tipo"]]["crecimiento"]
                    
                    puntos_ganados = self.calcular_puntos(estado_powerup["tipo"], "powerup", efectos_activos)
                    puntuacion += puntos_ganados
                    
                    estado_powerup["estado"] = "esperando"
                    estado_powerup["tiempo_restante"] = self.TIEMPO_ESPERA_POWERUP
                    estado_powerup["x"] = None
                    estado_powerup["y"] = None
                    estado_powerup["tipo"] = None

                self.mostrar_puntuacion(puntuacion, nivel, nivel_mundo, offset_x, offset_y)
                self.mostrar_estado_efectos(efectos_activos, offset_x, offset_y)
                self.mostrar_eventos_especiales(nivel_mundo, eventos_activos, offset_x, offset_y)
                self.mostrar_estado_powerup(estado_powerup, offset_x, offset_y)
                self.mostrar_estadisticas_consumibles(comida_consumida, powerups_consumidos, offset_x, offset_y)
                pygame.display.update()
                self.reloj.tick(velocidad)

            return True
            
        except Exception as e:
            print(f"Error en el juego: {e}")
            return True
    
    def ejecutar(self, usuario_actual=None):
        if usuario_actual is not None:
            niveles = obtener_niveles_maximos(usuario_actual["id"])
            usuario_actual["nivel_mundo_1"] = niveles[0]
            usuario_actual["nivel_mundo_2"] = niveles[1]
            usuario_actual["nivel_mundo_3"] = niveles[2]
        self.usuario_actual = usuario_actual or {
            "username": "Jugador", 
            "nivel": 1, 
            "id": 1, 
            "puntuacion": 0,
            "nivel_mundo_1": 1,
            "nivel_mundo_2": 0,
            "nivel_mundo_3": 0
        }
        ejecutando = True
        
        while ejecutando:
            # Resetear flags de click
            if hasattr(self, '_ultimo_click'):
                delattr(self, '_ultimo_click')
            if hasattr(self, '_ultimo_click_checkbox'):
                delattr(self, '_ultimo_click_checkbox')
            if hasattr(self, '_ultimo_click_switch'):
                delattr(self, '_ultimo_click_switch')
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE and self.estado != "menu_principal":
                        if self.estado == "jugando":
                            pygame.mixer.music.stop()
                        self.estado = "menu_principal"
            
            # Manejar estados
            if self.estado == "menu_principal":
                if not self.menu_principal():
                    ejecutando = False
            elif self.estado == "selector_niveles":
                if not self.selector_niveles():
                    ejecutando = False
            elif self.estado == "opciones":
                if not self.menu_opciones():
                    ejecutando = False
            elif self.estado == "jugando":
                if not self.iniciar_juego_nivel(self.nivel_seleccionado):
                    ejecutando = False
            
            pygame.display.flip()
            self.reloj.tick(60)
        
        pygame.quit()


def iniciar_juego(usuario_actual, game_finished):
    """Función principal que inicia el juego completo."""
    juego = PaimonSnake()
    juego.ejecutar(usuario_actual)
    game_finished()


# Para pruebas independientes
if __name__ == "__main__":
    usuario_test = {
        "username": "Jugador Test", 
        "nivel": 1, 
        "id": 1, 
        "puntuacion": 0,
        "nivel_mundo_1": 6,  # Para probar desbloqueo de nivel 2
        "nivel_mundo_2": 3,  # Para mostrar progreso en nivel 2
        "nivel_mundo_3": 0   # Nivel 3 bloqueado
    }
    def game_finished():
        print("Juego terminado")
    
    iniciar_juego(usuario_test, game_finished)
