import flet as ft
from view.login_view import mostrar_pantalla_login
from controller.usuarios_controller import repo

def main(page: ft.Page):
    page.title = "BlueTech - Sistema de monitorización hospitalaria"
    page.window_width = 900
    page.window_height = 600
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#F0F4FF"

    # Mostrar login
    mostrar_pantalla_login(page, repo)

if __name__ == "__main__":
    ft.app(target=main)
