from model.habitaciones_model import cargar_habitaciones
from model.sensores_model import (
    cargar_sensores_humedad,
    cargar_sensores_temperatura,
    cargar_sensores_calidad_aire,
    cargar_valores_comparativos
)

def obtener_datos_mapa():
    return {
        "habitaciones": cargar_habitaciones(),
        "humedad": cargar_sensores_humedad(),
        "temperatura": cargar_sensores_temperatura(),
        "calidad_aire": cargar_sensores_calidad_aire(),
        "rangos": cargar_valores_comparativos()
    }
