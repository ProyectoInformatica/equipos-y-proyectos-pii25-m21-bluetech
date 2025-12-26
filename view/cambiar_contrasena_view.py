# vista/cambiar_contrasena_view.py
import flet as ft
import hashlib


def mostrar_pantalla_cambiar_contrasena(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    # Limpia la página
    page.clean()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None
    page.bgcolor = None

    # Nuevo campo: contraseña temporal
    campo_temporal = ft.TextField(
        label="Contraseña temporal",
        password=True,
        can_reveal_password=True,
        width=320,
        prefix_icon=ft.Icons.KEY
    )

    campo_nueva = ft.TextField(
        label="Nueva contraseña",
        password=True,
        can_reveal_password=True,
        width=320,
        prefix_icon=ft.Icons.LOCK
    )

    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        width=320,
        prefix_icon=ft.Icons.LOCK
    )

    mensaje = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

    btn_guardar = ft.ElevatedButton(
        "Guardar nueva contraseña",
        bgcolor="blue",
        color="white",
        width=320,
        height=45
    )

    def manejar_guardar(e):
        temp = campo_temporal.value or ""
        p1 = campo_nueva.value or ""
        p2 = campo_confirmar.value or ""

        if temp.strip() == "" or p1.strip() == "" or p2.strip() == "":
            mensaje.value = "Rellena los 3 campos."
            mensaje.color = "red"
            page.update()
            return

        # Validar contraseña temporal contra el hash actual del usuario
        temp_hash = hashlib.sha256(temp.encode()).hexdigest()
        if temp_hash != usuario.contrasena_hash:
            mensaje.value = "La contraseña temporal es incorrecta."
            mensaje.color = "red"
            page.update()
            return

        if p1 != p2:
            mensaje.value = "Las contraseñas no coinciden."
            mensaje.color = "red"
            page.update()
            return

        # Guardar nueva contraseña (hash) + reset de control
        try:
            usuario.contrasena_hash = hashlib.sha256(p1.encode()).hexdigest()
            usuario.num_registros = 1
            usuario.estado = 1
            repo.guardar_cambios()
        except Exception:
            mensaje.value = "No se pudo actualizar la contraseña."
            mensaje.color = "red"
            page.update()
            return

        # Redirige automáticamente al menú tras cambiarla
        if usuario.rol == "administrador":
            mostrar_pantalla_menu_admin(page, repo, usuario)
        else:
            mostrar_pantalla_menu_trabajador(page, repo, usuario)

    btn_guardar.on_click = manejar_guardar

    # === TARJETA (DISEÑO AJUSTADO) ===
    tarjeta = ft.Container(
        content=ft.Column(
            [
                ft.Text("Cambio de contraseña", size=26, weight="bold", color="blue"),
                ft.Text(
                    f"Usuario: {usuario.nombre_usuario}",
                    size=14,
                    italic=True,
                    color="grey",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Introduce tu contraseña temporal y define una nueva contraseña.",
                    size=13,
                    color="grey",
                    text_align=ft.TextAlign.CENTER
                ),
                campo_temporal,   # nuevo
                campo_nueva,
                campo_confirmar,
                btn_guardar,
                mensaje,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        width=420,
        height=440,  # ajustada para 3 campos (sin tarjeta enorme)
    )

    # === FONDO + POSICIÓN TARJETA (MÁS A LA DERECHA) ===
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo_login.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=120),
                content=tarjeta
            ),
        ],
    )

    page.add(layout)
    page.update()
