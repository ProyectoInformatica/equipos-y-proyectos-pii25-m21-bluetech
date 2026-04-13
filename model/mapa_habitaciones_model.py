from Database.conexionBD import obtener_conexion
from model.eliminar_habitacion import eliminar_habitacion
from model.crear_habitaciones import crear_habitacion_con_sensores

# CARGA DE DATOS DESDE BD
def cargar_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_habitacion, estado, tipo_sala FROM habitacion")
    resultados = cursor.fetchall()
    datos = {
        "habitaciones": {
            "id_habitacion": [r[0] for r in resultados],
            "estado": [r[1] for r in resultados],
            "tipo_sala": [r[2] for r in resultados],
        }
    }
    conexion.close()
    return datos

# SENSORES DESDE BD
def cargar_sensores_humedad():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # Usamos una subconsulta para traer la última medición de cada sensor
    cursor.execute("""
        SELECT s.id_sensor, 
               (SELECT m.valor FROM medicion m 
                WHERE m.fk_id_sensor = s.id_sensor 
                ORDER BY m.fecha_hora DESC LIMIT 1) as ultimo_valor
        FROM sensor s
        JOIN parametro p ON s.fk_id_parametro = p.id_parametro
        WHERE p.nombre LIKE 'Humedad%'
    """)
    resultados = cursor.fetchall()
    conexion.close()
    
    # Manejamos posibles valores None si no hay mediciones aún
    return {
        "id_sensor": [r[0] for r in resultados],
        "humedad": [float(r[1]) if r[1] is not None else 0.0 for r in resultados]
    }

def cargar_sensores_temperatura():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT s.id_sensor, 
               (SELECT m.valor FROM medicion m 
                WHERE m.fk_id_sensor = s.id_sensor 
                ORDER BY m.fecha_hora DESC LIMIT 1) as ultimo_valor
        FROM sensor s
        JOIN parametro p ON s.fk_id_parametro = p.id_parametro
        WHERE p.nombre LIKE 'Temperatura%'
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return {
        "id_sensor": [r[0] for r in resultados],
        "temperatura": [float(r[1]) if r[1] is not None else 0.0 for r in resultados]
    }

def cargar_sensores_calidad_aire():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT s.id_sensor, 
               (SELECT m.valor FROM medicion m 
                WHERE m.fk_id_sensor = s.id_sensor 
                ORDER BY m.fecha_hora DESC LIMIT 1) as ultimo_valor
        FROM sensor s
        JOIN parametro p ON s.fk_id_parametro = p.id_parametro
        WHERE p.nombre LIKE '%Aire%'
    """)
    resultados = cursor.fetchall()
    conexion.close()
    
    valores = [float(r[1]) if r[1] is not None else 0.0 for r in resultados]
    return {
        "id_sensor": [r[0] for r in resultados],
        "calidad_aire": {
            "PM2.5": valores, "PM10": valores, "CO": valores,
            "NO2": valores, "CO2": valores, "TVOC": valores
        }
    }

def cargar_valores_comparativos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.nombre, v.min, v.max
        FROM valores_comparativos v
        JOIN parametro p ON v.id_parametro = p.id_parametro
    """)
    resultados = cursor.fetchall()
    conexion.close()
    rangos = {
        "temperatura": {},
        "humedad": {},
        "calidad_aire": {}
    }
    for nombre, min_val, max_val in resultados:
        if "Temperatura" in nombre:
            rangos["temperatura"] = {
                "min": float(min_val),
                "max": float(max_val)
            }
        elif "Humedad" in nombre:
            rangos["humedad"] = {
                "min": float(min_val),
                "max": float(max_val)
            }
        else:
            # calidad del aire (general)
            rangos["calidad_aire"] = {
                "PM2.5": {"max": float(max_val)},
                "PM10": {"max": float(max_val)},
                "CO": {"max": float(max_val)},
                "NO2": {"max": float(max_val)},
                "CO2": {"max": float(max_val)},
                "TVOC": {"max": float(max_val)},
            }
    return rangos

# FUNCIONES DE NEGOCIO
def crear_nueva_habitacion(estado, tipo_sala):
    return crear_habitacion_con_sensores(estado, tipo_sala)

def eliminar_habitacion_por_id(id_hab):
    return eliminar_habitacion(id_hab)

def duplicar_planta(datos, planta_index):
    habitaciones_por_planta = 10
    inicio = planta_index * habitaciones_por_planta
    fin = inicio + habitaciones_por_planta
    ids = datos["habitaciones"]["id_habitacion"]
    estados = datos["habitaciones"]["estado"]
    tipos = datos["habitaciones"]["tipo_sala"]
    for i in range(inicio, min(fin, len(ids))):
        crear_habitacion_con_sensores(estados[i], tipos[i])

def eliminar_planta_completa(datos, planta_index):
    habitaciones_por_planta = 10
    inicio = planta_index * habitaciones_por_planta
    fin = inicio + habitaciones_por_planta
    ids = datos["habitaciones"]["id_habitacion"]
    ids_planta = ids[inicio:fin]
    for id_hab in sorted(ids_planta, reverse=True):
        eliminar_habitacion(id_hab)