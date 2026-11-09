// Nodo luz: fotorresistencia en divisor con 10 k hacia A0. Muestra cada 5 s y publica el promedio
// de 12 muestras cada 60 s (valor ADC 0-1023). El umbral de "luz encendida" lo evalua n8n
// [umbral y horario POR CONFIRMAR]. Actuador: LED rojo fijo cuando el promedio indica lamparas
// apagadas (bajo UMBRAL_ADC); n8n decide si eso es una alerta segun el horario. Solo compilado.
// Submodulo opcional del fotoperiodo (USAR_RELES=1, entorno luz_rele): D1/D2/D5 mandan IN1-IN3 del modulo
// de reles (activo en bajo) de las planchas 2-4. Por ahora solo arrancan apagados; el horario por plancha
// llega en la fase de software [POR DEFINIR].
#include "nodo_comun.h"

constexpr uint8_t PIN_LDR = A0;
#if USAR_RELES
constexpr uint8_t PIN_RELE_P2 = D1;
constexpr uint8_t PIN_RELE_P3 = D2;
constexpr uint8_t PIN_RELE_P4 = D5;
constexpr uint8_t RELES[] = {PIN_RELE_P2, PIN_RELE_P3, PIN_RELE_P4};
#endif
constexpr uint32_t MUESTREO_MS = 5000;
constexpr uint8_t MUESTRAS = 12;
constexpr uint16_t UMBRAL_ADC = 300;  // [POR CONFIRMAR al calibrar junto a las lamparas]

uint32_t ultimoMuestreo = 0;
uint32_t suma = 0;
uint8_t n = 0;

void setup() {
#if USAR_RELES
  for (uint8_t p : RELES) {  // HIGH antes de OUTPUT: el pin nunca pasa por LOW (luz encendida) al arrancar
    digitalWrite(p, HIGH);
    pinMode(p, OUTPUT);
  }
#endif
  nodo::iniciar();
}

void loop() {
  nodo::atender(false);  // publica cada 60 s: no necesita latido aparte
  if (!nodo::transcurrido(ultimoMuestreo, MUESTREO_MS)) return;
  ultimoMuestreo = millis();
  suma += analogRead(PIN_LDR);
  if (++n < MUESTRAS) return;
  float promedio = (float)suma / n;
  nodo::alerta = promedio < UMBRAL_ADC;  // actuador: rojo = lamparas apagadas
  nodo::publicarLectura("luz", promedio, "adc");
  suma = 0;
  n = 0;
}
