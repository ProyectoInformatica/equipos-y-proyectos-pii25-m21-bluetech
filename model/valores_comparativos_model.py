from data.conexionBD import obtener_conexion

def obtener_valores_bd():
    """Obtiene los valores comparativos desde la BD y devuelve un dict para las vistas."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    query = """
        SELECT vc.*, p.nombre AS nombre_parametro, p.descripcion, p.unidad
        FROM valores_comparativos vc
        JOIN parametro p ON vc.id_parametro = p.id_parametro
    """
    cursor.execute(query)
    filas = cursor.fetchall()
    datos = {"temperatura": {}, "humedad": {}, "calidad_aire": {}}
    for fila in filas:
        nombre_parametro = fila["nombre_parametro"].lower()
        if "temperatura" in nombre_parametro:
            categoria = "temperatura"
        elif "humedad" in nombre_parametro:
            categoria = "humedad"
        elif "aire" in nombre_parametro or "co2" in nombre_parametro:
            categoria = "calidad_aire"
        else:
            continue  # Ignorar otros parámetros
        valor = {
            "min": fila["min"],
            "max": fila["max"],
            "unidad": fila["unidad"],
            "descripcion": fila["descripcion"]
        }
        # Para temperatura y humedad
        if categoria in ("temperatura", "humedad"):
            datos[categoria] = valor
        # Para calidad del aire, usar subclave 'CO2'
        elif categoria == "calidad_aire":
            datos["calidad_aire"]["CO2"] = valor
    cursor.close()
    conexion.close()
    return datos

def actualizar_valor_bd(categoria, subclave, campo, valor):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # Actualizar min/max en valores_comparativos
    if campo in ("min", "max"):
        query = """
            UPDATE valores_comparativos vc
            JOIN parametro p ON vc.id_parametro = p.id_parametro
            SET vc.{campo} = %s
            WHERE p.nombre = %s
        """.format(campo=campo)
        nombre_parametro = categoria_to_parametro(categoria, subclave)
        cursor.execute(query, (valor, nombre_parametro))
    # Actualizar unidad/descripcion en parametro
    elif campo in ("unidad", "descripcion"):
        query = f"UPDATE parametro SET {campo} = %s WHERE nombre = %s"
        nombre_parametro = categoria_to_parametro(categoria, subclave)
        cursor.execute(query, (valor, nombre_parametro))
    conexion.commit()
    cursor.close()
    conexion.close()

def categoria_to_parametro(categoria, subclave=None):
    if categoria == "temperatura":
        return "Temperatura"
    elif categoria == "humedad":
        return "Humedad Relativa"
    elif categoria == "calidad_aire" and subclave == "CO2":
        return "Calidad del Aire (CO2)"
    else:
        return categoria