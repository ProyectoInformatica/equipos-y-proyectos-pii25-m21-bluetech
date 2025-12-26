import flet as ft
import asyncio
from controller.mapa_habitaciones_controller import obtener_datos_mapa

def mostrar_pantalla_mapa_habitaciones_trabajadores(page: ft.Page, repo, usuario):
    from view.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.clean()
    page.title = "Mapa de Habitaciones - Hospital"
    page.bgcolor = "#F0F0F0"

    bloque_abierto = None
    habitacion_expandida_id = None
    habitaciones_parpadeo = []
    habitaciones_ui = {}
    COLOR_ALERTA = "#FF8181"

    # =======================
    # ACCIONES DE BOTONES
    # =======================
    def accion_actualizar(e):
        actualizar_sensores_y_colores()
        page.open(ft.SnackBar(ft.Text("🔄 Mapa actualizado manualmente"), duration=3000))
        page.update()

    # =======================
    # BLOQUE IZQUIERDO (ÍNDICE)
    # =======================
    bloque_izquierdo = ft.Column(
        [
            ft.Text("🗺️ Índice del mapa", size=18, weight="bold"),
            ft.Text("🟩 Todo dentro de los rangos", size=14),
            ft.Text("🟥 Datos fuera de rango", size=14),
            ft.Text("Borde negro → Sala ocupada", size=14),
            ft.Text("Sin borde → Sala libre", size=14),
            ft.Text("Texto amarillo → Valor fuera de rango", size=14),
            ft.Divider(),
            ft.Row(
                [
                    ft.ElevatedButton(icon=ft.Icons.REFRESH, text="Actualizar mapa", on_click=accion_actualizar),
                    ft.ElevatedButton(icon=ft.Icons.ARROW_BACK, text="Volver",
                                      on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario)),
                ],
                spacing=10
            ),
        ],
        width=420,
        spacing=12,
    )

    # =======================
    # BLOQUE DERECHO (MAPA)
    # =======================
    contenedor_plantas = ft.Column(
        spacing=30,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    bloque_derecho = ft.Container(
        content=contenedor_plantas,
        bgcolor="#E6F2FF",
        border=ft.border.all(4, "blue"),
        padding=20,
        expand=True,
        alignment=ft.alignment.top_center,
    )

    # =======================
    # CREAR HABITACIÓN
    # =======================
    def crear_habitacion(hab, rangos):
        nonlocal bloque_abierto

        idx = hab["index"]
        temp = hab["temperatura"]
        hum = hab["humedad"]
        calidad = hab["calidad_aire"]

        def fuera(valor, min=None, max=None):
            if min is not None and valor < min:
                return "yellow"
            if max is not None and valor > max:
                return "yellow"
            return "black"

        en_rango = (
            rangos["temperatura"]["min"] <= temp <= rangos["temperatura"]["max"]
            and rangos["humedad"]["min"] <= hum <= rangos["humedad"]["max"]
            and all(calidad[k][idx] <= rangos["calidad_aire"][k]["max"]
                    for k in rangos["calidad_aire"])
        )

        fondo = "green" if en_rango else "red"
        borde = ft.border.all(2, "black") if hab["estado"] == "ocupado" else None

        textos = [
            ft.Text(f"H{hab['id']}", size=8, weight="bold"),
            ft.Text(f"🌡️ {temp}°C", size=7, color=fuera(temp, rangos["temperatura"]["min"], rangos["temperatura"]["max"])),
            ft.Text(f"💧 {hum}%", size=7, color=fuera(hum, rangos["humedad"]["min"], rangos["humedad"]["max"])),
            ft.Text(f"PM2.5: {calidad['PM2.5'][idx]}", size=7, color=fuera(calidad['PM2.5'][idx], max=rangos["calidad_aire"]["PM2.5"]["max"])),
            ft.Text(f"PM10: {calidad['PM10'][idx]}", size=7, color=fuera(calidad['PM10'][idx], max=rangos["calidad_aire"]["PM10"]["max"])),
            ft.Text(f"CO: {calidad['CO'][idx]}", size=7),
            ft.Text(f"NO2: {calidad['NO2'][idx]}", size=7),
            ft.Text(f"CO2: {calidad['CO2'][idx]}", size=7),
            ft.Text(f"TVOC: {calidad['TVOC'][idx]}", size=7),
        ]

        contenido = ft.Column(textos, spacing=1, alignment=ft.MainAxisAlignment.CENTER)

        def toggle(e):
            nonlocal bloque_abierto

            if bloque_abierto and bloque_abierto != e.control:
                for i, t in enumerate(bloque_abierto.content.controls):
                    t.size = 7 if i > 0 else 8
                bloque_abierto.width = 80
                bloque_abierto.height = 120
                bloque_abierto.update()
                bloque_abierto = None

            if e.control.width == 80:
                e.control.width = 170
                e.control.height = 240
                for i, t in enumerate(textos):
                    t.size = 16 if i > 0 else 18
                bloque_abierto = e.control
            else:
                e.control.width = 80
                e.control.height = 120
                for i, t in enumerate(textos):
                    t.size = 7 if i > 0 else 8
                bloque_abierto = None

            e.control.update()

        hab_ui = ft.Container(
            content=contenido,
            width=80,
            height=120,
            bgcolor=fondo,
            border=borde,
            padding=3,
            alignment=ft.alignment.center,
            on_click=toggle,
        )

        # Guardar para actualización periódica
        habitaciones_ui[hab["id"]] = hab_ui

        if hab["estado"] == "ocupado" and not en_rango:
            habitaciones_parpadeo.append(hab_ui)

        return hab_ui

    # =======================
    # CONSTRUIR MAPA
    # =======================
    def reconstruir_mapa():
        contenedor_plantas.controls.clear()
        habitaciones_parpadeo.clear()
        habitaciones_ui.clear()
        habitaciones, rangos = obtener_datos_mapa()

        for planta in range((len(habitaciones) + 9) // 10):
            fila1 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            fila2 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

            for i, hab in enumerate(habitaciones[planta * 10 : planta * 10 + 10]):
                (fila1 if i < 5 else fila2).controls.append(crear_habitacion(hab, rangos))

            contenedor_plantas.controls.append(
                ft.Column(
                    [
                        ft.Text(f"🏥 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                        fila1,
                        fila2,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        page.update()

    # =======================
    # ACTUALIZACIÓN AUTOMÁTICA
    # =======================
    def actualizar_sensores_y_colores():
        if not habitaciones_ui:
            return

        habitaciones, rangos = obtener_datos_mapa()

        for hab in habitaciones:
            hab_ui = habitaciones_ui.get(hab["id"])
            if not hab_ui:
                continue

            temp = hab["temperatura"]
            hum = hab["humedad"]
            calidad = hab["calidad_aire"]
            idx = hab["index"]

            en_rango = (
                rangos["temperatura"]["min"] <= temp <= rangos["temperatura"]["max"]
                and rangos["humedad"]["min"] <= hum <= rangos["humedad"]["max"]
                and all(calidad[k][idx] <= rangos["calidad_aire"][k]["max"] for k in rangos["calidad_aire"])
            )

            hab_ui.bgcolor = "green" if en_rango else "red"
            hab_ui.data = {"color_original": hab_ui.bgcolor}

            controles = hab_ui.content.controls
            controles[1].value = f"🌡️ {temp}°C"
            controles[1].color = "black" if rangos["temperatura"]["min"] <= temp <= rangos["temperatura"]["max"] else "yellow"
            controles[2].value = f"💧 {hum}%"
            controles[2].color = "black" if rangos["humedad"]["min"] <= hum <= rangos["humedad"]["max"] else "yellow"

            for j, clave in enumerate(["PM2.5","PM10","CO","NO2","CO2","TVOC"], start=3):
                valor = calidad[clave][idx]
                controles[j].value = f"{clave}: {valor}"
                controles[j].color = "black" if valor <= rangos["calidad_aire"][clave]["max"] else "yellow"

            hab_ui.update()

    async def actualizar_periodicamente():
        while True:
            try:
                actualizar_sensores_y_colores()
            except Exception as e:
                print("Error actualización periódica:", e)
            await asyncio.sleep(10)

    async def parpadeo():
        while True:
            for h in habitaciones_parpadeo:
                h.bgcolor = COLOR_ALERTA
                h.update()
            await asyncio.sleep(2)
            for h in habitaciones_parpadeo:
                h.bgcolor = "red"
                h.update()
            await asyncio.sleep(6)

    # =======================
    # AGREGAR LAYOUT A LA PÁGINA
    # =======================
    page.add(ft.Row([bloque_izquierdo, bloque_derecho], expand=True))
    reconstruir_mapa()
    page.run_task(actualizar_periodicamente)  # <-- corutina ejecutándose correctamente
    page.run_task(parpadeo)  # <-- corutina de parpadeo
