import mysql.connector

try:
    # 1. Configurar la conexión
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Gabigoleador8",
        database="bluetech"
    )

    if conexion.is_connected():
        print("¡Conexión exitosa a la base de datos!")
        
        # 2. Crear un objeto cursor para ejecutar consultas
        cursor = conexion.cursor()
        
        # Ejemplo: Obtener la versión del servidor
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"Versión del servidor MySQL: {version[0]}")

except mysql.connector.Error as error:
    print(f"Error al conectar: {error}")

finally:
    # 3. Cerrar la conexión siempre
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("Conexión cerrada.")