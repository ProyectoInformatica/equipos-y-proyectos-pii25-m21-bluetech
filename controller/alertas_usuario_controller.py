from model.alertas_usuario_model import AlertasUsuarioModel
from datetime import datetime

class AlertasUsuarioController:
    def __init__(self):
        self.model = AlertasUsuarioModel()

    # ALERTAS
    def obtener_alertas(self):
        response = self.model.obtener_alertas()
        if response.get("status") == "ok":
            return response.get("alertas", [])
        return []

    def obtener_alertas_usuario(self, id_emisor):
        alertas = self.obtener_alertas()
        return [a for a in alertas if a["id_emisor"] == id_emisor]

    def crear_alerta(self, usuario, descripcion):
        id_emisor = getattr(usuario, "id_usuario", "Desconocido")
        rol = getattr(usuario, "rol", "Sin Rol")
        nombre = getattr(usuario, "nombre", "")
        apellidos = getattr(usuario, "apellidos", "")
        nombre_completo = f"{nombre} {apellidos}".strip()
        ticket = {
            "id_emisor": id_emisor,
            "id_rol": rol,
            "nombre_emisor": nombre_completo,
            "descripcion": descripcion,
            "estado": "pendiente",
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.model.crear_alerta(ticket)

    # MENSAJES
    def obtener_mensajes(self, id_alerta):
        response = self.model.obtener_mensajes(id_alerta)
        if response.get("status") == "ok":
            return response.get("mensajes", [])
        return []

    def enviar_mensaje(self, usuario, id_alerta, texto):
        nombre = getattr(usuario, "nombre", "")
        apellidos = getattr(usuario, "apellidos", "")
        nombre_usuario = getattr(usuario, "nombre_usuario", "")
        nombre_completo = f"{nombre} {apellidos}".strip() or nombre_usuario
        mensaje = {
            "id_alerta": id_alerta,
            "id_emisor": getattr(usuario, "id_usuario", "desconocido"),
            "nombre_emisor": nombre_completo,
            "rol": getattr(usuario, "rol", "usuario"),
            "texto": texto,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.model.enviar_mensaje(mensaje)

    # ASIGNAR TICKET (TÉCNICO)
    def asignar_ticket(self, id_alerta, usuario_tecnico):
        id_tecnico = getattr(usuario_tecnico, "id_usuario", "desconocido")
        nombre = getattr(usuario_tecnico, "nombre", "")
        apellidos = getattr(usuario_tecnico, "apellidos", "")
        nombre_usuario = getattr(usuario_tecnico, "nombre_usuario", "")
        nombre_completo = f"{nombre} {apellidos}".strip() or nombre_usuario
        return self.model.asignar_ticket(id_alerta, id_tecnico, nombre_completo)