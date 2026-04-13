from Database.conexionBD import obtener_conexion


def eliminar_habitacion(id_habitacion):
    conexion = obtener_conexion()

    if not conexion:
        return False, "Error de conexión"

    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM habitacion WHERE id_habitacion = %s", (id_habitacion,))
        if not cursor.fetchone():
            return False, "El ID no existe"

        cursor.execute("SELECT id_sensor FROM sensor WHERE fk_id_habitacion = %s", (id_habitacion,))
        sensores = cursor.fetchall()

        for sensor in sensores:
            id_sensor = sensor[0]

            cursor.execute("DELETE FROM alerta WHERE fk_id_sensor = %s", (id_sensor,))
            cursor.execute("DELETE FROM medicion WHERE fk_id_sensor = %s", (id_sensor,))
            cursor.execute("DELETE FROM ticket WHERE id_sensor = %s", (id_sensor,))  
            cursor.execute("DELETE FROM sensor WHERE id_sensor = %s", (id_sensor,))

        cursor.execute("DELETE FROM habitacion WHERE id_habitacion = %s", (id_habitacion,))

        conexion.commit()

        return True, f"Habitación {id_habitacion} eliminada"

    except Exception as e:
        conexion.rollback()
        return False, str(e)

    finally:
        conexion.close()