import json
import threading
import time
import random
import os
from copy import deepcopy
from datetime import datetime #fecha y hora actual
from valores_comparativos_model import cargar_valores
from ticket_model import TicketModel

ticket_model = TicketModel()
mutex = threading.Lock()

# ===============================
# FUNCIONES GENERALES
# ===============================
def leer_json(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error leyendo {ruta}: {e}")
        return {}

def escribir_json(ruta, datos):
    try:
        with open(ruta, "w") as f:
            json.dump(datos, f, indent=4)
    except Exception as e:
        print(f"Error escribiendo {ruta}: {e}")

# ===============================
# SISTEMA TICKETS
# ===============================
def cargar_limites():
    """Carga los rangos desde tu archivo de configuración."""
    try:
        with open("data/valores_comparativos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def comprobar_alerta(id_hab, id_sensor, tipo, valor):
    """Verifica el valor y llama al generador de tickets si es necesario."""
    rangos = cargar_limites()
    fuera_de_rango = False
    limite_str = ""
    descripcion = ""

    # Lógica para Temperatura y Humedad
    if tipo in ["temperatura", "humedad"] and tipo in rangos:
        conf = rangos[tipo]
        if valor < conf["min"] or valor > conf["max"]:
            fuera_de_rango = True
            limite_str = f"{conf['min']}-{conf['max']} {conf.get('unidad', '')}"
            descripcion = f"Valor de {tipo} fuera de rango: {valor}"

    # Lógica para Gases (Calidad del Aire)
    elif "calidad_aire" in rangos and tipo in rangos["calidad_aire"]:
        conf = rangos["calidad_aire"][tipo]
        if valor > conf["max"]:
            fuera_de_rango = True
            limite_str = f"Máx {conf['max']} {conf.get('unidad', '')}"
            descripcion = f"Nivel crítico de {tipo}: {valor}"

    if fuera_de_rango:
        # Aquí usamos la función que ya tiene el filtro de duplicados
        ticket_model.generar_ticket_automatico(
            id_habitacion=id_hab,
            id_sensor=id_sensor,
            nombre="Sistema Automático",
            tipo_sensor=tipo,
            valor_detectado=valor,
            limite_establecido=limite_str,
            descripcion=descripcion
        )

# ===============================
# HILO TEMPERATURA
# ===============================
def simular_temperatura(ruta, intervalo=5):
    while True:
        with mutex:
            data = leer_json(ruta)
            if "sensores_temp" in data:
                # Acceso directo para asegurar que se modifica el objeto 'data'
                ids = data["sensores_temp"].get("id_sensor", [])
                temps = data["sensores_temp"].get("temperatura", [])

                for i in range(len(temps)):
                    temps[i] = max(15, min(40, temps[i] + random.randint(-1, 1)))
                    # IMPORTANTE: No hace falta reasignar a data porque las listas son mutables
                    # Pero el ID es necesario para el ticket
                    comprobar_alerta(i+1, ids[i], "temperatura", temps[i])

                escribir_json(ruta, data) # Ahora 'data' lleva los valores nuevos
        time.sleep(intervalo)

# ===============================
# HILO HUMEDAD
# ===============================
def simular_humedad(ruta, intervalo=6):
    while True:
        with mutex:
            data = leer_json(ruta)
            if "sensores_hum" in data:
                ids = data["sensores_hum"].get("id_sensor", [])
                hums = data["sensores_hum"].get("humedad", [])

                for i in range(len(hums)):
                    hums[i] = max(20, min(90, hums[i] + random.randint(-3, 3)))
                    comprobar_alerta(i+1, ids[i], "humedad", hums[i])

                escribir_json(ruta, data)
        time.sleep(intervalo)

# ===============================
# HILO CALIDAD DEL AIRE
# ===============================
def simular_calidad_aire(ruta, intervalo=7):
    while True:
        with mutex:
            data = leer_json(ruta)
            if "sensores_cali_aire" in data:
                ids = data["sensores_cali_aire"].get("id_sensor", [])
                aire_dict = data["sensores_cali_aire"].get("calidad_aire", {})

                for gas, valores in aire_dict.items():
                    for i in range(len(valores)):
                        valores[i] = max(0, valores[i] + random.randint(-5, 5))
                        # Obtenemos el ID correspondiente al índice i
                        id_s = ids[i] if i < len(ids) else 0
                        comprobar_alerta(i+1, id_s, gas, valores[i])

                escribir_json(ruta, data)
        time.sleep(intervalo)

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    hilos = [
        threading.Thread(target=simular_temperatura, args=("data/sensores_temperatura.json",), daemon=True),
        threading.Thread(target=simular_humedad, args=("data/sensores_humedad.json",), daemon=True),
        threading.Thread(target=simular_calidad_aire, args=("data/sensores_calidad_aire.json",), daemon=True)
    ]

    for h in hilos:
        h.start()

    print("Simulación iniciada. Presione Ctrl+C para detener.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulación detenida.")