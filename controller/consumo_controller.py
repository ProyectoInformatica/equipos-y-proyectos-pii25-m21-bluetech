from model.consumo_model import ConsumoEnergeticoModel

def obtener_datos_consumo():
    """Obtiene datos actuales de consumo"""
    sensores = ConsumoEnergeticoModel.obtener_sensores()
    total = ConsumoEnergeticoModel.consumo_total()
    stats = ConsumoEnergeticoModel.obtener_estadisticas()
    return sensores, total, stats

def obtener_datos_graficos():
    """Prepara datos para gráficos"""
    historial = ConsumoEnergeticoModel.obtener_historial_total()
    sensores = ConsumoEnergeticoModel.obtener_sensores()
    
    # Datos para gráfico de línea (tiempo vs consumo total)
    puntos_linea = []
    for i, h in enumerate(historial):
        puntos_linea.append({"x": i, "y": h['valor']})
    
    # Datos para gráfico de barras (consumo por sensor)
    barras = [{"nombre": s.nombre, "valor": s.w_actual} for s in sensores]
    
    return puntos_linea, barras

def toggle_simulacion(callback_actualizacion=None):
    """Inicia o detiene la simulación"""
    if ConsumoEnergeticoModel.esta_simulando():
        ConsumoEnergeticoModel.detener_simulacion()
        return False
    else:
        ConsumoEnergeticoModel.iniciar_simulacion(callback_actualizacion)
        return True

def esta_simulando():
    return ConsumoEnergeticoModel.esta_simulando()