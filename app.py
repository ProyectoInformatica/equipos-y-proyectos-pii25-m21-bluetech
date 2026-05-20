from flask import Flask, request
from Database.conexionBD import obtener_conexion 

app = Flask(__name__)

# Mapeo de IDs de sensor (esto asume que los datos vienen de la Habitación 1)
# Deberás cambiar estos IDs según lo que diga tu tabla 'sensor'
ID_SENSOR_TEMP = 5
ID_SENSOR_HUM = 6
ID_SENSOR_GAS = 7
from flask import Flask, request
from Database.conexionBD import obtener_conexion

app = Flask(__name__)

# Sensores normales
ID_SENSOR_TEMP = 5
ID_SENSOR_HUM = 6
ID_SENSOR_GAS = 7

# Sensor biomédico
ID_SENSOR_BIO = 20 # <---- Añadido

# Añadido ----
def guardar_sensor_biordinario(valor, estado):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """INSERT INTO sensor_biordinario(id_sensor,valor,estado) VALUES(%s,%s,%s)"""
            cursor.execute(
                query,
                (ID_SENSOR_BIO, valor, estado)
            )
            conexion.commit()
        finally:
            cursor.close()
            conexion.close()
# ----

def guardar_medicion(id_sensor, valor):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            # NOW() inserta la fecha y hora actual automáticamente
            query = "INSERT INTO medicion (fecha_hora, valor, fk_id_sensor) VALUES (NOW(), %s, %s)"
            cursor.execute(query, (valor, id_sensor))
            conexion.commit()
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"Error al insertar en BD: {e}")

@app.route("/datos", methods=["GET"])
def recibir_datos():
    # Añadido ---
    sensor = request.args.get("sensor")
    if sensor == "biordinario":
        valor = request.args.get("valor")
        estado = request.args.get("estado")
        if valor is None or estado is None:
            return "Faltan datos biordinario", 400
        guardar_sensor_biordinario(int(valor),int(estado))
        return "Biordinario guardado", 200
    # ----

    temp = request.args.get("temp")
    hum = request.args.get("hum")
    gas = request.args.get("gas")

    if temp and hum and gas:
        print(f"Recibido: Temp={temp}, Hum={hum}, Gas={gas}")
        
        # Guardar cada valor como una entrada independiente en la tabla medicion
        guardar_medicion(ID_SENSOR_TEMP, temp)
        guardar_medicion(ID_SENSOR_HUM, hum)
        guardar_medicion(ID_SENSOR_GAS, gas)
        
        return "OK", 200
    else:
        return "Faltan datos", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
