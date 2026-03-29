import threading
import time
import random
import mysql.connector
from datetime import datetime

# ===============================
# CONFIGURACIÓN DE BASE DE DATOS
# ===============================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',       
    'password': 'Gabigoleador8',
    'database': 'bluetech'
}

# Variables globales que llenaremos dinámicamente
valores_actuales = {}
info_sensores = {} # Guardará a qué habitación pertenece cada sensor para el print
sensores_por_tipo = {
    'Temperatura': [],
    'Humedad': [],
    'Calidad de Aire': []
}
mutex = threading.Lock()

# ===============================
# INICIALIZACIÓN DINÁMICA
# ===============================
def cargar_sensores_desde_db():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        
        # Traemos los sensores, su tipo y la habitación a la que pertenecen
        cursor.execute("SELECT id_sensor, tipo_sensor, fk_id_habitacion FROM sensor")
        sensores = cursor.fetchall()
        
        for s in sensores:
            id_s = s['id_sensor']
            tipo = s['tipo_sensor']
            id_hab = s['fk_id_habitacion']
            
            info_sensores[id_s] = id_hab # Guardamos la info de la habitación
            
            # Los guardamos en su lista y les damos un valor inicial realista
            if tipo == 'Temperatura':
                sensores_por_tipo['Temperatura'].append(id_s)
                valores_actuales[id_s] = 24
            elif tipo == 'Humedad':
                sensores_por_tipo['Humedad'].append(id_s)
                valores_actuales[id_s] = 37
            elif tipo == 'Calidad de Aire':
                sensores_por_tipo['Calidad de Aire'].append(id_s)
                valores_actuales[id_s] = 400
                
        print(f"✅ ¡Éxito! {len(sensores)} sensores cargados desde MySQL.")
        print(f"  - Temperatura: {len(sensores_por_tipo['Temperatura'])} sensores")
        print(f"  - Humedad: {len(sensores_por_tipo['Humedad'])} sensores")
        print(f"  - Calidad de Aire: {len(sensores_por_tipo['Calidad de Aire'])} sensores\n")
        
        cursor.close()
        conexion.close()
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar a la DB: {e}")
        exit()

# ===============================
# FUNCIÓN PARA INSERTAR EN MYSQL
# ===============================
def insertar_medicion(id_sensor, valor, tipo):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        query = "INSERT INTO medicion (fecha_hora, valor, fk_id_sensor) VALUES (%s, %s, %s)"
        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(query, (ahora, int(valor), id_sensor))
        conexion.commit()
        
        # Print mejorado para ver en qué habitación estamos insertando el dato
        id_hab = info_sensores.get(id_sensor, "?")
        print(f"[{ahora}] Habitación {id_hab} | {tipo} -> Sensor {id_sensor:02d}: {int(valor)}")
        
        cursor.close()
        conexion.close()
    except mysql.connector.Error as e:
        print(f"Error de MySQL al insertar sensor {id_sensor}: {e}")

# ===============================
# HILOS DE SIMULACIÓN
# ===============================
def simular_temperatura(intervalo=5):
    while True:
        with mutex:
            for sensor in sensores_por_tipo['Temperatura']:
                cambio = random.choice([-1, 0, 1]) # Cambios más suaves para que sea realista
                valores_actuales[sensor] = max(18, min(32, valores_actuales[sensor] + cambio))
                insertar_medicion(sensor, valores_actuales[sensor], "Temp")
        time.sleep(intervalo)

def simular_humedad(intervalo=6):
    while True:
        with mutex:
            for sensor in sensores_por_tipo['Humedad']:
                cambio = random.choice([-2, -1, 0, 1, 2])
                valores_actuales[sensor] = max(30, min(60, valores_actuales[sensor] + cambio))
                insertar_medicion(sensor, valores_actuales[sensor], "Hum ")
        time.sleep(intervalo)

def simular_calidad_aire(intervalo=7):
    while True:
        with mutex:
            for sensor in sensores_por_tipo['Calidad de Aire']:
                cambio = random.choice([-15, -10, 0, 10, 15])
                valores_actuales[sensor] = max(350, min(800, valores_actuales[sensor] + cambio))
                insertar_medicion(sensor, valores_actuales[sensor], "Aire")
        time.sleep(intervalo)

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    print("="*40)
    print("  INICIANDO SIMULADOR BLUETECH v2.0")
    print("="*40)
    
    cargar_sensores_desde_db()
    
    if not valores_actuales:
        print("⚠️ No se encontraron sensores. Verifica tu tabla 'sensor'. Abortando.")
        exit()

    h_temp = threading.Thread(target=simular_temperatura, daemon=True)
    h_hum = threading.Thread(target=simular_humedad, daemon=True)
    h_aire = threading.Thread(target=simular_calidad_aire, daemon=True)

    h_temp.start()
    h_hum.start()
    h_aire.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Simulación detenida por el usuario.")