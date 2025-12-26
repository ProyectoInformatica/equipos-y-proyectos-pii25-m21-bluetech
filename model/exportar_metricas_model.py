import json
import pandas as pd


class ExportarMetricasModel:
    def obtener_sensores_combinados(self):
        with open("data/sensores_temperatura.json", "r", encoding="utf-8") as f:
            temp = json.load(f)["sensores_temp"]

        with open("data/sensores_humedad.json", "r", encoding="utf-8") as f:
            hum = json.load(f)["sensores_hum"]

        with open("data/sensores_calidad_aire.json", "r", encoding="utf-8") as f:
            aire = json.load(f)["sensores_cali_aire"]["calidad_aire"]

        df = pd.DataFrame({
            "id_sensor": temp["id_sensor"],
            "temperatura": temp["temperatura"],
            "humedad": hum["humedad"]
        })

        for key, values in aire.items():
            df[key] = values

        return df

    def obtener_usuarios(self):
        with open("data/usuarios.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data.get("usuarios", []))

    def obtener_habitaciones(self):
        with open("data/habitacion.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        hab = data.get("habitaciones", {})
        return pd.DataFrame({
            "id_habitacion": hab.get("id_habitacion", []),
            "estado": hab.get("estado", []),
            "tipo_sala": hab.get("tipo_sala", [])
        })
