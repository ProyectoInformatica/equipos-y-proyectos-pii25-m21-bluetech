import json
import threading
import time
import random
from copy import deepcopy

# ===============================
# FUNCIONES GENERALES
# ===============================
def leer_json(ruta):
    with open(ruta, "r") as f:
        return json.load(f)

def escribir_json(ruta, datos):
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=4)

mutex = threading.Lock()

# ===============================
# HILO TEMPERATURA
# ===============================
def simular_temperatura(ruta, intervalo=5):
    while True:
        with mutex:
            data = leer_json(ruta)
            temps = data.get("sensores_temp", {}).get("temperatura", [])

            for i in range(len(temps)):
                cambio = random.randint(-1, 1)
                temps[i] = max(15, min(40, temps[i] + cambio))

            escribir_json(ruta, data)

        time.sleep(intervalo)


# ===============================
# HILO HUMEDAD
# ===============================
def simular_humedad(ruta, intervalo=6):
    while True:
        with mutex:
            data = leer_json(ruta)
            hums = data.get("sensores_hum", {}).get("humedad", [])

            for i in range(len(hums)):
                cambio = random.randint(-3, 3)
                hums[i] = max(20, min(90, hums[i] + cambio))

            escribir_json(ruta, data)

        time.sleep(intervalo)

# ===============================
# HILO CALIDAD DEL AIRE
# ===============================
def simular_calidad_aire(ruta, intervalo=7):
    while True:
        with mutex:
            data = leer_json(ruta)
            aire = data.get("sensores_cali_aire", {}).get("calidad_aire", {})

            for gas, valores in aire.items():
                for i in range(len(valores)):
                    cambio = random.randint(-5, 5)
                    valores[i] = max(0, valores[i] + cambio)

            escribir_json(ruta, data)

        time.sleep(intervalo)


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    h_temp = threading.Thread(
        target=simular_temperatura,
        args=("sensores_temperatura.json",),
        daemon=True
    )

    h_hum = threading.Thread(
        target=simular_humedad,
        args=("sensores_humedad.json",),
        daemon=True
    )

    h_aire = threading.Thread(
        target=simular_calidad_aire,
        args=("sensores_calidad_aire.json",),
        daemon=True
    )

    h_temp.start()
    h_hum.start()
    h_aire.start()

    while True:
        time.sleep(1)
