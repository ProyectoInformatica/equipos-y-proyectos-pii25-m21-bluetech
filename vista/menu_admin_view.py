import flet as ft
# from vista.gestion_usuarios_view import mostrar_pantalla_gestion_usuarios
# from vista.estado_salas_view import mostrar_pantalla_estado_salas
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "white"

def mostrar_pantalla_menu_admin(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    page.clean()

    def crear_boton(texto, icono, on_click=None):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icono, size=20),
                ft.Text(texto)
            ], alignment=ft.MainAxisAlignment.START),
            style=ft.ButtonStyle(
                bgcolor=COLOR_PRINCIPAL,
                color=COLOR_TEXTO,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            expand=True,
            on_click=on_click
        )

    # Botones con navegación
    boton_gestion_usuarios = crear_boton("Gestión de usuarios", ft.Icons.PEOPLE,
        #on_click=lambda e: mostrar_pantalla_gestion_usuarios(page, repo, usuario)
        )
    boton_estado_salas = crear_boton("Visualizar / cambiar estado de salas", ft.Icons.MEETING_ROOM,
        #on_click=lambda e: mostrar_pantalla_estado_salas(page, repo, usuario)
        )
    boton_parametros_sanidad = crear_boton("Consultar / cambiar parámetros de sanidad", ft.Icons.HEALTH_AND_SAFETY,
        #on_click=lambda e: mostrar_pantalla_parametros_sanidad(page, repo, usuario)
        )
    boton_cerrar_sesion = crear_boton("Cerrar sesión", ft.Icons.LOGOUT,
        on_click=lambda e: mostrar_pantalla_login(page, repo))

    tarjeta_menu = ft.Container(
        content=ft.Column([
            ft.Text(
                "🔷 Menú principal - Administrador",
                size=26,
                weight="bold",
                color=COLOR_PRINCIPAL
            ),
            ft.Row(
            controls=[
                    ft.Icon(ft.Icons.MANAGE_ACCOUNTS, color="grey"),
                    ft.Text(f"Usuario autenticado: {usuario.nombre_usuario}", size=16, italic=True, color="grey")
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Divider(),
            boton_gestion_usuarios,
            boton_estado_salas,
            boton_parametros_sanidad,
            ft.Divider(),
            boton_cerrar_sesion
        ], spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        width=600,
        height=500
    )

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
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