from model.mapa_habitaciones_model import (
    cargar_datos,
    crear_nueva_habitacion,
    eliminar_habitacion_por_id,
    duplicar_planta,
    eliminar_planta_completa,
    cargar_sensores_humedad,
    cargar_sensores_temperatura,
    cargar_sensores_calidad_aire,
    cargar_valores_comparativos
)

def obtener_datos():
    datos = cargar_datos()

    ids = datos["habitaciones"]["id_habitacion"]
    estados = datos["habitaciones"]["estado"]

    # 🔑 Ordenar por ID de habitación
    ordenados = sorted(zip(ids, estados), key=lambda x: x[0])

    # Reconstruir listas ordenadas
    datos["habitaciones"]["id_habitacion"] = [h[0] for h in ordenados]
    datos["habitaciones"]["estado"] = [h[1] for h in ordenados]

    return datos

def agregar_habitacion(estado, tipo_sala):
    crear_nueva_habitacion(estado, tipo_sala)
    return cargar_datos()

def eliminar_habitacion_control(id_hab):
    datos = cargar_datos()
    ok, mensaje = eliminar_habitacion_por_id(id_hab, datos)
    datos = cargar_datos()
    return ok, mensaje, datos

def duplicar_planta_control(planta_index):
    datos = cargar_datos()
    duplicar_planta(datos, planta_index)
    return cargar_datos()

def eliminar_planta_control(planta_index):
    datos = cargar_datos()
    eliminar_planta_completa(datos, planta_index)
    return cargar_datos()

def obtener_sensores():
    return {
        "humedad": cargar_sensores_humedad(),
        "temperatura": cargar_sensores_temperatura(),
        "calidad_aire": cargar_sensores_calidad_aire(),
        "valores_comparativos": cargar_valores_comparativos()
    }
