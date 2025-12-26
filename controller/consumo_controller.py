from model.consumo_model import ConsumoEnergeticoModel

def obtener_datos_consumo():
    sensores = ConsumoEnergeticoModel.obtener_sensores()
    total = ConsumoEnergeticoModel.consumo_total(sensores)
    return sensores, total