import json
import os
from enum import Enum


def normaliza_rol(texto):
    """Devuelve 'Administrador' o 'Trabajador' a partir de texto libre."""
    if not isinstance(texto, str):
        return "Trabajador"
    t = texto.strip().lower()
    if t in ("admin", "administrador", "administrator"):
        return "Administrador"
    return "Trabajador"


class Rol(Enum):
    ADMINISTRADOR = "Administrador"
    TRABAJADOR = "Trabajador"


class Usuario:
    """Representa un usuario del sistema (admin o trabajador) con contraseña en texto plano."""

    def __init__(self, id_interno, username, nombre_mostrado, contrasena_plana, rol):
        self.id_interno = id_interno
        self.username = username
        self.nombre_mostrado = nombre_mostrado
        self.contrasena_plana = contrasena_plana
        self.rol = rol

    def verificar_contrasena(self, contrasena):
        """Compara la contraseña ingresada con la almacenada (texto plano)."""
        return contrasena == self.contrasena_plana

    def es_administrador(self):
        return self.rol == Rol.ADMINISTRADOR

    def es_trabajador(self):
        return self.rol == Rol.TRABAJADOR


class RepositorioCredenciales:
    """
    Carga admins.json y usuarios.json y permite verificar login sin hash.
    Admite claves heterogéneas:
      - Admins: id_admin, nombre, apellidos, nombre_usuario,
                contraseña_hash (texto plano) o contraseña (texto plano), rol
      - Usuarios: id_usuario, nombre (username) o nombre_usuario,
                  contraseña_hash (texto plano) o contraseña (texto plano), rol
    """
    def __init__(self, ruta_admins="admins.json", ruta_usuarios="usuarios.json"):
        self.ruta_admins = ruta_admins
        self.ruta_usuarios = ruta_usuarios
        self._usuarios = []  # Lista que contendrá objetos Usuario

        self._cargar_datos()  # Llamada al método que lee los JSON

    def _cargar_datos(self):
        """Carga administradores y usuarios desde los JSON"""
        try:
            # --- Carga administradores ---
            with open(self.ruta_admins, "r", encoding="utf-8") as f:
                data_admins = json.load(f)
                for admin in data_admins.get("admins", []):
                    usuario = Usuario(
                        id_usuario=admin.get("id_admin"),
                        nombre=admin.get("nombre_usuario"),
                        contrasena=admin.get("contraseña") or admin.get("contraseña_hash"),
                        rol=Rol.ADMINISTRADOR
                    )
                    self._usuarios.append(usuario)

            # --- Carga usuarios ---
            with open(self.ruta_usuarios, "r", encoding="utf-8") as f:
                data_usuarios = json.load(f)
                for user in data_usuarios.get("usuarios", []):
                    usuario = Usuario(
                        id_usuario=user.get("id_usuario"),
                        nombre=user.get("nombre"),
                        contrasena=user.get("contraseña") or user.get("contraseña_hash"),
                        rol=Rol.TRABAJADOR
                    )
                    self._usuarios.append(usuario)

        except FileNotFoundError as e:
            print(f"Error: No se encontró el archivo {e.filename}")
        except json.JSONDecodeError:
            print("Error: Uno de los JSON tiene un formato incorrecto.")

    def verificar_login(self, nombre_usuario, contrasena):
        """Busca coincidencia exacta de usuario y contraseña"""
        for usuario in self._usuarios:
            if usuario.nombre == nombre_usuario and usuario.contrasena == contrasena:
                return usuario
        return None

    def __init__(self, ruta_admins="admins.json", ruta_usuarios="usuarios.json"):
        self.ruta_admins = ruta_admins
        self.ruta_usuarios = ruta_usuarios
        self._usuarios = []
        self._cargar()

    def _leer_json(self, ruta):
        if not os.path.exists(ruta):
            return None
        f = open(ruta, "r", encoding="utf-8")
        contenido = f.read()
        f.close()
        if len(contenido.strip()) == 0:
            return None
        try:
            data = json.loads(contenido)
            return data
        except Exception:
            return None

    def _extraer_contrasena_plana(self, item):
        # Acepta tanto 'contraseña_hash' como 'contrasena_hash' o 'contraseña'/'contrasena'
        if "contraseña" in item and isinstance(item["contraseña"], str):
            return item["contraseña"]
        if "contrasena" in item and isinstance(item["contrasena"], str):
            return item["contrasena"]
        if "contraseña_hash" in item and isinstance(item["contraseña_hash"], str):
            return item["contraseña_hash"]
        if "contrasena_hash" in item and isinstance(item["contrasena_hash"], str):
            return item["contrasena_hash"]
        return ""

    def _cargar(self):
        self._usuarios = []

        # --- Admins ---
        data_admins = self._leer_json(self.ruta_admins)
        if isinstance(data_admins, dict) and "admins" in data_admins and isinstance(data_admins["admins"], list):
            for item in data_admins["admins"]:
                username = None
                if "nombre_usuario" in item and isinstance(item["nombre_usuario"], str):
                    username = item["nombre_usuario"]
                elif "nombre" in item and isinstance(item["nombre"], str):
                    username = item["nombre"]

                nombre_mostrado = None
                if "nombre" in item and isinstance(item["nombre"], str):
                    nombre_mostrado = item["nombre"]
                if "apellidos" in item and isinstance(item["apellidos"], str):
                    if nombre_mostrado is None:
                        nombre_mostrado = item["apellidos"]
                    else:
                        nombre_mostrado = nombre_mostrado + " " + item["apellidos"]
                if nombre_mostrado is None:
                    nombre_mostrado = username

                id_interno = item.get("id_admin", None)
                contrasena_plana = self._extraer_contrasena_plana(item)
                rol_txt = normaliza_rol(item.get("rol", "trabajador"))
                rol_enum = Rol.ADMINISTRADOR if rol_txt == "Administrador" else Rol.TRABAJADOR

                if isinstance(username, str) and len(username) > 0:
                    self._usuarios.append(
                        Usuario(
                            id_interno=id_interno,
                            username=username,
                            nombre_mostrado=nombre_mostrado,
                            contrasena_plana=contrasena_plana,
                            rol=rol_enum
                        )
                    )

        # --- Usuarios ---
        data_users = self._leer_json(self.ruta_usuarios)
        if isinstance(data_users, dict) and "usuarios" in data_users and isinstance(data_users["usuarios"], list):
            for item in data_users["usuarios"]:
                # En tu JSON, "nombre" suele ser el username (p.ej., "lgarcia"); si existe "nombre_usuario", se prioriza.
                username = None
                if "nombre_usuario" in item and isinstance(item["nombre_usuario"], str):
                    username = item["nombre_usuario"]
                elif "nombre" in item and isinstance(item["nombre"], str):
                    username = item["nombre"]

                nombre_mostrado = None
                if "nombre" in item and "apellidos" in item and isinstance(item["apellidos"], str):
                    # Si "nombre" es username pero también hay apellidos, lo mostramos como nombre visible completo
                    nombre_mostrado = item["nombre"] + " " + item["apellidos"]
                if nombre_mostrado is None:
                    nombre_mostrado = username

                id_interno = item.get("id_usuario", None)
                contrasena_plana = self._extraer_contrasena_plana(item)
                rol_txt = normaliza_rol(item.get("rol", "trabajador"))
                rol_enum = Rol.ADMINISTRADOR if rol_txt == "Administrador" else Rol.TRABAJADOR

                if isinstance(username, str) and len(username) > 0:
                    self._usuarios.append(
                        Usuario(
                            id_interno=id_interno,
                            username=username,
                            nombre_mostrado=nombre_mostrado,
                            contrasena_plana=contrasena_plana,
                            rol=rol_enum
                        )
                    )

    # -------- API de login ----------
    def buscar_por_username(self, username):
        for u in self._usuarios:
            if u.username == username:
                return u
        return None

    def verificar_login(self, username, contrasena):
        u = self.buscar_por_username(username)
        if u is None:
            return None
        if u.verificar_contrasena(contrasena):
            return u
        return None
    
    