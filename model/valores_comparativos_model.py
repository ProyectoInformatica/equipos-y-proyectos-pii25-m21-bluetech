import json

RUTA_JSON = "data/valores_comparativos.json"

def cargar_valores():
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_valores(data):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
