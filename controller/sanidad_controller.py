from model.modeloBlueTech import (
    cargar_valores_comparativos,
    guardar_valores_comparativos,
    consultar_parametros_sanidad
)

def obtener_valores_comparativos():
    return cargar_valores_comparativos()

def actualizar_valores_comparativos(data):
    return guardar_valores_comparativos(data)

def consultar_parametro(parametro=None):
    return consultar_parametros_sanidad(parametro)
