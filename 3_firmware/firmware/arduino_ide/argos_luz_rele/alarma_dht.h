// Reglas de aviso del nodo dht (CLAUDE.md §2 "Buzzer y LEDs"), sin Arduino: el firmware las usa con
// millis() y firmware/herramientas/prueba_alarma.cpp las prueba en la PC con un reloj simulado.
//
//   muestra(t, h)          cada 30 s; persistencia de 3 lecturas e histeresis 0.5 C / 2 % HR
//   orden_nube(on, ahora)  cmd/alarma; "on" caduca a los 150 s si n8n no lo repite
//   silenciar(ahora)       boton: 30 min
//   salidas(ahora)         buzzer = (alarma local o de la nube vigente) y no silenciado
#pragma once
#include <math.h>
#include <stdint.h>

namespace alarma {

// Mismos valores que la tabla Umbral de la BD; si cambian alla, cambiar aqui.
constexpr float T_MIN = 22.0f, T_MAX = 28.0f, T_HIST = 0.5f;
constexpr float H_MIN = 40.0f, H_MAX = 60.0f, H_HIST = 2.0f;
constexpr uint8_t PERSISTENCIA = 3;
constexpr uint32_t VIGENCIA_NUBE_MS = 150000UL;
constexpr uint32_t SILENCIO_MS = 30UL * 60UL * 1000UL;

inline bool transcurrido(uint32_t ahora, uint32_t desde, uint32_t ms) { return (uint32_t)(ahora - desde) >= ms; }

// Una variable vigilada con persistencia e histeresis (una alarma por episodio).
struct Vigilancia {
  float minimo, maximo, histeresis;
  uint8_t fuera = 0, dentro = 0;
  bool alarma = false;

  void evaluar(float v) {
    if (v < minimo || v > maximo) {
      dentro = 0;
      if (++fuera >= PERSISTENCIA) { fuera = PERSISTENCIA; alarma = true; }
    } else if (v >= minimo + histeresis && v <= maximo - histeresis) {
      fuera = 0;
      if (++dentro >= PERSISTENCIA) { dentro = PERSISTENCIA; alarma = false; }
    } else {
      fuera = dentro = 0;  // zona de histeresis: conserva el estado
    }
  }
  const char* etiqueta(float v) const { return !alarma ? "" : (v < minimo ? "BAJA" : "ALTA"); }
};

enum class Lectura { valida, invalida, falla_nueva };  // falla_nueva: publicar sensor_error una vez

struct Salidas {
  bool buzzer;      // suena
  bool rojo;        // LED rojo fijo: alerta propia (T o HR)
  bool falla;       // LED rojo parpadeo rapido
  bool alarma;      // alarma local o de la nube vigente (pantalla)
  bool silenciada;
};

class Alarma {
 public:
  Vigilancia temp{T_MIN, T_MAX, T_HIST};
  Vigilancia hum{H_MIN, H_MAX, H_HIST};
  float temperatura = NAN, humedad = NAN;  // ultima lectura valida

  Lectura muestra(float t, float h) {
    bool valida = !isnan(t) && !isnan(h) && t >= -10 && t <= 60 && h >= 0 && h <= 100;
    if (!valida) {
      if (invalidas < PERSISTENCIA) invalidas++;
      if (invalidas >= PERSISTENCIA && !falla) { falla = true; return Lectura::falla_nueva; }
      return Lectura::invalida;
    }
    invalidas = 0;
    falla = false;
    temperatura = t;
    humedad = h;
    temp.evaluar(t);
    hum.evaluar(h);
    return Lectura::valida;
  }

  void orden_nube(bool on, uint32_t ahora) {
    nube = on;
    if (on) ultima_orden = ahora;
  }

  void silenciar(uint32_t ahora) {
    silenciado = true;
    inicio_silencio = ahora;
  }

  Salidas salidas(uint32_t ahora) {
    if (silenciado && transcurrido(ahora, inicio_silencio, SILENCIO_MS)) silenciado = false;
    bool local = temp.alarma || hum.alarma;
    bool de_nube = nube && !transcurrido(ahora, ultima_orden, VIGENCIA_NUBE_MS);
    return {(local || de_nube) && !silenciado, local, falla, local || de_nube, silenciado};
  }

  bool hay_dato() const { return !isnan(temperatura); }

 private:
  uint8_t invalidas = 0;
  bool falla = false;
  bool nube = false;
  uint32_t ultima_orden = 0;
  bool silenciado = false;
  uint32_t inicio_silencio = 0;
};

}  // namespace alarma
