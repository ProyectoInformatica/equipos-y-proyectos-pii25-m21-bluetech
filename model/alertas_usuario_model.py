from data.conexionBD import obtener_conexion
from datetime import datetime

class AlertasUsuarioModel:

    def obtener_alertas(self):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error", "alertas": []}
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM alerta"
        cursor.execute(query)
        alertas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return {"status": "ok", "alertas": alertas}

    def crear_alerta(self, alerta):
        """
        alerta = {
            'descripcion': str,
            'id_emisor': int,
            'id_rol': int,
            'nombre_emisor': str,
            'estado': str,
            'fecha_hora': str (YYYY-MM-DD HH:MM)
        }
        """
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}
        cursor = conexion.cursor()
        query = """
            INSERT INTO alerta (estado, fecha_hora, descripcion, valor_detectado, nombre_emisor, tipo_sensor, fk_id_sensor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            alerta.get("estado", "Pendiente"),
            alerta.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            alerta.get("descripcion", ""),
            alerta.get("valor_detectado", "0"),
            alerta.get("nombre_emisor", ""),
            alerta.get("tipo_sensor", "Desconocido"),
            alerta.get("fk_id_sensor", 1)
        )
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"status": "ok"}

    def obtener_mensajes(self, id_alerta):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error", "mensajes": []}
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM mensajes WHERE fk_id_alerta = %s"
        cursor.execute(query, (id_alerta,))
        mensajes = cursor.fetchall()
        cursor.close()
        conexion.close()
        return {"status": "ok", "mensajes": mensajes}

    def enviar_mensaje(self, mensaje):
        """
        mensaje = {
            'id_alerta': int,
            'id_emisor': int,
            'nombre_emisor': str,
            'rol': str,
            'texto': str,
            'fecha_hora': str
        }
        """
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}
        cursor = conexion.cursor()
        query = """
            INSERT INTO mensajes (fk_id_alerta, id_emisor, nombre_emisor, rol, texto, fecha_hora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            mensaje.get("id_alerta"),
            mensaje.get("id_emisor"),
            mensaje.get("nombre_emisor"),
            mensaje.get("rol"),
            mensaje.get("texto"),
            mensaje.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"status": "ok"}

    def asignar_ticket(self, id_alerta, id_tecnico, nombre_tecnico):
        conexion = obtener_conexion()
        if not conexion:
            return {"status": "error"}
        cursor = conexion.cursor()
        query = """
            UPDATE ticket
            SET id_usuario = %s, estado = 'Asignado'
            WHERE id_ticket = %s
        """
        cursor.execute(query, (id_tecnico, id_alerta))
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"status": "ok"}