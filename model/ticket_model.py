from Database.conexionBD import obtener_conexion
from datetime import datetime

class TicketModel:
    def obtener_tickets(self):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error", "tickets": []}
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT * FROM ticket"
            cursor.execute(query)
            tickets = cursor.fetchall()
            for t in tickets:
                if isinstance(t.get('fecha_hora'), datetime):
                    t['fecha_hora'] = t['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S")
            return {"status": "ok", "tickets": tickets}
        finally:
            cursor.close()
            conexion.close()

    def crear_tickets(self, ticket_data):
        """Inserta un nuevo registro en la tabla ticket"""
        conexion = obtener_conexion()
        if not conexion: return {"status": "error"}
        try:
            cursor = conexion.cursor()
            query = """
                INSERT INTO ticket 
                (fecha_hora, estado, descripcion, id_rol_emisor, nombre_emisor, id_emisor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = (
                ticket_data.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ticket_data.get("estado", "Abierto"),
                ticket_data.get("descripcion", ""),
                ticket_data.get("id_rol_emisor", "1"),
                ticket_data.get("nombre_emisor", ""),
                ticket_data.get("id_emisor")
            )
            cursor.execute(query, valores)
            conexion.commit()
            return {"status": "ok", "id_ticket": cursor.lastrowid}
        except Exception as e:
            return {"status": "error", "mensaje": str(e)}
        finally:
            cursor.close()
            conexion.close()

    def obtener_mensajes(self, id_ticket):
        """Consulta mensajes filtrando por id_ticket (nueva FK en tu SQL)"""
        conexion = obtener_conexion()
        if not conexion: return {"status": "error", "mensajes": []}
        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT * FROM mensajes WHERE id_ticket = %s ORDER BY fecha_hora ASC"
            cursor.execute(query, (id_ticket,))
            mensajes = cursor.fetchall()
            for m in mensajes:
                if isinstance(m.get('fecha_hora'), datetime):
                    m['fecha_hora'] = m['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S")
            return {"status": "ok", "mensajes": mensajes}
        finally:
            cursor.close()
            conexion.close()

    def enviar_mensaje(self, mensaje):
        """Inserta mensaje en la tabla mensajes"""
        conexion = obtener_conexion()
        if not conexion: return {"status": "error"}
        try:
            cursor = conexion.cursor()
            query = """
                INSERT INTO mensajes (fecha_hora, texto, rol, nombre_emisor, id_ticket, id_emisor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = (
                mensaje.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                mensaje.get("texto"),
                mensaje.get("rol"),
                mensaje.get("nombre_emisor"),
                mensaje.get("id_ticket"),
                mensaje.get("id_emisor")
            )
            cursor.execute(query, valores)
            conexion.commit()
            return {"status": "ok"}
        finally:
            cursor.close()
            conexion.close()

    def asignar_ticket(self, id_ticket, id_tecnico, nombre_tecnico):
        """Asigna técnico al ticket"""
        conexion = obtener_conexion()
        if not conexion: return {"status": "error"}
        try:
            cursor = conexion.cursor()
            query = """
                UPDATE ticket
                SET id_tecnico = %s, nombre_tecnico = %s, estado = 'Asignado'
                WHERE id_ticket = %s
            """
            cursor.execute(query, (id_tecnico, nombre_tecnico, id_ticket))
            conexion.commit()
            return {"status": "ok"}
        finally:
            cursor.close()
            conexion.close()