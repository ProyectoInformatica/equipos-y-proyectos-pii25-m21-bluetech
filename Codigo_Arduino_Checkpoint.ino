#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"


const char* ssid       = "A56 de Gabriel";
const char* password   = "Gabigoleador8";

const char* serverName   = "http://10.172.199.138/datos";
const char* endpointMulti = "http://10.172.199.138/multiordinario";



#define DHTPIN   25
#define DHTTYPE  DHT11
DHT dht(DHTPIN, DHTTYPE);
#define MQ2PIN 32

#define LED_VERDE1    26
#define LED_AMARILLO1 27
#define LED_ROJO1     33
#define LED_VERDE2    18
#define LED_AMARILLO2 19
#define LED_ROJO2     21
#define LED_VERDE3    22
#define LED_AMARILLO3 23
#define LED_ROJO3     13
#define ZUMBADOR      14

// Umbrales
const int GAS_EXTREMO   = 2500;
const int GAS_MODERADO  = 1500;
const float TEMP_EXTREMA  = 35.0;
const float TEMP_MODERADA = 27.0;
const float HUM_EXTREMA   = 80.0;
const float HUM_MODERADA  = 60.0;

//
// TEMPORIZADORES
// 

unsigned long tiempoAnteriorSensores = 0;
const unsigned long INTERVALO_5_SEG  = 5000;

unsigned long tiempoAnteriorOrdinario = 0;
const unsigned long INTERVALO_1_MIN   = 60000;

// Variables para calcular la media del sensor multiordinario
int sumaEstados = 0;
int totalLecturas = 0;


void buzzerOn()  { ledcWrite(ZUMBADOR, 128); }
void buzzerOff() { ledcWrite(ZUMBADOR, 0);   }

void setSemaforo(int pinVerde, int pinAmarillo, int pinRojo, int nivel) {
  digitalWrite(pinVerde,    nivel == 0 ? HIGH : LOW);
  digitalWrite(pinAmarillo, nivel == 1 ? HIGH : LOW);
  digitalWrite(pinRojo,     nivel == 2 ? HIGH : LOW);
}
// FUNCIÓN DATABASELOADER()
void DataBaseLoader(String valorSensor) {
  if (WiFi.status() == WL_CONNECTED) {
    String peticionUrl = String(endpointMulti) + "?txt=" + valorSensor;
    HTTPClient clienteHttp;
    clienteHttp.begin(peticionUrl);
    int respuestaServer = clienteHttp.GET();
    Serial.print("-> [DataBaseLoader] HTTP Status: ");
    Serial.println(respuestaServer);
    clienteHttp.end();
  } 
  else {
    Serial.println("[DataBaseLoader] Sin conexión WiFi. Abortado.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  dht.begin();
  pinMode(MQ2PIN, INPUT);

  int leds[] = { LED_VERDE1, LED_AMARILLO1, LED_ROJO1, LED_VERDE2, LED_AMARILLO2, LED_ROJO2, LED_VERDE3, LED_AMARILLO3, LED_ROJO3 };
  for (int i = 0; i < 9; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }

  ledcAttach(ZUMBADOR, 2000, 8);
  buzzerOff();
  
  // 1. INICIALIZACIÓN DEL SENSOR MULTIORDINARIO

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n>>> WiFi CONECTADO <<<");
}



void loop() {
  
  //LECTURA CONTINUA DEL SENSOR MULTIORDINARIO
  if (comprobarDatosDisponibles()) {
    // Leemos el dato en formato char
    String estadoLeido = String(leerDatosOrdinarios()); 
    
    // Mapeamos el String a un valor numérico para poder calcular la media
    if (estadoLeido == "BAJO") {
      sumaEstados += 0;
    } else if (estadoLeido == "NORMAL") {
      sumaEstados += 1;
    } else if (estadoLeido == "ALTO") {
      sumaEstados += 2;
    }
    
    totalLecturas++; // Aumentamos el contador de muestras
  }


  //PROMEDIO CADA 1 MINUTO
  
  if (millis() - tiempoAnteriorOrdinario >= INTERVALO_1_MIN) {
    tiempoAnteriorOrdinario = millis(); // Reiniciamos el cronómetro de 1 min
    
    if (totalLecturas > 0) {
      // Calculamos la media
      int mediaNumerica = round((float)sumaEstados / totalLecturas);
      
      //volvems al formato alfanumerico
      String estadoPromedio = "";
      if (mediaNumerica == 0) estadoPromedio = "BAJO";
      else if (mediaNumerica == 1) estadoPromedio = "NORMAL";
      else estadoPromedio = "ALTO";
      
    
      Serial.println("  REPORTE 1 MINUTO: SENSOR MULTIORDINARIO");
      Serial.print("  Lecturas recogidas : "); Serial.println(totalLecturas);
      Serial.print("  Media alfanumérica : "); Serial.println(estadoPromedio);
      
      // Llamada al metodo para insertar en la BD
      DataBaseLoader(estadoPromedio);
      
      // Reseteamos variables
      sumaEstados = 0;
      totalLecturas = 0;
    }
  }

  if (millis() - tiempoAnteriorSensores >= INTERVALO_5_SEG) {
    tiempoAnteriorSensores = millis(); // Reiniciamos cronómetro de 5 seg

    float temperatura = dht.readTemperature();
    float humidity    = dht.readHumidity();
    int mq2Value      = analogRead(MQ2PIN);

    if (WiFi.status() == WL_CONNECTED) {
      String url = String(serverName)
                 + "?temp=" + String(temperatura)
                 + "&hum="  + String(humidity)
                 + "&gas="  + String(mq2Value);

      HTTPClient http;
      http.begin(url);
      http.GET();
      http.end();
    }

    int nivelTemp = (temperatura > TEMP_EXTREMA) ? 2 : ((temperatura > TEMP_MODERADA) ? 1 : 0);
    int nivelHum  = (humidity > HUM_EXTREMA)   ? 2 : ((humidity > HUM_MODERADA)   ? 1 : 0);
    int nivelGas  = (mq2Value > GAS_EXTREMO)   ? 2 : ((mq2Value > GAS_MODERADO)   ? 1 : 0);

    setSemaforo(LED_VERDE1, LED_AMARILLO1, LED_ROJO1, nivelTemp);
    setSemaforo(LED_VERDE2, LED_AMARILLO2, LED_ROJO2, nivelHum);
    setSemaforo(LED_VERDE3, LED_AMARILLO3, LED_ROJO3, nivelGas);

    bool alerta = (nivelTemp == 2 || nivelHum == 2 || nivelGas == 2);
    alerta ? buzzerOn() : buzzerOff();
  }
}