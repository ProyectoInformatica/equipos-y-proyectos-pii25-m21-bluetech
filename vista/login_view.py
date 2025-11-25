import flet as ft
from modeloBlueTech import Rol
from flet import Icons
from vista.menu_admin_view import mostrar_pantalla_menu_admin
from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador


def mostrar_pantalla_login(page: ft.Page, repo):
    # Limpia la página por si venimos de otra vista
    page.controls.clear()

    #logo con encabezado
    logo = ft.Image(src="img/logo.png", width=80, height=80)
    encabezado = ft.Row(
        controls=[
            logo,
            # Título
            ft.Text("Sistema BlueTech", size=28, weight="bold", color="blue")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # contenedor (tipo div)
    # subtítulo
    subtitulo = ft.Text(
        "Inicio de sesión",
        size=16
    )

    # Campos de entrada
    campo_usuario = ft.TextField(label="Nombre de usuario", prefix_icon=Icons.PERSON)
    campo_contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=Icons.LOCK)
    campo_rol = ft.Dropdown(
        label="Rol",
        options=[
            ft.dropdown.Option("Administrador"),
            ft.dropdown.Option("Trabajador")
        ]
    )
    mensaje = ft.Text(value="", size=14)

    # Función de manejo del login
    def manejar_login(evento):
        nombre_login = campo_usuario.value.strip()
        contrasena = campo_contrasena.value.strip()
        rol_texto = campo_rol.value

        if len(nombre_login) == 0 or len(contrasena) == 0 or rol_texto is None:
            mensaje.value = "Debes introducir usuario, contraseña y seleccionar un rol."
            mensaje.color = "red"
            page.update()
            return

        rol_seleccionado = None
        if rol_texto == "Administrador":
            rol_seleccionado = Rol.ADMINISTRADOR
        elif rol_texto == "Trabajador":
            rol_seleccionado = Rol.TRABAJADOR

        usuario = repo.verificar_login(nombre_login, contrasena, rol_seleccionado)

        if usuario is None:
            mensaje.value = "Credenciales incorrectas. Inténtalo de nuevo."
            mensaje.color = "red"
        else:
            mensaje.value = "Inicio de sesión correcto."
            mensaje.color = "green"
            page.update()

            if usuario.es_administrador():
                mostrar_pantalla_menu_admin(page, repo, usuario)
                return
            if usuario.es_trabajador():
                mostrar_pantalla_menu_trabajador(page, repo, usuario)
                return

        page.update()

    # Botón de login
    boton_login = ft.ElevatedButton(text="Iniciar sesión", on_click=manejar_login)

    # Tarjeta visual del formulario
    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Inicio de sesión", size=20, weight="bold"),
                campo_usuario,
                campo_contrasena,
                campo_rol,
                boton_login,
                mensaje
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor="white",
        border_radius=10,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=15, color="grey"),
        width=400
    )

    # Layout con fondo usando Stack
    layout = ft.Stack(
        controls=[
            # Imagen de fondo
            ft.Image(
                src="img/fondo_login.png", 
                fit=ft.ImageFit.COVER,
                expand=True
            ),

            # Contenido centrado encima del fondo
            ft.Container(
                left=600, 
                top=0,
                right = 0,
                bottom = 0,
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,       # Centra verticalmente
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centra horizontalmente
                    controls=[
                        ft.Image(src="img/avatar_usuario.png", width=150, height=150),

                        #Bloque formulario
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Inicio de sesión", size=20, weight="bold"),
                                    campo_usuario,
                                    campo_contrasena,
                                    campo_rol,
                                    boton_login,
                                    mensaje
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=10,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=15, color="grey"),
                            width=450
                        )
                    ]
                )
            )
        ]
    )


    page.add(layout)
