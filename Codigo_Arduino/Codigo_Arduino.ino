#include <WiFi.h>        // Librería para conectar la ESP32 a una red WiFi
#include <HTTPClient.h>  // Librería para enviar peticiones HTTP al servidor Flask
#include "DHT.h"         // Librería para leer el sensor DHT11

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN WIFI Y SERVIDORES FLASK
// ─────────────────────────────────────────────────────────────

// Credenciales de la red WiFi a la que se conecta la ESP32.
const char* ssid       = "iPhone de Brent";
const char* password   = "bntt2025";

// Ruta del servidor Flask para enviar los sensores originales:
// temperatura, humedad y gas.
const char* serverName = "http://172.20.10.4:5000/datos";

// NUEVA FUNCIONALIDAD CHECKPOINT:
// Ruta del servidor Flask para enviar los datos del sensor biordinario.
// Este sensor envía dos datos: uno numérico y otro alfanumérico.
//
// IMPORTANTE:
// La IP 172.20.10.4 corresponde al ordenador donde se está ejecutando Flask.
// No se debe usar localhost, porque para la ESP32 localhost sería la propia placa.
const char* serverBiordinario = "http://172.20.10.4:5000/biordinario";

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN DEL SENSOR DHT11
// ─────────────────────────────────────────────────────────────

// Pin donde está conectado el sensor DHT11.
#define DHTPIN   25

// Tipo de sensor utilizado.
#define DHTTYPE  DHT11

// Objeto que permite leer temperatura y humedad.
DHT dht(DHTPIN, DHTTYPE);

// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN DEL SENSOR MQ-2
// ─────────────────────────────────────────────────────────────

// Pin analógico donde está conectado el MQ-2.
// Este sensor devuelve un valor relacionado con gas/calidad del aire.
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

// Pin del zumbador.
// Se activa cuando algún sensor alcanza un nivel crítico.
#define ZUMBADOR 14

// ─────────────────────────────────────────────────────────────
// UMBRALES DE ALERTA
// ─────────────────────────────────────────────────────────────

// Umbrales del sensor MQ-2.
const int GAS_EXTREMO   = 2500;
const int GAS_MODERADO  = 1500;

// Umbrales de temperatura.
const float TEMP_EXTREMA  = 35.0;
const float TEMP_MODERADA = 27.0;

// Umbrales de humedad.
const float HUM_EXTREMA   = 80.0;
const float HUM_MODERADA  = 60.0;

// ─────────────────────────────────────────────────────────────
// FUNCIONES AUXILIARES
// ─────────────────────────────────────────────────────────────

// Activa el zumbador usando PWM.
// El valor 128 representa una intensidad intermedia.
void buzzerOn()  { 
  ledcWrite(ZUMBADOR, 128); 
}

// Apaga el zumbador.
void buzzerOff() { 
  ledcWrite(ZUMBADOR, 0);   
}

// Actualiza los LEDs de un sensor como si fueran un semáforo.
//
// nivel = 0 → verde
// nivel = 1 → amarillo
// nivel = 2 → rojo
void setSemaforo(int pinVerde, int pinAmarillo, int pinRojo, int nivel) {
  digitalWrite(pinVerde,    nivel == 0 ? HIGH : LOW);
  digitalWrite(pinAmarillo, nivel == 1 ? HIGH : LOW);
  digitalWrite(pinRojo,     nivel == 2 ? HIGH : LOW);
}

// ─────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────

// setup() se ejecuta una sola vez al arrancar la ESP32.
// Aquí se inicializan los sensores, los pines, el zumbador y la conexión WiFi.
void setup() {
  // Inicialización del monitor serie para mostrar mensajes de depuración.
  Serial.begin(115200);
  delay(2000);

  // Inicializa el sensor DHT11.
  dht.begin();

  // Configura el pin del MQ-2 como entrada.
  pinMode(MQ2PIN, INPUT);

  // Lista con todos los pines de LEDs para configurarlos de forma compacta.
  int leds[] = {
    LED_VERDE1, LED_AMARILLO1, LED_ROJO1,
    LED_VERDE2, LED_AMARILLO2, LED_ROJO2,
    LED_VERDE3, LED_AMARILLO3, LED_ROJO3
  };

  // Configura todos los LEDs como salida y los deja apagados al inicio.
  for (int i = 0; i < 9; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }

  // Configura el zumbador mediante PWM.
  // Frecuencia: 2000 Hz.
  // Resolución: 8 bits.
  ledcAttach(ZUMBADOR, 2000, 8);

  // El zumbador empieza apagado.
  buzzerOff();

  Serial.println("==============================");
  Serial.println("  Sistema de monitoreo IoT");
  Serial.println("==============================");
  Serial.println("Conectando a WiFi...");

  // Inicia la conexión WiFi con el nombre de red y contraseña definidos arriba.
  WiFi.begin(ssid, password);

  // Espera hasta que la ESP32 esté conectada a la red.
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Muestra por pantalla que la conexión se ha realizado correctamente.
  Serial.println();
  Serial.println(">>> WiFi CONECTADO <<<");

  // Muestra la IP local de la ESP32.
  // Esta IP NO es la misma que la IP del ordenador donde corre Flask.
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());

  Serial.println("==============================\n");
}

// ─────────────────────────────────────────────────────────────
// NUEVA FUNCIÓN CHECKPOINT: DatabaseInsert()
// ─────────────────────────────────────────────────────────────

/*
  DatabaseInsert()

  Esta función pertenece a la nueva funcionalidad del checkpoint.

  Objetivo:
  Enviar a Flask los datos generados por el nuevo sensor "biordinario".

  Parámetros:
  - valorNumerico: dato numérico generado por el sensor.
  - valorAlfanumerico: dato textual generado por el sensor.

  Funcionamiento:
  1. Comprueba que la ESP32 esté conectada al WiFi.
  2. Construye una URL con los parámetros num y txt.
  3. Envía una petición HTTP GET a la ruta /biordinario de Flask.
  4. Flask recibe esos datos en app.py.
  5. Flask realiza el INSERT en la tabla medicion_biordinario de MySQL.

  Importante:
  La ESP32 no se conecta directamente a MySQL.
  La ESP32 envía los datos a Flask, y Flask es quien inserta en la base de datos.
*/
void DatabaseInsert(float valorNumerico, String valorAlfanumerico) {
  // Solo se intenta enviar la información si la placa sigue conectada al WiFi.
  if (WiFi.status() == WL_CONNECTED) {

    // Construcción de la URL que recibirá Flask.
    //
    // Ejemplo de URL generada:
    // http://172.20.10.4:5000/biordinario?num=55.5&txt=NORMAL
    //
    // num → dato numérico
    // txt → dato alfanumérico
    String url = String(serverBiordinario)
                 + "?num=" + String(valorNumerico)
                 + "&txt=" + valorAlfanumerico;

    // Se crea el cliente HTTP para realizar la petición al servidor Flask.
    HTTPClient http;

    // Se indica al cliente HTTP la URL a la que debe conectarse.
    http.begin(url);

    // Se envía la petición GET.
    // El resultado se guarda en code.
    // Si todo funciona correctamente, Flask devuelve código 200.
    int code = http.GET();

    // Se muestra en el monitor serie la respuesta del servidor.
    Serial.print("Respuesta Flask biordinario: ");
    Serial.println(code);

    // Se cierra la conexión HTTP.
    http.end();

  } else {
    // Si no hay conexión WiFi, no se puede enviar la información a Flask.
    Serial.println("Error: WiFi no conectado. No se puede enviar biordinario.");
  }
}

// ─────────────────────────────────────────────────────────────
// LOOP
// ─────────────────────────────────────────────────────────────

// loop() se ejecuta continuamente mientras la ESP32 está encendida.
// En cada iteración:
// 1. Lee temperatura, humedad y gas.
// 2. Envía esos datos al servidor Flask.
// 3. Calcula el estado de los sensores.
// 4. Actualiza LEDs y zumbador.
// 5. Simula el nuevo sensor biordinario.
// 6. Envía los datos biordinarios mediante DatabaseInsert().
void loop() {
  // Espera 5 segundos entre lecturas para no saturar el servidor.
  delay(5000);

  // ───────────────────────────────────────────────────────────
  // LECTURA DE SENSORES ORIGINALES
  // ───────────────────────────────────────────────────────────

  // Lee temperatura desde el DHT11.
  float temperatura = dht.readTemperature();

  // Lee humedad desde el DHT11.
  float humedad = dht.readHumidity();

  // Lee el valor analógico del MQ-2.
  int mq2Value = analogRead(MQ2PIN);

  Serial.println("------------------------------");
  Serial.println("  LECTURA DE SENSORES");
  Serial.println("------------------------------");

  // Comprueba si el DHT11 ha devuelto valores válidos.
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

  // ───────────────────────────────────────────────────────────
  // ENVÍO DE SENSORES ORIGINALES A FLASK
  // ───────────────────────────────────────────────────────────

  Serial.println("------------------------------");
  Serial.println("  ENVIO AL SERVIDOR");
  Serial.println("------------------------------");

  // Si la ESP32 está conectada al WiFi, se envían los datos a Flask.
  if (WiFi.status() == WL_CONNECTED) {

    // Construye la URL para la ruta /datos.
    //
    // Ejemplo:
    // http://172.20.10.4:5000/datos?temp=25.5&hum=60&gas=1300
    //
    // Flask recibe estos parámetros con:
    // request.args.get("temp")
    // request.args.get("hum")
    // request.args.get("gas")
    String url = String(serverName)
               + "?temp=" + String(temperatura)
               + "&hum="  + String(humedad)
               + "&gas="  + String(mq2Value);

    Serial.print("  URL: ");
    Serial.println(url);

    // Crea el cliente HTTP para enviar la petición.
    HTTPClient http;

    // Inicia la conexión con la URL construida.
    http.begin(url);

    // Envía la petición GET al servidor Flask.
    int code = http.GET();

    // Si code es positivo, se ha recibido una respuesta HTTP.
    if (code > 0) {
      Serial.print("  Respuesta HTTP: ");
      Serial.println(code);
    } else {
      Serial.print("  [ERROR] HTTP: ");
      Serial.println(code);
    }

    // Cierra la conexión HTTP.
    http.end();

  } else {
    Serial.println("  [ERROR] WiFi desconectado");
  }

  // ───────────────────────────────────────────────────────────
  // CÁLCULO DE NIVELES DE ALERTA
  // ───────────────────────────────────────────────────────────

  // Nivel de temperatura:
  // 0 = normal, 1 = moderado, 2 = crítico.
  int nivelTemp = 0;
  if (temperatura > TEMP_EXTREMA) {
    nivelTemp = 2;
  } else if (temperatura > TEMP_MODERADA) {
    nivelTemp = 1;
  }

  // Nivel de humedad:
  // 0 = normal, 1 = moderado, 2 = crítico.
  int nivelHum = 0;
  if (humedad > HUM_EXTREMA) {
    nivelHum = 2;
  } else if (humedad > HUM_MODERADA) {
    nivelHum = 1;
  }

  // Nivel de gas:
  // 0 = normal, 1 = moderado, 2 = crítico.
  int nivelGas = 0;
  if (mq2Value > GAS_EXTREMO) {
    nivelGas = 2;
  } else if (mq2Value > GAS_MODERADO) {
    nivelGas = 1;
  }

  // ───────────────────────────────────────────────────────────
  // ACTUALIZACIÓN DE SEMÁFOROS
  // ───────────────────────────────────────────────────────────

  // Actualiza LEDs del sensor de temperatura.
  setSemaforo(LED_VERDE1, LED_AMARILLO1, LED_ROJO1, nivelTemp);

  // Actualiza LEDs del sensor de humedad.
  setSemaforo(LED_VERDE2, LED_AMARILLO2, LED_ROJO2, nivelHum);

  // Actualiza LEDs del sensor de gas.
  setSemaforo(LED_VERDE3, LED_AMARILLO3, LED_ROJO3, nivelGas);

  // ───────────────────────────────────────────────────────────
  // ZUMBADOR
  // ───────────────────────────────────────────────────────────

  // Si algún sensor está en nivel crítico, se activa el zumbador.
  bool alerta = (nivelTemp == 2 || nivelHum == 2 || nivelGas == 2);

  // Operador ternario:
  // si alerta es true → buzzerOn()
  // si alerta es false → buzzerOff()
  alerta ? buzzerOn() : buzzerOff();

  // ───────────────────────────────────────────────────────────
  // ESTADO EN MONITOR SERIE
  // ───────────────────────────────────────────────────────────

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

  // ───────────────────────────────────────────────────────────
  // NUEVA FUNCIONALIDAD CHECKPOINT: SENSOR BIORDINARIO
  // ───────────────────────────────────────────────────────────

  /*
    Simulación del nuevo sensor "biordinario".

    El enunciado indica que este sensor recoge dos datos:
    1. Un dato numérico.
    2. Un dato alfanumérico.

    Como no existe un sensor físico real en el montaje, se simula su lectura:

    - datoNumericoBiordinario:
      Se genera con random(10, 100).

    - datoAlfanumericoBiordinario:
      Se calcula en función del valor numérico:
        valor < 40       → "BAJO"
        valor < 70       → "NORMAL"
        valor >= 70      → "ALTO"

    Después, ambos valores se envían a Flask mediante DatabaseInsert().
  */

  // Genera un valor numérico simulado para el sensor biordinario.
  float datoNumericoBiordinario = random(10, 100);

  // Variable que almacenará el dato alfanumérico asociado.
  String datoAlfanumericoBiordinario;

  // Asigna el valor alfanumérico según el rango del dato numérico.
  if (datoNumericoBiordinario < 40) {
    datoAlfanumericoBiordinario = "BAJO";
  } else if (datoNumericoBiordinario < 70) {
    datoAlfanumericoBiordinario = "NORMAL";
  } else {
    datoAlfanumericoBiordinario = "ALTO";
  }

  // Muestra en el monitor serie los valores generados por el sensor biordinario.
  Serial.println("------------------------------");
  Serial.println("  SENSOR BIORDINARIO");
  Serial.println("------------------------------");

  Serial.print("  Valor numerico      : ");
  Serial.println(datoNumericoBiordinario);

  Serial.print("  Valor alfanumerico  : ");
  Serial.println(datoAlfanumericoBiordinario);

  // Envía los dos valores generados a Flask.
  //
  // Esta llamada cumple la funcionalidad solicitada:
  // DatabaseInsert() recibe los valores del sensor y los envía a la BBDD
  // a través del servidor Flask.
  DatabaseInsert(datoNumericoBiordinario, datoAlfanumericoBiordinario);
}