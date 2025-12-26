import json
import hashlib
import os

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


# ============================
# USUARIO (MODELO)
# ============================
class Usuario:
    def __init__(self, id_usuario, nombre_usuario, contrasena_hash, rol,
                num_registros=0, estado=1):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = contrasena_hash
        self.rol = rol
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


# ============================
# REPOSITORIO (MODELO)
# ============================
class RepositorioCredenciales:
    def __init__(self, ruta_usuarios="data/usuarios.json"):
        self.ruta_usuarios = ruta_usuarios
        self.usuarios = []
        self.cargar_datos()

    # ---------- helpers ----------
    def _obtener_nombre_login(self, entrada):
        return entrada.get("nombre_usuario") or entrada.get("nombre")

    def _obtener_contrasena_hash(self, entrada):
        if "contrasena_hash" in entrada:
            return entrada["contrasena_hash"]
        if "contraseña_hash" in entrada:
            return entrada["contraseña_hash"]

        plano = entrada.get("contraseña") or entrada.get("contrasena")
        if plano:
            return hashlib.sha256(plano.encode()).hexdigest()
        return None

    # ---------- carga ----------
    def cargar_datos(self):
        self.usuarios = []

        if not os.path.exists(self.ruta_usuarios):
            return

        with open(self.ruta_usuarios, "r", encoding="utf-8") as f:
            data = json.load(f)

        for u in data.get("usuarios", []):
            nombre = self._obtener_nombre_login(u)
            hash_pass = self._obtener_contrasena_hash(u)
            rol = u.get("rol")

            if nombre and hash_pass and rol:
                self.usuarios.append(
                    Usuario(
                        id_usuario=u.get("id_usuario"),
                        nombre_usuario=nombre,
                        contrasena_hash=hash_pass,
                        rol=rol,
                        num_registros=u.get("num_registros", 0),
                        estado=u.get("estado", 1)
                    )
                )

    # ---------- login ----------
    def verificar_login(self, usuario, contrasena):
        # Recargar usuarios para tener siempre la versión más reciente
        self.cargar_datos()
        
        hash_pass = hashlib.sha256(contrasena.encode()).hexdigest()
        for u in self.usuarios:
            if u.nombre_usuario == usuario and u.contrasena_hash == hash_pass:
                return u
        return None

    # ---------- guardar ----------
    def guardar_cambios(self):
        if not os.path.exists(self.ruta_usuarios):
            return False

        with open(self.ruta_usuarios, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entrada in data.get("usuarios", []):
            for u in self.usuarios:
                if entrada.get("id_usuario") == u.id_usuario:
                    entrada["contrasena_hash"] = u.contrasena_hash
                    entrada["num_registros"] = u.num_registros
                    entrada["estado"] = u.estado
                    entrada["rol"] = u.rol

        with open(self.ruta_usuarios, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    # ---------- CRUD ----------
    def eliminar_usuario_por_id(self, id_usuario):
        with open(self.ruta_usuarios, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["usuarios"] = [
            u for u in data.get("usuarios", [])
            if u.get("id_usuario") != id_usuario
        ]

        with open(self.ruta_usuarios, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.cargar_datos()
        return True

    def agregar_trabajador(self, nombre, apellidos, nombre_usuario, contrasena):
        nuevo_id = max([u.id_usuario for u in self.usuarios], default=0) + 1

        with open(self.ruta_usuarios, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["usuarios"].append({
            "id_usuario": nuevo_id,
            "nombre": nombre,
            "apellidos": apellidos,
            "nombre_usuario": nombre_usuario,
            "contraseña": contrasena,
            "rol": Rol.TRABAJADOR,
            "num_registros": 0,
            "estado": 1
        })

        with open(self.ruta_usuarios, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.cargar_datos()
        return True
