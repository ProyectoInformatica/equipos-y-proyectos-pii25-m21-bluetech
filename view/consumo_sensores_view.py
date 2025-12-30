import flet as ft

from controller.consumo_controller import obtener_datos_consumo

COLOR_PRINCIPAL = "blue"
COLOR_TEXTO = "white"

def mostrar_pantalla_consumo_sensores(page: ft.Page, usuario, on_volver):
    """Pantalla con métricas simuladas de consumo energético (MVC)."""

    # Limpia la página
    page.controls.clear()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None
    page.bgcolor = None

    # =========================
    # DATOS (VIENEN DEL CONTROLLER)
    # =========================
    sensores, consumo_total = obtener_datos_consumo()

    # =========================
    # PANEL AZUL (DISEÑO IGUAL)
    # =========================
    panel_sensores = ft.Container(
        bgcolor=COLOR_PRINCIPAL,
        border_radius=12,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    "MONITOR DE SISTEMA (IoT)",
                    weight="bold",
                    color=COLOR_TEXTO,
                    size=16,
                ),
                ft.Divider(color="white54", thickness=1),

                *[
                    ft.Text(
                        f"• {s.nombre}: {s.detalle}",
                        color="white",
                        size=13,
                    )
                    for s in sensores
                ],

                ft.Divider(color="white54", thickness=1),
                ft.Text(
                    f"Consumo Total Est.: ~{consumo_total:.1f} W",
                    weight="bold",
                    color="amber",
                    size=14,
                ),
            ],
            spacing=5,
        ),
    )

    # =========================
    # BOTÓN VOLVER (IGUAL)
    # =========================
    btn_volver = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ARROW_BACK, size=18),
                ft.Text("Volver al menú"),
            ],
            tight=True,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            bgcolor=COLOR_PRINCIPAL,
            color=COLOR_TEXTO,
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=lambda e: on_volver(),
    )

    # =========================
    # TARJETA PRINCIPAL (IGUAL)
    # =========================
    tarjeta = ft.Container(
        width=700,
        height=560,
        padding=30,
        bgcolor="white",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color="grey"),
        content=ft.Column(
            controls=[
                ft.Text(
                    "🔷 Consumo energético (sensores)",
                    size=26,
                    weight="bold",
                    color=COLOR_PRINCIPAL,
                ),
                ft.Divider(),

                panel_sensores,

                ft.Divider(),
                ft.Row([btn_volver], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    # =========================
    # LAYOUT FINAL (IGUAL)
    # =========================
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src="img/fondo.png",
                fit=ft.ImageFit.COVER,
                expand=True
            ),
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=tarjeta
            ),
        ],
    )

    page.add(layout)
    page.update()
