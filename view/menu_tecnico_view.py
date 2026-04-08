import flet as ft
from view.alertas_sistema_view import mostrar_pantalla_alertas_sistema
from view.alertas_usuario_tecnico_view import mostrar_pantalla_alertas_usuario

COLOR_TECNICO = ft.Colors.BLUE_700
COLOR_FONDO_ICONO = ft.Colors.BLUE_50

def mostrar_pantalla_menu_tecnico(page: ft.Page, repo, usuario):
    from view.login_view import mostrar_pantalla_login
    
    page.controls.clear()
    page.title = "BlueTech - Panel Técnico"
    
    # --- FUNCIONES ---
    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        page.controls.clear()
        mostrar_pantalla_login(page, repo)

    def crear_tarjeta_accion(texto, descripcion, icono, on_click):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icono, color=COLOR_TECNICO, size=30),
                    bgcolor=COLOR_FONDO_ICONO,
                    padding=12,
                    border_radius=12,
                ),
                ft.Column([
                    ft.Text(texto, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(descripcion, size=12, color=ft.Colors.BLUE_GREY_400),
                ], spacing=1),
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=15,
            on_click=on_click,
            on_hover=lambda e: setattr(
                e.control,
                "bgcolor",
                ft.Colors.GREY_50 if e.data == "true" else None
            ) or e.control.update(),
        )

    tarjeta_menu = ft.Container(
        width=480,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=40,
        shadow=ft.BoxShadow(
            blur_radius=30,
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)
        ),
        content=ft.Column([
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BUILD_CIRCLE_ROUNDED, color=COLOR_TECNICO, size=40),
                    ft.Text("Panel Operativo", size=26, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(
                    f"Técnico: {usuario.nombre_usuario}",
                    size=14,
                    color=ft.Colors.GREY,
                    italic=True
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),

            crear_tarjeta_accion(
                "Alertas del Sistema", 
                "Revisar fallos en hardware y sensores",
                ft.Icons.DASHBOARD_CUSTOMIZE_OUTLINED,
                lambda _: (page.controls.clear(), mostrar_pantalla_alertas_sistema(page, repo, usuario))
            ),

            ft.Container(height=5),

            crear_tarjeta_accion(
                "Mis Notificaciones", 
                "Alertas asignadas y mensajes de usuario",
                ft.Icons.NOTIFICATIONS_PAUSED_OUTLINED,
                lambda _: (page.controls.clear(), mostrar_pantalla_alertas_usuario(page, repo, usuario))
            ),

            ft.Divider(height=40),

            ft.TextButton(
                "Cerrar Sesión",
                icon=ft.Icons.POWER_SETTINGS_NEW,
                on_click=cerrar_sesion,
                style=ft.ButtonStyle(color=ft.Colors.RED_400)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit="cover", expand=True),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                alignment=ft.Alignment.CENTER,
                content=tarjeta_menu
            )
        ], expand=True)
    )