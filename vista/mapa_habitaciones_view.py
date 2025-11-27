import flet as ft
import json
import os
import asyncio
from funcionalidad.crear_habitaciones import crear_habitacion_con_sensores

# Ruta del archivo JSON
RUTA_JSON = "habitacion.json"

# Cargar datos desde el JSON
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

# Guardar datos en el JSON
def guardar_datos(datos):
    with open(RUTA_JSON, "w") as archivo:
        json.dump(datos, archivo, indent=4)

def main(page: ft.Page):
    global datos
    datos = cargar_datos()
    page.title = "Mapa de Habitaciones por Planta"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = "auto"
    page.bgcolor = "#F0F0F0"

    def actualizar(e):
        global datos
        # Aquí llamas a tu función actualizar_mapa()
        datos.update(cargar_datos())
        actualizar_mapa()

    # Botón con icono y texto
    boton_actualizar = ft.ElevatedButton(
        icon=ft.Icons.REFRESH,
        text="Actualizar",
        on_click=actualizar
    )

    # Fila alineada a la derecha
    fila_superior = ft.Row(
        controls=[boton_actualizar],
        alignment=ft.MainAxisAlignment.END
    )

    contenedor_plantas = ft.Column(spacing=30)

    def sensores_en_rango(index, temperatura, humedad, calidad_aire, rangos):
        if not (rangos["temperatura"]["min"] <= temperatura <= rangos["temperatura"]["max"]):
            return False
        if not (rangos["humedad"]["min"] <= humedad <= rangos["humedad"]["max"]):
            return False

        for clave, limites in rangos["calidad_aire"].items():
            if calidad_aire[clave][index] > limites["max"]:
                return False

        return True

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

        fondo = "green" if en_rango else ("red" if estado == "ocupado" else "orange")

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

        return ft.Container(
            content=contenido,
            width=120,
            height=200,
            bgcolor=fondo,
            border=ft.border.all(2, "black"),
            alignment=ft.alignment.center,
            padding=5
        )


    def actualizar_mapa():
        global datos
        datos = cargar_datos()
        contenedor_plantas.controls.clear()
        ids = datos["habitaciones"]["id_habitacion"]
        estados = datos["habitaciones"]["estado"]
        humedad_data = cargar_sensores_humedad()["humedad"]
        temperatura_data = cargar_sensores_temperatura()["temperatura"]
        calidad_aire_data = cargar_sensores_calidad_aire()["calidad_aire"]
        try:
            rangos = cargar_valores_comparativos()
        except Exception as e:
            print("Error cargando valores comparativos:", e)
            return

        total = len(ids)
        habitaciones_por_planta = 10

        for planta in range((total + 9) // 10):  # Calcula cuántas plantas hacen falta
            inicio = planta * habitaciones_por_planta
            fin = inicio + habitaciones_por_planta
            ids_planta = ids[inicio:fin]
            estados_planta = estados[inicio:fin]

            fila1 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            fila2 = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

            for i, (id_hab, estado) in enumerate(zip(ids_planta, estados_planta)):
                habitacion = crear_habitacion(
                    index=inicio + i,
                    id_hab=id_hab,
                    estado=estado,
                    humedad=humedad_data[inicio + i],
                    temperatura=temperatura_data[inicio + i],
                    calidad_aire=calidad_aire_data,
                    rangos=rangos
                )
                if i < 5:
                    fila1.controls.append(habitacion)
                else:
                    fila2.controls.append(habitacion)

            contenedor_plantas.controls.append(
                ft.Column([
                    ft.Text(f"🏢 Planta {planta + 1}", size=20, weight="bold", color="blue"),
                    fila1,
                    fila2
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )

        page.update()

    campo_estado = ft.Dropdown(
        label="Estado de la habitación",
        options=[ft.dropdown.Option("libre"), ft.dropdown.Option("ocupado")],
        value="libre"
    )

    def agregar_habitacion(e):
        global datos
        estado = campo_estado.value
        nuevo_id = crear_habitacion_con_sensores(estado) 
        datos.update(cargar_datos())  # recarga el JSON actualizado
        actualizar_mapa()

    boton_agregar = ft.ElevatedButton(text="➕ Añadir habitación", on_click=agregar_habitacion)

    fila_acciones = ft.Row(
        controls=[boton_agregar, campo_estado],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

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

    actualizar_mapa()

    # 🔁 Actualización automática cada 30 segundos
    async def actualizar_periodicamente():
        global datos
        while True:
            try:
                actualizar_mapa()
            except Exception as e:
                print("Error en actualización periódica:", e)
            await asyncio.sleep(10)

    page.run_task(actualizar_periodicamente)

ft.app(target=main)