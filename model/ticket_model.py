import json
import os
from datetime import datetime

RUTA_TICKETS = "data/tickets.json"

class TicketModel:
    def leer_tickets(self):
        if not os.path.exists(RUTA_TICKETS):
            return []
        try:
            with open(RUTA_TICKETS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def guardar_tickets(self, tickets):
        with open(RUTA_TICKETS, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=4)

    def generar_ticket_automatico(self, id_habitacion, id_sensor, nombre, tipo_sensor, valor_detectado, limite_establecido, descripcion, estado="pendiente"):
        tickets = self.leer_tickets()

        for t in tickets:
            if (t["id_sensor"] == id_sensor and 
                t["tipo_sensor"] == tipo_sensor and 
                t["estado"] != "finalizado"):
                return False
        
        nuevo_ticket = {
            "id_ticket": len(tickets) + 1,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id_habitacion": id_habitacion,
            "id_sensor": id_sensor,
            "nombre_emisor": nombre,
            "tipo_sensor": tipo_sensor, 
            "valor_detectado": valor_detectado,
            "limite_establecido": limite_establecido,
            "descripcion": descripcion,
            "estado": estado
        }

        tickets.append(nuevo_ticket)
        self.guardar_tickets(tickets)
        return True