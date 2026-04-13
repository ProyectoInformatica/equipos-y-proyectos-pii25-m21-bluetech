import pandas as pd
from datetime import datetime
import os
from Database.conexionBD import obtener_conexion

class ExportarMetricasModel:
    def _obtener_conexion(self):
        return obtener_conexion()

    def obtener_sensores_combinados(self):
        conexion = self._obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
            SELECT 
                m.fecha_hora,
                h.id_habitacion,
                h.tipo_sala,
                p.nombre AS parametro,
                m.valor
            FROM medicion m
            JOIN sensor s ON m.fk_id_sensor = s.id_sensor
            JOIN habitacion h ON s.fk_id_habitacion = h.id_habitacion
            JOIN parametro p ON s.fk_id_parametro = p.id_parametro
        """
        cursor.execute(query)
        data = cursor.fetchall()
        
        cursor.close()
        conexion.close()

        df_raw = pd.DataFrame(data)
        if df_raw.empty:
            return pd.DataFrame()

        df_pivot = df_raw.pivot_table(
            index=['fecha_hora', 'id_habitacion', 'tipo_sala'],
            columns='parametro',
            values='valor'
        ).reset_index()
        
        df_pivot.columns.name = None
        
        # Opcional: Asegurarnos de que fecha_hora no tenga la zona horaria para evitar problemas en Excel
        df_pivot['fecha_hora'] = df_pivot['fecha_hora'].dt.tz_localize(None)
        
        return df_pivot

    def obtener_usuarios(self):
        conexion = self._obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.id_usuario, 
                u.nombre_usuario, 
                u.nombre, 
                u.apellido, 
                u.num_registro, 
                r.nombre AS rol, 
                u.estado
            FROM usuario u
            JOIN rol r ON u.fk_id_rol = r.id_rol
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conexion.close()
        return pd.DataFrame(data)

    def obtener_habitaciones(self):
        conexion = self._obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT id_habitacion, tipo_sala, estado FROM habitacion"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conexion.close()
        return pd.DataFrame(data)

    def exportar_a_excel(self, carpeta_destino="descargas"):
        """
        Obtiene todos los DataFrames y los guarda en un único archivo Excel con múltiples hojas.
        """
        # 1. Crear la carpeta si no existe
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        # 2. Generar un nombre de archivo único con la fecha y hora actual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_bluetech_{timestamp}.xlsx"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        # 3. Obtener los datos
        print("Recolectando datos de la base de datos...")
        df_metricas = self.obtener_sensores_combinados()
        df_usuarios = self.obtener_usuarios()
        df_habitaciones = self.obtener_habitaciones()

        # 4. Escribir en el archivo Excel
        try:
            # Usamos pd.ExcelWriter para poder guardar múltiples hojas (tabs)
            with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
                if not df_metricas.empty:
                    df_metricas.to_excel(writer, sheet_name='Métricas Sensores', index=False)
                else:
                    pd.DataFrame({'Mensaje': ['No hay mediciones registradas']}).to_excel(writer, sheet_name='Métricas Sensores', index=False)
                
                df_usuarios.to_excel(writer, sheet_name='Usuarios del Sistema', index=False)
                df_habitaciones.to_excel(writer, sheet_name='Estado Habitaciones', index=False)

            print(f"✅ ¡Éxito! Reporte descargado en: {ruta_completa}")
            return ruta_completa
            
        except Exception as e:
            print(f"❌ Error al exportar el archivo Excel: {e}")
            return None
