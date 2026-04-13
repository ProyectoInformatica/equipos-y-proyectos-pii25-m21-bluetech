import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="bluetech"
        )
        return conexion

    except mysql.connector.Error as error:
        print("Error de conexión:", error)
        return None