import flet as ft
from view.menu_admin_view import mostrar_pantalla_menu_admin
from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico 
from view.cambiar_contrasena_view import mostrar_pantalla_cambiar_contrasena

def mostrar_pantalla_login(page: ft.Page, repo):
    page.controls.clear()
    page.title = "BlueTech - Login"
    page.window_resizable = False 
    
    def manejar_login(e):
        nombre_login = (campo_usuario.value or "").strip()
        contrasena = (campo_contrasena.value or "").strip()

        if not nombre_login or not contrasena:
            mensaje.value = "Por favor, completa todos los campos."
            mensaje.color = ft.Colors.RED_400
            page.update()
            return

        boton_login.disabled = True
        page.update()

        usuario = repo.verificar_login(nombre_login, contrasena)

        if usuario is None:
            mensaje.value = "Usuario o contraseña no válidos."
            mensaje.color = ft.Colors.RED_400
            boton_login.disabled = False
            page.update()
            return

        #--- Seguridad ---
        if usuario.estado == 3 or usuario.num_registros == 0 or usuario.num_registros >= 500:
            page.controls.clear()
            mostrar_pantalla_cambiar_contrasena(page, repo, usuario)
            return

        usuario.num_registros += 1
        usuario.estado = 1
        repo.guardar_cambios()

        #--- Redirección ---
        page.controls.clear()
        if usuario.es_administrador():
            mostrar_pantalla_menu_admin(page, repo, usuario)
        elif usuario.es_trabajador():
            mostrar_pantalla_menu_trabajador(page, repo, usuario)
        elif usuario.es_tecnico():
            mostrar_pantalla_menu_tecnico(page, repo, usuario)
        else:
            mensaje.value = "Error: Rol no reconocido."
            mensaje.color = ft.Colors.RED_400
            boton_login.disabled = False
            page.update()

    campo_usuario = ft.TextField(
        label="Nombre de usuario",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        border_radius=12,
        on_submit=manejar_login 
    )

    campo_contrasena = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_PERSON_ROUNDED,
        border_radius=12,
        on_submit=manejar_login 
    )

    mensaje = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

    boton_login = ft.ElevatedButton(
        content=ft.Text("Acceder al Sistema"),
        icon=ft.Icons.LOGIN_ROUNDED,
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_800,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=manejar_login
    )

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src="img/avatar_usuario.png", width=120, height=120),
                ft.Text("Bienvenido", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Introduce tus credenciales para continuar", color=ft.Colors.BLUE_GREY_400),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                campo_usuario,
                campo_contrasena,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                boton_login,
                mensaje,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=40,
        width=450,
        height=600,
        shadow=ft.BoxShadow(
            blur_radius=20
        ),
    )

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src="img/fondo_login.png",
                fit="cover",
                expand=True,
            ),
            ft.Container(
                expand=True
            ),
            ft.Container(
                content=formulario,
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.padding.only(right=100),
            )
        ],
    )

    page.add(layout)