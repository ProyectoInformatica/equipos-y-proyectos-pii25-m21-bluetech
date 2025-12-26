import json
import os

RUTA_JSON = "data/habitacion.json"

def cargar_datos():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    return {"habitaciones": {"id_habitacion": [], "estado": []}}

def guardar_habitaciones(data):
    with open(RUTA_JSON, "w") as f:
        json.dump(data, f, indent=4)

def cambiar_estado_habitacion(index):
    data = cargar_datos()
    estado_actual = data["habitaciones"]["estado"][index]
    nuevo_estado = "libre" if estado_actual == "ocupado" else "ocupado"
    data["habitaciones"]["estado"][index] = nuevo_estado
    guardar_habitaciones(data)
    return nuevo_estado
