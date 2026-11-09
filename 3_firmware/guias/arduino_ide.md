# Firmware: PlatformIO, Arduino IDE o "ESP32 IDE"

20-oct-2026. **`firmware/` sigue siendo la fuente de verdad.** Esta guía solo compila; **nadie flashea sin aprobación.**

## Recomendación

| Opción | Veredicto | Por qué |
|---|---|---|
| **PlatformIO** (VS Code o CLI) | **Principal** | Los 6 entornos ya compilan. Las versiones de plataforma y librerías están fijadas en `platformio.ini`, así que todos compilan lo mismo. `NODO_ID` y `USAR_OLED` van como `build_flags`, sin copiar código |
| **Arduino IDE 2.x** | Alternativa para quien lo prefiera | Funciona con los sketches generados (abajo). Las versiones de librerías se fijan a mano y el IDE ofrece actualizarlas: hay que rechazar esas actualizaciones |
| **"ESP32 IDE"** (core ESP32 o ESP-IDF) | **No aplica** | El hardware es **ESP8266** (NodeMCU ESP-12E). El core de ESP32 y ESP-IDF no compilan para ESP8266. Pasarse a ESP32 obliga a comprar 5 placas nuevas, fuera del presupuesto, y a rehacer pines y ADC |

## Arduino IDE 2.x paso a paso

### 1. Placa

1. En *Archivo → Preferencias → URLs adicionales de gestor de placas*, agrega:
   `https://arduino.esp8266.com/stable/package_esp8266com_index.json`
2. En *Herramientas → Placa → Gestor de placas*, instala **esp8266 by ESP8266 Community, versión 3.1.2**. Es el mismo core que usa PlatformIO con `espressif8266@4.2.1`.
3. Elige *Herramientas → Placa → ESP8266 Boards → NodeMCU 1.0 (ESP-12E Module)*. Deja el resto como viene: CPU de 80 MHz, Flash de 4 MB y Upload Speed de 115200.

### 2. Librerías (Gestor de librerías, **versión exacta**)

| Librería (autor) | Versión | La usan |
|---|---|---|
| PubSubClient (Nick O'Leary) | **2.8** | Todos |
| ArduinoJson (Benoit Blanchon) | **6.21.5** (no la 7) | Todos |
| DHT sensor library (Adafruit) | **1.4.6** | `dht` |
| Adafruit Unified Sensor (Adafruit) | **1.1.14** | `dht` |
| U8g2 (oliver) | **2.35.30** | `dht` con OLED |
| Adafruit ADS1X15 (Adafruit) | **2.5.0** | `acel` |
| Adafruit BusIO (Adafruit) | **1.16.1** | `acel` (dependencia del ADS1X15) |

> **Ojo, en esta PC:** la carpeta de librerías de Arduino ya tiene ArduinoJson **7.4.3**, DHT **1.4.7** y Unified Sensor **1.1.15**. Arduino IDE comparte esa carpeta con arduino-cli. Antes de compilar con el IDE, en el gestor elige la versión de la tabla (*Instalar* → versión). No lo cambié yo: es una configuración global, fuera del proyecto.

### 3. Sketches

Arduino IDE no tiene `build_flags`. Por eso se generan sketches con los `#define` al principio:

```bash
python firmware/herramientas/exportar_arduino.py
```

Crea `firmware/arduino_ide/argos_<entorno>/`, uno por entorno (`dht`, `dht_sin_oled`, `luz`, `pir`, `puerta`, `acel`). Cada carpeta lleva:
- un `.ino` casi vacío;
- `main.cpp`, generado desde `firmware/src/<nodo>/main.cpp`;
- las cabeceras.

**No edites ahí:** cambia `firmware/src` y vuelve a generar. El script conserva un `secrets.h` que hayas puesto en la carpeta.

1. Abre `argos_<entorno>.ino`.
2. **Credenciales:** copia `secrets.example.h` a `secrets.h` **en esa misma carpeta** y llénalo. Está en `.gitignore` y no se comparte. Sin `secrets.h`, el sketch compila con los valores de ejemplo.
3. Presiona **Verificar (✓)**. **Subir (→) solo con aprobación del equipo.**

## Por qué ArduinoJson 6.21.5 y no la 7

Lo probé compilando una copia temporal de `luz` y `dht` con **ArduinoJson 7.4.2**. **Compila**, con 11 advertencias de obsoleto:
- 6 × `StaticJsonDocument`;
- 2 × `createNestedArray`;
- 3 × `createNestedObject`.

O sea, hoy no se rompe el código, pero no conviene subir de versión:

1. **Cambia cómo usa la memoria.** En la 7, todo `JsonDocument` va siempre en el heap, y el tamaño de `StaticJsonDocument<N>` se ignora. El código actual reserva el documento en la pila (de 96 a 256 bytes) cada vez que publica. Con la 7, cada publicación pide y libera heap. En un ESP8266, con ≈ 40 KB libres con WiFi, eso puede fragmentar la memoria tras días de funcionamiento. No está probado y no compensa el riesgo.
2. **La API vieja va de salida.** `StaticJsonDocument`, `createNestedArray()` y `createNestedObject()` están marcadas como obsoletas; el registro de cambios de la 7 las da por eliminadas como clases o métodos propios. Una versión futura puede dejar de compilar el código.
3. **Migrar no aporta nada.** Los mensajes MQTT son pequeños y fijos. Migrar implicaría cambiar `StaticJsonDocument<N> doc;` por `JsonDocument doc;`, y `createNestedArray("lecturas")` por `doc["lecturas"].to<JsonArray>()`, más pruebas en hardware.

Por eso `platformio.ini` fija `bblanchon/ArduinoJson@6.21.5`. En Arduino IDE hay que fijarla a mano.

## Qué se probó (20-oct-2026)

| Prueba | Resultado |
|---|---|
| PlatformIO, 6 entornos (`pio run`, sin `-t upload`) | **SUCCESS** los 6 |
| arduino-cli 1.5.1 + core esp8266 3.1.2 + librerías de la tabla, en una carpeta **temporal** (sin tocar las globales), FQBN `esp8266:esp8266:nodemcuv2` | **Compilan los 6 sketches.** Código en flash ≈ 250–273 KB |
| Copia temporal con ArduinoJson 7.4.2 (`luz`, `dht`) | Compila con 11 advertencias de obsoleto |
| Flasheo | **No se hizo** |

## Fuentes

- [ArduinoJson: actualizar de la 6 a la 7](https://arduinojson.org/v7/how-to/upgrade-from-v6/)
- [ArduinoJson: CHANGELOG (v7.4.2)](https://github.com/bblanchon/ArduinoJson/blob/v7.4.2/CHANGELOG.md)
- [ArduinoJson 7: anuncio](https://arduinojson.org/news/2024/01/03/arduinojson-7/)
