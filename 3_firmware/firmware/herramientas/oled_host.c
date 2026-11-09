// Dibuja en la PC las vistas de la OLED con las mismas fuentes U8g2 del firmware.
//   oled_host estados <carpeta>   escribe estado_N.txt (128x64 de 0/1) para cada estado de prueba
//   oled_host glifos <archivo>    escribe un JSON con los glifos de cada fuente (para la pagina web)
// Compilar y correr: firmware/herramientas/oled_host.py
#include <stdio.h>
#include <string.h>
#include "u8g2.h"
#include "../include/vista_oled.h"

static u8g2_t u;

static void volcar(const char* ruta) {
  FILE* f = fopen(ruta, "w");
  const uint8_t* b = u8g2_GetBufferPtr(&u);
  for (int y = 0; y < 64; y++) {
    for (int x = 0; x < 128; x++) fputc(((b[(y / 8) * 128 + x] >> (y % 8)) & 1) ? '1' : '0', f);
    fputc('\n', f);
  }
  fclose(f);
}

static void estados(const char* dir) {
  struct { const char* nombre; VistaOled v; } casos[] = {
      {"En linea, normal", {25.4f, 48, true, false, true, false, false, "", ""}},
      {"Sin red", {25.4f, 48, true, false, false, false, false, "", ""}},
      {"Alarma: temperatura alta", {29.3f, 50, true, false, true, true, false, "ALTA", ""}},
      {"Alarma silenciada", {29.3f, 50, true, false, true, true, true, "ALTA", ""}},
      {"Alarma y sin red", {21.2f, 38, true, false, false, true, false, "BAJA", "BAJA"}},
      {"Falla del sensor", {0, 0, false, true, true, false, false, "", ""}},
      {"Valores de 3 digitos", {-10.5f, 100, true, false, true, true, false, "BAJA", "ALTA"}},
  };
  char ruta[512];
  for (int i = 0; i < (int)(sizeof casos / sizeof casos[0]); i++) {
    vista_oled_dibujar(&u, &casos[i].v);
    snprintf(ruta, sizeof ruta, "%s/estado_%d.txt", dir, i);
    volcar(ruta);
    printf("%d|%s\n", i, casos[i].nombre);
  }
}

typedef struct { const char* nombre; const uint8_t* fuente; const char* chars; bool utf8; } Fuente;

static void glifos(const char* ruta) {
  Fuente fs[] = {
      {"5x8", u8g2_font_5x8_tf, " ABCDEFGHIJKLMNOPQRSTUVWXYZ", false},
      {"logisoso26", u8g2_font_logisoso26_tn, "0123456789.-", false},
      {"logisoso16", u8g2_font_logisoso16_tn, "0123456789.-", false},
      {"helvB10", u8g2_font_helvB10_tf, " C°", true},
      {"helvB08", u8g2_font_helvB08_tf, " %HR", false},
  };
  FILE* f = fopen(ruta, "w");
  fprintf(f, "{");
  for (int i = 0; i < 5; i++) {
    fprintf(f, "%s\"%s\":{", i ? "," : "", fs[i].nombre);
    u8g2_SetFont(&u, fs[i].fuente);
    int primero = 1;
    const uint8_t* p = (const uint8_t*)fs[i].chars;
    while (*p) {
      uint16_t cp = *p++;
      if (fs[i].utf8 && cp == 0xC2) cp = *p++;
      uint8_t adv = u8g2_GetGlyphWidth(&u, cp);
      u8g2_ClearBuffer(&u);
      u8g2_SetFontMode(&u, 1);
      u8g2_DrawGlyph(&u, 20, 50, cp);
      const uint8_t* b = u8g2_GetBufferPtr(&u);
      int x0 = 999, x1 = -1, y0 = 999, y1 = -1;
      for (int y = 0; y < 64; y++)
        for (int x = 0; x < 128; x++)
          if ((b[(y / 8) * 128 + x] >> (y % 8)) & 1) {
            if (x < x0) x0 = x;
            if (x > x1) x1 = x;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
      fprintf(f, "%s\"%u\":{\"adv\":%d,\"dx\":%d,\"dy\":%d,\"w\":%d,\"h\":%d,\"filas\":[", primero ? "" : ",", cp, adv,
              x1 < 0 ? 0 : x0 - 20, y1 < 0 ? 0 : y0 - 50, x1 < 0 ? 0 : x1 - x0 + 1, y1 < 0 ? 0 : y1 - y0 + 1);
      for (int y = y0; y <= y1 && y1 >= 0; y++) {
        fputc('"', f);
        for (int x = x0; x <= x1; x++) fputc(((b[(y / 8) * 128 + x] >> (y % 8)) & 1) ? '1' : '0', f);
        fprintf(f, "\"%s", y < y1 ? "," : "");
      }
      fprintf(f, "]}");
      primero = 0;
    }
    fprintf(f, "}");
  }
  fprintf(f, "}\n");
  fclose(f);
}

int main(int argc, char** argv) {
  if (argc < 3) return 2;
  u8g2_Setup_ssd1309_i2c_128x64_noname0_f(&u, U8G2_R0, u8x8_byte_empty, u8x8_dummy_cb);
  if (!strcmp(argv[1], "estados")) estados(argv[2]);
  else if (!strcmp(argv[1], "glifos")) glifos(argv[2]);
  return 0;
}
