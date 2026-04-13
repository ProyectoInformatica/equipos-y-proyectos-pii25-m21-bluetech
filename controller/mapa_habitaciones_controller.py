# controller/mapa_habitaciones_admin_controller.py
from model.mapa_habitaciones_model import (
    cargar_datos,
    cargar_sensores_humedad,
    cargar_sensores_temperatura,
    cargar_sensores_calidad_aire,
    cargar_valores_comparativos,
    crear_nueva_habitacion,
    eliminar_habitacion_por_id
)

def obtener_datos_mapa():
    """Une los datos de habitaciones con sus sensores para la vista."""
    datos_base = cargar_datos()
    ids_hab = datos_base["habitaciones"]["id_habitacion"]
    estados_hab = datos_base["habitaciones"]["estado"]
    # NUEVA LÍNEA: Extraemos los tipos de sala del modelo
    tipos_hab = datos_base["habitaciones"]["tipo_sala"] 
    
    s_hum = cargar_sensores_humedad()
    s_temp = cargar_sensores_temperatura()
    s_cali = cargar_sensores_calidad_aire()
    rangos = cargar_valores_comparativos()

    habitaciones_procesadas = []
    
    for i in range(len(ids_hab)):
        h_val = s_hum["humedad"][i] if i < len(s_hum["humedad"]) else 0.0
        t_val = s_temp["temperatura"][i] if i < len(s_temp["temperatura"]) else 0.0
        
        dict_calidad = {}
        for clave, lista_valores in s_cali["calidad_aire"].items():
            dict_calidad[clave] = lista_valores[i] if i < len(lista_valores) else 0.0

        habitaciones_procesadas.append({
            "id": ids_hab[i],
            "estado": estados_hab[i],
            # NUEVA LÍNEA: Ahora sí pasamos el tipo a la vista
            "tipo": tipos_hab[i], 
            "temperatura": t_val,
            "humedad": h_val,
            "calidad_aire": dict_calidad,
            "index": i,
        })
        
    return habitaciones_procesadas, rangos

def agregar_habitacion(estado, tipo):
    return crear_nueva_habitacion(estado, tipo)

def eliminar_habitacion_control(id_hab):
    try:
        eliminar_habitacion_por_id(id_hab)
        return True, "Eliminado", None
    except Exception as e:
        return False, str(e), None

def duplicar_planta_control(indice_planta):
    try:
        from model.mapa_habitaciones_model import cargar_datos, duplicar_planta
        datos = cargar_datos()
        # El modelo ya se encarga de iterar y crear 10 habitaciones con sensores
        duplicar_planta(datos, int(indice_planta) - 1)
        return True, f"Planta {indice_planta} duplicada con éxito"
    except Exception as e:
        return False, str(e)

def eliminar_planta_control(indice_planta):
    try:
        from model.mapa_habitaciones_model import cargar_datos, eliminar_planta_completa
        datos = cargar_datos()
        eliminar_planta_completa(datos, int(indice_planta) - 1)
        return True, f"Planta {indice_planta} eliminada"
    except Exception as e:
        return False, str(e)