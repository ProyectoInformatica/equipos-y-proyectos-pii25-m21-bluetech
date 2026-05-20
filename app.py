"""
app.py

Este fichero actúa como servidor Flask del proyecto BlueTech.

Su función principal es recibir datos enviados desde la ESP32 mediante
peticiones HTTP GET y almacenarlos posteriormente en la base de datos MySQL.

Flujo general:
1. Arduino/ESP32 lee los sensores.
2. Arduino construye una URL con los valores leídos.
3. Flask recibe la petición en una ruta concreta.
4. Flask extrae los parámetros con request.args.get().
5. Flask realiza el INSERT en MySQL usando obtener_conexion().

Para el checkpoint se añade una nueva ruta /biordinario, que permite recibir
los datos de un nuevo sensor biordinario. Este sensor genera dos valores:
uno numérico y otro alfanumérico.
"""

from flask import Flask, request
from Database.conexionBD import obtener_conexion 

app = Flask(__name__)

# Mapeo de IDs de sensor (esto asume que los datos vienen de la Habitación 1)
# Deberás cambiar estos IDs según lo que diga tu tabla 'sensor'
ID_SENSOR_TEMP = 5
ID_SENSOR_HUM = 6
ID_SENSOR_GAS = 7

# NUEVA FUNCIONALIDAD CHECKPOINT:
# ID del nuevo sensor biordinario insertado en la tabla sensor.
# Este sensor genera dos datos por lectura:
# - Un valor numérico.
# - Un valor alfanumérico.
ID_SENSOR_BIORDINARIO = 21

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

def guardar_medicion_biordinario(valor_numerico, valor_alfanumerico):
    """
    Inserta en la base de datos una medición del nuevo sensor biordinario.

    Este sensor es diferente a los sensores originales porque no genera
    un único valor, sino dos datos asociados a la misma lectura:

    - valor_numerico: dato numérico generado por el sensor.
    - valor_alfanumerico: dato textual generado por el sensor.

    La información se guarda en la tabla medicion_biordinario, creada
    específicamente para adaptar la base de datos a este nuevo tipo de sensor.
    """

    # Se obtiene la conexión con MySQL usando la función común del proyecto.
    conexion = obtener_conexion()

    # Solo se intenta insertar si la conexión se ha creado correctamente.
    if conexion:
        try:
            # El cursor permite ejecutar consultas SQL desde Python.
            cursor = conexion.cursor()

            # Consulta SQL para insertar una nueva medición biordinaria.
            #
            # NOW() guarda automáticamente la fecha y hora actual.
            # valor_numerico guarda el dato numérico recibido desde Arduino.
            # valor_alfanumerico guarda el dato textual recibido desde Arduino.
            # fk_id_sensor asocia esta medición con el sensor biordinario.
            query = """
                INSERT INTO medicion_biordinario 
                (fecha_hora, valor_numerico, valor_alfanumerico, fk_id_sensor)
                VALUES (NOW(), %s, %s, %s)
            """

            # Se ejecuta la consulta sustituyendo los %s por los valores reales.
            cursor.execute(query, (
                valor_numerico,
                valor_alfanumerico,
                ID_SENSOR_BIORDINARIO
            ))

            # commit() confirma definitivamente el INSERT en la base de datos.
            conexion.commit()

            # Se cierran cursor y conexión para liberar recursos.
            cursor.close()
            conexion.close()

        except Exception as e:
            # Si ocurre algún error durante la inserción, se muestra por consola.
            print(f"Error al insertar medición biordinaria: {e}")

@app.route("/datos", methods=["GET"])
def recibir_datos():
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
    
@app.route("/biordinario", methods=["GET"])
def recibir_biordinario():
    """
    Ruta Flask creada para recibir los datos del nuevo sensor biordinario.

    Arduino envía una petición GET con esta estructura:

    /biordinario?num=55.5&txt=NORMAL

    Donde:
    - num representa el valor numérico del sensor.
    - txt representa el valor alfanumérico del sensor.

    Esta ruta recibe los datos, los valida y llama a la función que realiza
    la inserción en MySQL.
    """

    # Se recogen los parámetros enviados por Arduino en la URL.
    valor_num = request.args.get("num")
    valor_texto = request.args.get("txt")

    # Validación básica: si falta alguno de los dos datos, se devuelve error 400.
    if not valor_num or not valor_texto:
        return "Faltan datos del sensor biordinario", 400

    # El valor numérico llega como texto desde la URL.
    # Se convierte a float para asegurar que realmente es un dato numérico.
    try:
        valor_num = float(valor_num)
    except ValueError:
        return "El valor numerico no es valido", 400

    # Si los datos son correctos, se insertan en la base de datos.
    guardar_medicion_biordinario(valor_num, valor_texto)

    # Mensaje de depuración para comprobar en consola qué datos han llegado.
    print(f"Biordinario recibido -> num: {valor_num}, txt: {valor_texto}")

    # Respuesta HTTP correcta para Arduino.
    # En el monitor serie de Arduino debería aparecer código 200.
    return "OK biordinario", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
