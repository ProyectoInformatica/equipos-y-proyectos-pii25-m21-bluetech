import socket
import json

class ApiClient:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    def enviar_peticion(self, data):
        """
        Envía una petición al servidor y devuelve la respuesta
        """
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            mensaje = json.dumps(data)
            client.send(mensaje.encode())
            respuesta = client.recv(8192)
            client.close()
            return json.loads(respuesta.decode())
        except Exception as e:
            return {
                "status": "error",
                "mensaje": str(e)
            }

    # ALERTAS
    def obtener_alertas(self):
        request = {
            "accion": "obtener_alertas"
        }
        return self.enviar_peticion(request)

    def crear_alerta(self, ticket):
        request = {
            "accion": "crear_alerta",
            "alerta": ticket
        }
        return self.enviar_peticion(request)

    def asignar_ticket(self, id_alerta, id_tecnico, nombre_tecnico):
        request = {
            "accion": "asignar_tecnico",
            "id_alerta": id_alerta,
            "id_tecnico": id_tecnico,
            "nombre_tecnico": nombre_tecnico
        }
        return self.enviar_peticion(request)

    def cerrar_alerta(self, id_alerta):
        request = {
            "accion": "cerrar_alerta",
            "id_alerta": id_alerta
        }
        return self.enviar_peticion(request)

    # MENSAJES
    def obtener_mensajes(self, id_alerta):
        request = {
            "accion": "obtener_mensajes",
            "id_alerta": id_alerta
        }
        return self.enviar_peticion(request)

    def enviar_mensaje(self, mensaje):
        request = {
            "accion": "enviar_mensaje",
            "mensaje": mensaje
        }
        return self.enviar_peticion(request)