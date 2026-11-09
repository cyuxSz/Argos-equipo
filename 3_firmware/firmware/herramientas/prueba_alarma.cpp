// Prueba en la PC de include/alarma_dht.h (las reglas del buzzer del nodo dht) con un reloj simulado.
// Compilar y correr: python firmware/herramientas/prueba_alarma.py   (sale con 1 si algun caso falla)
#include <stdio.h>
#include "../include/alarma_dht.h"

using alarma::Alarma;
using alarma::Lectura;

static int fallas = 0;
#define CASO(cond, txt)                                    \
  do {                                                     \
    bool ok_ = (cond);                                     \
    printf("%s  %s\n", ok_ ? "ok   " : "FALLA", txt);      \
    if (!ok_) fallas++;                                    \
  } while (0)

constexpr uint32_t P = 30000;  // periodo de muestreo

int main() {
  {
    Alarma a;
    a.muestra(25, 50);
    CASO(!a.salidas(0).buzzer && !a.salidas(0).rojo, "dentro de rango: sin alarma");
    a.muestra(29, 50);
    a.muestra(29, 50);
    CASO(!a.salidas(0).buzzer, "2 lecturas fuera: aun sin alarma (persistencia 3)");
    a.muestra(29, 50);
    alarma::Salidas s = a.salidas(0);
    CASO(s.buzzer && s.rojo && s.alarma, "3 lecturas fuera: buzzer y LED rojo");
    CASO(a.temp.etiqueta(29)[0] == 'A', "etiqueta ALTA en la pantalla");
    for (int i = 0; i < 3; i++) a.muestra(27.8f, 50);
    CASO(a.salidas(0).buzzer, "27.8 C esta en la histeresis (28 - 0.5): sigue la alarma");
    for (int i = 0; i < 2; i++) a.muestra(27.0f, 50);
    CASO(a.salidas(0).buzzer, "2 lecturas normales: sigue (persistencia de cierre)");
    a.muestra(27.0f, 50);
    CASO(!a.salidas(0).buzzer && !a.salidas(0).rojo, "3 lecturas normales: se apaga");
  }
  {
    Alarma a;
    for (int i = 0; i < 3; i++) a.muestra(25, 38);
    CASO(a.salidas(0).buzzer && a.hum.etiqueta(38)[0] == 'B', "humedad baja (38 %): alarma, etiqueta BAJA");
  }
  {
    Alarma a;
    for (int i = 0; i < 3; i++) a.muestra(29, 50);
    a.silenciar(1000);
    alarma::Salidas s = a.salidas(1000 + P);
    CASO(!s.buzzer && s.rojo && s.silenciada, "boton: silencia el buzzer, el LED rojo sigue");
    CASO(!a.salidas(1000 + alarma::SILENCIO_MS - 1).buzzer, "silencio vigente a 29:59 min");
    CASO(a.salidas(1000 + alarma::SILENCIO_MS).buzzer, "a los 30 min vuelve a sonar si sigue la alarma");
  }
  {
    Alarma a;
    a.muestra(25, 50);
    a.orden_nube(true, 0);
    alarma::Salidas s = a.salidas(10000);
    CASO(s.buzzer && !s.rojo, "cmd/alarma=on: suena aunque la lectura local este bien; rojo solo es alerta propia");
    CASO(!a.salidas(alarma::VIGENCIA_NUBE_MS).buzzer, "on sin repetir caduca a los 150 s");
    a.orden_nube(true, 100000);
    a.orden_nube(true, 160000);
    CASO(a.salidas(250000).buzzer, "on repetido cada 60 s se mantiene");
    a.orden_nube(false, 260000);
    CASO(!a.salidas(260000).buzzer, "cmd/alarma=off apaga de inmediato");
  }
  {
    Alarma a;
    CASO(a.muestra(NAN, 50) == Lectura::invalida && a.muestra(NAN, 50) == Lectura::invalida,
         "2 lecturas invalidas: aun no es falla");
    CASO(a.muestra(NAN, NAN) == Lectura::falla_nueva && a.salidas(0).falla, "3 invalidas: sensor_error una vez");
    CASO(a.muestra(NAN, 50) == Lectura::invalida, "no repite sensor_error");
    CASO(a.muestra(85, 50) == Lectura::invalida, "85 C se descarta (fuera de -10..60)");
    CASO(a.muestra(25, 50) == Lectura::valida && !a.salidas(0).falla, "lectura valida quita la falla");
  }
  {
    Alarma a;
    for (int i = 0; i < 3; i++) a.muestra(29, 50);
    a.silenciar(0xFFFFF000u);  // millis() a punto de desbordarse (~49.7 dias)
    CASO(!a.salidas(0x00001000u).buzzer, "silencio sobrevive al desborde de millis()");
  }
  printf("\n%s (%d fallas)\n", fallas ? "HAY FALLAS" : "todo ok", fallas);
  return fallas ? 1 : 0;
}
