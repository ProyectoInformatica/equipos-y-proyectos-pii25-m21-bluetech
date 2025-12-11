import flet as ft
from modeloBlueTech import RepositorioCredenciales
from vista.login_view import mostrar_pantalla_login


def main(page: ft.Page):

    # Configuración básica de la ventana principal
    page.title = "BlueTech - Sistema de monitorización hospitalaria" #titulo de la parte superior de la pestaña
    #tamaño inicial de apertura de la pestaña
    page.window_width = 900 #ancho
    page.window_height = 600 #alto
    #alinea todo el contenido de la página al centro
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#F0F4FF" #color por defecto para el fondo de la pestaña

    # Crear el repositorio de credenciales (usa el JSON existente del modelo)
    repo = RepositorioCredenciales(ruta_usuarios="usuarios.json")

    # Mostrar la pantalla de inicio de sesión
    mostrar_pantalla_login(page, repo)

#inicializar la app
if __name__ == "__main__":
    ft.app(target=main)