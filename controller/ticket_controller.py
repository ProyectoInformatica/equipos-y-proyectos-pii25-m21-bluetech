from Client.client import ApiClient
from datetime import datetime

class TicketController:
    def __init__(self):
        self.client = ApiClient()
        # caches persistentes
        self.tickets_cache = {}
        self.mensajes_cache = {}
        self.ultimo_msj_id = {}   

    # --- TICKETS ---
    def obtener_tickets_procesados(self, usuario, rol_usuario):
        response = self.client.obtener_tickets(usuario.id_usuario, rol_usuario)
        nuevos_tickets = []
        if response.get("status") == "ok":
            nuevos = response.get("tickets", [])
            for t in nuevos:
                id_t = t["id_ticket"]
                # SOLO añadir si es nuevo o actualizado
                if id_t not in self.tickets_cache or self.tickets_cache[id_t] != t:
                    self.tickets_cache[id_t] = t
                    nuevos_tickets.append(t)
        return nuevos_tickets  # SOLO devolvemos nuevos

    def obtener_todos_los_tickets(self):
        return list(self.tickets_cache.values())

    # --- MENSAJES ---
    def actualizar_chat(self, id_ticket, solo_nuevos=False):
        ultimo = self.ultimo_msj_id.get(id_ticket, 0)
        nuevos = self.client.obtener_mensajes(id_ticket, ultimo)
        if id_ticket not in self.mensajes_cache:
            self.mensajes_cache[id_ticket] = []
        if nuevos:
            existentes = {m["id_mensaje"] for m in self.mensajes_cache[id_ticket]}
            for m in nuevos:
                if m["id_mensaje"] not in existentes:
                    self.mensajes_cache[id_ticket].append(m)
            self.ultimo_msj_id[id_ticket] = nuevos[-1]["id_mensaje"]
        return nuevos if solo_nuevos else self.mensajes_cache[id_ticket]

    def enviar_mensaje(self, usuario, id_ticket, texto):
        mensaje = {
            "id_ticket": id_ticket,
            "id_emisor": usuario.id_usuario,
            "nombre_emisor": usuario.nombre_usuario,
            "rol": usuario.rol,
            "texto": texto,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.client.enviar_mensaje(mensaje)

    # --- ADMINISTRACIÓN TICKETS ---
    def crear_ticket(self, usuario, descripcion, rol_destinatario):
        rol_map = {
            "trabajador": 1,
            "administrador": 2,
            "tecnico": 3
        }
        ticket = {
            "id_emisor": usuario.id_usuario,
            "id_rol_emisor": rol_map.get(usuario.rol),
            "nombre_emisor": usuario.nombre_usuario,
            "descripcion": descripcion,
            "estado": "pendiente",
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rol_destinatario": rol_destinatario,
            "id_destinatario": None,
            "nombre_destinatario": None
        }
        return self.client.crear_tickets(ticket)

    def asignar_ticket(self, id_ticket, usuario_tecnico):
        return self.client.asignar_ticket(id_ticket, usuario_tecnico.id_usuario, usuario_tecnico.nombre_usuario)

    def cerrar_ticket(self, id_ticket):
        return self.client.cerrar_ticket(id_ticket)

    def redirigir_ticket(self, id_ticket, rol_destino):
        self.client.asignar_ticket(id_ticket, None, None)
        return self.client.redirigir_ticket(id_ticket, rol_destino)