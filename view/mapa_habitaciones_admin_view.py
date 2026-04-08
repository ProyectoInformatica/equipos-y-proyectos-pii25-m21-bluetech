import flet as ft
import asyncio
from controller.mapa_habitaciones_controller import (
    obtener_datos_mapa, 
    agregar_habitacion,
    eliminar_habitacion_control,
    duplicar_planta_control,
    eliminar_planta_control
)

#--- ESTILOS ---
COLOR_DISPONIBLE = "#A8D5BA"
COLOR_OCUPADO = "#F2A2A2"
COLOR_ALERTA = "#FF0000"
COLOR_PASILLO = "#EDF2F7"

#Mantenemos la lista aquí para el efecto de parpadeo
habitaciones_parpadeo = []

def mostrar_pantalla_mapa_admin(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    global habitaciones_parpadeo 
    
    page.clean()
    page.title = "Sistema Hospitalario - Panel de Control"
    page.bgcolor = "#F8F9FA"

    #--- FUNCIÓN DE MENSAJE ---
    def mostrar_mensaje(texto, es_error=False):
        snack = ft.SnackBar(
            content=ft.Text(texto, color="white", weight="bold"),
            bgcolor=ft.Colors.RED_400 if es_error else ft.Colors.GREEN_400,
            duration=3000
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    #--- ELEMENTOS DE UI ---
    campo_estado = ft.Dropdown(
        label="Estado Inicial",
        options=[ft.dropdown.Option("libre"), ft.dropdown.Option("ocupado")],
        value="libre", border_radius=10
    )

    campo_tipo_sala = ft.Dropdown(
        label="Especialidad",
        options=[ft.dropdown.Option("S.hospitalizacion"), ft.dropdown.Option("S.aislamiento"), ft.dropdown.Option("S.urgencias")],
        value="S.hospitalizacion", border_radius=10
    )

    campo_planta = ft.Dropdown(label="Planta", options=[], width=120, border_radius=10)
    campo_id_text = ft.TextField(label="ID", width=80, border_radius=10, hint_text="Ej: 101")
    
    contenedor_plantas = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=30)

    #--- LÓGICA DE EVENTOS ---
    def actualizar(e=None):
        reconstruir_mapa()
        if e: mostrar_mensaje("Datos sincronizados con éxito", es_error=False)

    def agregar_habitacion_ui(e):
        res = agregar_habitacion(campo_estado.value, campo_tipo_sala.value)
        if res:
            reconstruir_mapa()
            mostrar_mensaje(f"✅ Habitación {res} creada correctamente", es_error=False)
        else:
            mostrar_mensaje("❌ Error al crear la habitación", es_error=True)

    def eliminar_habitacion_ui(e):
        try:
            if not campo_id_text.value:
                mostrar_mensaje("Introduce un ID para eliminar", es_error=True)
                return
            id_eliminar = int(campo_id_text.value)
            ok, mensaje_res, _ = eliminar_habitacion_control(id_eliminar)
            if ok:
                reconstruir_mapa()
                mostrar_mensaje(f"🗑️ Habitación {id_eliminar} eliminada", es_error=False)
                campo_id_text.value = ""
            else:
                mostrar_mensaje(f"Error: {mensaje_res}", es_error=True)
        except ValueError:
            mostrar_mensaje("El ID debe ser un número", es_error=True)
        page.update()

    #--- LÓGICA DE PLANTAS CON CONFIRMACIÓN ---
    def confirmar_accion_planta(titulo, mensaje, accion_callback):
        if not campo_planta.value:
            mostrar_mensaje("⚠️ Selecciona una planta en el desplegable", es_error=True)
            return

        def realizar_accion(e):
            dlg.open = False
            page.update()
            ok, res = accion_callback(campo_planta.value)
            if ok:
                reconstruir_mapa()
                mostrar_mensaje(f"✨ Operación exitosa: {res}", es_error=False)
            else:
                mostrar_mensaje(f"Fallo: {res}", es_error=True)

        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: (setattr(dlg, "open", False), page.update())),
                ft.ElevatedButton("Confirmar", bgcolor="red", color="white", on_click=realizar_accion),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    #--- LÓGICA DE ZOOM ---
    def abrir_detalle(h_info):
        tipo_sala = h_info.get("tipo") or h_info.get("tipo_sala") or h_info.get("especialidad") or "No definido"
        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalle Habitación {h_info['id']}", weight="bold"),
            content=ft.Column([
                ft.Text(f"Tipo: {tipo_sala}", size=16, weight="w500"), 
                ft.Divider(),
                ft.Row([ft.Icon(ft.Icons.THERMOSTAT, color="orange"), ft.Text(f"Temperatura: {h_info['temperatura']}°C")]),
                ft.Row([ft.Icon(ft.Icons.WATER_DROP, color="blue"), ft.Text(f"Humedad: {h_info['humedad']}%")]),
                ft.Row([ft.Icon(ft.Icons.AIR, color="green"), ft.Text(f"Calidad Aire (CO2): {h_info['calidad_aire'].get('CO2', 0)} ppm")]),
            ], tight=True, spacing=15),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: (setattr(dlg, "open", False), page.update()))],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    #--- CONSTRUCCIÓN DEL MAPA ---
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
        campo_planta.options = [ft.dropdown.Option(str(i+1)) for i in range(num_plantas)]
        
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
            ft.Text("GESTIÓN MAPA", size=22, weight="bold", color="blue900"),
            
            #--- LEYENDA ---
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=15, height=15, bgcolor=COLOR_DISPONIBLE, border_radius=3),
                        ft.Text("Dentro de rango", size=12)
                    ], spacing=10),
                    ft.Row([
                        ft.Container(width=15, height=15, bgcolor=COLOR_OCUPADO, border_radius=3),
                        ft.Text("Fuera de rango", size=12)
                    ], spacing=10),
                    ft.Row([
                        ft.Container(
                            width=15, height=15, bgcolor=COLOR_ALERTA, border_radius=3,
                            shadow=ft.BoxShadow(blur_radius=5, color=COLOR_ALERTA)
                        ),
                        ft.Text("Alerta: Fuera de rango y Ocupada", size=12, weight="bold")
                    ], spacing=10),
                ], spacing=5),
                padding=ft.padding.only(bottom=10)
            ),
            
            ft.Divider(),
            ft.Text("Nueva Habitación", weight="bold"),
            campo_estado, campo_tipo_sala,
            ft.ElevatedButton("Añadir Sala", icon=ft.Icons.ADD, on_click=agregar_habitacion_ui, width=250),
            ft.Divider(),
            ft.Text("Eliminar por ID", weight="bold"),
            ft.Row([campo_id_text, ft.IconButton(ft.Icons.DELETE_FOREVER, on_click=eliminar_habitacion_ui, icon_color="red")]),
            ft.Divider(),
            ft.Text("Gestión de Planta", weight="bold"),
            campo_planta,
            ft.Row([
                ft.IconButton(
                    ft.Icons.COPY, 
                    tooltip="Duplicar Planta",
                    on_click=lambda _: confirmar_accion_planta(
                        "Duplicar Planta", 
                        f"¿Deseas duplicar las 10 habitaciones de la Planta {campo_planta.value}?", 
                        duplicar_planta_control
                    )
                ),
                ft.IconButton(
                    ft.Icons.DELETE_SWEEP, 
                    icon_color="red", 
                    tooltip="Eliminar Planta",
                    on_click=lambda _: confirmar_accion_planta(
                        "Eliminar Planta", 
                        f"¡ATENCIÓN! ¿Seguro que quieres eliminar TODA la Planta {campo_planta.value}?", 
                        eliminar_planta_control
                    )
                )
            ]),
            ft.Container(expand=True),
            ft.ElevatedButton("Actualizar", icon=ft.Icons.REFRESH, on_click=actualizar, width=250),
            ft.TextButton("Volver al Menú", icon=ft.Icons.ARROW_BACK, on_click=lambda _: mostrar_pantalla_menu_admin(page, repo, usuario))
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
                await asyncio.sleep(5)
                reconstruir_mapa()
            except: break

    #Construcción
    page.add(ft.Row([sidebar, ft.Container(content=contenedor_plantas, expand=True, padding=20)], expand=True))
    
    reconstruir_mapa()
    page.run_task(tarea_parpadeo)
    page.run_task(tarea_actualizacion_automatica)