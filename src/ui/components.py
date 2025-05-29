"""
Módulo de componentes de la interfaz gráfica.

Este módulo contiene la clase `AplicacionGUI`, que maneja la lógica de la interfaz gráfica
de usuario (GUI) para el sistema de jugadores del juego "Culebrita Clásica".
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt

from database.connection import (
    connect_db,
    agregar_jugador,
    editar_jugador,
    eliminar_jugador,
    eliminar_partida,
    obtener_ranking_global,
    obtener_historial_personal,
    recalcular_puntuacion_maxima,
)
from database.models import Jugador
from game.main_menu import iniciar_juego
from utils.helpers import centrar_ventana


class AplicacionGUI:
    """
    Clase que representa la interfaz gráfica de usuario (GUI) de la aplicación.

    Args:
        master (tk.Tk): Ventana principal de Tkinter.
    """

    def __init__(self, master):
        """
        Inicializa la interfaz gráfica de usuario.

        Configura la ventana principal y muestra el formulario de inicio de sesión.
        """
        self.master = master
        self.master.title("Sistema de Jugadores - Culebrita")
        centrar_ventana(self.master, 400, 400)
        self.master.resizable(False, False)
        self.master.configure(bg="#1e1e1e")
        self.usuario_actual = None
        self.marco_login = tk.Frame(self.master, bg="#1e1e1e")
        self.marco_login.pack(expand=True, fill="both")
        self.crear_login()

    def crear_login(self):
        """
        Crea el formulario de inicio de sesión.
        """
        for widget in self.master.winfo_children():
            widget.destroy()
        self.marco_login = tk.Frame(self.master, bg="#1e1e1e")
        self.marco_login.pack(expand=True, fill="both")
        tk.Label(self.marco_login, text="Iniciar sesión", font=("Helvetica", 20), bg="#1e1e1e", fg="white").pack(pady=20)
        tk.Label(self.marco_login, text="Usuario:", font=("Helvetica", 14), bg="#1e1e1e", fg="white").pack(pady=5)
        self.usuario_entry = tk.Entry(self.marco_login, font=("Helvetica", 14))
        self.usuario_entry.pack(pady=5)
        tk.Label(self.marco_login, text="Contraseña:", font=("Helvetica", 14), bg="#1e1e1e", fg="white").pack(pady=5)
        self.password_entry = tk.Entry(self.marco_login, show="*", font=("Helvetica", 14))
        self.password_entry.pack(pady=5)
        tk.Button(self.marco_login, text="Entrar", font=("Helvetica", 14), command=self.login).pack(pady=15)
        tk.Button(self.marco_login, text="Registrarse", font=("Helvetica", 14), command=self.registro).pack(pady=5)
        tk.Button(self.marco_login, text="Salir", font=("Helvetica", 14), command=self.salir_app).pack(pady=5)

    def salir_app(self):
        """
        Cierra la aplicación.
        """
        self.master.destroy()

    def login(self):
        """
        Maneja el inicio de sesión de un usuario.

        - Verifica las credenciales ingresadas.
        - Carga el rol del usuario si las credenciales son correctas.
        """
        username = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == "" or password == "":
            messagebox.showerror("Error", "Complete todos los campos.")
            return

        try:
            conexion = connect_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT id, username, puntuacion, nivel, rol, password FROM jugadores WHERE username = %s", (username,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()

            if resultado:
                db_id, db_username, db_puntuacion, db_nivel, db_rol, db_password = resultado
                if bcrypt.checkpw(password.encode("utf-8"), db_password.encode("utf-8")):
                    self.usuario_actual = {
                        "id": db_id,
                        "username": db_username,
                        "puntuacion": db_puntuacion,
                        "nivel": db_nivel,
                        "rol": db_rol
                    }
                    self.mostrar_menu_principal()
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta.")
            else:
                messagebox.showerror("Error", "Usuario no encontrado. Regístrese.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {e}")

    def registro(self):
        """
        Maneja el registro de un nuevo usuario.

        - Verifica que los campos no estén vacíos.
        - Intenta registrar al usuario en la base de datos.
        """
        username = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == "" or password == "":
            messagebox.showerror("Error", "Complete todos los campos.")
            return
        if agregar_jugador(username, password):
            messagebox.showinfo("Registro", "Registro exitoso. Ahora inicie sesión.")
        else:
            messagebox.showerror("Error", "No se pudo registrar. Tal vez el usuario ya exista.")

    def mostrar_menu_principal(self):
        """
        Muestra el menú principal después de iniciar sesión.
        """
        for widget in self.master.winfo_children():
            widget.destroy()
        self.marco_menu = tk.Frame(self.master, bg="#1e1e1e")
        self.marco_menu.pack(expand=True, fill="both")
        tk.Label(
            self.marco_menu,
            text=f"Hola, {self.usuario_actual['username']}",
            font=("Helvetica", 18),
            bg="#1e1e1e",
            fg="white",
        ).pack(pady=10)

        if self.usuario_actual["rol"] == "admin":
            # Opciones solo para administradores
            tk.Button(self.marco_menu, text="Gestionar Jugadores", font=("Helvetica", 14), width=20, command=self.abrir_gestion_jugadores).pack(pady=8)
        else:
            # Opciones solo para usuarios
            tk.Button(self.marco_menu, text="Iniciar Partida", font=("Helvetica", 14), width=20, command=self.iniciar_partida).pack(pady=8)
            tk.Button(self.marco_menu, text="Ranking Mundial", font=("Helvetica", 14), width=20, command=self.mostrar_ranking_global).pack(pady=8)
            tk.Button(self.marco_menu, text="Mi Historial", font=("Helvetica", 14), width=20, command=self.mostrar_historial_personal).pack(pady=8)

        tk.Button(self.marco_menu, text="Cerrar Sesión", font=("Helvetica", 14), width=20, command=self.cerrar_sesion).pack(pady=8)

    def iniciar_partida(self):
        """
        Inicia una nueva partida del juego "Culebrita Clásica".
        """
        if self.usuario_actual["rol"] == "admin":
            messagebox.showerror("Acceso denegado", "Los administradores no pueden jugar.")
            return

        # Lógica para iniciar el juego (solo para usuarios)
        self.master.withdraw()
        def game_finished():
            self.master.after(0, lambda: [self.master.deiconify(), self.mostrar_menu_principal()])
        self.juego_thread = threading.Thread(target=iniciar_juego, args=(self.usuario_actual, game_finished))
        self.juego_thread.start()

    def mostrar_ranking_global(self):
        """
        Muestra el ranking global de jugadores.
        """
        if self.usuario_actual["rol"] == "admin":
            messagebox.showerror("Acceso denegado", "Los administradores no pueden ver el ranking.")
            return

        # Lógica para mostrar el ranking (solo para usuarios)
        ranking = obtener_ranking_global()
        self.ventana_ranking = tk.Toplevel(self.master)
        self.ventana_ranking.title("Ranking Mundial")
        centrar_ventana(self.ventana_ranking, 1000, 400)
        self.ventana_ranking.resizable(False, False)
        tree = ttk.Treeview(self.ventana_ranking, columns=("ID", "Usuario", "Puntuación","Nivel","Mundo"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Usuario", text="Usuario")
        tree.heading("Puntuación", text="Puntuación")
        tree.heading("Nivel", text="Nivel")
        tree.heading("Mundo", text="Mundo")
        tree.pack(expand=True, fill="both")
        for fila in ranking:
            tree.insert("", "end", values=fila)

    def mostrar_historial_personal(self):
        """
        Muestra el historial personal del usuario actual.
        """
        if self.usuario_actual["rol"] == "admin":
            messagebox.showerror("Acceso denegado", "Los administradores no tienen historial de partidas.")
            return
    
        # Lógica para mostrar el historial (solo para usuarios)
        historial = obtener_historial_personal(self.usuario_actual["id"])
        # Ordenar el historial en forma descendente según la fecha
        historial.sort(key=lambda x: (x[3] is None, x[3] or ''), reverse=True)
        puntuacion_maxima = max([fila[1] for fila in historial], default=0)
        self.ventana_historial = tk.Toplevel(self.master)
        self.ventana_historial.title("Mi Historial de Partidas")
        centrar_ventana(self.ventana_historial, 1000, 400)
        self.ventana_historial.resizable(False, False)
        tk.Label(self.ventana_historial, text=f"Puntuación Máxima: {puntuacion_maxima}", 
                 font=("Helvetica", 14), bg="#1e1e1e", fg="white").pack(pady=10)
        tree = ttk.Treeview(self.ventana_historial, columns=("ID", "Puntuación", "Nivel", "Mundo", "Fecha"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Puntuación", text="Puntuación")
        tree.heading("Nivel", text="Nivel")
        tree.heading("Mundo", text="Mundo")
        tree.heading("Fecha", text="Fecha")
        tree.pack(expand=True, fill="both")
        for fila in historial:
            tree.insert("", "end", values=fila)

    def abrir_gestion_jugadores(self):
        """
        Abre una ventana para gestionar jugadores (solo para administradores).
        """
        if hasattr(self, 'ventana_gestion') and self.ventana_gestion.winfo_exists():
            self.ventana_gestion.destroy()
        self.ventana_gestion = tk.Toplevel(self.master)
        self.ventana_gestion.title("Gestión de Jugadores")
        centrar_ventana(self.ventana_gestion, 600, 400)  # Centrar la ventana
        self.ventana_gestion.resizable(False, False)

        self.tree_gestion = ttk.Treeview(self.ventana_gestion, columns=("ID", "Usuario", "Puntuación", "Nivel", "Rol"), show="headings")
        self.tree_gestion.heading("ID", text="ID")
        self.tree_gestion.heading("Usuario", text="Usuario")
        self.tree_gestion.heading("Puntuación", text="Puntuación")
        self.tree_gestion.heading("Nivel", text="Nivel")
        self.tree_gestion.heading("Rol", text="Rol")
        self.tree_gestion.pack(expand=True, fill="both")

        self.cargar_jugadores_en_tree()

        tk.Button(self.ventana_gestion, text="Editar", command=self.editar_jugador_seleccionado).pack(side="left", padx=10, pady=10)
        tk.Button(self.ventana_gestion, text="Eliminar", command=self.eliminar_jugador_seleccionado).pack(side="left", padx=10, pady=10)
        tk.Button(self.ventana_gestion, text="Gestionar Partidas", command=self.abrir_gestion_partidas).pack(side="left", padx=10, pady=10)

    def cargar_jugadores_en_tree(self):
        ranking = obtener_ranking_global()
        for item in self.tree_gestion.get_children():
            self.tree_gestion.delete(item)
        for fila in ranking:
            try:
                conexion = connect_db()
                cursor = conexion.cursor()
                cursor.execute("SELECT rol FROM jugadores WHERE id=%s", (fila[0],))
                rol = cursor.fetchone()[0]
                cursor.close()
                conexion.close()
            except:
                rol = "user"
            self.tree_gestion.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], rol))

    def editar_jugador_seleccionado(self):
        item = self.tree_gestion.focus()
        if not item:
            messagebox.showerror("Error", "No se ha seleccionado ningún jugador. Se regresará a la ventana de gestión.")
            # Opcional: Cierra la ventana de gestión actual antes de reabrirla (si hace falta)
            self.ventana_gestion.destroy()
            self.abrir_gestion_jugadores()
            return
        datos = self.tree_gestion.item(item, "values")
        self.abrir_editar_jugador(datos)


    def abrir_editar_jugador(self, datos):
        """
        Abre una ventana para editar los datos de un jugador seleccionado.
        """
        self.ventana_editar = tk.Toplevel(self.master)
        self.ventana_editar.title("Editar Jugador")
        self.ventana_editar.geometry("400x400")
        centrar_ventana(self.ventana_editar, 400, 400)
        self.ventana_editar.resizable(False, False)

        tk.Label(self.ventana_editar, text="ID:").pack(pady=5)
        tk.Label(self.ventana_editar, text=datos[0]).pack(pady=5)

        tk.Label(self.ventana_editar, text="Usuario:").pack(pady=5)
        entry_usuario = tk.Entry(self.ventana_editar)
        entry_usuario.insert(0, datos[1])
        entry_usuario.pack(pady=5)

        tk.Label(self.ventana_editar, text="Puntuación:").pack(pady=5)
        entry_puntuacion = tk.Entry(self.ventana_editar)
        entry_puntuacion.insert(0, datos[2])
        entry_puntuacion.pack(pady=5)

        tk.Label(self.ventana_editar, text="Nivel:").pack(pady=5)
        entry_nivel = tk.Entry(self.ventana_editar)
        entry_nivel.insert(0, datos[3])
        entry_nivel.pack(pady=5)

        tk.Label(self.ventana_editar, text="Rol:").pack(pady=5)
        rol_var = tk.StringVar(value=datos[4])
        rol_menu = ttk.Combobox(self.ventana_editar, textvariable=rol_var, values=["admin", "user"])
        rol_menu.pack(pady=5)

        def guardar_cambios():
            nuevo_usuario = entry_usuario.get().strip()
            nueva_puntuacion = int(entry_puntuacion.get().strip())
            nuevo_nivel = int(entry_nivel.get().strip())
            nuevo_rol = rol_var.get().strip()

            if editar_jugador(datos[0], nuevo_usuario, nueva_puntuacion, nuevo_nivel, nuevo_rol):
                messagebox.showinfo("Éxito", "Jugador actualizado")
                self.ventana_editar.destroy()  # Cierra la ventana de edición
                self.abrir_gestion_jugadores()  # Regresa a la ventana de gestión de usuarios
            else:
                messagebox.showerror("Error", "No se pudo actualizar el jugador")

        tk.Button(self.ventana_editar, text="Guardar", command=guardar_cambios).pack(pady=10)
        tk.Button(self.ventana_editar, text="Cancelar", command=lambda: [self.ventana_editar.destroy(), self.abrir_gestion_jugadores()]).pack(pady=10)

    def eliminar_jugador_seleccionado(self):
        item = self.tree_gestion.focus()
        if not item:
            messagebox.showerror("Error", "No se ha seleccionado ningún jugador. Se regresará a la ventana de gestión.")
            self.ventana_gestion.destroy()
            self.abrir_gestion_jugadores()
            return
        datos = self.tree_gestion.item(item, "values")
        self.confirmar_eliminar_jugador(datos[0])


    def confirmar_eliminar_jugador(self, jugador_id):
        """
        Abre una ventana de confirmación para eliminar un jugador.
        """
        self.ventana_confirmar = tk.Toplevel(self.master)
        self.ventana_confirmar.title("Confirmar Eliminación")
        self.ventana_confirmar.geometry("300x150")
        centrar_ventana(self.ventana_confirmar, 300, 150)

        # Hacer que la ventana sea modal
        self.ventana_confirmar.grab_set()

        tk.Label(self.ventana_confirmar, text="¿Está seguro de que desea eliminar este jugador?").pack(pady=10)

        def eliminar():
            if eliminar_jugador(jugador_id):
                messagebox.showinfo("Éxito", "Jugador eliminado correctamente.")
                # Cierra la ventana de confirmación
                self.ventana_confirmar.destroy()
                # Cierra la ventana de gestión actual
                self.ventana_gestion.destroy()
                # Reabre la ventana de gestión de jugadores actualizada
                self.abrir_gestion_jugadores()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el jugador.")


        tk.Button(self.ventana_confirmar, text="Eliminar", command=eliminar).pack(side="left", padx=10, pady=10)
        tk.Button(self.ventana_confirmar, text="Cancelar", command=self.ventana_confirmar.destroy).pack(side="right", padx=10, pady=10)

    def abrir_gestion_partidas(self):
        item = self.tree_gestion.focus()
        if not item:
            messagebox.showerror("Error", "No se ha seleccionado ningún jugador. Se regresará a la ventana de gestión.")
            self.ventana_gestion.destroy()
            self.abrir_gestion_jugadores()
            return
        jugador_id = self.tree_gestion.item(item, "values")[0]
        self.gestionar_partidas(jugador_id)

    def gestionar_partidas(self, jugador_id):
        """
        Abre una ventana para gestionar las partidas de un jugador específico.
        """
        self.ventana_gestion_partidas = tk.Toplevel(self.master)
        self.ventana_gestion_partidas.title("Gestionar Partidas")
        self.ventana_gestion_partidas.geometry("600x400")
        centrar_ventana(self.ventana_gestion_partidas, 600, 400)

        # Crear el Treeview para mostrar las partidas
        tree = ttk.Treeview(self.ventana_gestion_partidas, columns=("ID", "Puntuación", "Nivel", "Fecha"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Puntuación", text="Puntuación")
        tree.heading("Nivel", text="Nivel")
        tree.heading("Fecha", text="Fecha")
        tree.pack(expand=True, fill="both")

        # Cargar las partidas del jugador
        partidas = obtener_historial_personal(jugador_id)
        for partida in partidas:
            tree.insert("", "end", values=partida)

        # Botón para eliminar la partida seleccionada
        def eliminar_partida_seleccionada():
            item = tree.focus()
            if not item:
                messagebox.showerror("Error", "Seleccione una partida para eliminar.")
                return
            partida_id = tree.item(item, "values")[0]
            if eliminar_partida(partida_id):
                messagebox.showinfo("Éxito", "Partida eliminada correctamente.")
                tree.delete(item)
                recalcular_puntuacion_maxima(jugador_id)
                # Una vez eliminada la partida, se cierra la ventana de gestión de partidas.
                self.ventana_gestion_partidas.destroy()
                # Retorna a la ventana de gestión de jugadores
                self.abrir_gestion_jugadores()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la partida.")


        # Botón para cerrar y regresar a la ventana de gestión de jugadores
        def cerrar_y_regresar():
            self.ventana_gestion_partidas.destroy()
            self.abrir_gestion_jugadores()  # Regresa a la ventana de gestión de jugadores

        tk.Button(self.ventana_gestion_partidas, text="Eliminar Partida", command=eliminar_partida_seleccionada).pack(pady=10)
        tk.Button(self.ventana_gestion_partidas, text="Cerrar", command=cerrar_y_regresar).pack(pady=10)

    def cerrar_sesion(self):
        """
        Cierra la sesión del usuario actual y vuelve al formulario de inicio de sesión.
        """
        self.usuario_actual = None
        if hasattr(self, "marco_menu"):
            self.marco_menu.destroy()
        self.crear_login()


def obtener_historial_personal(usuario_id):
    """
    Obtiene el historial de partidas de un usuario específico.
    """
    conexion = connect_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM jugadores WHERE id = %s", (usuario_id,))
    rol = cursor.fetchone()[0]
    if rol == "admin":
        return []  # Los administradores no tienen historial
    # Ordena por fecha descendente para mostrar la partida más reciente primero
    cursor.execute("SELECT id, puntuacion, nivel, mundo, fecha FROM partidas WHERE jugador_id = %s ORDER BY fecha DESC", (usuario_id,))
    historial = cursor.fetchall()
    cursor.close()
    conexion.close()
    return historial
