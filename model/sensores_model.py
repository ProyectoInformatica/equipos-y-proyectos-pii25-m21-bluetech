from data.conexionBD import obtener_conexion

def cargar_sensores_humedad():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT s.id_sensor, s.estado, s.fecha_instalacion, s.fk_id_habitacion, 
                    s.fk_id_parametro, s.consumo, s.tipo_sensor
            FROM sensor s
            JOIN parametro p ON s.fk_id_parametro = p.id_parametro
            WHERE p.nombre LIKE '%Humedad%'
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    return []

def cargar_sensores_temperatura():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT s.id_sensor, s.estado, s.fecha_instalacion, s.fk_id_habitacion, 
                    s.fk_id_parametro, s.consumo, s.tipo_sensor
            FROM sensor s
            JOIN parametro p ON s.fk_id_parametro = p.id_parametro
            WHERE p.nombre LIKE '%Temperatura%'
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    return []

def cargar_sensores_calidad_aire():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT s.id_sensor, s.estado, s.fecha_instalacion, s.fk_id_habitacion, 
                    s.fk_id_parametro, s.consumo, s.tipo_sensor
            FROM sensor s
            JOIN parametro p ON s.fk_id_parametro = p.id_parametro
            WHERE p.nombre LIKE '%Calidad del Aire%'
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    return []

def cargar_valores_comparativos():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT vc.id_rango, vc.min, vc.max, vc.id_parametro, p.nombre as parametro_nombre
            FROM valores_comparativos vc
            JOIN parametro p ON vc.id_parametro = p.id_parametro
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        return resultados
    return []