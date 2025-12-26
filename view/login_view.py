import flet as ft
from flet import Icons  # Iconos

from view.menu_admin_view import mostrar_pantalla_menu_admin
from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
from view.cambiar_contrasena_view import mostrar_pantalla_cambiar_contrasena


def mostrar_pantalla_login(page: ft.Page, repo):
    # Limpia la página
    page.controls.clear()

    # =========================
    # CAMPOS DE ENTRADA
    # =========================
    campo_usuario = ft.TextField(
        label="Nombre de usuario",
        prefix_icon=Icons.PERSON
    )

    campo_contrasena = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=Icons.LOCK
    )

    mensaje = ft.Text(value="", size=14)

    # =========================
    # MANEJO DEL LOGIN
    # =========================
    def manejar_login(e):
        nombre_login = (campo_usuario.value or "").strip()
        contrasena = (campo_contrasena.value or "").strip()

        # Validación básica
        if not nombre_login or not contrasena:
            mensaje.value = "Debes introducir usuario y contraseña."
            mensaje.color = "red"
            page.update()
            return

        # Login (rol detectado automáticamente)
        usuario = repo.verificar_login(nombre_login, contrasena)

        if usuario is None:
            mensaje.value = "Credenciales incorrectas."
            mensaje.color = "red"
            page.update()
            return

        # Forzar cambio de contraseña si aplica
        if usuario.estado == 3 or usuario.num_registros == 0 or usuario.num_registros >= 500:
            mostrar_pantalla_cambiar_contrasena(page, repo, usuario)
            return

        # Login normal
        usuario.num_registros += 1
        usuario.estado = 1
        repo.guardar_cambios()

        mensaje.value = "Inicio de sesión correcto."
        mensaje.color = "green"
        page.update()

        # Redirección por rol
        if usuario.es_administrador():
            mostrar_pantalla_menu_admin(page, repo, usuario)
            return

        if usuario.es_trabajador():
            mostrar_pantalla_menu_trabajador(page, repo, usuario)
            return

    # =========================
    # BOTÓN LOGIN
    # =========================
    boton_login = ft.ElevatedButton(
        text="Iniciar sesión",
        on_click=manejar_login,
        bgcolor="blue",
        color="white"
    )

    # =========================
    # DISEÑO (IGUAL AL TUYO)
    # =========================
    layout = ft.Stack(
        controls=[
            # Fondo
            ft.Image(
                src="img/fondo_login.png",
                fit=ft.ImageFit.COVER,
                expand=True
            ),

            # Contenedor principal
            ft.Container(
                left=600,
                top=0,
                right=0,
                bottom=0,
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(
                            src="img/avatar_usuario.png",
                            width=150,
                            height=150
                        ),

                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Inicio de sesión",
                                        size=20,
                                        weight="bold",
                                        color="blue"
                                    ),
                                    campo_usuario,
                                    campo_contrasena,
                                    boton_login,
                                    mensaje
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=10,
                            padding=20,
                            shadow=ft.BoxShadow(
                                blur_radius=15,
                                color="grey"
                            ),
                            width=450
                        )
                    ]
                )
            )
        ]
    )

    page.add(layout)
