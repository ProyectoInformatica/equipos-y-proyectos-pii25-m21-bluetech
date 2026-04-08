from model.ticket_model import TicketModelBD

class TicketController:
    def __init__(self):
        self.model = TicketModelBD()

    def obtener_pendientes(self):
        # Todos los tickets que no están finalizados
        return [t for t in self.model.leer_tickets() if t["estado"] != "finalizado"]

    def tomar_ticket(self, ticket_id, id_tecnico, nombre_tecnico):
        tickets = self.model.leer_tickets()
        modificado = False
        for t in tickets:
            if t["id_ticket"] == ticket_id and t["estado"] == "pendiente":
                t["estado"] = "en_proceso"
                t["tecnico_id"] = id_tecnico
                t["tecnico_nombre"] = nombre_tecnico
                modificado = True
        if modificado:
            self.model.guardar_tickets(tickets)
        return modificado
    
    def desasignar_ticket(self, ticket_id, id_tecnico):
        """Libera un ticket para que otros técnicos puedan tomarlo."""
        tickets = self.model.leer_tickets()
        modificado = False
        for t in tickets:
            # Solo podemos desasignar algo que ya está siendo atendido
            if t["id_ticket"] == ticket_id and t["estado"] == "en_proceso":
                if t["tecnico_id"] == id_tecnico:
                    t["estado"] = "pendiente"
                    t["tecnico_id"] = None
                    t["tecnico_nombre"] = None
                    modificado = True
        if modificado:
            self.model.guardar_tickets(tickets)
        return modificado

    def finalizar_ticket(self, ticket_id, id_tecnico):
        tickets = self.model.leer_tickets()
        modificado = False
        for t in tickets:
            if t["id_ticket"] == ticket_id and t["estado"] == "en_proceso":
                if t["tecnico_id"] == id_tecnico:
                    t["estado"] = "finalizado"
                    modificado = True
        if modificado:
            self.model.guardar_tickets(tickets)
        return modificado