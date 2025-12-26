import flet as ft
import asyncio
from controller.mapa_habitaciones_admin_controller import (
    obtener_datos,
    agregar_habitacion,
    eliminar_habitacion_control,
    duplicar_planta_control,
    eliminar_planta_control,
    obtener_sensores
)

# ---------------------------------------------------------------------
# Variables globales para UI
# ---------------------------------------------------------------------
habitaciones_parpadeo = []
COLOR_ALERTA = "#FF8181"
habitacion_expandida_id = None
habitaciones_ui = {}
necesita_reconstruccion = True

# ---------------------------------------------------------------------
# PANTALLA PRINCIPAL: MAPA EN DOS BLOQUES
# ---------------------------------------------------------------------
def mostrar_pantalla_mapa_admin(page: ft.Page, repo, usuario):
    from view.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()

    page.title = "Mapa de Habitaciones - Hospital"
    page.scroll = None
    page.bgcolor = "#F0F0F0"

    bloque_abierto = None
    global datos
    datos = obtener_datos()

    # -----------------------------------------------------------------
    # BOTONES SUPERIORES
    # -----------------------------------------------------------------
    boton_volver = ft.ElevatedButton(
        icon=ft.Icons.ARROW_BACK,
        text="Volver al menú",
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario)
    )

    def actualizar(e):
        global datos, necesita_reconstruccion
        necesita_reconstruccion = True
        datos = obtener_datos()
        reconstruir_mapa()
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

    campo_planta = ft.Dropdown(label="Selecciona planta", options=[], width=200)
    campo_id_text = ft.TextField(label="ID de habitación a eliminar", width=200)
    mensaje_error_eliminar = ft.Text("", size=12, color="red")

    # -----------------------------------------------------------------
    # CALLBACKS DE BOTONES
    # -----------------------------------------------------------------
    def agregar_habitacion_ui(e):
        global datos, necesita_reconstruccion
        necesita_reconstruccion = True
        estado = campo_estado.value
        tipo_sala = campo_tipo_sala.value
        agregar_habitacion(estado, tipo_sala)
        datos = obtener_datos()
        actualizar_dropdown_plantas()
        reconstruir_mapa()
        page.open(ft.SnackBar(ft.Text(f"✅ Habitación creada correctamente")))
        page.update()

    boton_agregar = ft.ElevatedButton(text="➕ Crear Sala", on_click=agregar_habitacion_ui)

    def eliminar_habitacion_ui(e):
        global datos, necesita_reconstruccion
        necesita_reconstruccion = True
        mensaje_error_eliminar.value = ""
        try:
            id_eliminar = int(campo_id_text.value)
        except:
            mensaje_error_eliminar.value = "❌ ID inválido"
            page.update()
            return

        ok, mensaje, datos = eliminar_habitacion_control(id_eliminar)
        if ok:
            actualizar_dropdown_plantas()
            reconstruir_mapa()
            mensaje_error_eliminar.value = ""
            page.open(ft.SnackBar(ft.Text(f"✅ Habitación H{id_eliminar} eliminada correctamente")))
        else:
            mensaje_error_eliminar.value = f"❌ {mensaje}"
        page.update()

    boton_eliminar_sala = ft.ElevatedButton(text="🗑️ Eliminar Sala", on_click=eliminar_habitacion_ui)

    def ejecutar_duplicacion(e, dlg):
        page.close(dlg)
        duplicar_planta_ui()
        page.open(ft.SnackBar(ft.Text("✅ Planta duplicada correctamente")))
        page.update()

    def ejecutar_eliminacion_planta(e, dlg):
        page.close(dlg)
        eliminar_planta_ui()
        page.open(ft.SnackBar(ft.Text("✅ Planta eliminada correctamente")))
        page.update()

    def cancelar_dialogo(e, dlg):
        page.close(dlg)
        page.open(ft.SnackBar(ft.Text("❌ Acción cancelada")))
        page.update()

    def duplicar_planta_ui():
        global datos, necesita_reconstruccion
        necesita_reconstruccion = True
        if not campo_planta.value:
            return
        datos = duplicar_planta_control(int(campo_planta.value)-1)
        actualizar_dropdown_plantas()
        reconstruir_mapa()

    def eliminar_planta_ui():
        global datos, necesita_reconstruccion
        necesita_reconstruccion = True
        if not campo_planta.value:
            return
        indice = int(campo_planta.value) - 1
        if not planta_completa(indice):
            page.open(ft.SnackBar(
                ft.Text("⚠️ La planta debe tener 10 habitaciones para duplicarse")
            ))
            page.update()
            return
        datos = eliminar_planta_control(int(campo_planta.value)-1)
        actualizar_dropdown_plantas()
        reconstruir_mapa()

    def mostrar_confirmacion_duplicar(e):
        if not campo_planta.value:
            page.open(ft.SnackBar(ft.Text("⚠️ Selecciona una planta para gestionar")))
            page.update()
            return
        indice = int(campo_planta.value) - 1
        if not planta_completa(indice):
            page.open(ft.SnackBar(
                ft.Text("⚠️ La planta debe tener 10 habitaciones para duplicarse")
            ))
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

    def mostrar_confirmacion_eliminar_planta(e):
        if not campo_planta.value:
            page.open(ft.SnackBar(ft.Text("⚠️ Selecciona una planta para gestionar")))
            page.update()
            return
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmación"),
            content=ft.Text(f"⚠️ ¿Quieres eliminar COMPLETAMENTE la planta {campo_planta.value}?"),
            actions=[
                ft.TextButton("Sí", on_click=lambda ev: ejecutar_eliminacion_planta(ev, dlg)),
                ft.TextButton("No", on_click=lambda ev: cancelar_dialogo(ev, dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg)

    boton_duplicar = ft.ElevatedButton(text="📑 Duplicar Planta", on_click=mostrar_confirmacion_duplicar)
    boton_eliminar_planta = ft.ElevatedButton(text="🗑️ Eliminar Planta", on_click=mostrar_confirmacion_eliminar_planta)

    # -----------------------------------------------------------------
    # FUNCIONES AUXILIARES DE UI
    # -----------------------------------------------------------------
    def planta_completa(indice_planta):
        datos_local = obtener_datos()
        total = len(datos_local["habitaciones"]["id_habitacion"])
        inicio = indice_planta * 10
        fin = inicio + 10
        return fin <= total

    def actualizar_dropdown_plantas():
        datos_local = obtener_datos()
        total = len(datos_local["habitaciones"]["id_habitacion"])
        plantas = (total + 9) // 10
        campo_planta.options = [ft.dropdown.Option(str(p+1)) for p in range(plantas)] if plantas > 0 else []
        page.update()

    actualizar_dropdown_plantas()

    contenedor_plantas = ft.Column(spacing=30, scroll=ft.ScrollMode.AUTO, expand=True)

    # -----------------------------------------------------------------
    # CREACIÓN DE HABITACIÓN (UI)
    # -----------------------------------------------------------------
    def crear_habitacion(index, id_hab, estado, humedad, temperatura, calidad_aire_data, rangos):
        # misma lógica de colores y textos que tu código original
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

        fondo = "green" if en_rango else "red"
        borde = ft.border.all(2, "black") if estado=="ocupado" else None
        textos = [
            ft.Text(f"H{id_hab}", size=8, weight="bold", color="gray"),
            ft.Text(f"🌡️ {temperatura}°C", size=7, color=color_si_fuera_rango(temperatura, rangos["temperatura"]["min"], rangos["temperatura"]["max"])),
            ft.Text(f"💧 {humedad}%", size=7, color=color_si_fuera_rango(humedad, rangos["humedad"]["min"], rangos["humedad"]["max"])),
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
        debe_parpadear = (estado=="ocupado" and not en_rango)
        contenido = ft.Column(textos, spacing=1, alignment=ft.MainAxisAlignment.CENTER)

        def toggle_expand(e):
            nonlocal bloque_abierto
            global habitacion_expandida_id
            id_actual = e.control.data.get("id_habitacion")
            if id_actual is None:
                return
            if necesita_reconstruccion:
                return
            if bloque_abierto and bloque_abierto!=e.control:
                if bloque_abierto.page:
                    bloque_abierto.width=80
                    bloque_abierto.height=120
                    for i, txt in enumerate(bloque_abierto.content.controls):
                        txt.size = 7 if i>0 else 8
                    bloque_abierto.update()
                bloque_abierto=None

            if e.control.width==80:
                e.control.width=170
                e.control.height=240
                for i, txt in enumerate(textos):
                    txt.size=16 if i>0 else 18
                bloque_abierto=e.control
                habitacion_expandida_id=id_actual
            else:
                e.control.width=80
                e.control.height=120
                for i, txt in enumerate(textos):
                    txt.size=7 if i>0 else 8
                bloque_abierto=None
                habitacion_expandida_id=None

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

    # -----------------------------------------------------------------
    # RECONSTRUIR MAPA
    # -----------------------------------------------------------------
    def reconstruir_mapa():
        global datos, habitaciones_parpadeo, bloque_abierto, habitacion_expandida_id, necesita_reconstruccion
        necesita_reconstruccion = False
        habitacion_expandida_id = None
        bloque_abierto = None
        habitaciones_ui.clear()
        contenedor_plantas.controls.clear()
        habitaciones_parpadeo.clear()
        datos = obtener_datos()

        sensores = obtener_sensores()
        humedad_data = sensores["humedad"]["humedad"]  # extraer la lista interna
        temperatura_data = sensores["temperatura"]["temperatura"]  # idem
        calidad_aire_data = sensores["calidad_aire"]["calidad_aire"]
        rangos = sensores["valores_comparativos"]

        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]
        total_habs = len(ids)
        total_plantas = (total_habs + 9) // 10

        for planta in range(total_plantas):
            inicio = planta * 10
            fin = min(inicio + 10, total_habs)
            fila1 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            fila2 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

            for i, (id_hab, estado) in enumerate(zip(ids[inicio:fin], estados[inicio:fin])):
                # extraer valores de rangos individuales
                temp_min = rangos["temperatura"]["min"][0] if isinstance(rangos["temperatura"]["min"], list) else rangos["temperatura"]["min"]
                temp_max = rangos["temperatura"]["max"][0] if isinstance(rangos["temperatura"]["max"], list) else rangos["temperatura"]["max"]

                hum_min = rangos["humedad"]["min"][0] if isinstance(rangos["humedad"]["min"], list) else rangos["humedad"]["min"]
                hum_max = rangos["humedad"]["max"][0] if isinstance(rangos["humedad"]["max"], list) else rangos["humedad"]["max"]

                # crear la habitación pasando los valores correctos
                hab_ui = crear_habitacion(
                    i + inicio,
                    id_hab,
                    estado,
                    humedad_data[i + inicio],
                    temperatura_data[i + inicio],
                    calidad_aire_data,
                    rangos
                )

                if habitacion_expandida_id == id_hab:
                    hab_ui.width = 170
                    hab_ui.height = 240
                    for i, txt in enumerate(hab_ui.content.controls):
                        txt.size = 16 if i > 0 else 18
                    bloque_abierto = hab_ui

                if i < 5:
                    fila1.controls.append(hab_ui)
                else:
                    fila2.controls.append(hab_ui)

            contenedor_plantas.controls.append(
                ft.Column(
                    [
                        ft.Text(f"🏥 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                        fila1,
                        fila2
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )

        page.update()

    # -----------------------------------------------------------------
    # ACTUALIZACIÓN AUTOMÁTICA Y PARPADEO
    # -----------------------------------------------------------------
    def actualizar_sensores_y_colores():
        global datos
        if not habitaciones_ui:
            return

        sensores = obtener_sensores()
        humedad_data = sensores["humedad"]["humedad"]
        temperatura_data = sensores["temperatura"]["temperatura"]
        calidad_aire_data = sensores["calidad_aire"]["calidad_aire"]
        rangos = sensores["valores_comparativos"]

        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]

        for i, id_hab in enumerate(ids):
            hab_ui = habitaciones_ui.get(id_hab)
            if not hab_ui:
                continue  # la habitación aún no existe en UI

            temperatura = temperatura_data[i]
            humedad = humedad_data[i]

            en_rango = (
                rangos["temperatura"]["min"] <= temperatura <= rangos["temperatura"]["max"]
                and rangos["humedad"]["min"] <= humedad <= rangos["humedad"]["max"]
                and all(calidad_aire_data[clave][i] <= rangos["calidad_aire"][clave]["max"]
                        for clave in rangos["calidad_aire"])
            )

            # actualizar color de fondo
            hab_ui.bgcolor = "green" if en_rango else "red"
            hab_ui.data["color_original"] = hab_ui.bgcolor

            # actualizar textos individuales
            controles = hab_ui.content.controls
            controles[1].value = f"🌡️ {temperatura}°C"
            controles[1].color = "black" if rangos["temperatura"]["min"] <= temperatura <= rangos["temperatura"]["max"] else "yellow"

            controles[2].value = f"💧 {humedad}%"
            controles[2].color = "black" if rangos["humedad"]["min"] <= humedad <= rangos["humedad"]["max"] else "yellow"

            for j, clave in enumerate(["PM2.5","PM10","CO","NO2","CO2","TVOC"], start=3):
                valor = calidad_aire_data[clave][i]
                controles[j].value = f"{clave}: {valor}"
                controles[j].color = "black" if valor <= rangos["calidad_aire"][clave]["max"] else "yellow"

            hab_ui.update()

    async def actualizar_periodicamente():
        while True:
            try:
                actualizar_sensores_y_colores()  # solo actualizar datos y colores
            except Exception as e:
                print("Error actualización periódica:", e)
            await asyncio.sleep(10)

    async def parpadeo_alerta():
        while True:
            for hab in list(habitaciones_parpadeo):
                if not hab.page:
                    continue
                hab.bgcolor = COLOR_ALERTA
                hab.update()

            await asyncio.sleep(2)

            for hab in list(habitaciones_parpadeo):
                if not hab.page:
                    continue
                hab.bgcolor = hab.data["color_original"]
                hab.update()

            await asyncio.sleep(6)


    # -----------------------------------------------------------------
    # LAYOUT PRINCIPAL
    # -----------------------------------------------------------------
    fila_agregar = ft.Row(
        controls=[boton_agregar, ft.Column([campo_estado, campo_tipo_sala], spacing=5, alignment=ft.MainAxisAlignment.START)],
        spacing=15,
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
            ft.Row([boton_eliminar_planta], spacing=5),
            ft.Divider(),
            ft.Row([boton_actualizar, boton_volver], spacing=10)
        ],
        width=420,
        spacing=15,
        alignment=ft.MainAxisAlignment.START
    )

    bloque_derecho = ft.Container(content=contenedor_plantas, bgcolor="#E6F2FF", border=ft.border.all(4, "blue"), padding=20, expand=True)

    layout_principal = ft.Row(controls=[bloque_izquierdo, bloque_derecho], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
    page.add(ft.Row(controls=[layout_principal], expand=True))

    reconstruir_mapa()
    page.run_task(actualizar_periodicamente)
    page.run_task(parpadeo_alerta)
