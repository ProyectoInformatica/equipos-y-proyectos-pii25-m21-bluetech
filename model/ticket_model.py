from data.conexionBD import obtener_conexion
from datetime import datetime

class TicketModelBD:
    def leer_tickets(self):
        """Devuelve todos los tickets desde la base de datos."""
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ticket")
            tickets = cursor.fetchall()
            return tickets
        finally:
            conexion.close()

    def generar_ticket_automatico(self, id_habitacion, id_sensor, nombre, tipo_sensor,
                                    valor_detectado, limite_establecido, descripcion,
                                    estado="Pendiente"):
        """
        Crea un ticket automáticamente si no existe un ticket activo para el mismo sensor y tipo.
        """
        conexion = obtener_conexion()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor(dictionary=True)
            # Verificar si ya hay un ticket activo para este sensor y tipo
            query_check = """
            SELECT * FROM ticket
            WHERE id_sensor = %s AND tipo_sensor = %s AND estado != 'Finalizado'
            """
            cursor.execute(query_check, (id_sensor, tipo_sensor))
            existente = cursor.fetchone()
            if existente:
                return False
            # Insertar nuevo ticket
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query_insert = """
            INSERT INTO ticket (estado, fecha_hora, descripcion, id_usuario, fk_id_rol)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, (estado, fecha_actual, descripcion, 1, 1))
            conexion.commit()
            return True
        except Exception as e:
            print("Error al generar ticket:", e)
            return False
        finally:
            conexion.close()