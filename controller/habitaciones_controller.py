from model.habitaciones_model import (
    cargar_datos,
    cambiar_estado_habitacion
)

def obtener_habitaciones():
    return cargar_datos()

def alternar_estado(index):
    return cambiar_estado_habitacion(index)
