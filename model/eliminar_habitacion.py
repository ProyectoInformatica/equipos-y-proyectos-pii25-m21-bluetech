from data.conexionBD import obtener_conexion

def eliminar_habitacion(id_habitacion):
    conexion = obtener_conexion()
    if not conexion:
        return False, "Error de conexión"
    try:
        cursor = conexion.cursor()
        # 1. Verificar si existe
        cursor.execute("SELECT * FROM habitacion WHERE id_habitacion = %s", (id_habitacion,))
        if not cursor.fetchone():
            return False, "El ID no existe"
        # 2. Obtener sensores asociados
        cursor.execute("SELECT id_sensor FROM sensor WHERE fk_id_habitacion = %s", (id_habitacion,))
        sensores = cursor.fetchall()
        # 3. Eliminar dependencias de sensores
        for sensor in sensores:
            id_sensor = sensor[0]
            cursor.execute("DELETE FROM alerta WHERE fk_id_sensor = %s", (id_sensor,))
            cursor.execute("DELETE FROM medicion WHERE fk_id_sensor = %s", (id_sensor,))
            cursor.execute("DELETE FROM sensor WHERE id_sensor = %s", (id_sensor,))
        # 4. Eliminar habitación
        cursor.execute("DELETE FROM habitacion WHERE id_habitacion = %s", (id_habitacion,))
        conexion.commit()
        return True, f"✅ Habitación {id_habitacion} eliminada correctamente"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()