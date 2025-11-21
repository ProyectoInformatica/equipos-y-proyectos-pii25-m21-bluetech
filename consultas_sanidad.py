

import json


def cargar_valores_recomendados(ruta="valores_comparativos.json"):
    """Carga el archivo JSON con los valores recomendados."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el archivo: {e}")
        return {}


VALORES = cargar_valores_recomendados()


#     FUNCIÓN PRINCIPAL DE CONSULTA

def consultar_parametros_sanidad(parametro=None):
    """
    Consulta valores recomendados de sanidad para temperatura,
    humedad o calidad del aire.

    Parámetros:
        parametro (str): Nombre del parámetro o None para todos.

    Retorna:
        dict: Información del parámetro solicitado.
    """

    if not VALORES:
        return {"error": "No se han podido cargar los valores del JSON."}

    # Sin parámetro → devolver todo
    if parametro is None:
        return VALORES

    parametro = parametro.strip().lower()

    # Temperatura u humedad
    if parametro in ["temperatura", "humedad"]:
        return VALORES.get(parametro)

    # Calidad del aire
    calidad = VALORES.get("calidad_aire", {})
    for clave, valor in calidad.items():
        if clave.lower() == parametro:
            return {clave: valor}

    # No encontrado
    return {"error": f"El parámetro '{parametro}' no existe."}


#     FORMATEADOR PARA MOSTRAR SALIDA LIMPIA

def mostrar_tabla(diccionario):
    """Muestra la información en formato visual y ordenado."""
    if "error" in diccionario:
        print("\n[ERROR] " + diccionario["error"])
        return

    print("\n================ RESULTADO ================\n")

    def print_param(nombre, info):
        if isinstance(info, dict):
            print(f"🔹 {nombre}:")
            for k, v in info.items():
                print(f"   - {k.capitalize()}: {v}")
            print()

    # Si se pide todo
    if "calidad_aire" in diccionario:
        print_param("Temperatura", diccionario["temperatura"])
        print_param("Humedad", diccionario["humedad"])

        print("----- Calidad del Aire -----\n")
        for clave, valor in diccionario["calidad_aire"].items():
            print_param(clave, valor)

    else:
        # Se pidió algo específico
        for clave, valor in diccionario.items():
            print_param(clave, valor)

    print("===========================================\n")


#     PRUEBAS

if __name__ == "__main__":
    print("\n========== PRUEBAS ==========\n")

    print("1) TODOS LOS VALORES:")
    mostrar_tabla(consultar_parametros_sanidad())

    print("2) TEMPERATURA:")
    mostrar_tabla(consultar_parametros_sanidad("temperatura"))

    print("3) HUMEDAD:")
    mostrar_tabla(consultar_parametros_sanidad("humedad"))

    print("4) PM2.5:")
    mostrar_tabla(consultar_parametros_sanidad("PM2.5"))

    print("5) PARÁMETRO INEXISTENTE:")
    mostrar_tabla(consultar_parametros_sanidad("ozono"))

    print("=========== FIN DE PRUEBAS ===========\n")
