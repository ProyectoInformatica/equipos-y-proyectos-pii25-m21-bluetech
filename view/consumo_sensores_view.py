import flet as ft
import threading
import time
from datetime import datetime
from controller.consumo_controller import (
    obtener_datos_consumo, 
    obtener_datos_graficos,
    toggle_simulacion,
    esta_simulando
)

COLOR_PRINCIPAL = ft.Colors.BLUE
COLOR_TEXTO = ft.Colors.WHITE
COLOR_ALERTA = ft.Colors.AMBER
COLOR_TEXTO_NORMAL = ft.Colors.BLACK

def mostrar_pantalla_consumo_sensores(page: ft.Page, usuario, on_volver):
    timer_running = [True]
    
    def cerrar_pagina():
        timer_running[0] = False
        if esta_simulando():
            toggle_simulacion()
    
    page.controls.clear()
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Controles UI
    stat_promedio = ft.Text("0.0 W", weight="bold", size=16, color=COLOR_PRINCIPAL)
    stat_min = ft.Text("0.0 W", size=14, color=COLOR_TEXTO_NORMAL)
    stat_max = ft.Text("0.0 W", size=14, color=COLOR_TEXTO_NORMAL)
    stat_tendencia = ft.Text("Estable", size=14, color=COLOR_TEXTO_NORMAL)
    texto_total = ft.Text("~0.0 W", size=28, weight="bold", color=COLOR_ALERTA)
    

    linea_datos = ft.LineChartData(
        data_points=[],
        stroke_width=3,
        color=ft.Colors.BLUE_500,
        curved=True, 
        stroke_cap_round=True,
        below_line_bgcolor="#1A2196F3" 
    )
    
    grafico_picos = ft.LineChart(
        data_series=[linea_datos],
        border=ft.border.only(
            bottom=ft.border.BorderSide(2, ft.Colors.GREY_300),
            left=ft.border.BorderSide(2, ft.Colors.GREY_300),
        ),
        left_axis=ft.ChartAxis(labels_size=30),
        bottom_axis=ft.ChartAxis(show_labels=False),
        tooltip_bgcolor=ft.Colors.BLUE_GREY,
        expand=True,
    )
    
    contenedor_grafico = ft.Container(
        content=grafico_picos, 
        width=400, 
        height=200, 
        padding=10,
        bgcolor=ft.Colors.WHITE
    )
    # =======================================================

    barras_container = ft.Column([], scroll=ft.ScrollMode.AUTO, height=150)
    lista_sensores = ft.Column([])
    
    def actualizar():
        try:
            sensores, total, stats = obtener_datos_consumo()
            puntos, barras = obtener_datos_graficos()
            
            # Actualizar Stats
            stat_promedio.value = f"{stats['promedio']:.2f} W"
            stat_min.value = f"{stats['min']:.2f} W"
            stat_max.value = f"{stats['max']:.2f} W"
            stat_tendencia.value = stats['tendencia']
            
            if "subiendo" in stats['tendencia']:
                stat_tendencia.color = ft.Colors.RED
            elif "bajando" in stats['tendencia']:
                stat_tendencia.color = ft.Colors.GREEN
            else:
                stat_tendencia.color = COLOR_TEXTO_NORMAL
            
            texto_total.value = f"~{total:.2f} W"
            
            # ACTUALIZAR DATOS DEL GRÁFICO
            if puntos:
                ultimos_puntos = puntos[-15:] # Mostrar los últimos 15 valores
                
                linea_datos.data_points = [
                    ft.LineChartDataPoint(i, p['y']) for i, p in enumerate(ultimos_puntos)
                ]
                
                # Ajuste dinámico de límites del eje Y
                valores_y = [p['y'] for p in ultimos_puntos]
                max_y = max(valores_y)
                min_y = min(valores_y)
                
                grafico_picos.max_y = max_y + (max_y * 0.2) if max_y > 0 else 10 
                grafico_picos.min_y = max(0, min_y - (min_y * 0.2))              
            
            # Actualizar Barras
            if barras:
                max_val = max(b['valor'] for b in barras) if barras else 1
                barras_container.controls = [
                    ft.Row([
                        ft.Text(b['nombre'].split()[0][:8], width=80, size=11, color=COLOR_TEXTO_NORMAL),
                        ft.ProgressBar(value=b['valor']/max_val if max_val > 0 else 0, width=150, color=COLOR_PRINCIPAL, bgcolor=ft.Colors.GREY_200),
                        ft.Text(f"{b['valor']:.2f}W", width=50, size=11, weight="bold", color=COLOR_TEXTO_NORMAL)
                    ]) for b in barras
                ]
            
            # Actualizar Lista de sensores
            if sensores:
                lista_sensores.controls = [
                    ft.Row([
                        ft.Icon(ft.Icons.BOLT, size=16, color=COLOR_PRINCIPAL),
                        ft.Text(s.nombre, expand=True, size=13, color=COLOR_TEXTO_NORMAL),
                        ft.Text(f"{s.w_actual:.2f}W", weight="bold", size=13, color=COLOR_PRINCIPAL)
                    ]) for s in sensores
                ]
            
            page.update()
        except Exception as e:
            print(f"Error actualización: {e}")
    
    # Configurar simulación 
    from model.consumo_model import simulador
    simulador.intervalo = 10.0
    
    if not esta_simulando():
        toggle_simulacion()
    
    # Thread de actualización
    def loop():
        while timer_running[0]:
            time.sleep(10)
            if timer_running[0] and esta_simulando():
                actualizar()
    
    threading.Thread(target=loop, daemon=True).start()
    
    page.add(
        ft.Stack([
            ft.Image(src="img/fondo.png", fit=ft.ImageFit.COVER),
            ft.Container(
                content=ft.Container(
                    width=800, height=680, padding=25, bgcolor=ft.Colors.WHITE, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK54),
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Consumo Energético IoT", size=24, weight="bold", color=COLOR_PRINCIPAL, expand=True),
                        ], alignment=ft.MainAxisAlignment.START), # Modificado para no esperar el texto derecho
                        
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, color=COLOR_TEXTO_NORMAL, size=18),
                            ft.Text(f"Usuario: {usuario.nombre_usuario if hasattr(usuario, 'nombre_usuario') else 'Admin'}", size=14, italic=True, color=COLOR_TEXTO_NORMAL),
                        ], spacing=5),
                        
                        ft.Divider(),
                        
                        ft.Row([
                            ft.Column([
                                ft.Container(
                                    bgcolor="#E3F2FD", border_radius=10, padding=10,
                                    content=ft.Column([
                                        ft.Text("Historial de Consumo (Picos)", weight="bold", size=14, color=COLOR_TEXTO_NORMAL),
                                        ft.Container(content=contenedor_grafico, border=ft.border.all(1, ft.Colors.GREY_400), border_radius=5)
                                    ])
                                ),
                                ft.Container(
                                    bgcolor="#E8F5E9", border_radius=10, padding=10,
                                    content=ft.Column([
                                        ft.Text("Consumo por Dispositivo", weight="bold", size=14, color=COLOR_TEXTO_NORMAL),
                                        barras_container
                                    ])
                                ),
                            ], expand=True, spacing=10),
                            
                            ft.Column([
                                ft.Container(
                                    bgcolor=COLOR_PRINCIPAL, border_radius=12, padding=15,
                                    content=ft.Column([
                                        ft.Text("⚡ ESTADÍSTICAS", weight="bold", color=COLOR_TEXTO, size=14),
                                        ft.Divider(color=ft.Colors.WHITE24),
                                        ft.Row([ft.Text("Promedio:", color=ft.Colors.WHITE70), stat_promedio], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Row([ft.Text("Mínimo:", color=ft.Colors.WHITE70), stat_min], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Row([ft.Text("Máximo:", color=ft.Colors.WHITE70), stat_max], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Row([ft.Text("Tendencia:", color=ft.Colors.WHITE70), stat_tendencia], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Divider(color=ft.Colors.WHITE24),
                                        ft.Text("Consumo Actual:", color=ft.Colors.WHITE70, size=12),
                                        texto_total
                                    ], spacing=8)
                                ),
                                ft.Container(
                                    border=ft.border.all(1, ft.Colors.GREY_200), border_radius=10, padding=10, expand=True,
                                    content=ft.Column([
                                        ft.Text("🔌 Dispositivos Activos", weight="bold", size=13, color=COLOR_TEXTO_NORMAL),
                                        ft.Divider(),
                                        lista_sensores
                                    ])
                                )
                            ], width=280, spacing=10)
                        ], expand=True, spacing=15),
                        
                        ft.Divider(),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=18), ft.Text("Volver al menú")], spacing=8),
                                style=ft.ButtonStyle(bgcolor=COLOR_PRINCIPAL, color=COLOR_TEXTO),
                                on_click=lambda e: [cerrar_pagina(), on_volver()]
                            )
                        ], alignment=ft.MainAxisAlignment.START)
                    ], spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                alignment=ft.alignment.center, expand=True
            )
        ], expand=True)
    )
    
    time.sleep(0.5)
    actualizar()