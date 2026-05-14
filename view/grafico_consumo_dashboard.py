import flet as ft
import flet_charts as fc
import threading
import time

from controller.consumo_controller import (
    obtener_datos_graficos,
    obtener_datos_consumo,
    toggle_simulacion,
    esta_simulando
)


def crear_panel_grafico_picos(page: ft.Page, altura=190):
    Y_MIN_BASE = 1.3
    Y_MAX_BASE = 1.9

    UMBRAL_NORMAL = 1.75
    UMBRAL_VIGILANCIA = 1.90

    COLOR_ESP32 = ft.Colors.INDIGO_400
    COLOR_DHT = ft.Colors.TEAL_400
    COLOR_MQ2 = ft.Colors.ORANGE_400
    COLOR_LEDS = ft.Colors.PURPLE_400

    COLOR_NORMAL = ft.Colors.GREEN_700
    COLOR_VIGILANCIA = ft.Colors.AMBER_700
    COLOR_CRITICO = ft.Colors.RED_600

    COLOR_NORMAL_BG = ft.Colors.GREEN_50
    COLOR_VIGILANCIA_BG = ft.Colors.AMBER_50
    COLOR_CRITICO_BG = ft.Colors.RED_50

    COLOR_BORDE = ft.Colors.GREY_200
    COLOR_TEXTO = ft.Colors.GREY_800
    COLOR_TEXTO_SUAVE = ft.Colors.GREY_500
    COLOR_FONDO_INTERIOR = "#FBFCFE"

    texto_valor_actual = ft.Text(
        "--.-- W",
        size=16,
        weight=ft.FontWeight.W_600,
        color=COLOR_TEXTO,
    )

    texto_etiqueta_estado = ft.Text(
        "Estado:",
        size=11,
        color=COLOR_TEXTO_SUAVE,
        weight=ft.FontWeight.W_500,
    )

    estado_actual_texto = ft.Text(
        "Sin datos",
        size=10,
        weight=ft.FontWeight.W_600,
        color=COLOR_TEXTO,
    )

    estado_actual_chip = ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=ft.Colors.GREY_100,
        content=estado_actual_texto,
    )

    cabecera_estado = ft.Row(
        [
            ft.Row(
                [
                    texto_etiqueta_estado,
                    estado_actual_chip,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            texto_valor_actual,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    grafico_picos = fc.LineChart(
        data_series=[],
        min_y=Y_MIN_BASE,
        max_y=Y_MAX_BASE,
        interactive=True,
        tooltip=fc.LineChartTooltip(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border_side=ft.BorderSide(width=1, color=ft.Colors.GREY_300),
            fit_inside_horizontally=True,
            fit_inside_vertically=True,
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            margin=8,
            max_width=95,
            show_on_top_of_chart_box_area=True,
        ),
        border=ft.Border(
            bottom=ft.BorderSide(width=1.0, color=ft.Colors.GREY_300),
            left=ft.BorderSide(width=1.0, color=ft.Colors.GREY_300),
        ),
        left_axis=fc.ChartAxis(show_labels=False),
        bottom_axis=fc.ChartAxis(show_labels=False),
        expand=True,
    )

    label_y_1 = ft.Text("1.9", size=10, color=COLOR_TEXTO_SUAVE)
    label_y_2 = ft.Text("1.7", size=10, color=COLOR_TEXTO_SUAVE)
    label_y_3 = ft.Text("1.5", size=10, color=COLOR_TEXTO_SUAVE)
    label_y_4 = ft.Text("1.3", size=10, color=COLOR_TEXTO_SUAVE)

    columna_valores_y = ft.Container(
        width=45,
        padding=ft.padding.only(top=6, bottom=8, right=8),
        content=ft.Column(
            [
                label_y_1,
                label_y_2,
                label_y_3,
                label_y_4,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            expand=True,
        ),
    )

    titulo_leyenda = ft.Text(
        "Consumo simulado",
        size=10,
        weight=ft.FontWeight.W_600,
        color=COLOR_TEXTO_SUAVE,
    )

    lista_sensores_leyenda = ft.Column(
        spacing=4,
        tight=True,
    )

    panel_leyenda = ft.Container(
        width=190,
        padding=ft.padding.only(left=12, top=2, bottom=4),
        border=ft.border.only(left=ft.BorderSide(1, ft.Colors.GREY_100)),
        content=ft.Column(
            [
                titulo_leyenda,
                lista_sensores_leyenda,
            ],
            spacing=8,
            expand=True,
        ),
    )

    area_grafico = ft.Container(
        expand=True,
        padding=ft.padding.only(left=2, right=8, top=2, bottom=4),
        content=ft.Row(
            [
                ft.Row(
                    [
                        columna_valores_y,
                        ft.Container(expand=True, content=grafico_picos),
                    ],
                    spacing=0,
                    expand=True,
                ),
                panel_leyenda,
            ],
            spacing=0,
            expand=True,
        ),
    )

    contenedor_grafico = ft.Container(
        height=altura,
        bgcolor=COLOR_FONDO_INTERIOR,
        border=ft.border.all(1, COLOR_BORDE),
        border_radius=16,
        padding=12,
        shadow=ft.BoxShadow(
            blur_radius=6,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 1),
        ),
        content=ft.Column(
            [
                cabecera_estado,
                area_grafico,
            ],
            spacing=8,
            expand=True,
        ),
    )

    activo = [True]

    def clasificar_estado(valor_actual):
        if valor_actual < UMBRAL_NORMAL:
            return "Normal", COLOR_NORMAL, COLOR_NORMAL_BG
        elif valor_actual < UMBRAL_VIGILANCIA:
            return "Vigilancia", COLOR_VIGILANCIA, COLOR_VIGILANCIA_BG
        else:
            return "Crítico", COLOR_CRITICO, COLOR_CRITICO_BG

    def obtener_color_sensor(nombre):
        if nombre == "ESP32":
            return COLOR_ESP32
        elif nombre == "DHT11":
            return COLOR_DHT
        elif nombre == "MQ-2":
            return COLOR_MQ2
        elif nombre == "3 LEDs activos":
            return COLOR_LEDS
        else:
            return ft.Colors.GREY_400

    def actualizar_leyenda_sensores(sensores):
        lista_sensores_leyenda.controls = [
            ft.Row(
                [
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=obtener_color_sensor(sensor.nombre),
                    ),
                    ft.Text(
                        sensor.nombre,
                        size=9,
                        color=ft.Colors.GREY_600,
                        expand=True,
                        no_wrap=True,
                    ),
                    ft.Text(
                        f"{sensor.w_actual:.2f} W",
                        size=10,
                        color=COLOR_TEXTO,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            for sensor in sensores
        ]

    def actualizar():
        try:
            puntos, _ = obtener_datos_graficos()
            sensores, total, _ = obtener_datos_consumo()

            if puntos:
                ultimos_puntos = puntos[-20:]
                ultimo_valor = float(ultimos_puntos[-1]["y"])

                estado, color_estado, color_fondo_estado = clasificar_estado(ultimo_valor)
                estado_actual_texto.value = estado
                estado_actual_texto.color = color_estado
                estado_actual_chip.bgcolor = color_fondo_estado
                texto_valor_actual.value = f"{ultimo_valor:.2f} W"

                valores_y = [float(p["y"]) for p in ultimos_puntos]
                min_real = min(valores_y)
                max_real = max(valores_y)

                margen = 0.08
                min_dinamico = min_real - margen
                max_dinamico = max_real + margen

                if max_dinamico - min_dinamico < 0.35:
                    centro = (max_dinamico + min_dinamico) / 2
                    min_dinamico = centro - 0.18
                    max_dinamico = centro + 0.18

                grafico_picos.min_y = min_dinamico
                grafico_picos.max_y = max_dinamico

                rango = grafico_picos.max_y - grafico_picos.min_y
                label_y_1.value = f"{grafico_picos.max_y:.1f}"
                label_y_2.value = f"{(grafico_picos.max_y - rango / 3):.1f}"
                label_y_3.value = f"{(grafico_picos.max_y - 2 * rango / 3):.1f}"
                label_y_4.value = f"{grafico_picos.min_y:.1f}"

                puntos_grafico = []

                for i, p in enumerate(ultimos_puntos):
                    valor_y = float(p["y"])
                    puntos_grafico.append(
                        fc.LineChartDataPoint(
                            x=float(i),
                            y=valor_y,
                            show_tooltip=True,
                            tooltip=f"{valor_y:.2f} W",
                        )
                    )

                serie_consumo = fc.LineChartData(
                    points=puntos_grafico,
                    stroke_width=2,
                    color=ft.Colors.BLUE_500,
                    curved=True,
                    curve_smoothness=0.30,
                    rounded_stroke_cap=True,
                    rounded_stroke_join=True,
                    below_line_gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=[
                            ft.Colors.with_opacity(0.14, ft.Colors.BLUE_500),
                            ft.Colors.with_opacity(0.02, ft.Colors.BLUE_500),
                        ],
                    ),
                    shadow=ft.BoxShadow(
                        blur_radius=3,
                        spread_radius=0,
                        color=ft.Colors.with_opacity(0.06, ft.Colors.BLUE_500),
                        offset=ft.Offset(0, 1),
                    ),
                )

                grafico_picos.data_series = [serie_consumo]

            actualizar_leyenda_sensores(sensores)
            page.update()

        except Exception as e:
            print(f"Error gráfico dashboard: {e}")

    if not esta_simulando():
        toggle_simulacion()

    def loop():
        while activo[0]:
            time.sleep(2)
            if activo[0] and esta_simulando():
                actualizar()

    threading.Thread(target=loop, daemon=True).start()

    time.sleep(0.5)
    actualizar()

    return contenedor_grafico