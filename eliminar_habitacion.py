import json

def eliminar_habitacion(id_eliminar, datos,
                        cargar_sensores_humedad,
                        cargar_sensores_temperatura,
                        cargar_sensores_calidad_aire):
    if id_eliminar not in datos["habitaciones"]["id_habitacion"]:
        return False, "El ID no existe"

    index = datos["habitaciones"]["id_habitacion"].index(id_eliminar)

    # Eliminar de datos principales
    datos["habitaciones"]["id_habitacion"].pop(index)
    datos["habitaciones"]["estado"].pop(index)

    # Eliminar sensores asociados
    sensores_hum = cargar_sensores_humedad()
    sensores_temp = cargar_sensores_temperatura()
    sensores_cali = cargar_sensores_calidad_aire()

    # Humedad
    if "id_sensor" in sensores_hum:
        sensores_hum["id_sensor"].pop(index)
    if "humedad" in sensores_hum:
        sensores_hum["humedad"].pop(index)

    # Temperatura
    if "id_sensor" in sensores_temp:
        sensores_temp["id_sensor"].pop(index)
    if "temperatura" in sensores_temp:
        sensores_temp["temperatura"].pop(index)

    # Calidad del aire
    if "id_sensor" in sensores_cali:
        sensores_cali["id_sensor"].pop(index)
    if "calidad_aire" in sensores_cali:
        for clave in sensores_cali["calidad_aire"]:
            sensores_cali["calidad_aire"][clave].pop(index)

    # Guardar cambios
    with open("habitacion.json", "w") as archivo:
        json.dump(datos, archivo, indent=4)
    with open("sensores_humedad.json", "w") as archivo:
        json.dump({"sensores_hum": sensores_hum}, archivo, indent=4)
    with open("sensores_temperatura.json", "w") as archivo:
        json.dump({"sensores_temp": sensores_temp}, archivo, indent=4)
    with open("sensores_calidad_aire.json", "w") as archivo:
        json.dump({"sensores_cali_aire": sensores_cali}, archivo, indent=4)

    #mensaje de confirmación
    return True, f"✅ Habitación {id_eliminar} eliminada correctamente"

