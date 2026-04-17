import socket
import json
import threading
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

HOST = "127.0.0.1"
PORT = 5000


def manejar_cliente(conn, addr):
    from model.ticket_model import TicketModel
    model = TicketModel()

    print(f"Cliente conectado: {addr}")

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            request = json.loads(data.decode())
            accion = request.get("accion")

            if accion == "obtener_tickets":
                conn.send(json.dumps(model.obtener_tickets()).encode())

            elif accion == "crear_tickets":
                ticket = request.get("ticket", {})
                ticket.setdefault(
                    "fecha_hora",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                conn.send(json.dumps(model.crear_tickets(ticket)).encode())

            elif accion == "obtener_mensajes":
                conn.send(json.dumps(
                    model.obtener_mensajes(request.get("id_ticket"))
                ).encode())

            elif accion == "enviar_mensaje":
                mensaje = request.get("mensaje", {})
                mensaje.setdefault(
                    "fecha_hora",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                conn.send(json.dumps(
                    model.enviar_mensaje(mensaje)
                ).encode())

            elif accion == "asignar_tecnico":
                conn.send(json.dumps(
                    model.asignar_ticket(
                        request.get("id_ticket"),
                        request.get("id_destinatario"),
                        request.get("nombre_destinatario")
                    )
                ).encode())

            elif accion == "cerrar_ticket":
                conn.send(json.dumps(
                    model.cerrar_ticket(request.get("id_ticket"))
                ).encode())

            elif accion == "redirigir_ticket":
                conn.send(json.dumps(
                    model.redirigir_ticket(
                        request.get("id_ticket"),
                        request.get("rol_destino")
                    )
                ).encode())

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
        print(f"Cliente desconectado: {addr}")


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=manejar_cliente,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    iniciar_servidor()