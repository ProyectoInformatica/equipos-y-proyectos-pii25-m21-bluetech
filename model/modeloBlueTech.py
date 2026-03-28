# model/modeloBlueTech.py
import hashlib
import mysql.connector
from data.conexionBD import obtener_conexion

# ============================
# CONSTANTES
# ============================
RUTA_VALORES_COMPARATIVOS = "data/valores_comparativos.json"


# ============================
# ROLES
# ============================
class Rol:
    ADMINISTRADOR = "administrador"
    TRABAJADOR = "trabajador"
    TECNICO = "tecnico"


# ============================
# USUARIO (MODELO)
# ============================
class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena_hash, rol,
                 num_registros=0, estado=1):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = contrasena_hash
        self.rol = (rol or "").lower()
        self.num_registros = num_registros
        self.estado = estado

    def verificar_contrasena(self, contrasena_ingresada):
        return hashlib.sha256(
            contrasena_ingresada.encode("utf-8")
        ).hexdigest() == self.contrasena_hash

    def es_administrador(self):
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        return self.rol == Rol.TRABAJADOR

    def es_tecnico(self):
        return self.rol == Rol.TECNICO


# ============================
# REPOSITORIO (MODELO)
# ============================
class RepositorioCredenciales:
    def __init__(self, ruta_usuarios=None):
        self.usuarios = []
        self.cargar_datos()

    # ---------- helpers ----------
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

    def _siguiente_id_por_rol(self, rol):
        if rol == Rol.TRABAJADOR:
            base = 1001
        elif rol == Rol.ADMINISTRADOR:
            base = 2001
        elif rol == Rol.TECNICO:
            base = 3001
        else:
            return None

        self.cargar_datos()

        usados = {
            usuario.id_usuario
            for usuario in self.usuarios
            if usuario.rol == rol
        }

        nuevo = base
        while nuevo in usados:
            nuevo += 1

        return nuevo

    # ---------- carga ----------
    def cargar_datos(self):
        self.usuarios = []

        conexion = obtener_conexion()
        if conexion is None:
            return

        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    u.id_usuario,
                    u.nombre_usuario,
                    u.password_hash,
                    r.nombre AS rol,
                    u.num_registro,
                    u.estado
                FROM usuario u
                INNER JOIN rol r
                    ON u.fk_id_rol = r.id_rol
                ORDER BY u.id_usuario
            """)

            filas = cursor.fetchall()

            for fila in filas:
                self.usuarios.append(
                    Usuario(
                        id_usuario=fila["id_usuario"],
                        nombre_usuario=fila["nombre_usuario"],
                        contrasena_hash=fila["password_hash"],
                        rol=fila["rol"],
                        num_registros=fila["num_registro"],
                        estado=fila["estado"]
                    )
                )

        except mysql.connector.Error as error:
            print("Error al cargar usuarios:", error)

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    # ---------- login ----------
    def verificar_login(self, usuario, contrasena, rol=None):
        self.cargar_datos()

        hash_pass = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        rol_buscado = (rol or "").lower() if rol is not None else None

        for usuario_bd in self.usuarios:
            if usuario_bd.nombre_usuario == usuario and usuario_bd.contrasena_hash == hash_pass:
                if rol_buscado is None or usuario_bd.rol == rol_buscado:
                    return usuario_bd

        return None

    # ---------- guardar ----------
    def guardar_cambios(self):
        conexion = obtener_conexion()
        if conexion is None:
            return False

        cursor = None
        try:
            cursor = conexion.cursor()

            for usuario in self.usuarios:
                fk_id_rol = self._obtener_id_rol(usuario.rol)

                if fk_id_rol is None:
                    continue

                cursor.execute("""
                    UPDATE usuario
                    SET
                        nombre_usuario = %s,
                        password_hash = %s,
                        num_registro = %s,
                        fk_id_rol = %s,
                        estado = %s
                    WHERE id_usuario = %s
                """, (
                    usuario.nombre_usuario,
                    usuario.contrasena_hash,
                    usuario.num_registros,
                    fk_id_rol,
                    usuario.estado,
                    usuario.id_usuario
                ))

            conexion.commit()
            return True

        except mysql.connector.Error as error:
            conexion.rollback()
            print("Error al guardar cambios:", error)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    # ---------- CRUD ----------
    def eliminar_usuario_por_id(self, id_usuario):
        conexion = obtener_conexion()
        if conexion is None:
            return False

        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (id_usuario,)
            )
            conexion.commit()
            self.cargar_datos()
            return True

        except mysql.connector.Error as error:
            conexion.rollback()
            print("Error al eliminar usuario:", error)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    def agregar_trabajador(self, nombre, apellidos, nombre_usuario, contrasena):
        conexion = obtener_conexion()
        if conexion is None:
            return False

        cursor = None
        try:
            cursor = conexion.cursor()

            nuevo_id = self._siguiente_id_por_rol(Rol.TRABAJADOR)
            fk_id_rol = self._obtener_id_rol(Rol.TRABAJADOR)
            hash_pass = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()

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
            """, (
                nuevo_id,
                nombre_usuario,
                nombre,
                apellidos,
                0,
                fk_id_rol,
                3,
                hash_pass
            ))

            conexion.commit()
            self.cargar_datos()
            return True

        except mysql.connector.Error as error:
            conexion.rollback()
            print("Error al agregar trabajador:", error)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

    def agregar_tecnico(self, nombre, apellidos, nombre_usuario, contrasena):
        conexion = obtener_conexion()
        if conexion is None:
            return False

        cursor = None
        try:
            cursor = conexion.cursor()

            nuevo_id = self._siguiente_id_por_rol(Rol.TECNICO)
            fk_id_rol = self._obtener_id_rol(Rol.TECNICO)
            hash_pass = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()

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
            """, (
                nuevo_id,
                nombre_usuario,
                nombre,
                apellidos,
                0,
                fk_id_rol,
                3,
                hash_pass
            ))

            conexion.commit()
            self.cargar_datos()
            return True

        except mysql.connector.Error as error:
            conexion.rollback()
            print("Error al agregar técnico:", error)
            return False

        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()