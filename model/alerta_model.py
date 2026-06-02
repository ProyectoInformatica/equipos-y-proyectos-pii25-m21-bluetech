from Database.conexionBD import obtener_conexion

class AlertaModelBD:

    def leer_tickets(self):
        conexion = obtener_conexion()
        if not conexion:
            return []

        try:
            cursor = conexion.cursor(dictionary=True)

            query = """
                SELECT
                    a.id_alerta,
                    a.fecha,
                    a.id_habitacion,
                    a.id_sensor,
                    a.nombre_emisor,
                    a.tipo_sensor,

                    COALESCE(m.valor, a.valor_detectado) AS valor_detectado,

                    a.descripcion,
                    a.estado,
                    a.tecnico_id,
                    a.tecnico_nombre,

                    vc.min AS limite_min,
                    vc.max AS limite_max

                FROM alerta a

                INNER JOIN sensor s
                    ON a.id_sensor = s.id_sensor

                LEFT JOIN valores_comparativos vc
                    ON s.fk_id_parametro = vc.id_parametro

                LEFT JOIN (
                    SELECT m1.*
                    FROM medicion m1
                    INNER JOIN (
                        SELECT
                            fk_id_sensor,
                            MAX(fecha_hora) AS ultima_fecha
                        FROM medicion
                        GROUP BY fk_id_sensor
                    ) ult
                    ON m1.fk_id_sensor = ult.fk_id_sensor
                    AND m1.fecha_hora = ult.ultima_fecha
                ) m
                    ON m.fk_id_sensor = s.id_sensor

                ORDER BY a.fecha DESC
            """

            cursor.execute(query)
            return cursor.fetchall()

        finally:
            conexion.close()

    def actualizar_estado_alerta(
        self,
        id_alerta,
        nuevo_estado,
        id_tecnico=None,
        nombre_tecnico=None
    ):
        conexion = obtener_conexion()
        if not conexion:
            return False

        try:
            cursor = conexion.cursor()

            query = """
                UPDATE alerta
                SET
                    estado = %s,
                    tecnico_id = %s,
                    tecnico_nombre = %s
                WHERE id_alerta = %s
            """

            cursor.execute(
                query,
                (
                    nuevo_estado,
                    id_tecnico,
                    nombre_tecnico,
                    id_alerta
                )
            )

            conexion.commit()
            return True

        finally:
            conexion.close()