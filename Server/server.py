import socket
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

def manejar_cliente(conn, addr):
    # Creamos una instancia del modelo
    from model.alertas_usuario_model import AlertasUsuarioModel
    model = AlertasUsuarioModel()

    print(f"Cliente conectado: {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            request = json.loads(data.decode())
            accion = request.get("accion")

            # OBTENER ALERTAS
            if accion == "obtener_alertas":
                response = model.obtener_alertas()
                conn.send(json.dumps(response).encode())

            # CREAR ALERTA
            elif accion == "crear_alerta":
                alerta = request.get("alerta", {})
                # Ajustamos fecha_hora si no viene
                if "fecha_hora" not in alerta:
                    alerta["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = model.crear_alerta(alerta)
                conn.send(json.dumps(result).encode())

            # OBTENER MENSAJES
            elif accion == "obtener_mensajes":
                id_alerta = request.get("id_alerta")
                response = model.obtener_mensajes(id_alerta)
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
                id_alerta = request.get("id_alerta")
                id_tecnico = request.get("id_tecnico")
                nombre_tecnico = request.get("nombre_tecnico")
                result = model.asignar_ticket(id_alerta, id_tecnico, nombre_tecnico)
                conn.send(json.dumps(result).encode())
            
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
        thread = threading.Thread(
            target=manejar_cliente,
            args=(conn, addr)
        )
        thread.start()

if __name__ == "__main__":
    import json
    iniciar_servidor()