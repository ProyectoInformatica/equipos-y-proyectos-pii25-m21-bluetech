# controller/gestion_usuarios_controller.py
import hashlib
from model.usuario_model import UsuariosModel

AVISO_MIGRACION = "⚠️ IDs sin migrar. Actualiza usuarios.json."


class GestionUsuariosController:
    def __init__(self):
        self.model = UsuariosModel()

    def comprobar_migracion(self):
        """
        Devuelve una tupla (ok, aviso):
        - ok: True si todos los IDs están migrados, False si hay IDs antiguos
        - aviso: None si ok, mensaje de advertencia si hay IDs antiguos
        """
        ok = self.model.ids_migrados()
        return ok, None if ok else AVISO_MIGRACION

    def obtener_listados(self):
        """
        Devuelve dos listas:
        - trabajadores
        - administradores
        """
        data = self.model.leer()
        usuarios = data.get("usuarios", [])

        trabajadores = []
        administradores = []

        for u in usuarios:
            if u.get("rol") == "trabajador":
                trabajadores.append({
                    "id": u.get("id_usuario"),
                    "login": u.get("nombre_usuario")
                })
            elif u.get("rol") == "administrador":
                administradores.append({
                    "id": u.get("id_usuario"),
                    "login": u.get("nombre_usuario")
                })

        trabajadores.sort(key=lambda x: x["id"])
        administradores.sort(key=lambda x: x["id"])

        return trabajadores, administradores

    def crear_usuario(self, payload):
        if not self.model.ids_migrados():
            return False, AVISO_MIGRACION

        login = payload.get("login", "").strip()

        # Evitar duplicados
        if self.model.existe_login(login):
            return False, "El nombre de usuario ya existe. Por favor, pruebe con otro."

        data = self.model.leer()
        rol = payload["rol"]

        nuevo_id = self.model.siguiente_id(rol)

        # Construimos el registro completo siguiendo el formato exacto
        nuevo_usuario = {
            "nombre": payload.get("nombre", "").strip(),
            "apellidos": payload.get("apellidos", "").strip(),
            "nombre_usuario": login,
            "contrasena_hash": payload.get("hash", ""),
            "rol": rol,
            "num_registros": 0,
            "estado": 3,
            "id_usuario": nuevo_id,
        }

        data["usuarios"].append(nuevo_usuario)
        self.model.escribir(data)

        return True, nuevo_id

    def eliminar_usuario(self, user_id):
        data = self.model.leer()
        antes = len(data["usuarios"])

        data["usuarios"] = [
            u for u in data["usuarios"] if u.get("id_usuario") != user_id
        ]

        if len(data["usuarios"]) == antes:
            return False, "Usuario no encontrado"

        self.model.escribir(data)
        return True, None
