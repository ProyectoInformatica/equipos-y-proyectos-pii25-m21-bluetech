import flet as ft


COLOR_PRINCIPAL = "blue"  # mismo color que los menús
COLOR_TEXTO = "white"


def mostrar_pantalla_consumo_sensores(page: ft.Page, usuario, on_volver):
    """Pantalla con métricas (simuladas) de consumo energético de sensores.

    NOTA: Los valores son fijos (simulación) hasta integrar sensores reales.
    """

    # Limpia la página
    page.controls.clear()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = None
    page.bgcolor = None

    # ---- Valores simulados (FIJOS) ----
    sensores = [
        {"nombre": "ESP32 + CAM (OV2640)", "detalle": "~2.0 W (Peak)", "w": 2.0},
        {"nombre": "DHT11", "detalle": "~0.1 W", "w": 0.1},
        {"nombre": "MQ-2 (Humo)", "detalle": "~1.6 W", "w": 1.6},
        {"nombre": "HC-SR04 (Distancia)", "detalle": "~0.2 W", "w": 0.2},
        {"nombre": "Ventilador 5V + LEDs", "detalle": "~1.5 W", "w": 1.5},
        {"nombre": "Motor DC 12V", "detalle": "~2.4 W", "w": 2.4},
    ]

    consumo_total = sum(s["w"] for s in sensores)

    # ---- Panel azul (similar a la captura) ----
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
                        f"• {s['nombre']}: {s['detalle']}",
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
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.BADGE, color="grey"),
                        ft.Text(
                            f"Usuario autenticado: {usuario.nombre_usuario}",
                            size=16,
                            italic=True,
                            color="grey",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
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

    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER, expand=True),
            ft.Container(expand=True, alignment=ft.alignment.center, content=tarjeta),
        ],
    )

    page.add(layout)
    page.update()
