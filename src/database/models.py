from .connection import connect_db


class Jugador:
    """
    Clase que representa a un jugador en el sistema.

    Args:
        jugador_id (int): ID único del jugador.
        username (str): Nombre de usuario del jugador.
        puntuacion (int): Puntuación actual del jugador.
        nivel (int): Nivel actual del jugador.
        rol (str): Rol del jugador (por defecto, "user").
    """

    def __init__(self, jugador_id, username, puntuacion, nivel, rol="user"):
        """
        Inicializa una instancia de la clase Jugador.
        """
        self.id = jugador_id
        self.username = username
        self.puntuacion = puntuacion
        self.nivel = nivel
        self.rol = rol

    def mostrar_informacion(self):
        """
        Devuelve una representación en forma de cadena de la información del jugador.

        Returns:
            str: Información del jugador en formato legible.
        """
        return f"ID: {self.id} | Usuario: {self.username} | Puntuación: {self.puntuacion} | Nivel: {self.nivel} | Rol: {self.rol}"

    def actualizar_puntuacion(self, nueva_puntuacion, nuevo_nivel):
        """
        Actualiza la puntuación y el nivel del jugador en la base de datos.

        Args:
            nueva_puntuacion (int): Nueva puntuación del jugador.
            nuevo_nivel (int): Nuevo nivel del jugador.
        """
        self.puntuacion = nueva_puntuacion
        self.nivel = nuevo_nivel
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE jugadores SET puntuacion = %s, nivel = %s WHERE id = %s",
            (self.puntuacion, self.nivel, self.id)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

    @staticmethod
    def buscar_por_id(jugador_id):
        """
        Busca un jugador en la base de datos por su ID.

        Args:
            jugador_id (int): ID del jugador a buscar.

        Returns:
            Jugador | None: Una instancia de la clase Jugador si se encuentra, o None si no existe.
        """
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, username, puntuacion, nivel, rol FROM jugadores WHERE id = %s",
            (jugador_id,)
        )
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        if resultado:
            return Jugador(*resultado)
        else:
            return None