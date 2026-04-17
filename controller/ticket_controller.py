from Client.client import ApiClient
from datetime import datetime

class TicketController:
    def __init__(self):
        self.client = ApiClient()

    # TICKETS
    def obtener_tickets(self):
        response = self.client.obtener_tickets()
        if response.get("status") == "ok":
            return response.get("tickets", [])
        return []
    
    def obtener_tickets_admin(self, id_usuario):
        tickets = self.obtener_tickets()
        return [
            t for t in tickets
            if t.get("rol_destinatario") == 2 or t.get("id_emisor") == id_usuario
        ]

    def obtener_tickets_tecnico(self, id_usuario):
        tickets = self.obtener_tickets()
        return [
            t for t in tickets
            if t.get("rol_destinatario") == 3 or t.get("id_emisor") == id_usuario
        ]

    def obtener_tickets_usuario(self, id_emisor):
        tickets = self.obtener_tickets()
        return [a for a in tickets if a["id_emisor"] == id_emisor]

    def crear_ticket(self, usuario, descripcion, rol_destinatario):
        id_emisor = usuario.id_usuario
        rol_map = {
            "trabajador": 1,
            "administrador": 2,
            "tecnico": 3
        }
        id_rol_emisor = getattr(usuario, "fk_id_rol", None)
        if id_rol_emisor is None:
            rol_texto = getattr(usuario, "rol", None)
            id_rol_emisor = rol_map.get(rol_texto)
        if id_rol_emisor is None:
            raise ValueError(f"Rol inválido del usuario: {getattr(usuario,'rol',None)}")
        nombre_completo = usuario.nombre_usuario
        ticket = {
            "id_emisor": id_emisor,
            "id_rol_emisor": id_rol_emisor,
            "nombre_emisor": nombre_completo,
            "descripcion": descripcion,
            "estado": "pendiente",
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rol_destinatario": int(rol_destinatario),
            "id_destinatario": None,
            "nombre_destinatario": None
        }
        return self.client.crear_tickets(ticket)

    def redirigir_ticket(self, id_ticket, rol_destino):
        return self.client.redirigir_ticket(id_ticket, rol_destino)

    # MENSAJES
    def obtener_mensajes(self, id_ticket):
        response = self.client.obtener_mensajes(id_ticket)
        if response.get("status") == "ok":
            return response.get("mensajes", [])
        return []

    def enviar_mensaje(self, usuario, id_ticket, texto):
        nombre = getattr(usuario, "nombre", "")
        apellidos = getattr(usuario, "apellidos", "")
        nombre_usuario = getattr(usuario, "nombre_usuario", "")
        nombre_completo = f"{nombre} {apellidos}".strip() or nombre_usuario
        mensaje = {
            "id_ticket": id_ticket,
            "id_emisor": getattr(usuario, "id_usuario", "desconocido"),
            "nombre_emisor": nombre_completo,
            "rol": getattr(usuario, "rol", "usuario"),
            "texto": texto,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.client.enviar_mensaje(mensaje)

    # ASIGNAR TICKET (TÉCNICO)
    def asignar_ticket(self, id_ticket, usuario_tecnico):
        id_tecnico = getattr(usuario_tecnico, "id_usuario", "desconocido")
        nombre = getattr(usuario_tecnico, "nombre", "")
        apellidos = getattr(usuario_tecnico, "apellidos", "")
        nombre_usuario = getattr(usuario_tecnico, "nombre_usuario", "")
        nombre_completo = f"{nombre} {apellidos}".strip() or nombre_usuario
        return self.client.asignar_ticket(id_ticket, id_tecnico, nombre_completo)
    
    def cerrar_ticket(self, id_ticket):
        return self.client.cerrar_ticket(id_ticket)