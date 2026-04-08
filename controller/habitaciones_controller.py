from model.habitaciones_model import (
    cambiar_estado_habitacion,
    obtener_habitaciones 
)

def listar_habitaciones():
    return obtener_habitaciones()

def alternar_estado(id_habitacion):
    return cambiar_estado_habitacion(id_habitacion)