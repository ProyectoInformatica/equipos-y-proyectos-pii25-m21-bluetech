import flet as ft
import json
import os
import asyncio
from eliminar_habitacion import eliminar_habitacion  # Importar archivo eliminar_habitaciones
from crear_habitaciones import crear_habitacion_con_sensores  # Importar archivo crear_habitaciones

# Ruta del archivo JSON
RUTA_JSON = "habitacion.json"

# Cargar datos desde el JSON de habitacion
def cargar_datos():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    else:
        # Si no existe el archivo, inicializa estructura vacía
        return {"habitaciones": {"id_habitacion": [], "estado": []}}

# Cargar datos de sensores de humedad
def cargar_sensores_humedad():
    with open("sensores_humedad.json", "r") as archivo:
        return json.load(archivo)["sensores_hum"]

# Cargar datos de sensores de temperatura
def cargar_sensores_temperatura():
    with open("sensores_temperatura.json", "r") as archivo:
        return json.load(archivo)["sensores_temp"]

# Cargar datos de sensores de calidad del aire
def cargar_sensores_calidad_aire():
    with open("sensores_calidad_aire.json", "r") as archivo:
        return json.load(archivo)["sensores_cali_aire"]

# Cargar datos de valores comparativos (rangos aceptables)
def cargar_valores_comparativos():
    with open("valores_comparativos.json", "r") as archivo:
        return json.load(archivo)

def mostrar_pantalla_mapa_admin(page: ft.Page, repo, usuario):
    from vista.menu_admin_view import mostrar_pantalla_menu_admin
    page.clean()

    # Botón volver al menú
    boton_volver = ft.ElevatedButton(
        icon=ft.Icons.ARROW_BACK,
        text="Volver al menú",
        on_click=lambda e: mostrar_pantalla_menu_admin(page, repo, usuario)
    )

    global datos
    datos = cargar_datos()

    # Configuración inicial de la página
    page.title = "Mapa de Habitaciones por Planta"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = "auto"
    page.bgcolor = "#F0F0F0"

    #función para el boton de actualizar
    def actualizar(e):
        global datos
        datos.update(cargar_datos()) # Recarga datos desde JSON
        actualizar_mapa() # Redibuja el mapa

    # Botón actualizar con icono y texto
    boton_actualizar = ft.ElevatedButton(
        icon=ft.Icons.REFRESH,
        text="Actualizar",
        on_click=actualizar
    )

    # Coloca los botones de actualizar y volver al menu
    fila_superior = ft.Row(
        controls=[boton_volver, boton_actualizar],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Contenedor principal de plantas
    contenedor_plantas = ft.Column(spacing=30)

    # Dropdown de estado de habitacion para seleccionar el estado antes de crearla
    campo_estado = ft.Dropdown(
        label="Estado de la habitación",
        options=[ft.dropdown.Option("libre"), ft.dropdown.Option("ocupado")],
        value="libre"
    )

    #función para crear nuevas habitaciones
    def agregar_habitacion(e):
        global datos
        estado = campo_estado.value #recoge el estado introducido
        crear_habitacion_con_sensores(estado)  #crea una nueva habitación pasandole el estado
        datos = cargar_datos()  # recarga el JSON actualizado
        actualizar_dropdown_ids() #actualiza el dropdown de ids de eliminar
        actualizar_dropdown_plantas() #actualiza el dropdown de plantas de duplicar
        actualizar_mapa() #actualiza el mapa

    #botón para añadir nueva habitación llamando a la funcion agregar habitación
    boton_agregar = ft.ElevatedButton(text="➕ Añadir habitación", on_click=agregar_habitacion)

    #Dropdown de platas existentes (Para duplicar plantas)
    campo_planta = ft.Dropdown(
        label="Selecciona planta a duplicar",
        options=[],
        width=200
    )

    #función para actualizar el dropdown de las plantas para el caso de que se haya eliminado alguna de estas
    def actualizar_dropdown_plantas():
        datos_local = cargar_datos()
        total = len(datos_local["habitaciones"]["id_habitacion"])
        plantas = (total + 9) // 10 # Cada planta tiene 10 habitaciones
        campo_planta.options = [ft.dropdown.Option(str(p+1)) for p in range(plantas)]
        page.update()

    #actualiza el dropdown de las plantas (de duplicar plantas)
    actualizar_dropdown_plantas()

    #Dropdown para seleccionar el id de la habitación (para eliminar habitaciones)
    campo_id = ft.Dropdown(
        label="Selecciona ID de habitación",
        options=[],
        width=200
    )

    #Función para actualizar el dropdown de ids en caso de eliminarse alguna sala
    def actualizar_dropdown_ids():
        datos_local = cargar_datos()
        ids = sorted(datos_local["habitaciones"]["id_habitacion"]) #ordena los ids
        campo_id.options = [ft.dropdown.Option(str(i)) for i in ids]
        page.update()

    #Actualiza el dropdown de ids (para eliminar habitaciones)
    actualizar_dropdown_ids()

    #función para eliminar habitaciones
    def eliminar_habitaciones(e):
        global datos
        if not campo_id.value: #error en caso de que el id no se haya seleccionado
            page.open(ft.SnackBar(ft.Text("⚠️ Error: debes seleccionar un ID de habitación")))
            page.update()
            return
        #
        id_eliminar = int(campo_id.value)
        ok, mensaje = eliminar_habitacion(id_eliminar, datos, cargar_sensores_humedad, cargar_sensores_temperatura, cargar_sensores_calidad_aire)
        #
        if ok:
            datos = cargar_datos() #guarda los datos
            actualizar_dropdown_ids() #actualiza los ids existentes
            actualizar_dropdown_plantas() #actualiza las plantas existentes
            actualizar_mapa() #actualiza el mapa
        page.open(ft.SnackBar(ft.Text(mensaje)))
        page.update()

    #Botón para eliminar una sala seleccionada
    boton_eliminar = ft.ElevatedButton(text="🗑️ Eliminar sala", on_click=eliminar_habitaciones)

    # Función de confirmación antes de duplicar una planta
    def mostrar_confirmacion(e):
        if not campo_planta.value: #error en caso de que no se hay seleccionado ninguna planta 
            page.open(ft.SnackBar(ft.Text("⚠️ Error: debes seleccionar una planta antes de duplicar")))
            page.update()
            return
        # Verificar que la planta seleccionada tiene 10 habitaciones
        planta = int(campo_planta.value) - 1
        habitaciones_por_planta = 10
        inicio = planta * habitaciones_por_planta
        fin = inicio + habitaciones_por_planta
        ids = datos["habitaciones"]["id_habitacion"]
        ids_planta = ids[inicio:fin]
        if len(ids_planta) < habitaciones_por_planta:
            # Mostrar error en caso de que la planta seleccionada no tenga 10 habitaciones
            page.open(ft.SnackBar(ft.Text("⚠️ Error: la planta seleccionada no tiene 10 habitaciones completas")))
            page.update()
            return
        #Si pasa la validación, mostrar una alerta de confirmación
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmación"),
            content=ft.Text("¿Estás seguro de que quieres duplicar esta planta?"),
            actions=[
                ft.TextButton("Sí", on_click=lambda ev: ejecutar_duplicacion(ev, dlg_modal)), #realiza la duplicación de planta
                ft.TextButton("No", on_click=lambda ev: cancelar_duplicacion(ev, dlg_modal)), #cancela la duplicación de planta
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        #muestra la alerta
        page.open(dlg_modal) 

    #función para realizar la duplicación de plantas
    def ejecutar_duplicacion(e, dlg_modal):
        page.close(dlg_modal)
        duplicar_planta(e)
        #Mensaje de confirmación visual
        page.open(ft.SnackBar(ft.Text("✅ Planta duplicada correctamente")))
        page.update()

    #función para cancelar la duplicación de planta
    def cancelar_duplicacion(e, dlg_modal):
        page.close(dlg_modal)
        #Mensaje de cancelación de duplicación de planta
        page.open(ft.SnackBar(ft.Text("❌ Duplicación cancelada")))
        page.update()

    #Botón para duplicar una planta
    boton_duplicar = ft.ElevatedButton(text="📑 Duplicar planta", on_click=mostrar_confirmacion)

    #función para duplicar una planta entera
    def duplicar_planta(e):
        global datos
        if not campo_planta.value:
            return

        # Cada planta tiene 10 habitaciones
        planta = int(campo_planta.value) - 1
        habitaciones_por_planta = 10
        inicio = planta * habitaciones_por_planta
        fin = inicio + habitaciones_por_planta

        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]

        # Crear 10 habitaciones nuevas usando la función existente
        for i in range(inicio, min(fin, len(ids))):
            estado_original = estados[i]
            crear_habitacion_con_sensores(estado_original)

        # Actualizar datos, dropdowns y mapa
        datos.update(cargar_datos())
        actualizar_dropdown_ids()
        actualizar_dropdown_plantas()
        actualizar_mapa()

        # Mensaje de confirmación visual
        page.snack_bar = ft.SnackBar(ft.Text("✅ Se han creado 10 habitaciones nuevas"))
        page.snack_bar.open = True
        page.update()
    
    #Contenido botones (contiene todos los botones y dropdows)
    fila_acciones = ft.Row(
        controls=[boton_agregar, campo_estado, boton_duplicar, campo_planta, boton_eliminar, campo_id],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

    #función que construye el bloque visula de cada habitación
    def crear_habitacion(index, id_hab, estado, humedad, temperatura, calidad_aire, rangos):
        # Función auxiliar: devuelve color de texto amarillo si el valor está fuera de rango
        def color_si_fuera_rango(valor, min_val=None, max_val=None):
            if min_val is not None and valor < min_val:
                return "yellow"
            if max_val is not None and valor > max_val:
                return "yellow"
            return "black"
        # Validación general para el fondo
        en_rango = (
            rangos["temperatura"]["min"] <= temperatura <= rangos["temperatura"]["max"]
            and rangos["humedad"]["min"] <= humedad <= rangos["humedad"]["max"]
            and all(calidad_aire[clave][index] <= rangos["calidad_aire"][clave]["max"]
                    for clave in rangos["calidad_aire"])
        )
        # Color de fondo según estado y si cumple con los rangos establecidos
        fondo = "green" if en_rango else ("red" if estado == "ocupado" else "orange")
        # Contenido textual de la habitación (ID + valores de sensores)
        contenido = ft.Column([
            ft.Text(f"H{id_hab}", size=16, weight="bold", color="gray"),
            ft.Text(f"🌡️ {temperatura}°C", size=15,
                    color=color_si_fuera_rango(temperatura, rangos["temperatura"]["min"], rangos["temperatura"]["max"])),
            ft.Text(f"💧 {humedad}%", size=15,
                    color=color_si_fuera_rango(humedad, rangos["humedad"]["min"], rangos["humedad"]["max"])),
            ft.Text(f"PM2.5: {calidad_aire['PM2.5'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["PM2.5"][index], max_val=rangos["calidad_aire"]["PM2.5"]["max"])),
            ft.Text(f"PM10: {calidad_aire['PM10'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["PM10"][index], max_val=rangos["calidad_aire"]["PM10"]["max"])),
            ft.Text(f"CO: {calidad_aire['CO'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["CO"][index], max_val=rangos["calidad_aire"]["CO"]["max"])),
            ft.Text(f"NO2: {calidad_aire['NO2'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["NO2"][index], max_val=rangos["calidad_aire"]["NO2"]["max"])),
            ft.Text(f"CO2: {calidad_aire['CO2'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["CO2"][index], max_val=rangos["calidad_aire"]["CO2"]["max"])),
            ft.Text(f"TVOC: {calidad_aire['TVOC'][index]}", size=13,
                    color=color_si_fuera_rango(calidad_aire["TVOC"][index], max_val=rangos["calidad_aire"]["TVOC"]["max"]))
        ], spacing=1, alignment=ft.MainAxisAlignment.CENTER)
        # Devuelve el contenedor visual de la habitación
        return ft.Container(
            content=contenido,
            width=120,
            height=200,
            bgcolor=fondo,
            border=ft.border.all(2, "black"),
            alignment=ft.alignment.center,
            padding=5
        )

    # Función que actualiza/redibuja el mapa completo de habitaciones
    def actualizar_mapa():
        global datos
        datos = cargar_datos()
        contenedor_plantas.controls.clear() # Limpia el mapa antes de redibujar
        #Cargar datos de habitaciones y sensores
        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]
        humedad_data = cargar_sensores_humedad()["humedad"]
        temperatura_data = cargar_sensores_temperatura()["temperatura"]
        calidad_aire_data = cargar_sensores_calidad_aire()["calidad_aire"]
        # Crear lista de tuplas con todos los datos de cada habitación
        habitaciones = [
            (id_hab, estado, temperatura, humedad,
            {clave: calidad_aire_data[clave][i] for clave in calidad_aire_data})
            for i, (id_hab, estado, temperatura, humedad) in enumerate(zip(ids, estados, temperatura_data, humedad_data))
        ]
        # Ordenar habitaciones por ID para que aparezcan en orden
        habitaciones.sort(key=lambda x: x[0])
        try: # Rangos de validación
            rangos = cargar_valores_comparativos() 
        except Exception as e:#maneja error en caso de no conseguir cargar los rangos de validación
            print("Error cargando valores comparativos:", e) 
            return
        # Construir plantas (10 habitaciones por planta)
        for planta in range((len(habitaciones) + 9) // 10):
            inicio = planta * 10
            fin = inicio + 10
            fila1 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            fila2 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            # Crear visualización de cada habitación en la planta
            for i, (id_hab, estado, temperatura, humedad, calidad_aire) in enumerate(habitaciones[inicio:fin]):
                habitacion = crear_habitacion(
                    index=i,
                    id_hab=id_hab,
                    estado=estado,
                    humedad=humedad,
                    temperatura=temperatura,
                    calidad_aire=calidad_aire_data,
                    rangos=rangos
                )
                if i < 5:
                    fila1.controls.append(habitacion)
                else:
                    fila2.controls.append(habitacion)
            # Añadir la planta completa al contenedor principal
            contenedor_plantas.controls.append(
                ft.Column([
                    ft.Text(f"🏢 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                    fila1,
                    fila2
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )
        page.update() # Refresca la interfaz

    # Añadir todo al layout principal
    page.add(
        ft.Column(
            controls=[
                fila_superior,
                ft.Text("🗺️ Mapa de Habitaciones", size=24, weight="bold", color="blue"),
                fila_acciones,
                contenedor_plantas
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

    #Inicializa el mapa al arrancar
    actualizar_mapa()

    #Actualización automática cada 10 segundos
    async def actualizar_periodicamente():
        global datos
        while True:
            try:
                actualizar_mapa()
            except Exception as e: #mensaje en caso de fallo al actualizar automaticamente el mapa
                print("Error en actualización periódica:", e)
            await asyncio.sleep(10) #actualizado cada 10 seg

    # Lanza la tarea de actualización periódica
    page.run_task(actualizar_periodicamente)