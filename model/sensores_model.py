import json

def cargar_sensores_humedad():
    with open("data/sensores_humedad.json") as f:
        return json.load(f)["sensores_hum"]

def cargar_sensores_temperatura():
    with open("data/sensores_temperatura.json") as f:
        return json.load(f)["sensores_temp"]

def cargar_sensores_calidad_aire():
    with open("data/sensores_calidad_aire.json") as f:
        return json.load(f)["sensores_cali_aire"]

def cargar_valores_comparativos():
    with open("data/valores_comparativos.json") as f:
        return json.load(f)
