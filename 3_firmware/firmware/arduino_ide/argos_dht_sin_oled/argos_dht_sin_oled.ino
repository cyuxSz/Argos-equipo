// Argos, nodo dht_sin_oled. GENERADO por firmware/herramientas/exportar_arduino.py desde firmware/src/dht/main.cpp (editar alla y regenerar).
// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.
#define NODO_ID "dht"
#define USAR_OLED 0
// Nodo dht: DHT22 + buzzer (via 2N2222) + boton + LED verde/rojo (+ OLED SSD1309 2.42" I2C).
// Firmware de REFERENCIA: valida pines y el contrato MQTT de CLAUDE.md. Solo se ha compilado;
// no se ha probado en hardware. No flashear sin aprobacion.
// WiFi, MQTT y LED en nodo_comun.h; reglas de aviso en alarma_dht.h (probadas en la PC).
#include "nodo_comun.h"
#include "alarma_dht.h"
#include <DHT.h>
#if USAR_OLED
#include <Wire.h>
#include <U8g2lib.h>
#include "vista_oled.h"
#endif

// ── Pines (CLAUDE.md §3; LED en nodo_comun.h) ───────────────────────────────
#if USAR_OLED
constexpr uint8_t PIN_DHT = D4;  // GPIO2: D1/D2 quedan para la OLED (I2C)
#else
constexpr uint8_t PIN_DHT = D2;  // GPIO4
#endif
constexpr uint8_t PIN_BUZZER = D5;  // base de Q1 via R3 (1 k); R4 (10 k) a GND
constexpr uint8_t PIN_BOTON = D6;   // a GND, INPUT_PULLUP

constexpr uint32_t PERIODO_MS = 30000;   // muestreo y publicacion
constexpr uint32_t PANTALLA_MS = 30000;  // OLED se apaga sola
constexpr uint32_t PULSACION_LARGA_MS = 1500;
constexpr uint32_t ANTIRREBOTE_MS = 40;

const char* const TOPIC_CMD_ALARMA = "invernadero/cmd/alarma";
const char* const TOPIC_CMD_SILENCIAR = "invernadero/cmd/silenciar";

DHT dht(PIN_DHT, DHT22);
alarma::Alarma reglas;
#if USAR_OLED
U8G2_SSD1309_128X64_NONAME0_F_HW_I2C pantalla(U8G2_R2, U8X8_PIN_NONE);  // R2: el modulo va girado 180 (conector abajo)
#endif

uint32_t ultimoMuestreo = 0;
uint32_t pantallaEncendidaEn = 0;
bool pantallaEncendida = false;

// ── MQTT + API ───────────────────────────────────────────────────────────────
// Manda T y HR juntas: por MQTT (tiempo real) y por HTTP POST a la API (se guardan en MySQL).
void publicarTelemetria() {
  Serial.printf("[dht] T = %.1f C  HR = %.1f %%\n", reglas.temperatura, reglas.humedad);
  StaticJsonDocument<256> doc;
  JsonArray lecturas = doc.createNestedArray("lecturas");
  JsonObject t = lecturas.createNestedObject();
  t["parametro"] = "temperatura";
  t["valor"] = roundf(reglas.temperatura * 10) / 10;
  t["unidad"] = "C";
  JsonObject h = lecturas.createNestedObject();
  h["parametro"] = "humedad";
  h["valor"] = roundf(reglas.humedad * 10) / 10;
  h["unidad"] = "%";
  nodo::enviarLecturas(doc);
}

// GET /api/comandos/dht -> {"alarma":"on"|"off"}. Respaldo de cmd/alarma por si MQTT no esta conectado:
// la orden de la nube llega por cualquiera de los dos caminos.
void consultarComandos() {
  String r;
  if (api::pedir("GET", "/api/comandos/" NODO_ID, nullptr, &r) != 200) return;
  StaticJsonDocument<96> doc;
  if (deserializeJson(doc, r)) return;  // respuesta que no es JSON: se ignora
  const char* orden = doc["alarma"] | "";
  if (strcmp(orden, "on") == 0) reglas.orden_nube(true, millis());
  else if (strcmp(orden, "off") == 0) reglas.orden_nube(false, millis());
}

void silenciar() {
  reglas.silenciar(millis());
  Serial.println("[dht] buzzer silenciado 30 min (boton)");
  if (nodo::mqtt.connected()) nodo::mqtt.publish(TOPIC_CMD_SILENCIAR, "{\"minutos\":30}");
  api::accion("buzzer", "off", "manual", 30 * 60);  // evento de actuacion: silencio manual de 30 min
}

void alRecibir(char* topic, byte* payload, unsigned int largo) {
  if (strcmp(topic, TOPIC_CMD_ALARMA) != 0) return;
  String orden;
  for (unsigned int i = 0; i < largo; i++) orden += (char)payload[i];
  orden.trim();
  Serial.printf("[dht] cmd/alarma por MQTT: %s\n", orden.c_str());
  if (orden == "on") reglas.orden_nube(true, millis());
  else if (orden == "off") reglas.orden_nube(false, millis());
}

void suscribir() { nodo::mqtt.subscribe(TOPIC_CMD_ALARMA); }

// ── sensor ───────────────────────────────────────────────────────────────────
void muestrear() {
  switch (reglas.muestra(dht.readTemperature(), dht.readHumidity())) {
    case alarma::Lectura::valida: publicarTelemetria(); break;
    case alarma::Lectura::falla_nueva: nodo::publicarEvento("sensor_error"); break;
    case alarma::Lectura::invalida: Serial.println("[dht] lectura invalida (NaN o fuera de rango): no se envia"); break;
  }
  consultarComandos();
}

// ── boton ────────────────────────────────────────────────────────────────────
void encenderPantalla() {
#if USAR_OLED
  pantallaEncendida = true;
  pantallaEncendidaEn = millis();
  pantalla.setPowerSave(0);
#endif
}

void atenderBoton() {
  static bool estable = HIGH, anterior = HIGH;
  static uint32_t cambio = 0, presionadoEn = 0;
  bool lectura = digitalRead(PIN_BOTON);
  if (lectura != anterior) { cambio = millis(); anterior = lectura; }
  if (!nodo::transcurrido(cambio, ANTIRREBOTE_MS) || lectura == estable) return;
  estable = lectura;
  if (estable == LOW) {
    presionadoEn = millis();
    return;
  }
#if USAR_OLED
  if (nodo::transcurrido(presionadoEn, PULSACION_LARGA_MS)) silenciar();  // larga = silencia
  else encenderPantalla();                                                 // corta = pantalla
#else
  (void)presionadoEn;  // sin pantalla, cualquier pulsacion silencia
  silenciar();
#endif
}

// ── salidas ──────────────────────────────────────────────────────────────────
#if USAR_OLED
void dibujarPantalla(const alarma::Salidas& s) {
  static uint32_t ultimoDibujo = 0;
  if (!pantallaEncendida) return;
  if (nodo::transcurrido(pantallaEncendidaEn, PANTALLA_MS)) {
    pantalla.setPowerSave(1);
    pantallaEncendida = false;
    return;
  }
  if (!nodo::transcurrido(ultimoDibujo, 1000)) return;
  ultimoDibujo = millis();
  // La vista vive en include/vista_oled.h (se revisa en la PC con herramientas/oled_host.py)
  VistaOled v = {reglas.temperatura, reglas.humedad, reglas.hay_dato(), s.falla, nodo::enLinea(), s.alarma,
                 s.silenciada, reglas.temp.etiqueta(reglas.temperatura), reglas.hum.etiqueta(reglas.humedad)};
  vista_oled_dibujar(pantalla.getU8g2(), &v);
  pantalla.sendBuffer();
}
#endif

// ── setup / loop ─────────────────────────────────────────────────────────────
void setup() {
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_BOTON, INPUT_PULLUP);
  dht.begin();
#if USAR_OLED
  Wire.begin();  // ESP8266: SDA = D2 (GPIO4), SCL = D1 (GPIO5)
  pantalla.begin();
  encenderPantalla();
#endif
  nodo::iniciar();
  nodo::mqtt.setCallback(alRecibir);
  nodo::alConectar = suscribir;
  ultimoMuestreo = millis() - PERIODO_MS + 3000;  // primera lectura a los ~3 s
}

void loop() {
  nodo::atender(false);  // publica cada 30 s: no necesita latido aparte
  if (nodo::transcurrido(ultimoMuestreo, PERIODO_MS)) {
    ultimoMuestreo = millis();
    muestrear();
  }
  atenderBoton();
  alarma::Salidas s = reglas.salidas(millis());
  digitalWrite(PIN_BUZZER, s.buzzer ? HIGH : LOW);
  nodo::alerta = s.rojo;         // fijo = alerta propia
  nodo::sensorFalla = s.falla;   // parpadeo rapido
#if USAR_OLED
  dibujarPantalla(s);
#endif
}
