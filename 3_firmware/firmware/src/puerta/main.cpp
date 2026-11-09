// Nodo puerta: reed MC-38 entre D5 (INPUT_PULLUP) y GND. Iman cerca = LOW = puerta cerrada.
// Publica puerta_abierta / puerta_cerrada en cada cambio (antirrebote 50 ms) y un latido cada 60 s.
// El limite de "abierta mas de 2 min" lo evalua n8n. LED rojo fijo mientras la puerta esta abierta.
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"

constexpr uint8_t PIN_REED = D5;
constexpr uint32_t ANTIRREBOTE_MS = 50;

bool estable = HIGH, anterior = HIGH;
uint32_t cambio = 0;
bool publicado = false;  // publica el estado inicial al conectar por primera vez

void setup() {
  pinMode(PIN_REED, INPUT_PULLUP);
  estable = anterior = digitalRead(PIN_REED);
  nodo::iniciar();
}

void loop() {
  nodo::atender(true);
  bool lectura = digitalRead(PIN_REED);
  if (lectura != anterior) {
    cambio = millis();
    anterior = lectura;
  }
  bool cambiado = nodo::transcurrido(cambio, ANTIRREBOTE_MS) && lectura != estable;
  if (cambiado) estable = lectura;
  if (cambiado || (!publicado && WiFi.status() == WL_CONNECTED)) {  // estado inicial al tener red
    publicado = true;
    nodo::publicarEvento(estable == HIGH ? "puerta_abierta" : "puerta_cerrada");
  }
  nodo::alerta = (estable == HIGH);  // actuador: rojo fijo con la puerta abierta
}
