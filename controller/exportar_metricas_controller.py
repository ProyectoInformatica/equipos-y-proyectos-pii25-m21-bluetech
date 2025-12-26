from model.exportar_metricas_model import ExportarMetricasModel


class ExportarMetricasController:
    def __init__(self):
        self.model = ExportarMetricasModel()

    def generar_csv(self, tipo):
        try:
            if tipo == "sensores":
                df = self.model.obtener_sensores_combinados()
                nombre = "sensores_completos.csv"

            elif tipo == "usuarios":
                df = self.model.obtener_usuarios()
                nombre = "usuarios.csv"

            elif tipo == "habitaciones":
                df = self.model.obtener_habitaciones()
                nombre = "habitaciones.csv"

            else:
                return False, "Tipo de exportación no válido"

            if df.empty:
                return False, "No hay datos para exportar"

            csv_content = df.to_csv(index=False, encoding="utf-8-sig")
            return True, (nombre, csv_content)

        except Exception as e:
            return False, str(e)
