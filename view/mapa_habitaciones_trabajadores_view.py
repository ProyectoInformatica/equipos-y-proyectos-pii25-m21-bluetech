import flet as ft
import asyncio
from controller.mapa_habitaciones_controller import obtener_datos_mapa

#--- ESTILOS ---
COLOR_DISPONIBLE = "#A8D5BA"
COLOR_OCUPADO = "#F2A2A2"
COLOR_ALERTA = "#FF0000"
COLOR_PASILLO = "#EDF2F7"

habitaciones_parpadeo = []

def mostrar_pantalla_mapa_habitaciones_trabajadores(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador
    global habitaciones_parpadeo 
    
    page.clean()
    page.title = "Monitorización de Habitaciones"
    page.bgcolor = "#F8F9FA"

    #--- FUNCIÓN DE MENSAJE ---
    def mostrar_mensaje(texto):
        snack = ft.SnackBar(content=ft.Text(texto), bgcolor=ft.Colors.BLUE_700)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    #--- ELEMENTOS DE UI ---
    contenedor_plantas = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=30)

    #--- LÓGICA DE DETALLE ---
    def abrir_detalle(h_info):
        # Mismo modal de detalle que en admin
        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalle Habitación {h_info['id']}", weight="bold"),
            content=ft.Column([
                ft.Divider(),
                ft.Row([ft.Icon(ft.Icons.THERMOSTAT, color="orange"), ft.Text(f"Temperatura: {h_info['temperatura']}°C")]),
                ft.Row([ft.Icon(ft.Icons.WATER_DROP, color="blue"), ft.Text(f"Humedad: {h_info['humedad']}%")]),
                ft.Row([ft.Icon(ft.Icons.AIR, color="green"), ft.Text(f"CO2: {h_info['calidad_aire'].get('CO2', 0)} ppm")]),
            ], tight=True, spacing=15),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: (setattr(dlg, "open", False), page.update()))],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    #--- CONSTRUCCIÓN DE TARJETAS ---
    def crear_habitacion_estilo_mapa(h_info, rangos):
        id_hab = h_info["id"]
        estado_db = h_info["estado"]
        temp = h_info["temperatura"]
        hum = h_info["humedad"]
        co2 = h_info["calidad_aire"].get("CO2", 0)
        
        r_temp = rangos.get("temperatura", {"min": 20, "max": 30})
        r_hum = rangos.get("humedad", {"min": 34, "max": 40})
        max_co2 = rangos.get("calidad_aire", {}).get("CO2", {}).get("max", 500)

        fuera_de_rango = (temp < r_temp["min"] or temp > r_temp["max"] or 
                         hum < r_hum["min"] or hum > r_hum["max"] or co2 > max_co2)

        color_base = COLOR_DISPONIBLE if not fuera_de_rango else COLOR_OCUPADO
        
        container_hab = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{id_hab}", weight="bold", size=18),
                    ft.Icon(ft.Icons.ZOOM_IN, size=16, color="black45"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(f"{temp}°C | {hum}%", size=12, weight="w500"),
                ft.Row([
                    ft.Icon(ft.Icons.AIR, size=12, color="blue700"),
                    ft.Text(f"{co2} ppm", size=11, color="blue900", weight="bold"),
                ], spacing=5),
                ft.Text(f"Estado: {estado_db}", size=10),
            ], spacing=3),
            width=150, height=120,
            bgcolor=color_base,
            border=ft.border.all(1, "black26"),
            border_radius=10,
            padding=12,
            ink=True,
            on_click=lambda _: abrir_detalle(h_info),
            data={"color_original": color_base}
        )

        if fuera_de_rango and estado_db == "ocupado":
            habitaciones_parpadeo.append(container_hab)
        return container_hab

    def reconstruir_mapa():
        global habitaciones_parpadeo
        lista_hab, rangos = obtener_datos_mapa()
        habitaciones_parpadeo.clear()
        contenedor_plantas.controls.clear()
        
        num_plantas = (len(lista_hab) + 9) // 10
        
        for p in range(num_plantas):
            hab_planta = lista_hab[p*10 : (p+1)*10]
            fila_sup = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            for h in hab_planta[:5]: 
                fila_sup.controls.append(crear_habitacion_estilo_mapa(h, rangos))

            pasillo = ft.Container(
                content=ft.Text(f"PLANTA {p+1}", weight="bold", color="black45"),
                bgcolor=COLOR_PASILLO, height=40, width=800, alignment=ft.Alignment(0, 0)
            )

            fila_inf = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            for h in hab_planta[5:]: 
                fila_inf.controls.append(crear_habitacion_estilo_mapa(h, rangos))

            contenedor_plantas.controls.append(ft.Column([fila_sup, pasillo, fila_inf], horizontal_alignment="center"))
        page.update()

    #--- SIDEBAR ---
    sidebar = ft.Container(
        content=ft.Column([
            ft.Text("MAPA HOSPITAL", size=22, weight="bold", color="blue900"),
            ft.Divider(),
            
            #--- ÍNDICE ---
            ft.Text("Leyenda de estados:", weight="bold"),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Container(width=15, height=15, bgcolor=COLOR_DISPONIBLE, border_radius=3), ft.Text("Óptimo", size=12)]),
                    ft.Row([ft.Container(width=15, height=15, bgcolor=COLOR_OCUPADO, border_radius=3), ft.Text("Fuera de rango", size=12)]),
                    ft.Row([
                        ft.Container(width=15, height=15, bgcolor=COLOR_ALERTA, border_radius=3, shadow=ft.BoxShadow(blur_radius=5, color=COLOR_ALERTA)),
                        ft.Text("Alerta Crítica (Ocupada)", size=12, weight="bold")
                    ]),
                ], spacing=8),
                padding=ft.padding.only(bottom=10)
            ),
            
            ft.Divider(),
            ft.Container(expand=True),
            
            ft.ElevatedButton(
                "Actualizar", 
                icon=ft.Icons.REFRESH, 
                on_click=lambda _: (reconstruir_mapa(), mostrar_mensaje("Datos actualizados")), 
                width=250
            ),
            ft.TextButton(
                "Volver al Menú", 
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: mostrar_pantalla_menu_trabajador(page, repo, usuario)
            )
        ], spacing=10),
        width=280, padding=20, bgcolor="white",
        border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
        shadow=ft.BoxShadow(blur_radius=10, color="black12")
    )

    #--- TAREAS ASÍNCRONAS ---
    async def tarea_parpadeo():
        while True:
            try:
                if habitaciones_parpadeo:
                    actuales = list(habitaciones_parpadeo)
                    for h in actuales: h.bgcolor = COLOR_ALERTA
                    page.update()
                    await asyncio.sleep(0.5)
                    for h in actuales: h.bgcolor = h.data.get("color_original", COLOR_OCUPADO)
                    page.update()
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(1)
            except: break

    async def tarea_actualizacion_automatica():
        while True:
            try:
                await asyncio.sleep(10)
                reconstruir_mapa()
            except: break

    #--- DISEÑO FINAL ---
    page.add(ft.Row([sidebar, ft.Container(content=contenedor_plantas, expand=True, padding=20)], expand=True))
    
    reconstruir_mapa()
    page.run_task(tarea_parpadeo)
    page.run_task(tarea_actualizacion_automatica)