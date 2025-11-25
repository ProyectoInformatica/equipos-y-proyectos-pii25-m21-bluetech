import flet as ft
# from vista.estado_salas_view import mostrar_pantalla_estado_salas
# from vista.parametros_sanidad_view import mostrar_pantalla_parametros_sanidad


def mostrar_pantalla_menu_trabajador(page: ft.Page, repo, usuario):
    from vista.login_view import mostrar_pantalla_login
    # Limpia la página antes de dibujar el menú
    page.controls.clear()

    titulo = ft.Text(
        "Menú principal - Trabajador",
        size=22,
        weight="bold"
    )

    info_usuario = ft.Text("Usuario autenticado: " + usuario.nombre_usuario)

    # Botones del menú de trabajador
    boton_estado_salas = ft.ElevatedButton(
        text="Visualizar / cambiar estado de salas",
        # on_click=lambda e: mostrar_pantalla_estado_salas(page, repo, usuario)
    )

    boton_parametros_sanidad = ft.ElevatedButton(
        text="Consultar parámetros de sanidad",
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