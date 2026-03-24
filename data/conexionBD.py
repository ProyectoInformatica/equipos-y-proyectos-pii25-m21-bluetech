import mysql.connector

try:
    # 1. Configurar la conexión (Tus datos ya están aquí)
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Gabigoleador8",
        database="bluetech"
    )

    if conexion.is_connected():
        print("¡Conexión exitosa a la base de datos bluetech!")
        
        cursor = conexion.cursor()
        
        # --- EL CAMBIO ESTÁ AQUÍ ---
        # Cambia 'nombre_de_tu_tabla' por la tabla que quieras ver
        tabla_a_consultar = "rol" 
        
        print(f"\n--- Contenido de la tabla: {tabla_a_consultar} ---")
        cursor.execute(f"SELECT * FROM {tabla_a_consultar}")
        
        # fetchall() trae todas las filas de golpe
        filas = cursor.fetchall()
        
        if not filas:
            print("La tabla está vacía o no tiene registros.")
        else:
            for fila in filas:
                # Imprime cada registro. Cada 'fila' es una tupla.
                print(fila)

except mysql.connector.Error as error:
    print(f"Error al conectar o consultar: {error}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("\nConexión cerrada.")