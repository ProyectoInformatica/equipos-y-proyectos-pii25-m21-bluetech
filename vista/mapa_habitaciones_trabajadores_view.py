import flet as ft
import json
import os
import asyncio

RUTA_JSON = "habitacion.json"

# -----------------------------
# Funciones de carga de datos
# -----------------------------
def cargar_datos():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    else:
        return {"habitaciones": {"id_habitacion": [], "estado": [], "tipo_sala": []}}

def cargar_sensores_humedad():
    with open("sensores_humedad.json", "r") as archivo:
        return json.load(archivo)["sensores_hum"]

def cargar_sensores_temperatura():
    with open("sensores_temperatura.json", "r") as archivo:
        return json.load(archivo)["sensores_temp"]

def cargar_sensores_calidad_aire():
    with open("sensores_calidad_aire.json", "r") as archivo:
        return json.load(archivo)["sensores_cali_aire"]

def cargar_valores_comparativos():
    with open("valores_comparativos.json", "r") as archivo:
        return json.load(archivo)

# -----------------------------
# Pantalla mapa trabajadores
# -----------------------------
def mostrar_pantalla_mapa_habitaciones_trabajadores(page: ft.Page, repo, usuario):
    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador

    page.clean()
    page.title = "Mapa de Habitaciones - Hospital"
    page.scroll = None
    page.bgcolor = "#F0F0F0"

    # Estado interno de UI
    bloque_abierto = None
    habitaciones_ui = {}
    habitaciones_parpadeo = []
    COLOR_ALERTA = "#FF8181"
    necesita_reconstruccion = True

    # -----------------------------------------------------------------
    # Botones que estarán en el bloque izquierdo (debajo de la leyenda)
    # -----------------------------------------------------------------
    def accion_actualizar(e):
        nonlocal necesita_reconstruccion
        necesita_reconstruccion = True
        page.open(ft.SnackBar(ft.Text("🔄 Mapa actualizado manualmente")))
        page.update()

    boton_volver = ft.ElevatedButton(
        icon=ft.Icons.ARROW_BACK,
        text="Volver al menú",
        on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario)
    )

    boton_actualizar = ft.ElevatedButton(
        icon=ft.Icons.REFRESH,
        text="Actualizar mapa",
        on_click=accion_actualizar
    )

    # -----------------------------
    # Bloque izquierdo (leyenda + botones)
    # -----------------------------
    bloque_izquierdo = ft.Column(
        controls=[
            ft.Text("🗺️ Índice del mapa", size=18, weight="bold"),
            ft.Column([
                ft.Text("🟩 Todo bien", size=14),
                ft.Text("🟥 Datos fuera de los rangos establecidos", size=14),
                ft.Text("Recuadro con bordes -> Sala ocupada", size=14),
                ft.Text("Recuadro sin bordes -> Sala libre", size=14),
                ft.Text("Texto amarillo -> Datos fuera de rango", size=14),
            ], spacing=5),
            ft.Divider(),
            ft.Row([boton_actualizar, boton_volver], spacing=10),
        ],
        width=420,
        spacing=15,
        alignment=ft.MainAxisAlignment.START
    )

    # -----------------------------
    # Bloque derecho (mapa)
    # -----------------------------
    contenedor_plantas = ft.Column(spacing=30, scroll=ft.ScrollMode.AUTO, expand=True)
    bloque_derecho = ft.Container(
        content=contenedor_plantas,
        bgcolor="#E6F2FF",
        border=ft.border.all(4, "blue"),
        padding=20,
        expand=True
    )

    # -----------------------------
    # Crear habitación visual
    # -----------------------------
    def crear_habitacion(index, id_hab, estado, humedad, temperatura, calidad_aire_data, rangos):
        def color_si_fuera_rango(valor, min_val=None, max_val=None):
            if min_val is not None and valor < min_val:
                return "yellow"
            if max_val is not None and valor > max_val:
                return "yellow"
            return "black"

        en_rango = (
            rangos["temperatura"]["min"] <= temperatura <= rangos["temperatura"]["max"]
            and rangos["humedad"]["min"] <= humedad <= rangos["humedad"]["max"]
            and all(calidad_aire_data.get(clave, [float("inf")] * (index + 1))[index] <= rangos["calidad_aire"][clave]["max"]
                    for clave in rangos["calidad_aire"])
        )

        fondo = "green" if en_rango else "red"
        borde = ft.border.all(2, "black") if estado == "ocupado" else None

        textos = [
            ft.Text(f"H{id_hab}", size=8, weight="bold", color="gray"),
            ft.Text(f"🌡️ {temperatura}°C", size=7,
                color=color_si_fuera_rango(temperatura, rangos["temperatura"]["min"], rangos["temperatura"]["max"])),
            ft.Text(f"💧 {humedad}%", size=7,
                color=color_si_fuera_rango(humedad, rangos["humedad"]["min"], rangos["humedad"]["max"])),
            ft.Text(f"PM2.5: {calidad_aire_data.get('PM2.5', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("PM2.5", [0])[index], max_val=rangos["calidad_aire"]["PM2.5"]["max"])),
            ft.Text(f"PM10: {calidad_aire_data.get('PM10', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("PM10", [0])[index], max_val=rangos["calidad_aire"]["PM10"]["max"])),
            ft.Text(f"CO: {calidad_aire_data.get('CO', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("CO", [0])[index], max_val=rangos["calidad_aire"]["CO"]["max"])),
            ft.Text(f"NO2: {calidad_aire_data.get('NO2', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("NO2", [0])[index], max_val=rangos["calidad_aire"]["NO2"]["max"])),
            ft.Text(f"CO2: {calidad_aire_data.get('CO2', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("CO2", [0])[index], max_val=rangos["calidad_aire"]["CO2"]["max"])),
            ft.Text(f"TVOC: {calidad_aire_data.get('TVOC', [None])[index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data.get("TVOC", [0])[index], max_val=rangos["calidad_aire"]["TVOC"]["max"])),
        ]

        color_original = fondo
        debe_parpadear = (estado == "ocupado" and not en_rango)

        contenido = ft.Column(textos, spacing=1, alignment=ft.MainAxisAlignment.CENTER)

        def toggle_expand(e):
            nonlocal bloque_abierto
            id_actual = e.control.data.get("id_habitacion")
            if id_actual is None:
                return
            if bloque_abierto and bloque_abierto != e.control:
                if bloque_abierto.page:
                    bloque_abierto.width = 80
                    bloque_abierto.height = 120
                    for i, txt in enumerate(bloque_abierto.content.controls):
                        txt.size = 7 if i > 0 else 8
                    bloque_abierto.update()
                bloque_abierto = None

            if e.control.width == 80:
                e.control.width = 170
                e.control.height = 240
                for i, txt in enumerate(textos):
                    txt.size = 16 if i > 0 else 18
                bloque_abierto = e.control
            else:
                e.control.width = 80
                e.control.height = 120
                for i, txt in enumerate(textos):
                    txt.size = 7 if i > 0 else 8
                bloque_abierto = None

            if e.control.page:
                e.control.update()

        habitacion = ft.Container(
            content=contenido,
            width=80,
            height=120,
            bgcolor=fondo,
            border=borde,
            alignment=ft.alignment.center,
            padding=3,
            on_click=toggle_expand,
            data={"color_original": color_original, "id_habitacion": id_hab}
        )

        if debe_parpadear:
            habitaciones_parpadeo.append(habitacion)

        habitaciones_ui[id_hab] = habitacion
        return habitacion

    # -----------------------------
    # Reconstrucción del mapa
    # -----------------------------
    def reconstruir_mapa():
        nonlocal necesita_reconstruccion, bloque_abierto
        necesita_reconstruccion = False
        bloque_abierto = None
        habitaciones_ui.clear()
        contenedor_plantas.controls.clear()
        habitaciones_parpadeo.clear()

        datos = cargar_datos()
        ids = datos["habitaciones"].get("id_habitacion", [])
        estados = datos["habitaciones"].get("estado", [])

        humedad_data = cargar_sensores_humedad().get("humedad", [])
        temperatura_data = cargar_sensores_temperatura().get("temperatura", [])
        calidad_aire_data = cargar_sensores_calidad_aire().get("calidad_aire", {})

        total = min(len(ids), len(estados), len(temperatura_data), len(humedad_data))
        habitaciones = [
            (ids[i], estados[i], temperatura_data[i], humedad_data[i])
            for i in range(total)
        ]
        habitaciones.sort(key=lambda x: x[0])

        try:
            rangos = cargar_valores_comparativos()
        except Exception as e:
            print("Error cargando valores comparativos:", e)
            return

        total_habs = len(habitaciones)
        total_plantas = (total_habs + 9) // 10

        for planta in range(total_plantas):
            inicio = planta * 10
            fin = min(inicio + 10, total_habs)
            fila1 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            fila2 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

            for i, (id_hab, estado, temperatura, humedad) in enumerate(habitaciones[inicio:fin]):
                index_local = inicio + i
                hab_ui = crear_habitacion(
                    index=index_local,
                    id_hab=id_hab,
                    estado=estado,
                    humedad=humedad,
                    temperatura=temperatura,
                    calidad_aire_data=calidad_aire_data,
                    rangos=rangos,
                )
                if i < 5:
                    fila1.controls.append(hab_ui)
                else:
                    fila2.controls.append(hab_ui)

            contenedor_plantas.controls.append(
                ft.Column(
                    [
                        ft.Text(f"🏥 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                        fila1,
                        fila2,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        page.update()

    # -----------------------------
    # Refrescos parciales: datos y colores
    # -----------------------------
    def refrescar_datos():
        if necesita_reconstruccion:
            reconstruir_mapa()
            return

        humedad_data = cargar_sensores_humedad().get("humedad", [])
        temperatura_data = cargar_sensores_temperatura().get("temperatura", [])
        calidad_aire_data = cargar_sensores_calidad_aire().get("calidad_aire", {})

        ids_ordenados = sorted(habitaciones_ui.keys())
        for i, id_hab in enumerate(ids_ordenados):
            hab = habitaciones_ui[id_hab]
            if not hab.page:
                continue

            if i >= len(temperatura_data) or i >= len(humedad_data):
                continue

            textos = hab.content.controls
            textos[1].value = f"🌡️ {temperatura_data[i]}°C"
            textos[2].value = f"💧 {humedad_data[i]}%"
            textos[3].value = f"PM2.5: {calidad_aire_data.get('PM2.5', [None]*len(ids_ordenados))[i]}"
            textos[4].value = f"PM10: {calidad_aire_data.get('PM10', [None]*len(ids_ordenados))[i]}"
            textos[5].value = f"CO: {calidad_aire_data.get('CO', [None]*len(ids_ordenados))[i]}"
            textos[6].value = f"NO2: {calidad_aire_data.get('NO2', [None]*len(ids_ordenados))[i]}"
            textos[7].value = f"CO2: {calidad_aire_data.get('CO2', [None]*len(ids_ordenados))[i]}"
            textos[8].value = f"TVOC: {calidad_aire_data.get('TVOC', [None]*len(ids_ordenados))[i]}"

            hab.update()

    def refrescar_colores():
        try:
            rangos = cargar_valores_comparativos()
            humedad_data = cargar_sensores_humedad().get("humedad", [])
            temperatura_data = cargar_sensores_temperatura().get("temperatura", [])
            calidad_aire_data = cargar_sensores_calidad_aire().get("calidad_aire", {})

            ids_ordenados = sorted(habitaciones_ui.keys())
            datos_local = cargar_datos()
            ids_originales = datos_local["habitaciones"].get("id_habitacion", [])
            estados_originales = datos_local["habitaciones"].get("estado", [])

            for i, id_hab in enumerate(ids_ordenados):
                hab = habitaciones_ui[id_hab]
                if not hab.page:
                    continue

                if i >= len(temperatura_data) or i >= len(humedad_data):
                    continue

                def color_si_fuera_rango(valor, min_val=None, max_val=None):
                    if min_val is not None and valor < min_val:
                        return "yellow"
                    if max_val is not None and valor > max_val:
                        return "yellow"
                    return "black"

                en_rango = (
                    rangos["temperatura"]["min"] <= temperatura_data[i] <= rangos["temperatura"]["max"]
                    and rangos["humedad"]["min"] <= humedad_data[i] <= rangos["humedad"]["max"]
                    and all(
                        calidad_aire_data.get(clave, [float("inf")] * (i + 1))[i] <= rangos["calidad_aire"][clave]["max"]
                        for clave in rangos["calidad_aire"]
                    )
                )

                hab.bgcolor = "green" if en_rango else "red"

                try:
                    idx_original = ids_originales.index(id_hab)
                    estado_actual = estados_originales[idx_original]
                except ValueError:
                    estado_actual = "libre"

                hab.border = ft.border.all(2, "black") if estado_actual == "ocupado" else None

                textos = hab.content.controls
                textos[1].color = color_si_fuera_rango(temperatura_data[i], rangos["temperatura"]["min"], rangos["temperatura"]["max"])
                textos[2].color = color_si_fuera_rango(humedad_data[i], rangos["humedad"]["min"], rangos["humedad"]["max"])
                textos[3].color = color_si_fuera_rango(calidad_aire_data.get("PM2.5", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["PM2.5"]["max"])
                textos[4].color = color_si_fuera_rango(calidad_aire_data.get("PM10", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["PM10"]["max"])
                textos[5].color = color_si_fuera_rango(calidad_aire_data.get("CO", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["CO"]["max"])
                textos[6].color = color_si_fuera_rango(calidad_aire_data.get("NO2", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["NO2"]["max"])
                textos[7].color = color_si_fuera_rango(calidad_aire_data.get("CO2", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["CO2"]["max"])
                textos[8].color = color_si_fuera_rango(calidad_aire_data.get("TVOC", [0]*len(ids_ordenados))[i], max_val=rangos["calidad_aire"]["TVOC"]["max"])

                hab.update()
        except Exception as e:
            print("Error actualizando colores:", e)

    # -----------------------------
    # Actualización automática
    # -----------------------------
    async def actualizar_periodicamente():
        nonlocal necesita_reconstruccion
        while True:
            try:
                if necesita_reconstruccion:
                    reconstruir_mapa()
                else:
                    refrescar_datos()
                    refrescar_colores()
            except Exception as e:
                print("Error en actualización periódica:", e)
            await asyncio.sleep(10)

    # -----------------------------
    # Parpadeo de alerta
    # -----------------------------
    async def parpadeo_alerta():
        while True:
            for hab in list(habitaciones_parpadeo):
                try:
                    hab.bgcolor = COLOR_ALERTA
                    hab.update()
                except Exception:
                    pass
            await asyncio.sleep(2)
            for hab in list(habitaciones_parpadeo):
                try:
                    if hab.page:
                        hab.bgcolor = hab.data.get("color_original", "red")
                        hab.update()
                except Exception:
                    pass
            await asyncio.sleep(6)

    # -----------------------------
    # Layout principal (izquierda + derecha)
    # -----------------------------
    layout_principal = ft.Row(
        controls=[bloque_izquierdo, bloque_derecho],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    page.add(ft.Row(controls=[layout_principal], expand=True))

    # Inicializa el mapa y lanza tareas
    reconstruir_mapa()
    page.run_task(actualizar_periodicamente)
    page.run_task(parpadeo_alerta)
