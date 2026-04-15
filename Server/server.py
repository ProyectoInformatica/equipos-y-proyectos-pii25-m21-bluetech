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
    # Creamos una instancia del modelo
    from model.ticket_model import TicketModel
    model = TicketModel()

    print(f"Cliente conectado: {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            request = json.loads(data.decode())
            accion = request.get("accion")

            # OBTENER TICKETS
            if accion == "obtener_tickets":
                response = model.obtener_tickets()
                conn.send(json.dumps(response).encode())

            # CREAR TICKETS
            elif accion == "crear_tickets":
                tickets = request.get("ticket", {})
                # Ajustamos fecha_hora si no viene
                if "fecha_hora" not in tickets:
                    tickets["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = model.crear_tickets(tickets)
                conn.send(json.dumps(result).encode())

            # OBTENER MENSAJES
            elif accion == "obtener_mensajes":
                id_ticket = request.get("id_ticket")
                response = model.obtener_mensajes(id_ticket)
                conn.send(json.dumps(response).encode())

            # ENVIAR MENSAJE
            elif accion == "enviar_mensaje":
                mensaje = request.get("mensaje", {})
                if "fecha_hora" not in mensaje:
                    mensaje["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = model.enviar_mensaje(mensaje)
                conn.send(json.dumps(result).encode())

            # ASIGNAR TECNICO
            elif accion == "asignar_tecnico":
                id_ticket = request.get("id_ticket")
                id_tecnico = request.get("id_tecnico")
                nombre_tecnico = request.get("nombre_tecnico")
                result = model.asignar_ticket(id_ticket, id_tecnico, nombre_tecnico)
                conn.send(json.dumps(result).encode())
            
            elif accion == "cerrar_ticket":
                id_ticket = request.get("id_ticket")
                if not id_ticket:
                    response = {"status": "error", "mensaje": "id_ticket vacío"}
                else:
                    response = model.cerrar_ticket(id_ticket)
                conn.send(json.dumps(response).encode())
            
        except Exception as e:
            print("Error:", e)
            break

    conn.close()
    print(f"Cliente desconectado: {addr}")


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=manejar_cliente,args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()