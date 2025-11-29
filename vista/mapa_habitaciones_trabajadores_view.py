import flet as ft
import json
import os
import asyncio

# Ruta del archivo JSON
RUTA_JSON = "habitacion.json"

#funciones para cargar los datos de los json correspondientes
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

def mostrar_pantalla_mapa_habitaciones_trabajadores(page: ft.Page, repo, usuario):
    from vista.menu_trabajador_view import mostrar_pantalla_menu_trabajador 
    global datos
    datos = cargar_datos()
    page.clean()  

    # Configuración inicial de la página
    page.title = "Mapa de Habitaciones por Planta"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = "auto"
    page.bgcolor = "#F0F0F0"

    contenedor_plantas = ft.Column(spacing=30)

    #función para el boton de actualizar
    def actualizar(e):
        global datos
        datos.update(cargar_datos())
        actualizar_mapa()

    # Botón para actualizar el mapa
    boton_actualizar = ft.ElevatedButton(
        icon=ft.Icons.REFRESH,
        text="Actualizar mapa",
        on_click=actualizar
    )

    # Botón volver al menú
    boton_volver = ft.ElevatedButton(
        icon=ft.Icons.ARROW_BACK,
        text="Volver al menú",
        on_click=lambda e: mostrar_pantalla_menu_trabajador(page, repo, usuario)
    )

    # Fila superior con ambos botones
    fila_superior = ft.Row(
        controls=[boton_volver, boton_actualizar],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    #función que construye el bloque visula de cada habitación
    def crear_habitacion(index, id_hab, estado, humedad, temperatura, calidad_aire, rangos):
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
        contenedor_plantas.controls.clear()  # Limpia el mapa antes de redibujar
        # Cargar datos de habitaciones y sensores
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
        except Exception as e: #maneja error en caso de no conseguir cargar los rangos de validación
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
        page.update()  # Refresca la interfaz

    # Añadir todo al layout principal
    page.add(
        ft.Column(
            controls=[
                fila_superior,
                ft.Text("🗺️ Mapa de Habitaciones", size=24, weight="bold", color="blue"),
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
