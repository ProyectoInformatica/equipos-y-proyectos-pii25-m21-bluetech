from Database.conexionBD import obtener_conexion

def cambiar_estado_habitacion(id_habitacion):
    conexion = obtener_conexion()

    if conexion is None:
        print("Error de conexión")
        return None

    try:
        cursor = conexion.cursor()
        # 1. OBTENER ESTADO ACTUAL
        cursor.execute(
            "SELECT estado FROM habitacion WHERE id_habitacion = %s",
            (id_habitacion,)
        )
        resultado = cursor.fetchone()
        if resultado is None:
            print("Habitación no encontrada")
            return None
        estado_actual = resultado[0]
        # 2. CAMBIAR ESTADO
        nuevo_estado = "libre" if estado_actual == "ocupado" else "ocupado"
        cursor.execute(
            "UPDATE habitacion SET estado = %s WHERE id_habitacion = %s",
            (nuevo_estado, id_habitacion)
        )
        conexion.commit()
        return nuevo_estado
    
    except Exception as e:
        print("Error:", e)
        conexion.rollback()
        return None

    finally:
        cursor.close()
        conexion.close()

def obtener_habitaciones():
    conexion = obtener_conexion()

    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_habitacion, estado, tipo_sala FROM habitacion")
        habitaciones = cursor.fetchall()
        return habitaciones

    except Exception as e:
        print("Error:", e)
        return []

    finally:
        cursor.close()
        conexion.close()