# model/usuarios_model.py
import json

BASE_ID_TRABAJADOR = 1001
BASE_ID_ADMIN = 2001


class UsuariosModel:
    def __init__(self, ruta="data/usuarios.json"):
        self.ruta = ruta

    def leer(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data.get("usuarios"), list):
                data["usuarios"] = []
            return data
        except FileNotFoundError:
            return {"usuarios": []}

    def escribir(self, data):
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def ids_migrados(self):
        data = self.leer()
        for u in data["usuarios"]:
            rol = (u.get("rol") or "").lower()
            uid = u.get("id_usuario")
            if rol == "trabajador" and uid < BASE_ID_TRABAJADOR:
                return False
            if rol == "administrador" and uid < BASE_ID_ADMIN:
                return False
        return True

    def siguiente_id(self, rol):
        data = self.leer()
        base = BASE_ID_TRABAJADOR if rol == "trabajador" else BASE_ID_ADMIN
        usados = {u["id_usuario"] for u in data["usuarios"] if u["rol"] == rol}
        nuevo = base
        while nuevo in usados:
            nuevo += 1
        return nuevo

    def existe_login(self, login):
        data = self.leer()
        login = login.strip().lower()

        for u in data.get("usuarios", []):
            if (u.get("nombre_usuario") or "").lower() == login:
                return True
        return False