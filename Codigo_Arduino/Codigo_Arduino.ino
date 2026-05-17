#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// WiFi
const char* ssid       = "iPhone de Brent";
const char* password   = "bntt2025";
const char* serverName = "http://172.20.10.4:5000/datos";

// DHT11
#define DHTPIN   25
#define DHTTYPE  DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQ-2
#define MQ2PIN 32

// ── LEDs por sensor ───────────────────────────────────────────
#define LED_VERDE1    26
#define LED_AMARILLO1 27
#define LED_ROJO1     33

#define LED_VERDE2    18
#define LED_AMARILLO2 19
#define LED_ROJO2     21

#define LED_VERDE3    22
#define LED_AMARILLO3 23
#define LED_ROJO3     13

// ── Zumbador ──────────────────────────────────────────────────
#define ZUMBADOR 14

// ── Umbrales ──────────────────────────────────────────────────
const int   GAS_EXTREMO   = 2500;
const int   GAS_MODERADO  = 1500;
const float TEMP_EXTREMA  = 35.0;
const float TEMP_MODERADA = 27.0;
const float HUM_EXTREMA   = 80.0;
const float HUM_MODERADA  = 60.0;

// ── Helpers zumbador (API v3.x) ───────────────────────────────
void buzzerOn()  { ledcWrite(ZUMBADOR, 128); }
void buzzerOff() { ledcWrite(ZUMBADOR, 0);   }

// ── Helper semáforo ───────────────────────────────────────────
void setSemaforo(int pinVerde, int pinAmarillo, int pinRojo, int nivel) {
  digitalWrite(pinVerde,    nivel == 0 ? HIGH : LOW);
  digitalWrite(pinAmarillo, nivel == 1 ? HIGH : LOW);
  digitalWrite(pinRojo,     nivel == 2 ? HIGH : LOW);
}

// ─────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  delay(2000);

  dht.begin();
  pinMode(MQ2PIN, INPUT);

  int leds[] = {
    LED_VERDE1, LED_AMARILLO1, LED_ROJO1,
    LED_VERDE2, LED_AMARILLO2, LED_ROJO2,
    LED_VERDE3, LED_AMARILLO3, LED_ROJO3
  };
  for (int i = 0; i < 9; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }

  // Zumbador (API v3.x)
  ledcAttach(ZUMBADOR, 2000, 8);
  buzzerOff();

  Serial.println("==============================");
  Serial.println("  Sistema de monitoreo IoT");
  Serial.println("==============================");
  Serial.println("Conectando a WiFi...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println(">>> WiFi CONECTADO <<<");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
  Serial.println("==============================\n");
}

void loop() {
  delay(5000);

  float temperatura = dht.readTemperature();
  float humedad     = dht.readHumidity();
  int   mq2Value    = analogRead(MQ2PIN);

  // ── Lectura de sensores ──────────────────────────────────
  Serial.println("------------------------------");
  Serial.println("  LECTURA DE SENSORES");
  Serial.println("------------------------------");

  if (isnan(temperatura) || isnan(humedad)) {
    Serial.println("[ERROR] Fallo al leer el DHT11");
  } else {
    Serial.print("  Temperatura : ");
    Serial.print(temperatura);
    Serial.println(" °C");

    Serial.print("  Humedad     : ");
    Serial.print(humedad);
    Serial.println(" %");
  }

  Serial.print("  Gas MQ-2    : ");
  Serial.println(mq2Value);

  // ── Envío HTTP ───────────────────────────────────────────
  Serial.println("------------------------------");
  Serial.println("  ENVIO AL SERVIDOR");
  Serial.println("------------------------------");

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
    Serial.println("  [ERROR] WiFi desconectado");
  }

  // ── Calcular niveles ─────────────────────────────────────
  int nivelTemp = 0;
  if      (temperatura > TEMP_EXTREMA)  nivelTemp = 2;
  else if (temperatura > TEMP_MODERADA) nivelTemp = 1;

  int nivelHum = 0;
  if      (humedad > HUM_EXTREMA)  nivelHum = 2;
  else if (humedad > HUM_MODERADA) nivelHum = 1;

  int nivelGas = 0;
  if      (mq2Value > GAS_EXTREMO)  nivelGas = 2;
  else if (mq2Value > GAS_MODERADO) nivelGas = 1;

  // ── Actualizar semáforos ─────────────────────────────────
  setSemaforo(LED_VERDE1, LED_AMARILLO1, LED_ROJO1, nivelTemp);
  setSemaforo(LED_VERDE2, LED_AMARILLO2, LED_ROJO2, nivelHum);
  setSemaforo(LED_VERDE3, LED_AMARILLO3, LED_ROJO3, nivelGas);

  // ── Zumbador ─────────────────────────────────────────────
  bool alerta = (nivelTemp == 2 || nivelHum == 2 || nivelGas == 2);
  alerta ? buzzerOn() : buzzerOff();

  // ── Estado en monitor serie ──────────────────────────────
  const char* etiquetas[] = {"VERDE  ✔", "AMARILLO ⚠", "ROJO  ✘"};

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
  Serial.println(alerta ? "ACTIVO  !" : "Silencio");
  Serial.println("==============================\n");