from model.alerta_model import AlertaModelBD

class AlertaController:

    def __init__(self):
        self.model = AlertaModelBD()

    def obtener_pendientes(self):
        tickets = self.model.leer_tickets()

        return [
            t for t in tickets
            if t["estado"].lower() != "finalizado"
        ]

    def tomar_ticket(
        self,
        id_alerta,
        id_usuario,
        nombre_usuario
    ):
        return self.model.actualizar_estado_alerta(
            id_alerta,
            "En_Proceso",
            id_usuario,
            nombre_usuario
        )

    def desasignar_ticket(self, id_alerta):
        return self.model.actualizar_estado_alerta(
            id_alerta,
            "Pendiente",
            None,
            None
        )

    def finalizar_ticket(
        self,
        id_alerta,
        id_usuario,
        nombre_usuario
    ):
        return self.model.actualizar_estado_alerta(
            id_alerta,
            "Finalizado",
            id_usuario,
            nombre_usuario
        )