import json
import os

RUTA_JSON = "valores_recomendados.json"


# -----------------------------
# Cargar valores recomendados
# -----------------------------
def cargar_valores_recomendados():
    """Lee el archivo JSON y devuelve los valores recomendados."""
    if not os.path.exists(RUTA_JSON):
        raise FileNotFoundError("ERROR: No se encontró el archivo valores_recomendados.json")

    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# Guardar valores recomendados
# -----------------------------
def guardar_valores_recomendados(data):
    """Guarda los valores actualizados en el archivo JSON."""
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -----------------------------
# Actualizar un parámetro de sanidad
# -----------------------------
def actualizar_parametro_sanidad(categoria, parametro, clave, nuevo_valor):
    """
    Actualiza un valor dentro del archivo de sanidad.
    
    categoria: 'temperatura', 'humedad', 'calidad_aire'
    parametro:
        - Para 'temperatura' o 'humedad': usar None
        - Para 'calidad_aire': 'PM2.5', 'CO', etc.
    clave: 'min', 'max', 'unidad', 'descripcion'
    nuevo_valor: valor nuevo a aplicar
    """
    
    data = cargar_valores_recomendados()

    if categoria not in data:
        raise KeyError(f"Categoría '{categoria}' no existe en el JSON.")

    # Temperatura u humedad
    if categoria in ("temperatura", "humedad"):
        if parametro is not None:
            raise ValueError("Para temperatura/humedad NO se usa parámetro secundario.")
        if clave not in data[categoria]:
            raise KeyError(f"La clave '{clave}' no existe en {categoria}.")
        data[categoria][clave] = nuevo_valor

    # Calidad del aire
    elif categoria == "calidad_aire":
        if parametro not in data["calidad_aire"]:
            raise KeyError(f"El parámetro '{parametro}' no existe en calidad_aire.")
        if clave not in data["calidad_aire"][parametro]:
            raise KeyError(f"La clave '{clave}' no existe en {parametro}.")
        data["calidad_aire"][parametro][clave] = nuevo_valor

    # Guardar cambios
    guardar_valores_recomendados(data)
    return True



# -----------------------------
# PRUEBAS DE FUNCIONAMIENTO
# -----------------------------
if __name__ == "__main__":
    print("\n=== CARGA DE VALORES ===")
    valores = cargar_valores_recomendados()
    print(json.dumps(valores, indent=4, ensure_ascii=False))

    print("\n=== PRUEBA 1: Cambiar temperatura máxima a 28 °C ===")
    actualizar_parametro_sanidad("temperatura", None, "max", 28)
    
    print("\n=== PRUEBA 2: Cambiar PM2.5 máximo a 20 µg/m³ ===")
    actualizar_parametro_sanidad("calidad_aire", "PM2.5", "max", 20)
    
    print("\n=== RESULTADO FINAL ===")
    valores_actualizados = cargar_valores_recomendados()
    print(json.dumps(valores_actualizados, indent=4, ensure_ascii=False))
