import pandas as pd
from datetime import datetime
import os
from Database.conexionBD import obtener_conexion

class ExportarMetricasModel:

    def _obtener_conexion(self):
        return obtener_conexion()

    def obtener_tablas(self):
        conexion = self._obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES")
        tablas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conexion.close()
        return tablas

    def obtener_tabla_df(self, nombre_tabla):
        conexion = self._obtener_conexion()
        df = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conexion)
        conexion.close()
        return df

    def exportar_seleccion(self, tablas, formato):
        carpeta = os.path.join(os.path.expanduser("~"), "Desktop", "BlueTechMetricas")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if formato == "excel":
            ruta = os.path.join(carpeta, f"reporte_{timestamp}.xlsx")
            with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
                for tabla in tablas:
                    df = self.obtener_tabla_df(tabla)
                    if df.empty:
                        df = pd.DataFrame({"Mensaje": ["Sin datos"]})
                    df.to_excel(writer, sheet_name=tabla, index=False)
            return ruta

        elif formato == "csv":
            rutas = []
            for tabla in tablas:
                df = self.obtener_tabla_df(tabla)
                ruta = os.path.join(carpeta, f"{tabla}_{timestamp}.csv")
                if df.empty:
                    with open(ruta, "w", encoding="utf-8-sig") as f:
                        f.write("Sin datos")
                else:
                    df.to_csv(ruta, index=False, encoding="utf-8-sig")
                rutas.append(ruta)
            return rutas