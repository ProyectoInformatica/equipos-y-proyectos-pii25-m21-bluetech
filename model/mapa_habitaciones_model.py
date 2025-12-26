import json
import os
from model.eliminar_habitacion import eliminar_habitacion
from model.crear_habitaciones import crear_habitacion_con_sensores

RUTA_JSON = "data/habitacion.json"

def cargar_datos():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    else:
        return {"habitaciones": {"id_habitacion": [], "estado": []}}

def cargar_json(ruta, clave):
    with open(ruta, "r") as f:
        return json.load(f)[clave]

def cargar_sensores():
    return {
        "humedad": cargar_json("data/sensores_humedad.json", "sensores_hum")["humedad"],
        "temperatura": cargar_json("data/sensores_temperatura.json", "sensores_temp")["temperatura"],
        "calidad_aire": cargar_json("data/sensores_calidad_aire.json", "sensores_cali_aire")["calidad_aire"],
    }

def cargar_rangos():
    with open("data/valores_comparativos.json", "r") as f:
        return json.load(f)

def cargar_sensores_humedad():
    with open("data/sensores_humedad.json", "r") as archivo:
        return json.load(archivo)["sensores_hum"]

def cargar_sensores_temperatura():
    with open("data/sensores_temperatura.json", "r") as archivo:
        return json.load(archivo)["sensores_temp"]

def cargar_sensores_calidad_aire():
    with open("data/sensores_calidad_aire.json", "r") as archivo:
        return json.load(archivo)["sensores_cali_aire"]

def cargar_valores_comparativos():
    with open("data/valores_comparativos.json", "r") as archivo:
        return json.load(archivo)

# ------------------------------------------------
# FUNCIONES DE NEGOCIO
# ------------------------------------------------
def crear_nueva_habitacion(estado, tipo_sala):
    nuevo_id = crear_habitacion_con_sensores(estado, tipo_sala)
    return nuevo_id

def eliminar_habitacion_por_id(id_hab, datos):
    return eliminar_habitacion(id_hab, datos, cargar_sensores_humedad, cargar_sensores_temperatura, cargar_sensores_calidad_aire)

def duplicar_planta(datos, planta_index):
    habitaciones_por_planta = 10
    inicio = planta_index * habitaciones_por_planta
    fin = inicio + habitaciones_por_planta
    ids = datos["habitaciones"]["id_habitacion"]
    estados = datos["habitaciones"]["estado"]
    tipos = datos["habitaciones"]["tipo_sala"]

    for i in range(inicio, min(fin, len(ids))):
        crear_habitacion_con_sensores(estados[i], tipos[i])

def eliminar_planta_completa(datos, planta_index):
    habitaciones_por_planta = 10
    inicio = planta_index * habitaciones_por_planta
    fin = inicio + habitaciones_por_planta
    ids = datos["habitaciones"]["id_habitacion"]
    ids_planta = ids[inicio:fin]
    for id_hab in sorted(ids_planta, reverse=True):
        eliminar_habitacion(id_hab, datos, cargar_sensores_humedad, cargar_sensores_temperatura, cargar_sensores_calidad_aire)