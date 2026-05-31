#include <WiFi.h>        // Librería para conectar la ESP32 a una red WiFi
#include <HTTPClient.h>  // Librería para enviar peticiones HTTP al servidor Flask
#include "DHT.h"         // Librería para leer el sensor DHT11

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN WIFI Y SERVIDOR FLASK
// ─────────────────────────────────────────────────────────────

const char* ssid     = "lucia";
const char* password = "12345678";

// IP del ordenador usando la zona con cobertura inalámbrica móvil de Windows.
const char* serverName = "http://192.168.137.1:5000/datos";

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN DEL SENSOR DHT11
// ─────────────────────────────────────────────────────────────

#define DHTPIN 25
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN DEL SENSOR MQ-2
// ─────────────────────────────────────────────────────────────

// A0 del MQ-2 debe ir conectado a GPIO32.
#define MQ2PIN 32

// ─────────────────────────────────────────────────────────────
// LEDS TIPO SEMÁFORO
// ─────────────────────────────────────────────────────────────

// Sensor 1: temperatura
#define LED_VERDE1    26
#define LED_AMARILLO1 27
#define LED_ROJO1     33

// Sensor 2: humedad
#define LED_VERDE2    18
#define LED_AMARILLO2 19
#define LED_ROJO2     21

// Sensor 3: gas/calidad del aire
#define LED_VERDE3    22
#define LED_AMARILLO3 23
#define LED_ROJO3     13

// ─────────────────────────────────────────────────────────────
// ZUMBADOR
// ─────────────────────────────────────────────────────────────

#define ZUMBADOR 14

// ─────────────────────────────────────────────────────────────
// UMBRALES DE ALERTA
// ─────────────────────────────────────────────────────────────

// Umbrales del sensor MQ-2.
const int GAS_EXTREMO  = 2500;
const int GAS_MODERADO = 1500;

// Umbrales de temperatura.
const float TEMP_EXTREMA  = 35.0;
const float TEMP_MODERADA = 27.0;

// Umbrales de humedad.
const float HUM_EXTREMA  = 80.0;
const float HUM_MODERADA = 60.0;

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN DE TIEMPOS
// ─────────────────────────────────────────────────────────────

// Intervalo entre lecturas de sensores y envíos a Flask.
const unsigned long INTERVALO_LECTURA = 5000;

// Tiempo que el buzzer permanece sonando en cada pitido.
const unsigned long TIEMPO_BUZZER_ON = 100;

// Tiempo de silencio entre pitidos.
const unsigned long TIEMPO_BUZZER_OFF = 1500;

// Guarda el instante de la última lectura de sensores.
unsigned long ultimaLectura = 0;

// Guarda el instante del último cambio de estado del buzzer.
unsigned long ultimoCambioBuzzer = 0;

// Indica si el buzzer está encendido o apagado.
bool estadoBuzzer = false;

// Indica si actualmente hay una alerta crítica.
bool alertaActual = false;

// ─────────────────────────────────────────────────────────────
// FUNCIONES AUXILIARES
// ─────────────────────────────────────────────────────────────

// Activa el zumbador usando PWM.
void buzzerOn() {
  ledcWrite(ZUMBADOR, 128);
}

// Apaga el zumbador.
void buzzerOff() {
  ledcWrite(ZUMBADOR, 0);
}

// Controla el buzzer de forma intermitente.
//
// Si hay alerta:
//   - emite un pitido corto
//   - espera un tiempo de silencio
//   - vuelve a pitar
//
// Si no hay alerta:
//   - apaga el buzzer completamente.
void actualizarBuzzer(bool alerta) {
  if (!alerta) {
    buzzerOff();
    estadoBuzzer = false;
    ultimoCambioBuzzer = millis();
  } else {
    unsigned long ahora = millis();

    if (estadoBuzzer) {
      if (ahora - ultimoCambioBuzzer >= TIEMPO_BUZZER_ON) {
        buzzerOff();
        estadoBuzzer = false;
        ultimoCambioBuzzer = ahora;
      }
    } else {
      if (ahora - ultimoCambioBuzzer >= TIEMPO_BUZZER_OFF) {
        buzzerOn();
        estadoBuzzer = true;
        ultimoCambioBuzzer = ahora;
      }
    }
  }
}

// Actualiza los LEDs de un sensor como si fueran un semáforo.
// nivel = 0 → verde
// nivel = 1 → amarillo
// nivel = 2 → rojo
void setSemaforo(int pinVerde, int pinAmarillo, int pinRojo, int nivel) {
  digitalWrite(pinVerde,    nivel == 0 ? HIGH : LOW);
  digitalWrite(pinAmarillo, nivel == 1 ? HIGH : LOW);
  digitalWrite(pinRojo,     nivel == 2 ? HIGH : LOW);
}

// Apaga todos los LEDs si hay un fallo de lectura.
void apagarSemaforos() {
  digitalWrite(LED_VERDE1, LOW);
  digitalWrite(LED_AMARILLO1, LOW);
  digitalWrite(LED_ROJO1, LOW);

  digitalWrite(LED_VERDE2, LOW);
  digitalWrite(LED_AMARILLO2, LOW);
  digitalWrite(LED_ROJO2, LOW);

  digitalWrite(LED_VERDE3, LOW);
  digitalWrite(LED_AMARILLO3, LOW);
  digitalWrite(LED_ROJO3, LOW);
}

// Intenta reconectar la WiFi si se ha desconectado.
void reconectarWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("  [AVISO] WiFi desconectado. Intentando reconectar...");

    WiFi.disconnect();
    WiFi.begin(ssid, password);

    int intentos = 0;

    while (WiFi.status() != WL_CONNECTED && intentos < 20) {
      delay(500);
      Serial.print(".");
      intentos++;
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("  WiFi reconectado correctamente.");
      Serial.print("  IP local de la ESP32: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("  [ERROR] No se pudo reconectar al WiFi.");
    }
  }
}

// ─────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  delay(2000);

  // Inicializa el sensor DHT11.
  dht.begin();

  // Configura el pin del MQ-2 como entrada.
  pinMode(MQ2PIN, INPUT);

  // Lista de LEDs para configurarlos de forma compacta.
  int leds[] = {
    LED_VERDE1, LED_AMARILLO1, LED_ROJO1,
    LED_VERDE2, LED_AMARILLO2, LED_ROJO2,
    LED_VERDE3, LED_AMARILLO3, LED_ROJO3
  };

  // Configura los LEDs como salida y los deja apagados.
  for (int i = 0; i < 9; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }

  // Configura el zumbador mediante PWM.
  // Esta función es válida para ESP32 core 3.x.
  ledcAttach(ZUMBADOR, 2000, 8);

  // El zumbador empieza apagado.
  buzzerOff();

  Serial.println("==============================");
  Serial.println("  Sistema de monitoreo IoT");
  Serial.println("==============================");
  Serial.println("Conectando a WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int intentos = 0;

  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(">>> WiFi CONECTADO <<<");
    Serial.print("IP local de la ESP32: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("[ERROR] No se pudo conectar al WiFi.");
    Serial.println("El sistema seguira leyendo sensores, pero no enviara datos si no hay conexion.");
  }

  Serial.println("==============================\n");
}

// ─────────────────────────────────────────────────────────────
// LOOP
// ─────────────────────────────────────────────────────────────

void loop() {
  // El buzzer se actualiza continuamente.
  // Esto permite que el pitido sea intermitente y no se quede fijo.
  actualizarBuzzer(alertaActual);

  // Solo se leen sensores y se envían datos cada 5 segundos.
  if (millis() - ultimaLectura < INTERVALO_LECTURA) {
    return;
  }

  ultimaLectura = millis();

  // ───────────────────────────────────────────────────────────
  // LECTURA DE SENSORES
  // ───────────────────────────────────────────────────────────

  float temperatura = dht.readTemperature();
  float humedad = dht.readHumidity();
  int mq2Value = analogRead(MQ2PIN);

  Serial.println("------------------------------");
  Serial.println("  LECTURA DE SENSORES");
  Serial.println("------------------------------");

  // Si el DHT11 falla, no se envían datos a la base de datos.
  if (isnan(temperatura) || isnan(humedad)) {
    Serial.println("[ERROR] Fallo al leer el DHT11.");
    Serial.println("[ERROR] No se envian datos a la base de datos en esta lectura.");

    apagarSemaforos();

    alertaActual = false;
    actualizarBuzzer(alertaActual);

    Serial.println("==============================\n");

  } else {
    Serial.print("  Temperatura : ");
    Serial.print(temperatura);
    Serial.println(" C");

    Serial.print("  Humedad     : ");
    Serial.print(humedad);
    Serial.println(" %");

    Serial.print("  Gas MQ-2    : ");
    Serial.println(mq2Value);

    if (mq2Value >= 4095) {
      Serial.println("[AVISO] El MQ-2 esta dando 4095.");
      Serial.println("[AVISO] Puede estar saturado, mal conectado o usando D0 en vez de A0.");
    }

    // ─────────────────────────────────────────────────────────
    // ENVÍO DE DATOS A FLASK
    // ─────────────────────────────────────────────────────────

    Serial.println("------------------------------");
    Serial.println("  ENVIO AL SERVIDOR");
    Serial.println("------------------------------");

    reconectarWiFi();

    if (WiFi.status() == WL_CONNECTED) {
      String url = String(serverName)
                   + "?temp=" + String(temperatura)
                   + "&hum="  + String(humedad)
                   + "&gas="  + String(mq2Value);

      Serial.print("  URL: ");
      Serial.println(url);

      HTTPClient http;

      http.begin(url);

      int code = http.GET();

      if (code > 0) {
        Serial.print("  Respuesta HTTP: ");
        Serial.println(code);
      } else {
        Serial.print("  [ERROR] HTTP: ");
        Serial.println(code);
      }

      http.end();

    } else {
      Serial.println("  [ERROR] WiFi desconectado. No se envian datos.");
    }

    // ─────────────────────────────────────────────────────────
    // CÁLCULO DE NIVELES DE ALERTA
    // ─────────────────────────────────────────────────────────

    int nivelTemp = 0;

    if (temperatura > TEMP_EXTREMA) {
      nivelTemp = 2;
    } else if (temperatura > TEMP_MODERADA) {
      nivelTemp = 1;
    }

    int nivelHum = 0;

    if (humedad > HUM_EXTREMA) {
      nivelHum = 2;
    } else if (humedad > HUM_MODERADA) {
      nivelHum = 1;
    }

    int nivelGas = 0;

    if (mq2Value > GAS_EXTREMO) {
      nivelGas = 2;
    } else if (mq2Value > GAS_MODERADO) {
      nivelGas = 1;
    }

    // ─────────────────────────────────────────────────────────
    // ACTUALIZACIÓN DE SEMÁFOROS
    // ─────────────────────────────────────────────────────────

    setSemaforo(LED_VERDE1, LED_AMARILLO1, LED_ROJO1, nivelTemp);
    setSemaforo(LED_VERDE2, LED_AMARILLO2, LED_ROJO2, nivelHum);
    setSemaforo(LED_VERDE3, LED_AMARILLO3, LED_ROJO3, nivelGas);

    // ─────────────────────────────────────────────────────────
    // ZUMBADOR INTERMITENTE
    // ─────────────────────────────────────────────────────────

    alertaActual = (nivelTemp == 2 || nivelHum == 2 || nivelGas == 2);
    actualizarBuzzer(alertaActual);

    // ─────────────────────────────────────────────────────────
    // ESTADO EN MONITOR SERIE
    // ─────────────────────────────────────────────────────────

    const char* etiquetas[] = {
      "VERDE",
      "AMARILLO",
      "ROJO"
    };

    Serial.println("------------------------------");
    Serial.println("  ESTADO SEMAFOROS");
    Serial.println("------------------------------");

    Serial.print("  [Temp]  Sensor 1 : ");
    Serial.println(etiquetas[nivelTemp]);

    Serial.print("  [Hum]   Sensor 2 : ");
    Serial.println(etiquetas[nivelHum]);

    Serial.print("  [Gas]   Sensor 3 : ");
    Serial.println(etiquetas[nivelGas]);

    Serial.println("------------------------------");
    Serial.print("  ZUMBADOR         : ");

    if (alertaActual) {
      Serial.println("ACTIVO INTERMITENTE");
    } else {
      Serial.println("Silencio");
    }

    Serial.println("==============================\n");
  }
}