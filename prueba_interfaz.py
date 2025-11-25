import flet as ft
from modeloBlueTech import RepositorioCredenciales
from vista.login_view import mostrar_pantalla_login


def main(page: ft.Page):

    # Configuración básica de la ventana principal
    page.title = "BlueTech - Sistema de monitorización hospitalaria"
    page.window_width = 900
    page.window_height = 600
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#F0F4FF"

    # Crear el repositorio de credenciales (usa el JSON existente del modelo)
    repo = RepositorioCredenciales(ruta_usuarios="usuarios.json")

    # Mostrar la pantalla de inicio de sesión
    mostrar_pantalla_login(page, repo)


if __name__ == "__main__":
    ft.app(target=main)