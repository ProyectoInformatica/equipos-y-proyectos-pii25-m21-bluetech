from model.mapa_habitaciones_model import (
    cargar_datos,
    cargar_sensores,
    cargar_rangos
)

def obtener_datos_mapa():
    datos = cargar_datos()
    sensores = cargar_sensores()
    rangos = cargar_rangos()

    ids = datos["habitaciones"].get("id_habitacion", [])
    estados = datos["habitaciones"].get("estado", [])

    total = min(
        len(ids),
        len(estados),
        len(sensores["temperatura"]),
        len(sensores["humedad"]),
    )

    habitaciones = []
    for i in range(total):
        habitaciones.append({
            "id": ids[i],
            "estado": estados[i],
            "temperatura": sensores["temperatura"][i],
            "humedad": sensores["humedad"][i],
            "calidad_aire": sensores["calidad_aire"],
            "index": i,
        })

    habitaciones.sort(key=lambda h: h["id"])
    return habitaciones, rangos
