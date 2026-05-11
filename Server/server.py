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
        f = conn.makefile('r', encoding='utf-8')
        while True:
            line = f.readline()
            if not line:
                break
            request = json.loads(line)
            accion = request.get("accion")
            # 🟢 STREAMING TICKETS
            if accion == "obtener_tickets":
                data = model.obtener_tickets_filtrados(
                    request.get("id_usuario"),
                    request.get("rol_usuario")
                )
                tickets = data.get("tickets", [])
                header = json.dumps({
                    "status": "streaming",
                    "total": len(tickets)
                }) + "\n"
                conn.send(header.encode())
                for t in tickets:
                    linea = json.dumps(t) + "\n"
                    conn.send(linea.encode())
            # 🟢 CREAR TICKET
            elif accion == "crear_tickets":
                ticket = request.get("ticket", {})
                ticket.setdefault(
                    "fecha_hora",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                conn.send((json.dumps(model.crear_tickets(ticket)) + "\n").encode())
            # 🟢 STREAMING MENSAJES
            elif accion == "obtener_mensajes":
                id_ticket = request.get("id_ticket")
                ultimo_id = request.get("ultimo_id", 0)
                mensajes = model.obtener_mensajes(id_ticket, ultimo_id)
                header = json.dumps({
                    "status": "streaming",
                    "total": len(mensajes)
                }) + "\n"
                conn.send(header.encode())
                for m in mensajes:
                    if isinstance(m.get('fecha_hora'), datetime):
                        m['fecha_hora'] = m['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S")
                    conn.send((json.dumps(m) + "\n").encode())
            elif accion == "enviar_mensaje":
                mensaje = request.get("mensaje", {})
                mensaje.setdefault(
                    "fecha_hora",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                conn.send((json.dumps(model.enviar_mensaje(mensaje)) + "\n").encode())
            elif accion == "asignar_tecnico":
                conn.send((json.dumps(
                    model.asignar_ticket(
                        request.get("id_ticket"),
                        request.get("id_destinatario"),
                        request.get("nombre_destinatario")
                    )
                ) + "\n").encode())
            elif accion == "cerrar_ticket":
                conn.send((json.dumps(
                    model.cerrar_ticket(request.get("id_ticket"))
                ) + "\n").encode())
            elif accion == "redirigir_ticket":
                conn.send((json.dumps(
                    model.redirigir_ticket(
                        request.get("id_ticket"),
                        request.get("rol_destino")
                    )
                ) + "\n").encode())
    except Exception as e:
        print(f"Error con {addr}: {e}")
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