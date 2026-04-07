import random
import time
import threading
from datetime import datetime
from collections import deque

class SensorConsumo:
    def __init__(self, nombre, detalle, w_base, variacion=0.2):
        self.nombre = nombre
        self.detalle_base = detalle
        self.w_base = w_base
        self.variacion = variacion  # Porcentaje de variación permitida
        self.w_actual = w_base
        self.historial = deque(maxlen=50)  # Últimos 50 valores
        
    def actualizar(self):
        """Simula fluctuación realista del consumo"""
        # Variación aleatoria entre -variacion% y +variacion%
        factor = 1 + random.uniform(-self.variacion, self.variacion)
        self.w_actual = self.w_base * factor
        self.historial.append({
            'timestamp': datetime.now(),
            'valor': self.w_actual
        })
        return self.w_actual
    
    @property
    def detalle(self):
        return f"~{self.w_actual:.2f} W (Base: {self.w_base}W)"

class SimuladorConsumo:
    def __init__(self):
        self.sensores = [
            SensorConsumo("ESP32 + CAM (OV2640)", "2.0 W", 2.0, 0.15),
            SensorConsumo("DHT11", "0.1 W", 0.1, 0.05),
            SensorConsumo("MQ-2 (Humo)", "1.6 W", 1.6, 0.20),
            SensorConsumo("HC-SR04 (Distancia)", "0.2 W", 0.2, 0.10),
            SensorConsumo("Ventilador 5V + LEDs", "1.5 W", 1.5, 0.30),  # Alto consumo variable
            SensorConsumo("Motor DC 12V", "2.4 W", 2.4, 0.40),  # Muy variable
        ]
        self.historial_total = deque(maxlen=100)  # Historial de consumo total
        self._simulando = False
        self._thread = None
        self.callback_actualizacion = None
        
    def iniciar_simulacion(self, intervalo=2.0, callback=None):
        """Inicia la simulación en segundo plano"""
        self.callback_actualizacion = callback
        if not self._simulando:
            self._simulando = True
            self._thread = threading.Thread(target=self._loop_simulacion, args=(intervalo,), daemon=True)
            self._thread.start()
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self._simulando = False
        
    def _loop_simulacion(self, intervalo):
        """Loop de actualización periódica"""
        while self._simulando:
            self.actualizar_datos()
            if self.callback_actualizacion:
                self.callback_actualizacion()
            time.sleep(intervalo)
    
    def actualizar_datos(self):
        """Actualiza todos los sensores y el total"""
        total = 0
        for sensor in self.sensores:
            total += sensor.actualizar()
        self.historial_total.append({
            'timestamp': datetime.now(),
            'valor': total
        })
        return total
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del consumo"""
        if not self.historial_total:
            return {"promedio": 0, "min": 0, "max": 0, "tendencia": "estable"}
        
        valores = [h['valor'] for h in self.historial_total]
        promedio = sum(valores) / len(valores)
        min_val = min(valores)
        max_val = max(valores)
        
        # Calcular tendencia (últimos 5 vs anteriores 5)
        tendencia = "estable"
        if len(valores) >= 10:
            reciente = sum(valores[-5:]) / 5
            anterior = sum(valores[-10:-5]) / 5
            diff = ((reciente - anterior) / anterior) * 100
            if diff > 5:
                tendencia = "subiendo ↑"
            elif diff < -5:
                tendencia = "bajando ↓"
        
        return {
            "promedio": promedio,
            "min": min_val,
            "max": max_val,
            "tendencia": tendencia,
            "actual": valores[-1] if valores else 0
        }


simulador = SimuladorConsumo()

class ConsumoEnergeticoModel:
    @staticmethod
    def obtener_sensores():
        return simulador.sensores
    
    @staticmethod
    def consumo_total():
        return sum(s.w_actual for s in simulador.sensores)
    
    @staticmethod
    def obtener_historial_sensor(nombre_sensor):
        for sensor in simulador.sensores:
            if sensor.nombre == nombre_sensor:
                return list(sensor.historial)
        return []
    
    @staticmethod
    def obtener_historial_total():
        return list(simulador.historial_total)
    
    @staticmethod
    def obtener_estadisticas():
        return simulador.obtener_estadisticas()
    
    @staticmethod
    def iniciar_simulacion(callback=None):
        simulador.iniciar_simulacion(intervalo=1.5, callback=callback)
    
    @staticmethod
    def detener_simulacion():
        simulador.detener_simulacion()
    
    @staticmethod
    def esta_simulando():
        return simulador._simulando