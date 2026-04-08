import flet as ft
import asyncio
from controller.mapa_habitaciones_controller import obtener_datos_mapa

#--- ESTILOS DEL MAPA ---
COLOR_DISPONIBLE = "#A8D5BA"
COLOR_OCUPADO = "#F2A2A2"
COLOR_ALERTA = "#FF0000"
COLOR_PASILLO = "#EDF2F7"

def mostrar_pantalla_menu_trabajador(page: ft.Page, repo, usuario):
    #Imports diferidos
    from view.login_view import mostrar_pantalla_login
    from view.estado_salas_view import mostrar_pantalla_estado_salas
    from view.mapa_habitaciones_trabajadores_view import mostrar_pantalla_mapa_habitaciones_trabajadores
    from view.valores_comparativos_trabajadores_view import mostrar_pantalla_parametros_sanidad_trabajador
    from view.consumo_sensores_view import mostrar_pantalla_consumo_sensores

    page.clean()
    page.title = "BlueTech - Panel Operativo"
    page.bgcolor = "#F0F2F5"
    page.padding = 0

    habitaciones_parpadeo = []
    contenedor_mapa_vivo = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=20)

    #--- NAVEGACIÓN ---
    def navegar(func):
        page.clean()
        func()

    def cerrar_sesion(e):
        usuario.estado = 2
        repo.guardar_cambios()
        navegar(lambda: mostrar_pantalla_login(page, repo))

    #--- LÓGICA DEL MAPA INTEGRADO ---
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
                ft.Text(f"{id_hab}", weight="bold", size=15),
                ft.Text(f"{temp}°C | {hum}%", size=10),
                ft.Row([ft.Icon(ft.Icons.AIR, size=10), ft.Text(f"{co2}", size=9)], spacing=2),
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
            width=115, height=90,
            bgcolor=color_base,
            border_radius=10,
            padding=8,
            data={"color_original": color_base}
        )

        if fuera_de_rango and estado_db == "ocupado":
            habitaciones_parpadeo.append(container_hab)
        return container_hab

    def reconstruir_mapa_dashboard():
        lista_hab, rangos = obtener_datos_mapa()
        habitaciones_parpadeo.clear()
        contenedor_mapa_vivo.controls.clear()
        
        num_plantas = (len(lista_hab) + 9) // 10
        for p in range(num_plantas):
            hab_planta = lista_hab[p*10 : (p+1)*10]
            fila_sup = ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            fila_inf = ft.Row(spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            
            for i, h in enumerate(hab_planta):
                (fila_sup if i < 5 else fila_inf).controls.append(crear_habitacion_estilo_mapa(h, rangos))

            pasillo = ft.Container(
                content=ft.Text(f"PLANTA {p+1}", size=11, weight="bold", color="black45"),
                bgcolor=COLOR_PASILLO, height=30, width=650, 
                alignment=ft.Alignment(0, 0), border_radius=5
            )
            contenedor_mapa_vivo.controls.append(ft.Column([fila_sup, pasillo, fila_inf], horizontal_alignment="center"))
        page.update()

    #--- SIDEBAR ---
    sidebar = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Image(src="img/avatar_usuario.png", width=45, height=45, border_radius=25),
                ft.Column([
                    ft.Text(f"{usuario.nombre_usuario}", size=16, weight="bold"),
                    ft.Text("Personal Operativo", size=12, color="grey600"),
                ], spacing=1)
            ], spacing=10),
            
            ft.Divider(height=40, color="transparent"),
            
            ft.Text("HERRAMIENTAS", size=11, color="grey500", weight="bold"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DASHBOARD_ROUNDED, color="blue"), 
                title=ft.Text("Dashboard"), 
                selected=True
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.MAP_OUTLINED), 
                title=ft.Text("Mapa de Hospital"),
                on_click=lambda _: navegar(lambda: mostrar_pantalla_mapa_habitaciones_trabajadores(page, repo, usuario))
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.MEETING_ROOM_OUTLINED), 
                title=ft.Text("Estado de Salas"),
                on_click=lambda _: navegar(lambda: mostrar_pantalla_estado_salas(page, repo, usuario, origen="trabajador"))
            ),
            
            ft.Divider(height=20, color="transparent"),

            ft.Text("CONSULTAS", size=11, color="grey500", weight="bold"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.HEALTH_AND_SAFETY_OUTLINED), 
                title=ft.Text("Parámetros Sanidad"),
                on_click=lambda _: navegar(lambda: mostrar_pantalla_parametros_sanidad_trabajador(page, repo, usuario))
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BOLT_OUTLINED), 
                title=ft.Text("Consumo Sensores"),
                on_click=lambda _: navegar(lambda: mostrar_pantalla_consumo_sensores(page, usuario, lambda: mostrar_pantalla_menu_trabajador(page, repo, usuario)))
            ),

            ft.Container(expand=True),
            ft.TextButton("Cerrar Sesión", icon=ft.Icons.LOGOUT, on_click=cerrar_sesion, style=ft.ButtonStyle(color="red"))
        ], spacing=0),
        width=270, bgcolor="white", padding=25, shadow=ft.BoxShadow(blur_radius=10, color="black12")
    )

    #--- PANEL PRINCIPAL ---
    tarjeta_mapa = ft.Container(
        expand=True, bgcolor="white", border_radius=15, padding=25,
        shadow=ft.BoxShadow(blur_radius=15, color="black12"),
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Estado de Planta", size=22, weight="bold"),
                    ft.Text("Monitorización en vivo para personal operativo", size=14, color="grey600"),
                ]),
                ft.IconButton(ft.Icons.FULLSCREEN_ROUNDED, on_click=lambda _: navegar(lambda: mostrar_pantalla_mapa_habitaciones_trabajadores(page, repo, usuario)))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=30),
            ft.Container(content=contenedor_mapa_vivo, expand=True)
        ])
    )

    tarjeta_inferior = ft.Container(
        height=180, bgcolor="white", border_radius=15, padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color="black12"),
        content=ft.Column([
            ft.Text("Métricas y Estadísticas", size=18, weight="bold"),
            ft.Container(expand=True, content=ft.Text("Espacio reservado para gráficos mensuales...", color="grey400"), alignment=ft.Alignment(0,0))
        ]),
        alignment=ft.Alignment(0, 0)
    )

    panel_principal = ft.Container(
        expand=True, padding=30,
        content=ft.Column([
            ft.Text(f"Bienvenido, {usuario.nombre_usuario}", size=28, weight="bold", color="blue900"),
            tarjeta_mapa,
            tarjeta_inferior,
        ], spacing=25)
    )

    #--- TAREAS ASÍNCRONAS ---
    async def parpadeo_dashboard():
        while True:
            try:
                if habitaciones_parpadeo:
                    for h in habitaciones_parpadeo: h.bgcolor = COLOR_ALERTA
                    page.update()
                    await asyncio.sleep(0.5)
                    for h in habitaciones_parpadeo: h.bgcolor = h.data["color_original"]
                    page.update()
                    await asyncio.sleep(0.5)
                else: await asyncio.sleep(1)
            except: break
    
    async def auto_actualizar():
        while True:
            try:
                await asyncio.sleep(5)
                reconstruir_mapa_dashboard()
            except:
                break

    #Composición
    page.add(ft.Row([sidebar, panel_principal], expand=True, spacing=0))
    
    reconstruir_mapa_dashboard()
    page.run_task(parpadeo_dashboard)
    page.run_task(auto_actualizar)