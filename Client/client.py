import socket
import json

class ApiClient:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    # TICKETS
    def obtener_tickets(self, id_usuario, rol_usuario):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            request = {
                "accion": "obtener_tickets",
                "id_usuario": id_usuario,
                "rol_usuario": rol_usuario
            }
            client.send((json.dumps(request) + "\n").encode())
            f = client.makefile('r', encoding='utf-8')
            header = json.loads(f.readline())
            tickets = []
            for _ in range(header.get("total", 0)):
                tickets.append(json.loads(f.readline()))
            client.close()
            return {"status": "ok", "tickets": tickets}
        except Exception as e:
            return {"status": "error", "mensaje": str(e)}

    # MENSAJES
    def obtener_mensajes(self, id_ticket, ultimo_id=0):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            request = {
                "accion": "obtener_mensajes",
                "id_ticket": id_ticket,
                "ultimo_id": ultimo_id
            }
            client.send((json.dumps(request) + "\n").encode())
            f = client.makefile('r', encoding='utf-8')
            header = json.loads(f.readline())
            mensajes = []
            for _ in range(header.get("total", 0)):
                mensajes.append(json.loads(f.readline()))
            client.close()
            return mensajes
        except:
            return []

    def enviar_peticion(self, data):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))
        client.send((json.dumps(data) + "\n").encode())
        respuesta = client.recv(8192)
        client.close()
        return json.loads(respuesta.decode())

    def crear_tickets(self, ticket):
        return self.enviar_peticion({"accion": "crear_tickets", "ticket": ticket})

    def enviar_mensaje(self, mensaje):
        return self.enviar_peticion({"accion": "enviar_mensaje", "mensaje": mensaje})

    def asignar_ticket(self, id_ticket, id_destinatario, nombre_destinatario):
        return self.enviar_peticion({
            "accion": "asignar_tecnico",
            "id_ticket": id_ticket,
            "id_destinatario": id_destinatario,
            "nombre_destinatario": nombre_destinatario
        })

    def cerrar_ticket(self, id_ticket):
        return self.enviar_peticion({
            "accion": "cerrar_ticket",
            "id_ticket": id_ticket
        })

    def redirigir_ticket(self, id_ticket, rol_destino):
        return self.enviar_peticion({
            "accion": "redirigir_ticket",
            "id_ticket": id_ticket,
            "rol_destino": rol_destino
        })