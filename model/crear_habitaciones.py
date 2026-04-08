from data.conexionBD import obtener_conexion
from datetime import datetime
import random

def crear_habitacion_con_sensores(estado_habitacion, tipo_sala):
    conexion = obtener_conexion()
    if conexion is None: return None

    try:
        cursor = conexion.cursor()
        #1. Crear Habitación
        cursor.execute("INSERT INTO habitacion (tipo_sala, estado) VALUES (%s, %s)", (tipo_sala, estado_habitacion))
        id_habitacion = cursor.lastrowid

        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        fecha_hora_ahora = datetime.now()

        #Definimos sensores y rangos de valores realistas para la primera medición
        sensores = [
            ("Temperatura", 1, random.uniform(4.0, 6.0), random.uniform(21.0, 25.0)),
            ("Humedad", 2, random.uniform(2.0, 4.0), random.uniform(35.0, 45.0)),
            ("Calidad de Aire", 3, random.uniform(8.0, 12.0), random.uniform(350.0, 450.0))
        ]

        for tipo, id_parametro, consumo, valor_inicial in sensores:
            #2. Insertar Sensor
            cursor.execute("""
                INSERT INTO sensor (estado, fecha_instalacion, fk_id_habitacion, fk_id_parametro, consumo, tipo_sensor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ("Activo", fecha_hoy, id_habitacion, id_parametro, round(consumo, 2), tipo))
            
            id_sensor = cursor.lastrowid
            cursor.execute("""
                INSERT INTO medicion (fecha_hora, valor, fk_id_sensor)
                VALUES (%s, %s, %s)
            """, (fecha_hora_ahora, round(valor_inicial, 2), id_sensor))

        conexion.commit()
        return id_habitacion

    except Exception as e:
        print("Error al crear habitación:", e)
        conexion.rollback()
        return None
    finally:
        cursor.close()
        conexion.close()