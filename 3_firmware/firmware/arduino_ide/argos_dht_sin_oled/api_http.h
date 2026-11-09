// Cliente HTTP de la API REST de Argos (servidor/api/RestApi.js).
// El nodo GUARDA sus datos por HTTP (la API es la unica que escribe en MySQL; el nodo nunca toca la BD)
// y usa MQTT aparte para lo de tiempo real (estado/LWT, cmd/alarma). Si uno de los dos falla, el otro sigue.
//
// Manejo de errores:
//   - sin WiFi: no intenta (no bloquea el loop) y lo dice por el monitor serial
//   - sin respuesta o error del servidor (5xx): reintenta UNA vez
//   - 400 (dato rechazado) o 401 (clave): no reintenta, porque repetirlo daria lo mismo; lo explica por serial
#pragma once
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

namespace api {

constexpr uint16_t TIMEOUT_MS = 2000;  // tope de espera por peticion: el loop no se congela mas que esto
inline WiFiClient red;                 // conexion propia (MQTT usa otra)

// Hace una peticion y regresa el codigo HTTP (negativo = no hubo conexion). Imprime el resultado.
inline int pedir(const char* metodo, const char* ruta, const char* cuerpo, String* respuesta = nullptr) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[api] %s %s: sin WiFi, no se envia\n", metodo, ruta);
    return -1;
  }
  HTTPClient http;
  http.setTimeout(TIMEOUT_MS);
  String url = String("http://") + API_HOST + ":" + String(API_PORT) + ruta;
  if (!http.begin(red, url)) {
    Serial.printf("[api] URL invalida: %s\n", url.c_str());
    return -1;
  }
  http.addHeader("X-API-Key", API_KEY);
  int codigo;
  if (cuerpo) {
    http.addHeader("Content-Type", "application/json");
    codigo = http.POST(cuerpo);
  } else {
    codigo = http.GET();
  }
  String r = codigo > 0 ? http.getString() : HTTPClient::errorToString(codigo);
  http.end();
  Serial.printf("[api] %s %s -> %d %s\n", metodo, ruta, codigo, r.c_str());
  if (respuesta) *respuesta = r;
  return codigo;
}

// POST con un reintento. true si la API lo guardo (2xx).
inline bool enviar(const char* ruta, const char* json) {
  Serial.printf("[api] enviando %s\n", json);
  int c = pedir("POST", ruta, json);
  if (c < 0 || c >= 500) {
    delay(200);
    c = pedir("POST", ruta, json);
  }
  if (c == 400) Serial.println("[api] la API rechazo el dato (400): no se guardo");
  if (c == 401) Serial.println("[api] clave incorrecta (401): revisa API_KEY en secrets.h");
  return c >= 200 && c < 300;
}

// Evento de actuacion: el LED rojo o el buzzer cambio de estado.
// origen: "local" (lo decidio el nodo) o "manual" (boton). duracion_s = 0 -> hasta el siguiente cambio.
inline bool accion(const char* actuador, const char* comando, const char* origen, uint16_t duracion_s = 0) {
  char json[160];
  if (duracion_s)
    snprintf(json, sizeof json, "{\"nodo\":\"%s\",\"actuador\":\"%s\",\"comando\":\"%s\",\"origen\":\"%s\",\"duracion_s\":%u}",
             NODO_ID, actuador, comando, origen, duracion_s);
  else
    snprintf(json, sizeof json, "{\"nodo\":\"%s\",\"actuador\":\"%s\",\"comando\":\"%s\",\"origen\":\"%s\"}",
             NODO_ID, actuador, comando, origen);
  return enviar("/api/acciones", json);
}

}  // namespace api
