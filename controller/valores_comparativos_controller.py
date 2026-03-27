from model.valores_comparativos_model import obtener_valores_bd, actualizar_valor_bd

def obtener_valores():
    """Devuelve los valores en formato dict para las vistas."""
    return obtener_valores_bd()

def actualizar_valores(data):
    """Recibe el dict completo modificado y lo actualiza en la BD."""
    # temperatura
    for campo, valor in data["temperatura"].items():
        actualizar_valor_bd("temperatura", None, campo, valor)
    # humedad
    for campo, valor in data["humedad"].items():
        actualizar_valor_bd("humedad", None, campo, valor)
    # calidad del aire
    for subclave, valores in data["calidad_aire"].items():
        for campo, valor in valores.items():
            actualizar_valor_bd("calidad_aire", subclave, campo, valor)