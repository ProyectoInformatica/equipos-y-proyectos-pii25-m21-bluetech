import flet as ft
import json
import os
import asyncio
from eliminar_habitacion import eliminar_habitacion
from crear_habitaciones import crear_habitacion_con_sensores

# ---------------------------------------------------------------------
# CARGA DE DATOS DESDE JSON (habitaciones y sensores)
# ---------------------------------------------------------------------
RUTA_JSON = "habitacion.json"

def cargar_datos():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    else:
        return {"habitaciones": {"id_habitacion": [], "estado": []}}

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

# Habitaciones que deben parpadear
habitaciones_parpadeo = []
COLOR_ALERTA = "#FF8181"
habitacion_expandida_id = None
habitaciones_ui = {}
necesita_reconstruccion = True

# ---------------------------------------------------------------------
# PANTALLA PRINCIPAL: MAPA EN DOS BLOQUES
# ---------------------------------------------------------------------
def mostrar_pantalla_mapa_admin(page: ft.Page, repo, usuario):
    from vista.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()

    page.title = "Mapa de Habitaciones - Hospital"
    page.scroll = None
    page.bgcolor = "#F0F0F0"

    bloque_abierto = None
    global datos
    datos = cargar_datos()

    # -----------------------------------------------------------------
    # BOTONES SUPERIORES
    # -----------------------------------------------------------------
    boton_volver = ft.ElevatedButton(
        icon=ft.Icons.ARROW_BACK,
        text="Volver al menú",
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario)
    )

    def actualizar(e):
        global datos
        global necesita_reconstruccion
        necesita_reconstruccion = True
        datos.update(cargar_datos())
        page.open(ft.SnackBar(ft.Text("🔄 Mapa actualizado manualmente")))
        page.update()

    boton_actualizar = ft.ElevatedButton(
        icon=ft.Icons.REFRESH,
        text="Actualizar",
        on_click=actualizar
    )

    # -----------------------------------------------------------------
    # PANEL DE GESTIÓN
    # -----------------------------------------------------------------
    campo_estado = ft.Dropdown(
        label="Estado de la habitación",
        options=[ft.dropdown.Option("libre"), ft.dropdown.Option("ocupado")],
        value="libre"
    )

    # Dropdown de estado
    campo_estado = ft.Dropdown(
        label="Estado de la habitación",
        options=[ft.dropdown.Option("libre"), ft.dropdown.Option("ocupado")],
        value="libre"
    )

    # Dropdown de tipo de sala
    campo_tipo_sala = ft.Dropdown(
        label="Tipo de sala",
        options=[
            ft.dropdown.Option("S.aislamiento"),
            ft.dropdown.Option("S.hospitalizacion"),
            ft.dropdown.Option("S.cuidados_intensivos(UCI)"),
            ft.dropdown.Option("S.espera"),
            ft.dropdown.Option("S.urgencias"),
            ft.dropdown.Option("S.recuperacion")
        ],
        value="S.hospitalizacion"
    )

    def agregar_habitacion(e):
        global datos
        global necesita_reconstruccion
        necesita_reconstruccion = True
        estado = campo_estado.value
        tipo_sala = campo_tipo_sala.value
        nuevo_id = crear_habitacion_con_sensores(estado, tipo_sala)
        datos = cargar_datos()
        actualizar_dropdown_plantas()
        page.open(ft.SnackBar(ft.Text(f"✅ Habitación H{nuevo_id} creada correctamente")))
        reconstruir_mapa()
        page.update()

    campo_planta = ft.Dropdown(label="Selecciona planta", options=[], width=200)

    boton_agregar = ft.ElevatedButton(text="➕ Crear Sala", on_click=agregar_habitacion)

    # TextField para eliminar habitación por ID
    campo_id_text = ft.TextField(label="ID de habitación a eliminar", width=200)
    mensaje_error_eliminar = ft.Text("", size=12, color="red")

    # -----------------------------------------------------------------
    # DUPLICAR PLANTAS (manteniendo funcionalidad original)
    # -----------------------------------------------------------------
    def mostrar_confirmacion_duplicar(e):
        if not campo_planta.value:
            page.open(ft.SnackBar(ft.Text("⚠️ Selecciona una planta para gestionar")))
            page.update()
            return

        planta = int(campo_planta.value) - 1
        habitaciones_por_planta = 10
        inicio = planta * habitaciones_por_planta
        fin = inicio + habitaciones_por_planta
        ids = datos["habitaciones"]["id_habitacion"]
        ids_planta = ids[inicio:fin]

        if len(ids_planta) < habitaciones_por_planta:
            page.open(ft.SnackBar(ft.Text("⚠️ La planta seleccionada no tiene 10 habitaciones completas")))
            page.update()
            return

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmación"),
            content=ft.Text("¿Quieres duplicar esta planta (crear 10 salas nuevas con mismos estados)?"),
            actions=[
                ft.TextButton("Sí", on_click=lambda ev: ejecutar_duplicacion(ev, dlg)),
                ft.TextButton("No", on_click=lambda ev: cancelar_dialogo(ev, dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg)

    def ejecutar_duplicacion(e, dlg):
        page.close(dlg)
        duplicar_planta()
        page.open(ft.SnackBar(ft.Text("✅ Planta duplicada correctamente")))
        page.update()

    def cancelar_dialogo(e, dlg):
        page.close(dlg)
        page.open(ft.SnackBar(ft.Text("❌ Acción cancelada")))
        page.update()

    def duplicar_planta():
        global datos
        global necesita_reconstruccion
        necesita_reconstruccion = True
        if not campo_planta.value:
            return
        planta = int(campo_planta.value) - 1
        habitaciones_por_planta = 10
        inicio = planta * habitaciones_por_planta
        fin = inicio + habitaciones_por_planta
        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]

        for i in range(inicio, min(fin, len(ids))):
            estado_original = estados[i]
            tipo_sala_original = datos["habitaciones"]["tipo_sala"][i]
            crear_habitacion_con_sensores(estado_original, tipo_sala_original)

        datos.update(cargar_datos())
        actualizar_dropdown_plantas()
        reconstruir_mapa()

    boton_duplicar = ft.ElevatedButton(text="📑 Duplicar Planta", on_click=mostrar_confirmacion_duplicar)

    # -----------------------------------------------------------------
    # ELIMINAR HABITACIÓN
    # -----------------------------------------------------------------
    def eliminar_habitacion_ui(e):
        global datos
        global necesita_reconstruccion
        necesita_reconstruccion = True
        mensaje_error_eliminar.value = ""
        try:
            id_eliminar = int(campo_id_text.value)
        except:
            mensaje_error_eliminar.value = "❌ ID inválido"
            page.update()
            return

        ok, mensaje = eliminar_habitacion(
            id_eliminar,
            datos,
            cargar_sensores_humedad,
            cargar_sensores_temperatura,
            cargar_sensores_calidad_aire
        )
        if ok:
            datos = cargar_datos()
            actualizar_dropdown_plantas()
            reconstruir_mapa()
            mensaje_error_eliminar.value = ""
            page.open(ft.SnackBar(ft.Text(f"✅ Habitación H{id_eliminar} eliminada correctamente")))
        else:
            mensaje_error_eliminar.value = f"❌ {mensaje}"
        page.update()

    boton_eliminar_sala = ft.ElevatedButton(text="🗑️ Eliminar Sala", on_click=eliminar_habitacion_ui)

    # -----------------------------------------------------------------
    # DROPDOWN DE PLANTAS
    # -----------------------------------------------------------------
    def actualizar_dropdown_plantas():
        datos_local = cargar_datos()
        total = len(datos_local["habitaciones"]["id_habitacion"])
        plantas = (total + 9) // 10
        campo_planta.options = [ft.dropdown.Option(str(p + 1)) for p in range(plantas)] if plantas > 0 else []
        page.update()

    actualizar_dropdown_plantas()

    # -----------------------------------------------------------------
    # BLOQUE IZQUIERDO
    # -----------------------------------------------------------------

    # Combinar todo en fila con columna para los dropdowns
    fila_agregar = ft.Row(
        controls=[
            boton_agregar,
            ft.Column(
                controls=[campo_estado, campo_tipo_sala],
                spacing=5,  # espacio entre los dropdowns
                alignment=ft.MainAxisAlignment.START
            )
        ],
        spacing=15,  # espacio entre el botón y la columna
        vertical_alignment=ft.CrossAxisAlignment.START
    )

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
            ft.Text("⚙️ Panel de gestión", size=18, weight="bold"),
            ft.Row([fila_agregar], spacing=5),
            ft.Divider(),
            ft.Row([boton_eliminar_sala, campo_id_text], spacing=5),
            mensaje_error_eliminar,
            ft.Divider(),
            ft.Text("⚙️ Gestión de Plantas", size=18, weight="bold"),
            ft.Row([boton_duplicar, campo_planta], spacing=5),
            ft.Divider(),
            ft.Row([boton_actualizar, boton_volver], spacing=10)
        ],
        width=420,
        spacing=15,
        alignment=ft.MainAxisAlignment.START
    )

    # -----------------------------------------------------------------
    # BLOQUE DERECHO: MAPA DE HOSPITAL
    # -----------------------------------------------------------------
    contenedor_plantas = ft.Column(spacing=30, scroll=ft.ScrollMode.AUTO, expand=True)
    bloque_derecho = ft.Container(
        content=contenedor_plantas,
        bgcolor="#E6F2FF",
        border=ft.border.all(4, "blue"),
        padding=20,
        expand=True
    )

    # -----------------------------------------------------------------
    # CREACIÓN VISUAL DE HABITACIÓN
    # -----------------------------------------------------------------
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
            and all(calidad_aire_data[clave][index] <= rangos["calidad_aire"][clave]["max"]
                    for clave in rangos["calidad_aire"])
        )

        if en_rango:
            fondo = "green"
            borde = None
        elif estado == "ocupado":
            fondo = "red"
            borde = ft.border.all(2, "black")
        else:
            fondo = "red"
            borde = None

        textos = [
            ft.Text(f"H{id_hab}", size=8, weight="bold", color="gray"),
            ft.Text(f"🌡️ {temperatura}°C", size=7,
                color=color_si_fuera_rango(temperatura, rangos["temperatura"]["min"], rangos["temperatura"]["max"])),
            ft.Text(f"💧 {humedad}%", size=7,
                color=color_si_fuera_rango(humedad, rangos["humedad"]["min"], rangos["humedad"]["max"])),
            ft.Text(f"PM2.5: {calidad_aire_data['PM2.5'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["PM2.5"][index], max_val=rangos["calidad_aire"]["PM2.5"]["max"])),
            ft.Text(f"PM10: {calidad_aire_data['PM10'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["PM10"][index], max_val=rangos["calidad_aire"]["PM10"]["max"])),
            ft.Text(f"CO: {calidad_aire_data['CO'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["CO"][index], max_val=rangos["calidad_aire"]["CO"]["max"])),
            ft.Text(f"NO2: {calidad_aire_data['NO2'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["NO2"][index], max_val=rangos["calidad_aire"]["NO2"]["max"])),
            ft.Text(f"CO2: {calidad_aire_data['CO2'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["CO2"][index], max_val=rangos["calidad_aire"]["CO2"]["max"])),
            ft.Text(f"TVOC: {calidad_aire_data['TVOC'][index]}", size=7,
                color=color_si_fuera_rango(calidad_aire_data["TVOC"][index], max_val=rangos["calidad_aire"]["TVOC"]["max"])),
        ]

        color_original = fondo
        debe_parpadear = (estado == "ocupado" and not en_rango)

        contenido = ft.Column(textos, spacing=1, alignment=ft.MainAxisAlignment.CENTER)

        def toggle_expand(e):
            nonlocal bloque_abierto
            global habitacion_expandida_id
            id_actual = e.control.data.get("id_habitacion")
            if id_actual is None:
                return
            # cerrar el anterior solo si sigue vivo
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
                habitacion_expandida_id = id_actual
            else:
                e.control.width = 80
                e.control.height = 120
                for i, txt in enumerate(textos):
                    txt.size = 7 if i > 0 else 8
                bloque_abierto = None
                habitacion_expandida_id = None

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
            data={
                "color_original": color_original,
                "id_habitacion": id_hab
            }
        )

        if debe_parpadear:
            habitaciones_parpadeo.append(habitacion)
        
        habitaciones_ui[id_hab] = habitacion
        return habitacion

    # -----------------------------------------------------------------
    # ACTUALIZACIÓN DEL MAPA
    # -----------------------------------------------------------------
    def reconstruir_mapa():
        global datos, habitaciones_parpadeo, bloque_abierto, necesita_reconstruccion
        necesita_reconstruccion = False
        bloque_abierto = None
        habitaciones_ui.clear()
        contenedor_plantas.controls.clear()
        habitaciones_parpadeo.clear()
        datos = cargar_datos()

        humedad_data = cargar_sensores_humedad()["humedad"]
        temperatura_data = cargar_sensores_temperatura()["temperatura"]
        calidad_aire_data = cargar_sensores_calidad_aire()["calidad_aire"]

        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]

        habitaciones = [
            (id_hab, estado, temperatura, humedad)
            for id_hab, estado, temperatura, humedad in zip(ids, estados, temperatura_data, humedad_data)
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
                    rangos=rangos
                )
                if i < 5:
                    fila1.controls.append(hab_ui)
                else:
                    fila2.controls.append(hab_ui)

            contenedor_plantas.controls.append(
                ft.Column([ft.Text(f"🏥 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                            fila1, fila2], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )

        page.update()

    def refrescar_datos():
        if necesita_reconstruccion:
            reconstruir_mapa()
            return

        humedad_data = cargar_sensores_humedad()["humedad"]
        temperatura_data = cargar_sensores_temperatura()["temperatura"]
        calidad_aire_data = cargar_sensores_calidad_aire()["calidad_aire"]

        rangos = cargar_valores_comparativos()

        for i, id_hab in enumerate(sorted(habitaciones_ui.keys())):
            hab = habitaciones_ui[id_hab]
            if not hab.page:
                continue

            textos = hab.content.controls

            textos[1].value = f"🌡️ {temperatura_data[i]}°C"
            textos[2].value = f"💧 {humedad_data[i]}%"
            textos[3].value = f"PM2.5: {calidad_aire_data['PM2.5'][i]}"
            textos[4].value = f"PM10: {calidad_aire_data['PM10'][i]}"
            textos[5].value = f"CO: {calidad_aire_data['CO'][i]}"
            textos[6].value = f"NO2: {calidad_aire_data['NO2'][i]}"
            textos[7].value = f"CO2: {calidad_aire_data['CO2'][i]}"
            textos[8].value = f"TVOC: {calidad_aire_data['TVOC'][i]}"

            hab.update()

    # -----------------------------------------------------------------
    # ACTUALIZACIÓN AUTOMÁTICA
    # -----------------------------------------------------------------
    async def actualizar_periodicamente():
        while True:
            try:
                refrescar_datos()
            except Exception as e:
                print("Error en actualización periódica:", e)
            await asyncio.sleep(10)  # cada 10 seg

    # -----------------------------------------------------------------
    # PARPADEO DE ALERTA
    # -----------------------------------------------------------------
    async def parpadeo_alerta():
        while True:
            for hab in list(habitaciones_parpadeo):
                hab.bgcolor = COLOR_ALERTA
                hab.update()
            await asyncio.sleep(2)
            for hab in list(habitaciones_parpadeo):
                if hab.page:
                    hab.bgcolor = hab.data["color_original"]
                    hab.update()
            await asyncio.sleep(6) # cada 6 seg

    # -----------------------------------------------------------------
    # LAYOUT PRINCIPAL
    # -----------------------------------------------------------------
    layout_principal = ft.Row(
        controls=[bloque_izquierdo, bloque_derecho],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    page.add(ft.Row(controls=[layout_principal], expand=True))

    reconstruir_mapa()
    page.run_task(actualizar_periodicamente)
    page.run_task(parpadeo_alerta)
