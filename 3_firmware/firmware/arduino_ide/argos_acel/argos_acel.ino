// Argos, nodo acel. GENERADO por firmware/herramientas/exportar_arduino.py desde firmware/src/acel/main.cpp (editar alla y regenerar).
// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.
#define NODO_ID "acel"
// Nodo acel: GY-61 (ADXL335) leido por un ADS1115 (I2C 0x48, D1 SCL / D2 SDA).
// Calcula |a| en g y publica "golpe" cuando | |a| - 1 g | supera el umbral. El umbral se calibra
// en sitio [POR CONFIRMAR]; el cierre de la alerta (5 min) lo hace n8n. Latido cada 60 s.
// Actuador: LED rojo encendido 5 s despues de cada golpe.
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

constexpr float CERO_V = 1.65f;         // 0 g a 3.3 V (ratiometrico) [calibrar]
constexpr float SENSIBILIDAD = 0.330f;  // V/g a 3.3 V [calibrar]
constexpr float UMBRAL_G = 0.5f;        // [POR CONFIRMAR en sitio]
constexpr uint32_t ANTIRREBOTE_MS = 2000;
constexpr uint32_t ROJO_MS = 5000;

Adafruit_ADS1115 ads;
uint32_t ultimoGolpe = 0;
bool primerGolpe = true;

float eje(uint8_t canal) { return (ads.computeVolts(ads.readADC_SingleEnded(canal)) - CERO_V) / SENSIBILIDAD; }

void setup() {
  nodo::iniciar();
  Wire.begin();  // SDA = D2, SCL = D1
  ads.setGain(GAIN_ONE);                 // +-4.096 V
  ads.setDataRate(RATE_ADS1115_860SPS);  // ~3 ms por canal
  nodo::sensorFalla = !ads.begin(0x48);
}

void loop() {
  nodo::atender(true);
  nodo::alerta = !primerGolpe && !nodo::transcurrido(ultimoGolpe, ROJO_MS);
  if (nodo::sensorFalla) return;
  float x = eje(0), y = eje(1), z = eje(2);
  float desviacion = fabsf(sqrtf(x * x + y * y + z * z) - 1.0f);
  if (desviacion > UMBRAL_G && (primerGolpe || nodo::transcurrido(ultimoGolpe, ANTIRREBOTE_MS))) {
    primerGolpe = false;
    ultimoGolpe = millis();
    nodo::publicarEvento("golpe", desviacion);
  }
}
