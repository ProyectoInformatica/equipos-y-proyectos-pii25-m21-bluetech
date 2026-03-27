from data.conexionBD import obtener_conexion
from datetime import datetime
import random

def crear_habitacion_con_sensores(estado_habitacion, tipo_sala):
    conexion = obtener_conexion()
    
    if conexion is None:
        print("Error de conexión")
        return None
    
    try:
        cursor = conexion.cursor()
        # 1. INSERTAR HABITACIÓN
        query_habitacion = """
        INSERT INTO habitacion (tipo_sala, estado)
        VALUES (%s, %s)
        """
        cursor.execute(query_habitacion, (tipo_sala, estado_habitacion))
        conexion.commit()
        # ID generado automáticamente
        id_habitacion = cursor.lastrowid
        # 2. CREAR SENSORES
        fecha = datetime.now().strftime("%Y-%m-%d")
        # (tipo_sensor, fk_id_parametro, consumo)
        sensores = [
            ("Temperatura", 1, random.uniform(4.0, 6.0)),
            ("Humedad", 2, random.uniform(2.0, 4.0)),
            ("Calidad de Aire", 4, random.uniform(8.0, 12.0))
        ]
        query_sensor = """
        INSERT INTO sensor 
        (estado, fecha_instalacion, fk_id_habitacion, fk_id_parametro, consumo, tipo_sensor)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for tipo, id_parametro, consumo in sensores:
            cursor.execute(query_sensor, (
                "Activo",
                fecha,
                id_habitacion,
                id_parametro,
                round(consumo, 2),  
                tipo
            ))
        conexion.commit()
        print(f"Habitación {id_habitacion} creada con sensores correctamente")
        return id_habitacion
    
    except Exception as e:
        print("Error al crear habitación:", e)
        conexion.rollback()
        return None
    
    finally:
        cursor.close()
        conexion.close()