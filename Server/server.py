import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 5000

ALERTAS_FILE = "data/alertas.json"
MENSAJES_FILE = "data/mensajes.json"

def cargar_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def manejar_cliente(conn, addr):
    print(f"Cliente conectado: {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            request = json.loads(data.decode())
            accion = request.get("accion")

            # -------------------------
            # OBTENER ALERTAS
            # -------------------------
            if accion == "obtener_alertas":
                alertas = cargar_json(ALERTAS_FILE)
                response = {
                    "status": "ok",
                    "alertas": alertas
                }
                conn.send(json.dumps(response).encode())

            # -------------------------
            # CREAR ALERTA
            # -------------------------
            elif accion == "crear_alerta":
                alertas = cargar_json(ALERTAS_FILE)
                nueva = request["alerta"]
                nueva["id_alerta"] = len(alertas) + 1
                alertas.append(nueva)
                guardar_json(ALERTAS_FILE, alertas)
                conn.send(json.dumps({"status": "ok"}).encode())

            # -------------------------
            # OBTENER MENSAJES
            # -------------------------
            elif accion == "obtener_mensajes":
                mensajes = cargar_json(MENSAJES_FILE)
                id_alerta = request["id_alerta"]
                mensajes_alerta = [
                    m for m in mensajes if m["id_alerta"] == id_alerta
                ]
                conn.send(json.dumps({
                    "status": "ok",
                    "mensajes": mensajes_alerta
                }).encode())

            # -------------------------
            # ENVIAR MENSAJE
            # -------------------------
            elif accion == "enviar_mensaje":
                mensajes = cargar_json(MENSAJES_FILE)
                nuevo = request["mensaje"]
                nuevo["id_mensaje"] = len(mensajes) + 1
                mensajes.append(nuevo)
                guardar_json(MENSAJES_FILE, mensajes)
                conn.send(json.dumps({"status": "ok"}).encode())

            # -------------------------
            # ASIGNAR TECNICO
            # -------------------------
            elif accion == "asignar_tecnico":
                alertas = cargar_json(ALERTAS_FILE)
                id_alerta = request.get("id_alerta")
                id_tecnico = request.get("id_tecnico")
                nombre_tecnico = request.get("nombre_tecnico")
                encontrada = False
                asignada = False
                for alerta in alertas:
                    if alerta.get("id_alerta") == id_alerta:
                        encontrada = True
                        if alerta.get("estado") != "pendiente":
                            asignada = True
                        else:
                            alerta["id_tecnico"] = id_tecnico
                            alerta["nombre_tecnico"] = nombre_tecnico
                            alerta["estado"] = "en curso"
                if not encontrada:
                    conn.send(json.dumps({
                        "status": "error",
                        "mensaje": "Ticket no encontrado"
                    }).encode())
                elif asignada:
                    conn.send(json.dumps({
                        "status": "error",
                        "mensaje": "Ticket ya asignado"
                    }).encode())
                else:
                    guardar_json(ALERTAS_FILE, alertas)
                    conn.send(json.dumps({
                        "status": "ok"
                    }).encode())
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
    iniciar_servidor()