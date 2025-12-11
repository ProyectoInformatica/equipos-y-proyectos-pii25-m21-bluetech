import json
import os

RUTA_JSON = "valores_comparativos.json"


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
# Actualizar parámetros con interacción del usuario
# -----------------------------
def menu_actualizar_parametros():
    data = cargar_valores_recomendados()

    print("\n=== CATEGORÍAS DISPONIBLES ===")
    for i, categoria in enumerate(data.keys(), start=1):
        print(f"{i}. {categoria}")

    opcion_categoria = input("\nSeleccione una categoría (número): ").strip()

    # Convertir a nombre real
    categorias_lista = list(data.keys())
    try:
        categoria = categorias_lista[int(opcion_categoria) - 1]
    except:
        print("Opción inválida.")
        return

    # Si es temperatura u humedad
    if categoria in ("temperatura", "humedad"):

        print(f"\nValores actuales de {categoria}:")
        for k, v in data[categoria].items():
            print(f" - {k}: {v}")

        clave = input("\nIndique qué clave modificar (min, max, unidad, descripcion): ").strip()

        if clave not in data[categoria]:
            print("Clave inválida.")
            return

        nuevo_valor = input("Nuevo valor: ").strip()

        # Conversión automática a número si procede
        if nuevo_valor.isnumeric():
            nuevo_valor = float(nuevo_valor)

        data[categoria][clave] = nuevo_valor

    # Si es calidad del aire
    elif categoria == "calidad_aire":

        print("\n=== Parámetros de calidad del aire ===")
        for i, param in enumerate(data[categoria].keys(), start=1):
            print(f"{i}. {param}")

        opcion_param = input("\nSeleccione un parámetro (número): ").strip()

        parametros_lista = list(data[categoria].keys())
        try:
            parametro = parametros_lista[int(opcion_param) - 1]
        except:
            print("Opción inválida.")
            return

        print(f"\nValores actuales de {parametro}:")
        for k, v in data[categoria][parametro].items():
            print(f" - {k}: {v}")

        clave = input("\nIndique qué clave modificar (min, max, unidad, descripcion): ").strip()

        if clave not in data[categoria][parametro]:
            print("Clave inválida.")
            return

        nuevo_valor = input("Nuevo valor: ").strip()

        if nuevo_valor.isnumeric():
            nuevo_valor = float(nuevo_valor)

        data[categoria][parametro][clave] = nuevo_valor

    guardar_valores_recomendados(data)
    print("\n✔ Parámetro actualizado correctamente.")


# -----------------------------
# PROGRAMA PRINCIPAL
# -----------------------------
if __name__ == "__main__":

    while True:
        print("\n==============================")
        print("      CONFIGURAR SANIDAD      ")
        print("==============================")
        print("1. Ver valores actuales")
        print("2. Modificar valores")
        print("3. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            valores = cargar_valores_recomendados()
            print(json.dumps(valores, indent=4, ensure_ascii=False))

        elif opcion == "2":
            menu_actualizar_parametros()

        elif opcion == "3":
            print("Programa finalizado.")
            break

        else:
            print("Opción inválida. Intente nuevamente.")
