import flet as ft
import hashlib

def mostrar_pantalla_cambiar_contrasena(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    from view.menu_tecnico_view import mostrar_pantalla_menu_tecnico

    page.controls.clear()
    page.title = "BlueTech - Cambiar Contraseña"

    #--- CAMPOS ---
    campo_temporal = ft.TextField(
        label="Contraseña temporal",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.KEY_ROUNDED,
        border_radius=12,
        bgcolor=ft.Colors.WHITE
    )

    campo_nueva = ft.TextField(
        label="Nueva contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_RESET_ROUNDED,
        border_radius=12,
        bgcolor=ft.Colors.WHITE
    )

    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
        border_radius=12,
        bgcolor=ft.Colors.WHITE
    )

    mensaje = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

    #--- LÓGICA ---
    def manejar_cambio(e):
        temp = (campo_temporal.value or "").strip()
        p1 = (campo_nueva.value or "").strip()
        p2 = (campo_confirmar.value or "").strip()

        if not all([temp, p1, p2]):
            mensaje.value = "Completa todos los campos."
            mensaje.color = ft.Colors.RED_400
            page.update()
            return

        #Verificación con el atributo del modelo: contrasena_hash
        if hashlib.sha256(temp.encode()).hexdigest() != usuario.contrasena_hash:
            mensaje.value = "La contraseña temporal es incorrecta."
            mensaje.color = ft.Colors.RED_400
            page.update()
            return

        if p1 != p2:
            mensaje.value = "Las contraseñas nuevas no coinciden."
            mensaje.color = ft.Colors.RED_400
            page.update()
            return

        try:
            #Actualizamos el hash y el estado en el objeto
            usuario.contrasena_hash = hashlib.sha256(p1.encode()).hexdigest()
            usuario.estado = 1 
            usuario.num_registros = 1
            repo.guardar_cambios()

            #Redirección según rol
            page.controls.clear()
            if usuario.es_administrador():
                mostrar_pantalla_menu_admin(page, repo, usuario)
            elif usuario.es_trabajador():
                mostrar_pantalla_menu_trabajador(page, repo, usuario)
            elif usuario.es_tecnico():
                mostrar_pantalla_menu_tecnico(page, repo, usuario)
            
        except Exception as ex:
            mensaje.value = f"Error al guardar: {str(ex)}"
            page.update()

    #--- BOTÓN ---
    boton_guardar = ft.ElevatedButton(
        content=ft.Text("Actualizar Contraseña"),
        icon=ft.Icons.SAVE_ROUNDED,
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_800,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=manejar_cambio
    )

    #--- FORMULARIO ---
    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src="img/avatar_usuario.png", width=120, height=120),
                ft.Text("Seguridad", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Debes actualizar tu contraseña para continuar", color=ft.Colors.BLUE_GREY_400, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                campo_temporal,
                campo_nueva,
                campo_confirmar,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                boton_guardar,
                mensaje,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=40,
        width=450,
        height=650, 
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK26),
    )

    #--- LAYOUT ---
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src="img/fondo_login.png",
                fit="cover",
                expand=True,
            ),
            ft.Container(
                content=formulario,
                alignment=ft.Alignment(1, 0), 
                padding=ft.padding.only(right=100),
            )
        ],
    )

    page.add(layout)
    page.update()