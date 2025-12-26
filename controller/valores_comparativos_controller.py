from model.valores_comparativos_model import cargar_valores, guardar_valores

def obtener_valores():
    return cargar_valores()

def actualizar_valores(data):
    guardar_valores(data)
