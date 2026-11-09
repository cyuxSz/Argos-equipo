// Vista de la OLED 2.42" del nodo dht (128 x 64 px, 0.43 mm por punto). C puro: el firmware la usa
// con pantalla.getU8g2() y firmware/herramientas/oled_host.c la dibuja en la PC con las MISMAS fuentes,
// para revisar espacios y tamanos sin hardware.
//
//   y  0- 8  barra de estado (5x8): EN LINEA / SIN RED / ALARMA / ALARMA SILENCIADA / FALLA DEL SENSOR
//   y 13-39  temperatura, digitos de 26 px (~11 mm), con unidad y etiqueta ALTA/BAJA a la derecha
//   y 47-63  humedad, digitos de 16 px (~7 mm), con "% HR" y etiqueta a la derecha
// Con alarma o falla la barra se invierte (fondo claro) para que se note de lejos.
#pragma once
#ifdef ARDUINO
#include <U8g2lib.h>
#else
#include <stdio.h>
#include "u8g2.h"
#endif
#include <stdbool.h>

typedef struct {
  float temperatura, humedad;
  bool hay_dato;        // false: aun sin lectura valida
  bool sensor_falla;
  bool en_linea;        // WiFi y broker conectados
  bool alarma;          // alarma local o de la nube vigente
  bool silenciada;
  const char* etiqueta_t;  // "", "ALTA" o "BAJA"
  const char* etiqueta_h;
} VistaOled;

static inline void vista_oled_dibujar(u8g2_t* u, const VistaOled* v) {
  char b[16];
  const char* estado = "EN LINEA";
  bool invertida = false;
  if (v->sensor_falla) { estado = "FALLA DEL SENSOR"; invertida = true; }
  else if (v->alarma) { estado = v->silenciada ? "ALARMA SILENCIADA" : "ALARMA"; invertida = true; }
  else if (!v->en_linea) estado = "SIN RED";

  u8g2_ClearBuffer(u);
  u8g2_SetFontMode(u, 1);
  u8g2_SetFont(u, u8g2_font_5x8_tf);
  if (invertida) {
    u8g2_SetDrawColor(u, 1);
    u8g2_DrawBox(u, 0, 0, 128, 10);
    u8g2_SetDrawColor(u, 0);
  }
  u8g2_DrawStr(u, 2, 8, estado);
  if (invertida && !v->en_linea) {
    u8g2_uint_t w = u8g2_GetStrWidth(u, "SIN RED");
    u8g2_DrawStr(u, 126 - w, 8, "SIN RED");
  }
  u8g2_SetDrawColor(u, 1);

  bool dato = v->hay_dato && !v->sensor_falla;
  if (dato) snprintf(b, sizeof b, "%.1f", v->temperatura); else snprintf(b, sizeof b, "--.-");
  u8g2_SetFont(u, u8g2_font_logisoso26_tn);
  u8g2_uint_t w = u8g2_DrawStr(u, 0, 39, b);
  u8g2_SetFont(u, u8g2_font_helvB10_tf);
  u8g2_DrawUTF8(u, w + 4, 24, "\xC2\xB0" "C");
  u8g2_SetFont(u, u8g2_font_5x8_tf);
  if (dato) u8g2_DrawStr(u, w + 4, 36, v->etiqueta_t);

  if (dato) snprintf(b, sizeof b, "%.0f", v->humedad); else snprintf(b, sizeof b, "--");
  u8g2_SetFont(u, u8g2_font_logisoso16_tn);
  w = u8g2_DrawStr(u, 0, 63, b);
  u8g2_SetFont(u, u8g2_font_helvB08_tf);
  w += u8g2_DrawStr(u, w + 4, 63, "% HR");
  u8g2_SetFont(u, u8g2_font_5x8_tf);
  if (dato) u8g2_DrawStr(u, w + 10, 63, v->etiqueta_h);
}
