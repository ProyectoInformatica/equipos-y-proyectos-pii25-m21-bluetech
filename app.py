from flask import Flask, request

from Database.conexionBD import obtener_conexion 

app = Flask(__name__)



ID_SENSOR_TEMP  = 5
ID_SENSOR_HUM   = 6
ID_SENSOR_GAS   = 7
ID_SENSOR_MULTI = 20  # ID asignado para el sensor multiordinario


def guardar_medicion(id_sensor, valor):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Usamos la estructura idéntica de tu SQL: fecha_hora, valor, fk_id_sensor
            query = "INSERT INTO medicion (fecha_hora, valor, fk_id_sensor) VALUES (NOW(), %s, %s)"
            cursor.execute(query, (valor, id_sensor))
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"[BD] Inserción correcta: Sensor {id_sensor} -> Valor {valor}")
        except Exception as e:
            print(f"[BD ERROR] Fallo al insertar en la base de datos: {e}")


@app.route("/datos", methods=["GET"])
def recibir_datos():
    temp = request.args.get("temp")
    hum = request.args.get("hum")
    gas = request.args.get("gas")

    if temp and hum and gas:
        # Insertamos las lecturas individuales en tu tabla 'medicion'
        guardar_medicion(ID_SENSOR_TEMP, int(float(temp)))
        guardar_medicion(ID_SENSOR_HUM, int(float(hum)))
        guardar_medicion(ID_SENSOR_GAS, int(gas))
        return "OK - Datos Estándar Procesados", 200
    else:
        return "Error: Faltan parámetros (temp, hum o gas)", 400


@app.route("/multiordinario", methods=["GET"])
def recibir_multiordinario():
    # Captura el parámetro 'txt' enviado por el método DataBaseLoader() de la ESP32
    txt = request.args.get("txt")

    if txt:
        print(f"[HTTP] Recibida media del Sensor Multiordinario: {txt}")
        
       )
        diccionario_estados = {
            "BAJO": 0,
            "NORMAL": 1,
            "ALTO": 2
        }
        
        
        valor_numerico_mapeado = diccionario_estados.get(txt.upper(), -1)
        
        
        guardar_medicion(ID_SENSOR_MULTI, valor_numerico_mapeado)
        
        return f"OK - Media del Multiordinario ({txt}) guardada como {valor_numerico_mapeado}", 200
    else:
        return "Error: Falta el parámetro alfanumérico 'txt'", 400


if __name__ == "__main__":
    # Escucha en todas las IPs de la red local en el puerto 5000
    app.run(host="0.0.0.0", port=5000, debug=True)