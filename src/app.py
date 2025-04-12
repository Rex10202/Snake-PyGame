import tkinter as tk
from database.connection import crear_tabla_jugadores, crear_tabla_partidas
from ui.components import AplicacionGUI


def main():
    """
    Función principal de la aplicación.

    - Crea las tablas necesarias en la base de datos si no existen.
    - Inicia la interfaz gráfica de usuario (GUI) utilizando Tkinter.
    """
    crear_tabla_jugadores()  # Crea la tabla de jugadores si no existe
    crear_tabla_partidas()  # Crea la tabla de partidas si no existe

    root = tk.Tk()
    AplicacionGUI(root)  # Inicializa la interfaz gráfica
    root.mainloop()  # Inicia el bucle principal de la GUI


if __name__ == "__main__":
    main()
