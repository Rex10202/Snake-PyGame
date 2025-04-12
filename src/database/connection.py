import os
import mysql.connector
import bcrypt


def connect_db():
    """
    Establece la conexión con la base de datos MySQL usando variables de entorno.

    Returns:
        mysql.connector.connection.MySQLConnection: Objeto de conexión a la base de datos.

    Raises:
        EnvironmentError: Si faltan variables de entorno necesarias.
        mysql.connector.Error: Si ocurre un error al conectar a la base de datos.
    """
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    if not all([db_host, db_user, db_password, db_name]):
        raise EnvironmentError("Faltan variables de entorno para la conexión a la base de datos.")
    try:
        conexion = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return conexion
    except mysql.connector.Error as err:
        raise


def crear_tabla_jugadores():
    """
    Crea la tabla 'jugadores' en la base de datos si no existe.

    La tabla incluye los siguientes campos:
        - id: ID único del jugador.
        - username: Nombre de usuario único.
        - password: Contraseña encriptada.
        - puntuacion: Puntuación actual del jugador.
        - nivel: Nivel actual del jugador.
        - rol: Rol del jugador (por defecto, "user").
    """
    conexion = connect_db()
    if conexion is not None:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jugadores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                puntuacion INT DEFAULT 0,
                nivel INT DEFAULT 1,
                rol VARCHAR(20) DEFAULT 'user' CHECK (rol IN ('user', 'admin'))
            );
        """)
        conexion.commit()
        cursor.close()
        conexion.close()


def crear_tabla_partidas():
    """
    Crea la tabla 'partidas' en la base de datos si no existe.

    La tabla incluye los siguientes campos:
        - id: ID único de la partida.
        - jugador_id: ID del jugador asociado.
        - puntuacion: Puntuación obtenida en la partida.
        - nivel: Nivel alcanzado en la partida.
        - fecha: Fecha y hora de la partida (por defecto, la actual).
    """
    conexion = connect_db()
    if conexion is not None:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                jugador_id INT,
                puntuacion INT,
                nivel INT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jugador_id) REFERENCES jugadores(id)
            );
        """)
        conexion.commit()
        cursor.close()
        conexion.close()


def agregar_jugador(username, password, puntuacion=0, nivel=1, rol="user"):
    """
    Agrega un nuevo jugador a la base de datos.

    Args:
        username (str): Nombre de usuario único.
        password (str): Contraseña del jugador (se encripta antes de guardarla).
        puntuacion (int): Puntuación inicial del jugador (por defecto, 0).
        nivel (int): Nivel inicial del jugador (por defecto, 1).
        rol (str): Rol del jugador (por defecto, "user").

    Returns:
        bool: True si el jugador se agregó correctamente, False en caso de error.
    """
    if rol not in ["user", "admin"]:
        print("Error: Rol inválido.")
        return False

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO jugadores (username, password, puntuacion, nivel, rol) VALUES (%s, %s, %s, %s, %s)",
            (username, hashed_password.decode('utf-8'), puntuacion, nivel, rol)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al agregar jugador: {e}")
        return False


def editar_jugador(jugador_id, username, puntuacion, nivel, rol):
    """
    Edita los datos de un jugador existente en la base de datos.

    Args:
        jugador_id (int): ID del jugador a editar.
        username (str): Nuevo nombre de usuario.
        puntuacion (int): Nueva puntuación.
        nivel (int): Nuevo nivel.
        rol (str): Nuevo rol del jugador.

    Returns:
        bool: True si el jugador se editó correctamente, False en caso de error.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()

        # Actualizar los datos del jugador (excepto la puntuación máxima)
        cursor.execute(
            "UPDATE jugadores SET username=%s, nivel=%s, rol=%s WHERE id=%s",
            (username, nivel, rol, jugador_id)
        )

        # Registrar la nueva puntuación en el historial
        cursor.execute(
            "INSERT INTO partidas (jugador_id, puntuacion, nivel, fecha) VALUES (%s, %s, %s, NOW())",
            (jugador_id, puntuacion, nivel)
        )

        # Recalcular la puntuación máxima del jugador
        cursor.execute(
            "SELECT MAX(puntuacion) FROM partidas WHERE jugador_id = %s",
            (jugador_id,)
        )
        nueva_puntuacion_maxima = cursor.fetchone()[0] or 0  # Si no hay partidas, la puntuación máxima es 0

        # Actualizar la puntuación máxima en la tabla jugadores
        cursor.execute(
            "UPDATE jugadores SET puntuacion = %s WHERE id = %s",
            (nueva_puntuacion_maxima, jugador_id)
        )

        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as err:
        print("Error al editar jugador:", err)
        return False


def eliminar_jugador(jugador_id):
    """
    Elimina un jugador de la base de datos junto con sus partidas asociadas.

    Args:
        jugador_id (int): ID del jugador a eliminar.

    Returns:
        bool: True si el jugador y sus partidas se eliminaron correctamente, False en caso de error.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()

        # Eliminar las partidas asociadas al jugador
        cursor.execute("DELETE FROM partidas WHERE jugador_id = %s", (jugador_id,))

        # Eliminar al jugador
        cursor.execute("DELETE FROM jugadores WHERE id = %s", (jugador_id,))

        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as err:
        print("Error al eliminar jugador:", err)
        return False


def obtener_ranking_global():
    """
    Obtiene el ranking global de jugadores con su mayor puntuación,
    excluyendo a los administradores.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()

        # Consulta para obtener el ID, usuario, mayor puntuación, nivel y rol de cada jugador
        cursor.execute("""
            SELECT j.id, j.username, 
                   COALESCE(MAX(p.puntuacion), 0) AS mayor_puntuacion, 
                   j.nivel, j.rol
            FROM jugadores j
            LEFT JOIN partidas p ON j.id = p.jugador_id
            WHERE j.rol != 'admin'  -- Excluir administradores
            GROUP BY j.id, j.username, j.nivel, j.rol
            ORDER BY mayor_puntuacion DESC
        """)
        ranking = cursor.fetchall()

        cursor.close()
        conexion.close()
        return ranking
    except Exception as e:
        print(f"Error al obtener el ranking global: {e}")
        return []


def obtener_historial_personal(usuario_id):
    """
    Obtiene el historial de partidas de un usuario específico en orden cronológico inverso.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, puntuacion, nivel, fecha 
            FROM partidas 
            WHERE jugador_id = %s 
            ORDER BY fecha DESC
        """, (usuario_id,))
        historial = cursor.fetchall()
        cursor.close()
        conexion.close()
        return historial
    except Exception as e:
        print(f"Error al obtener el historial personal: {e}")
        return []


def registrar_partida(jugador_id, puntuacion, nivel):
    """
    Registra una partida jugada en la base de datos.

    Args:
        jugador_id (int): ID del jugador.
        puntuacion (int): Puntuación obtenida en la partida.
        nivel (int): Nivel alcanzado en la partida.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO partidas (jugador_id, puntuacion, nivel) VALUES (%s, %s, %s)",
            (jugador_id, puntuacion, nivel)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
    except mysql.connector.Error as err:
        print("Error al registrar la partida:", err)


def verificar_jugador(username, password):
    """
    Verifica las credenciales de un jugador.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña ingresada.

    Returns:
        bool: True si las credenciales son correctas, False en caso contrario.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT password FROM jugadores WHERE username = %s", (username,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            hashed_password = resultado[0]
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
        return False
    except Exception as e:
        print(f"Error al verificar jugador: {e}")
        return False


def eliminar_partida(partida_id):
    """
    Elimina una partida de la base de datos.

    Args:
        partida_id (int): ID de la partida a eliminar.

    Returns:
        bool: True si la partida se eliminó correctamente, False en caso de error.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM partidas WHERE id = %s", (partida_id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as err:
        print("Error al eliminar partida:", err)
        return False


def recalcular_puntuacion_maxima(jugador_id):
    """
    Recalcula la puntuación máxima de un jugador basándose en las partidas restantes.

    Args:
        jugador_id (int): ID del jugador.
    """
    try:
        conexion = connect_db()
        cursor = conexion.cursor()

        # Obtener la nueva puntuación máxima
        cursor.execute("SELECT MAX(puntuacion) FROM partidas WHERE jugador_id = %s", (jugador_id,))
        nueva_puntuacion_maxima = cursor.fetchone()[0] or 0  # Si no hay partidas, la puntuación máxima es 0

        # Actualizar la puntuación máxima en la tabla jugadores
        cursor.execute("UPDATE jugadores SET puntuacion = %s WHERE id = %s", (nueva_puntuacion_maxima, jugador_id))

        conexion.commit()
        cursor.close()
        conexion.close()
    except mysql.connector.Error as err:
        print("Error al recalcular la puntuación máxima:", err)


