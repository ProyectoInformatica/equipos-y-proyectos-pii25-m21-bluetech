from model.mapa_habitaciones_model import (
    cargar_datos,
    cargar_sensores_humedad,
    cargar_sensores_temperatura,
    cargar_sensores_calidad_aire,
    cargar_valores_comparativos
)

def obtener_datos_mapa():
    datos = cargar_datos()
    ids = datos["habitaciones"]["id_habitacion"]
    estados = datos["habitaciones"]["estado"]
    ordenados = sorted(zip(ids, estados), key=lambda x: x[0])
    ids = [h[0] for h in ordenados]
    estados = [h[1] for h in ordenados]
    sensores_hum = cargar_sensores_humedad()
    sensores_temp = cargar_sensores_temperatura()
    sensores_cali = cargar_sensores_calidad_aire()
    rangos = cargar_valores_comparativos()
    temperaturas = sensores_temp["temperatura"]
    humedades = sensores_hum["humedad"]
    calidad_aire = sensores_cali["calidad_aire"]
    total = min(
        len(ids),
        len(estados),
        len(temperaturas),
        len(humedades),
    )
    habitaciones = []
    for i in range(total):
        habitaciones.append({
            "id": ids[i],
            "estado": estados[i],
            "temperatura": temperaturas[i],
            "humedad": humedades[i],
            "calidad_aire": {
                clave: calidad_aire[clave][i] for clave in calidad_aire
            },
            "index": i,
        })
    return habitaciones, rangos