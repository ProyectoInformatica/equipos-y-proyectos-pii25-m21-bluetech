import flet as ft
# from vista.gestion_usuarios_view import mostrar_pantalla_gestion_usuarios
# from vista.estado_salas_view import mostrar_pantalla_estado_salas
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad


def mostrar_pantalla_menu_admin(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    # Limpia la página antes de dibujar el menú
    page.controls.clear()

    titulo = ft.Text(
        "Menú principal - Administrador",
        size=22,
        weight="bold"
    )

    info_usuario = ft.Text("Usuario autenticado: " + usuario.nombre_usuario)

    # Botones del menú de administrador
    boton_gestion_usuarios = ft.ElevatedButton(
        text="Gestión de usuarios",
        # on_click=lambda e: mostrar_pantalla_gestion_usuarios(page, repo, usuario)
    )

    boton_estado_salas = ft.ElevatedButton(
        text="Visualizar / cambiar estado de salas",
        # on_click=lambda e: mostrar_pantalla_estado_salas(page, repo, usuario)
    )

    boton_parametros_sanidad = ft.ElevatedButton(
        text="Consultar / cambiar parámetros de sanidad",
        # on_click=lambda e: mostrar_pantalla_parametros_sanidad(page, repo, usuario)
    )

    boton_cerrar_sesion = ft.ElevatedButton(
        text="Cerrar sesión",
        on_click=lambda e: mostrar_pantalla_login(page, repo)
    )

    layout = ft.Column(
        controls=[
            titulo,
            info_usuario,
            ft.Divider(),
            boton_gestion_usuarios,
            boton_estado_salas,
            boton_parametros_sanidad,
            ft.Divider(),
            boton_cerrar_sesion
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START
    )

    page.add(layout)
    page.update()
