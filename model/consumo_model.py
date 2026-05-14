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
        self.variacion = variacion
        self.w_actual = w_base
        self.historial = deque(maxlen=50)

    def actualizar(self):
        """Simula fluctuación realista del consumo"""
        factor = 1 + random.uniform(-self.variacion, self.variacion)
        self.w_actual = self.w_base * factor
        self.historial.append({
            "timestamp": datetime.now(),
            "valor": self.w_actual
        })
        return self.w_actual

    @property
    def detalle(self):
        return f"~{self.w_actual:.2f} W (Base: {self.w_base} W)"


class SimuladorConsumo:
    def __init__(self):
        self.sensores = [
            SensorConsumo("ESP32", "0.80 W", 0.80, 0.08),
            SensorConsumo("DHT11", "0.02 W", 0.02, 0.10),
            SensorConsumo("MQ-2", "0.75 W", 0.75, 0.12),
            SensorConsumo("3 LEDs activos", "0.12 W", 0.12, 0.05),
        ]

        self.simulando = False
        self.hilo = None
        self.historial_total = deque(maxlen=50)
        self.intervalo = 2.0

    def _bucle_simulacion(self, callback):
        while self.simulando:
            total_w = 0

            for sensor in self.sensores:
                total_w += sensor.actualizar()

            self.historial_total.append({
                "timestamp": datetime.now(),
                "valor": total_w
            })

            if callback:
                callback()

            time.sleep(self.intervalo)

    def iniciar(self, callback=None):
        if not self.simulando:
            self.simulando = True
            self.hilo = threading.Thread(
                target=self._bucle_simulacion,
                args=(callback,),
                daemon=True
            )
            self.hilo.start()

    def detener(self):
        self.simulando = False
        if self.hilo:
            self.hilo.join(timeout=1.0)

    def obtener_estadisticas(self):
        valores = [h["valor"] for h in self.historial_total]

        if not valores:
            return {
                "promedio": 0,
                "min": 0,
                "max": 0,
                "tendencia": "Estable",
                "actual": 0
            }

        promedio = sum(valores) / len(valores)
        min_val = min(valores)
        max_val = max(valores)

        tendencia = "Estable"
        if len(valores) >= 10:
            reciente = sum(valores[-5:]) / 5
            anterior = sum(valores[-10:-5]) / 5

            if anterior > 0:
                diff = ((reciente - anterior) / anterior) * 100
                if diff > 5:
                    tendencia = "Subiendo"
                elif diff < -5:
                    tendencia = "Bajando"

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
        simulador.iniciar(callback)

    @staticmethod
    def detener_simulacion():
        simulador.detener()

    @staticmethod
    def esta_simulando():
        return simulador.simulando