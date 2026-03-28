import flet as ft

from view.alertas_sistema_view import mostrar_pantalla_alertas_sistema
from view.alertas_usuario_tecnico_view import mostrar_pantalla_alertas_usuario

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "white"

def mostrar_pantalla_menu_tecnico(page: ft.Page, repo, usuario):
    from view.login_view import mostrar_pantalla_login
    page.clean()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None
    page.bgcolor = None

    # CREAR BOTONES
    def crear_boton(texto, icono, on_click=None):
        return ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(icono, size=20),
                    ft.Text(texto)
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            style=ft.ButtonStyle(
                bgcolor=COLOR_PRINCIPAL,
                color=COLOR_TEXTO,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            expand=True,
            on_click=on_click
        )

    # NAVEGACION
    def ir_alertas_sistema(e):
        mostrar_pantalla_alertas_sistema(
            page=page,
            repo=repo,
            usuario=usuario
        )

    def ir_alertas_usuario(e):
        mostrar_pantalla_alertas_usuario(
            page=page,
            repo=repo,
            usuario=usuario
        )

    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        mostrar_pantalla_login(page, repo)

    # BOTONES
    boton_alertas_sistema = crear_boton(
        "Alertas Sistema",
        ft.Icons.WARNING_AMBER,
        on_click=ir_alertas_sistema
    )

    boton_alertas_usuario = crear_boton(
        "Alertas Usuario",
        ft.Icons.NOTIFICATIONS_ACTIVE,
        on_click=ir_alertas_usuario
    )

    boton_cerrar_sesion = crear_boton(
        "Cerrar sesión",
        ft.Icons.LOGOUT,
        on_click=cerrar_sesion
    )

    # TARJETA MENU
    tarjeta_menu = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "🛠️ Menú principal - Técnico",
                    size=26,
                    weight="bold",
                    color=COLOR_PRINCIPAL
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.BADGE, color="grey"),
                        ft.Text(
                            f"Técnico: {usuario.nombre_usuario}",
                            size=16,
                            italic=True,
                            color="grey"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(),
                boton_alertas_sistema,
                boton_alertas_usuario,
                ft.Divider(),
                boton_cerrar_sesion
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="grey"
        ),
        width=500,
        height=420
    )

    # LAYOUT
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src="img/fondo.png",
                fit=ft.ImageFit.COVER,
                expand=True
            ),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    controls=[tarjeta_menu],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]
    )

    page.add(layout)
    page.update()