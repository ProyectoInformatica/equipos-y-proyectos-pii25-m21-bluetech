from data.conexionBD import obtener_conexion

class SensorConsumo:
    def __init__(self, nombre, detalle, w):
        self.nombre = nombre
        self.detalle = detalle
        self.w = w

    def __str__(self):
        return f"{self.nombre} - {self.detalle}"

class ConsumoEnergeticoModel:
    @staticmethod
    def obtener_sensores():
        sensores = []
        conexion = obtener_conexion()
        if conexion is None:
            return sensores
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT tipo_sensor, consumo FROM sensor")
            for tipo_sensor, consumo in cursor.fetchall():
                try:
                    w = float(consumo)
                except:
                    w = 0.0
                sensores.append(
                    SensorConsumo(
                        nombre=tipo_sensor,
                        detalle=f"{w} W",
                        w=w
                    )
                )
        except Exception as e:
            print("Error al obtener sensores:", e)
        finally:
            cursor.close()
            conexion.close()
        return sensores
    
    @staticmethod
    def consumo_total(sensores):
        return sum(s.w for s in sensores)