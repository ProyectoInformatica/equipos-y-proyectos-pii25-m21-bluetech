class SensorConsumo:
    def __init__(self, nombre, detalle, w):
        self.nombre = nombre
        self.detalle = detalle
        self.w = w

class ConsumoEnergeticoModel:
    @staticmethod
    def obtener_sensores():
        # Valores simulados (hasta sensores reales)
        return [
            SensorConsumo("ESP32 + CAM (OV2640)", "~2.0 W (Peak)", 2.0),
            SensorConsumo("DHT11", "~0.1 W", 0.1),
            SensorConsumo("MQ-2 (Humo)", "~1.6 W", 1.6),
            SensorConsumo("HC-SR04 (Distancia)", "~0.2 W", 0.2),
            SensorConsumo("Ventilador 5V + LEDs", "~1.5 W", 1.5),
            SensorConsumo("Motor DC 12V", "~2.4 W", 2.4),
        ]

    @staticmethod
    def consumo_total(sensores):
        return sum(s.w for s in sensores)
