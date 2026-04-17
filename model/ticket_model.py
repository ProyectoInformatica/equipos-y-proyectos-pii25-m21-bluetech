from Database.conexionBD import obtener_conexion
from datetime import datetime

class TicketModel:

    def obtener_tickets(self):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error", "tickets": []}
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ticket")
            tickets = cursor.fetchall()

            for t in tickets:
                if isinstance(t.get('fecha_hora'), datetime):
                    t['fecha_hora'] = t['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S")

            return {"status": "ok", "tickets": tickets}
        finally:
            cursor.close()
            conexion.close()

    def crear_tickets(self, ticket_data):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}

        try:
            cursor = conexion.cursor()

            query = """
            INSERT INTO ticket 
            (fecha_hora, estado, descripcion, id_rol_emisor,
             nombre_emisor, id_emisor, rol_destinatario,
             id_destinatario, nombre_destinatario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                ticket_data.get("fecha_hora"),
                ticket_data.get("estado"),
                ticket_data.get("descripcion"),
                ticket_data.get("id_rol_emisor"),
                ticket_data.get("nombre_emisor"),
                ticket_data.get("id_emisor"),
                ticket_data.get("rol_destinatario"),
                ticket_data.get("id_destinatario"),
                ticket_data.get("nombre_destinatario"),
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
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error", "mensajes": []}

        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM mensajes WHERE id_ticket = %s ORDER BY fecha_hora ASC",
                (id_ticket,)
            )
            mensajes = cursor.fetchall()

            for m in mensajes:
                if isinstance(m.get('fecha_hora'), datetime):
                    m['fecha_hora'] = m['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S")

            return {"status": "ok", "mensajes": mensajes}

        finally:
            cursor.close()
            conexion.close()

    def enviar_mensaje(self, mensaje):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}

        try:
            cursor = conexion.cursor()

            query = """
                INSERT INTO mensajes 
                (fecha_hora, texto, rol, nombre_emisor, id_ticket, id_emisor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            valores = (
                mensaje.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                mensaje.get("texto"),
                mensaje.get("rol"),
                mensaje.get("nombre_emisor"),
                mensaje.get("id_ticket"),
                mensaje.get("id_emisor"),
            )

            cursor.execute(query, valores)
            conexion.commit()

            return {"status": "ok"}

        finally:
            cursor.close()
            conexion.close()

    def asignar_ticket(self, id_ticket, id_destinatario, nombre_destinatario):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}

        try:
            cursor = conexion.cursor()

            query = """
                UPDATE ticket
                SET id_destinatario = %s,
                    nombre_destinatario = %s,
                    estado = 'Asignado'
                WHERE id_ticket = %s
            """

            cursor.execute(query, (id_destinatario, nombre_destinatario, id_ticket))
            conexion.commit()

            return {"status": "ok"}

        finally:
            cursor.close()
            conexion.close()

    def cerrar_ticket(self, id_ticket):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}

        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE ticket SET estado = 'cerrado' WHERE id_ticket = %s",
                (id_ticket,)
            )
            conexion.commit()

            return {"status": "ok", "id_ticket": id_ticket, "estado": "cerrado"}

        finally:
            cursor.close()
            conexion.close()

    def redirigir_ticket(self, id_ticket, rol_destino):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}

        try:
            cursor = conexion.cursor()

            query = """
                UPDATE ticket
                SET rol_destinatario = %s,
                    id_destinatario = NULL,
                    nombre_destinatario = NULL,
                    estado = 'pendiente'
                WHERE id_ticket = %s
            """

            cursor.execute(query, (rol_destino, id_ticket))
            conexion.commit()

            return {"status": "ok"}

        finally:
            cursor.close()
            conexion.close()