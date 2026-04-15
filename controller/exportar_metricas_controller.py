from model.exportar_metricas_model import ExportarMetricasModel

class ExportarMetricasController:
    def __init__(self):
        self.model = ExportarMetricasModel()

    def obtener_tablas(self):
        return self.model.obtener_tablas()

    def exportar(self, tablas, formato):
        try:
            if not tablas:
                return False, "Selecciona al menos una tabla"
            resultado = self.model.exportar_seleccion(tablas, formato)
            return True, resultado
        except Exception as e:
            return False, str(e)