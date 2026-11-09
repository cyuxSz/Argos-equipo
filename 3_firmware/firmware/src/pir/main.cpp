// Nodo pir: HC-SR501 en D5 (salida de 3.3 V). Publica "movimiento" en cada flanco de subida,
// con antirrebote de 10 s, y un latido cada 60 s. El horario de acceso lo evalua n8n.
// Actuador: LED rojo encendido 5 s despues de cada deteccion.
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"

constexpr uint8_t PIN_PIR = D5;
constexpr uint32_t ANTIRREBOTE_MS = 10000;
constexpr uint32_t ROJO_MS = 5000;
uint32_t ultimaDeteccion = 0;
bool hayDeteccion = false;

uint32_t ultimoMovimiento = 0;
bool primerMovimiento = true;
bool anterior = LOW;

void setup() {
  pinMode(PIN_PIR, INPUT);
  nodo::iniciar();
}

void loop() {
  nodo::atender(true);
  bool ahora = digitalRead(PIN_PIR);
  if (ahora == HIGH) { ultimaDeteccion = millis(); hayDeteccion = true; }
  nodo::alerta = hayDeteccion && !nodo::transcurrido(ultimaDeteccion, ROJO_MS);
  if (ahora == HIGH && anterior == LOW &&
      (primerMovimiento || nodo::transcurrido(ultimoMovimiento, ANTIRREBOTE_MS))) {
    primerMovimiento = false;
    ultimoMovimiento = millis();
    nodo::publicarEvento("movimiento");
  }
  anterior = ahora;
}
