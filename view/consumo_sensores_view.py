import flet as ft
from controller.consumo_controller import obtener_datos_consumo

#Definición de estilos globales
COLOR_PRINCIPAL = ft.Colors.BLUE_800
COLOR_TEXTO = ft.Colors.WHITE
COLOR_ACCENTO = ft.Colors.AMBER_500

def mostrar_pantalla_consumo_sensores(page: ft.Page, usuario, on_volver):
    """Pantalla con métricas de consumo energético (IoT) optimizada."""
    
    page.controls.clear()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_900

    #--- OBTENCIÓN DE DATOS ---
    sensores, consumo_total = obtener_datos_consumo()

    #--- COMPONENTES VISUALES ---
    lista_sensores = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SENSORS, color=ft.Colors.WHITE70, size=20),
                    ft.Text(f"{s.nombre}:", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                    ft.Text(s.detalle, color=ft.Colors.BLUE_100),
                ], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                border_radius=8,
            )
            for s in sensores
        ]
    )

    panel_info_iot = ft.Container(
        bgcolor=COLOR_PRINCIPAL,
        border_radius=15,
        padding=25,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[COLOR_PRINCIPAL, ft.Colors.BLUE_900],
        ),
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.3, "black")),
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.SETTINGS_INPUT_COMPONENT, color=COLOR_ACCENTO),
                    ft.Text(
                        "MONITOR DE SISTEMA (IoT)",
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO,
                        size=18
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(color=ft.Colors.WHITE24),
                ft.Container(content=lista_sensores, height=200),
                ft.Divider(color=ft.Colors.WHITE24),
                ft.Row([
                    ft.Text("Consumo Total Estimado:", color=ft.Colors.WHITE70),
                    ft.Text(f"{consumo_total:.1f} W", size=22, weight=ft.FontWeight.BOLD, color=COLOR_ACCENTO),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            spacing=15,
        ),
    )

    #--- BOTÓN VOLVER ---
    btn_volver = ft.ElevatedButton(
        content=ft.Text("Volver al menú", color=COLOR_TEXTO),
        icon=ft.Icons.ARROW_BACK_IOS_NEW,
        style=ft.ButtonStyle(
            bgcolor=COLOR_PRINCIPAL,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=lambda _: on_volver(),
    )

    #--- TARJETA PRINCIPAL ---
    tarjeta = ft.Container(
        width=550,
        padding=40,
        bgcolor=ft.Colors.WHITE,
        border_radius=25,
        shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.4, "black")),
        content=ft.Column(
            controls=[
                ft.Image(src="img/logo.png", height=60, visible=True),
                ft.Text(
                    "Métricas de Energía",
                    size=28,
                    weight=ft.FontWeight.W_800,
                    color=ft.Colors.BLUE_GREY_900
                ),
                ft.Text(
                    "Análisis de consumo en tiempo real de los nodos activos.",
                    color=ft.Colors.BLUE_GREY_400,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                panel_info_iot,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                btn_volver,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    #--- LAYOUT FINAL ---
    layout = ft.Stack(
        expand=True,
        controls=[
            ft.Image(
                src="img/fondo.png",
                fit="cover", 
                width=page.window.width,
                height=page.window.height,
            ),
            ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)),
            ft.Container(
                content=tarjeta,
                alignment=ft.Alignment(0, 0),
            ),
        ],
    )

    page.add(layout)
    page.update()