def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana en la pantalla.

    Args:
        ventana (tk.Tk | tk.Toplevel): La ventana de Tkinter que se desea centrar.
        ancho (int): Ancho de la ventana.
        alto (int): Alto de la ventana.
    """
    ventana.update_idletasks()  # Actualiza las tareas pendientes de la ventana
    pantalla_ancho = ventana.winfo_screenwidth()  # Ancho de la pantalla
    pantalla_alto = ventana.winfo_screenheight()  # Alto de la pantalla
    x = (pantalla_ancho // 2) - (ancho // 2)  # Coordenada X para centrar
    y = (pantalla_alto // 2) - (alto // 2)  # Coordenada Y para centrar
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")  # Establece la posición y tamaño de la ventana
