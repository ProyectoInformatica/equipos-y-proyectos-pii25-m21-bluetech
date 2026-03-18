# controller/gestion_usuarios_controller.py
import hashlib
from model.usuario_model import UsuariosModel

AVISO_MIGRACION = "⚠️ IDs sin migrar. Actualiza usuarios.json: trabajadores 1001+, administradores 2001+ y técnicos 3001+."


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
        data = self.model.leer()
        usuarios = data.get("usuarios", [])

        trabajadores = []
        administradores = []
        tecnicos = []

        for u in usuarios:
            rol = (u.get("rol") or "").lower()
            registro = {
                "id": u.get("id_usuario"),
                "login": u.get("nombre_usuario")
            }

            if rol == "trabajador":
                trabajadores.append(registro)
            elif rol == "administrador":
                administradores.append(registro)
            elif rol == "tecnico":
                tecnicos.append(registro)

        trabajadores.sort(key=lambda x: x["id"])
        administradores.sort(key=lambda x: x["id"])
        tecnicos.sort(key=lambda x: x["id"])

        return trabajadores, administradores, tecnicos

    def crear_usuario(self, payload):
        rol = (payload.get("rol") or "").strip().lower()

        if rol not in ("trabajador", "administrador", "tecnico"):
            return False, "Rol no válido."

        if not self.model.ids_migrados():
            return False, AVISO_MIGRACION

        login = payload.get("login", "").strip()

        if not login:
            return False, "Debe introducir un nombre de usuario."

        # Evitar duplicados
        if self.model.existe_login(login):
            return False, "El nombre de usuario ya existe. Por favor, pruebe con otro."

        data = self.model.leer()

        # Generar ID según rol
        nuevo_id = self.model.siguiente_id(rol)

        # Construir usuario
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
