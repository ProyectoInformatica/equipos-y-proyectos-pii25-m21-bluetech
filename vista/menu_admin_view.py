import flet as ft
# from vista.gestion_usuarios_view import mostrar_pantalla_gestion_usuarios
# from vista.estado_salas_view import mostrar_pantalla_estado_salas
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad


def mostrar_pantalla_menu_admin(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    page.controls.clear()

    # Campos visuales
    titulo = ft.Text(
        "🔷 Menú principal - Administrador",
        size=26,
        weight="bold",
        color="blue"
    )

    info_usuario = ft.Text(
        f"👤 Usuario autenticado: {usuario.nombre_usuario}",
        size=16,
        italic=True,
        color="grey"
    )

    def crear_boton(texto, icono, on_click=None):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icono, size=20),
                ft.Text(texto)
            ], alignment=ft.MainAxisAlignment.START),
            style=ft.ButtonStyle(
                bgcolor="blue",
                color="white",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            expand=True,
            on_click=on_click
        )

    # Botones
    boton_gestion_usuarios = crear_boton("Gestión de usuarios", ft.Icons.PEOPLE)
    boton_estado_salas = crear_boton("Visualizar / cambiar estado de salas", ft.Icons.MEETING_ROOM)
    boton_parametros_sanidad = crear_boton("Consultar / cambiar parámetros de sanidad", ft.Icons.HEALTH_AND_SAFETY)
    boton_cerrar_sesion = crear_boton("Cerrar sesión", ft.Icons.LOGOUT, on_click=lambda e: mostrar_pantalla_login(page, repo))

    # Tarjeta de menú
    tarjeta_menu = ft.Container(
        content=ft.Column([
            boton_gestion_usuarios,
            boton_estado_salas,
            boton_parametros_sanidad,
            ft.Divider(),
            boton_cerrar_sesion
        ], spacing=15),
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        width=450
    )

    # Layout con fondo usando Stack
    layout = ft.Stack(
        controls=[
            # Imagen de fondo
            ft.Image(
                src="img/fondo.png",  # Asegúrate de que esta ruta sea correcta
                fit=ft.ImageFit.COVER,
                expand=True
            ),

            # Contenido centrado encima del fondo
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column([
                    titulo,
                    info_usuario,
                    tarjeta_menu
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30)
            )
        ]
    )

    page.add(layout)
    page.update()
