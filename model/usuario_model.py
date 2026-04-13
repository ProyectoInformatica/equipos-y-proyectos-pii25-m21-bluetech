# model/usuario_model.py
from Database.conexionBD import obtener_conexion
import mysql.connector

BASE_ID_TRABAJADOR = 1001
BASE_ID_ADMIN = 2001
BASE_ID_TECNICO = 3001


class UsuariosModel:
    def __init__(self):
        pass

    def _obtener_id_rol(self, rol_nombre):
        conexion = obtener_conexion()
        if conexion is None:
            return None

        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_rol FROM rol WHERE LOWER(nombre) = LOWER(%s)",
                (rol_nombre,)
            )
            resultado = cursor.fetchone()

            if resultado is not None:
                return resultado[0]

            return None

        except mysql.connector.Error as error:
            print("Error al obtener id_rol:", error)
            return None

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    def leer(self):
        conexion = obtener_conexion()
        if conexion is None:
            return {"usuarios": []}

        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre,
                    u.apellido AS apellidos,
                    u.nombre_usuario,
                    r.nombre AS rol,
                    u.num_registro AS num_registros,
                    u.estado,
                    u.password_hash AS contrasena_hash
                FROM usuario u
                INNER JOIN rol r
                    ON u.fk_id_rol = r.id_rol
                ORDER BY u.id_usuario
            """)
            filas = cursor.fetchall()

            if filas is None:
                return {"usuarios": []}

            return {"usuarios": filas}

        except mysql.connector.Error as error:
            print("Error al leer usuarios:", error)
            return {"usuarios": []}

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    def escribir(self, data):
        conexion = obtener_conexion()
        if conexion is None:
            return

        cursor = None
        try:
            cursor = conexion.cursor()
            usuarios = data.get("usuarios", [])

            ids_nuevos = []
            for usuario in usuarios:
                if "id_usuario" in usuario and usuario["id_usuario"] is not None:
                    ids_nuevos.append(usuario["id_usuario"])

            if ids_nuevos:
                marcadores = ",".join(["%s"] * len(ids_nuevos))
                sql_delete = f"DELETE FROM usuario WHERE id_usuario NOT IN ({marcadores})"
                cursor.execute(sql_delete, ids_nuevos)
            else:
                cursor.execute("DELETE FROM usuario")

            for usuario in usuarios:
                rol = (usuario.get("rol") or "").strip().lower()
                fk_id_rol = self._obtener_id_rol(rol)

                if fk_id_rol is None:
                    continue

                cursor.execute("""
                    INSERT INTO usuario (
                        id_usuario,
                        nombre_usuario,
                        nombre,
                        apellido,
                        num_registro,
                        fk_id_rol,
                        estado,
                        password_hash
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nombre_usuario = VALUES(nombre_usuario),
                        nombre = VALUES(nombre),
                        apellido = VALUES(apellido),
                        num_registro = VALUES(num_registro),
                        fk_id_rol = VALUES(fk_id_rol),
                        estado = VALUES(estado),
                        password_hash = VALUES(password_hash)
                """, (
                    usuario.get("id_usuario"),
                    usuario.get("nombre_usuario", ""),
                    usuario.get("nombre", ""),
                    usuario.get("apellidos", ""),
                    usuario.get("num_registros", 0),
                    fk_id_rol,
                    usuario.get("estado", 1),
                    usuario.get("contrasena_hash", "")
                ))

            conexion.commit()

        except mysql.connector.Error as error:
            conexion.rollback()
            print("Error al escribir usuarios:", error)

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    def ids_migrados(self):
        data = self.leer()

        for usuario in data["usuarios"]:
            rol = (usuario.get("rol") or "").lower()
            uid = usuario.get("id_usuario")

            if uid is None:
                return False

            if rol == "trabajador" and uid < BASE_ID_TRABAJADOR:
                return False

            if rol == "administrador" and uid < BASE_ID_ADMIN:
                return False

            if rol == "tecnico" and uid < BASE_ID_TECNICO:
                return False

        return True

    def siguiente_id(self, rol):
        data = self.leer()
        rol = (rol or "").lower()

        if rol == "trabajador":
            base = BASE_ID_TRABAJADOR
        elif rol == "administrador":
            base = BASE_ID_ADMIN
        elif rol == "tecnico":
            base = BASE_ID_TECNICO
        else:
            return None

        usados = {
            usuario["id_usuario"]
            for usuario in data["usuarios"]
            if (usuario.get("rol") or "").lower() == rol
        }

        nuevo = base
        while nuevo in usados:
            nuevo += 1

        return nuevo

    def existe_login(self, login):
        conexion = obtener_conexion()
        if conexion is None:
            return False

        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT 1 FROM usuario WHERE LOWER(nombre_usuario) = LOWER(%s) LIMIT 1",
                (login.strip(),)
            )
            resultado = cursor.fetchone()

            if resultado is not None:
                return True

            return False

        except mysql.connector.Error as error:
            print("Error al comprobar login:", error)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()