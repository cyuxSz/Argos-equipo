# Flujo del firmware de los nodos

Actualizado el 9-nov-2026. Sale del código de `firmware/` (compilado, sin probar en placa). La parte común está en `include/nodo_comun.h`; el envío a la API, en `include/api_http.h`; las reglas del buzzer, en `include/alarma_dht.h`.

Cada lectura o evento sale por **dos caminos independientes**: MQTT (tiempo real, si hay broker) y **HTTP POST a la API** (`/api/mediciones`, `/api/eventos`, `/api/latido`, `/api/acciones`), que es lo que se guarda en MySQL. Si el POST falla por red o error 5xx se reintenta una vez; un 400 o 401 no se reintenta.

## 1. Parte común (los 5 nodos)

Cada `loop()` empieza con `nodo::atender()`: mantiene WiFi y MQTT, manda el latido y pinta los LED.

```mermaid
flowchart TD
  A([Encendido]) --> B["nodo::iniciar()<br/>LED D7/D8 como salida, WiFi STA,<br/>broker MQTT, keep-alive 45 s"]
  B --> C["setup() propio del nodo<br/>(pines y sensor)"]
  C --> L{{"loop()"}}
  L --> W{"¿WiFi conectado?"}
  W -- no --> LED
  W -- sí --> M{"¿MQTT conectado?"}
  M -- sí --> ML["mqtt.loop()"]
  M -- no --> R{"¿pasaron 5 s<br/>desde el último intento?"}
  R -- no --> ML
  R -- sí --> CX["conectar con LWT offline retenido<br/>publicar estado online retenido<br/>(reset_reason, uptime_s, rssi)"]
  CX --> ML
  ML --> LAT{"¿nodo con latido<br/>y pasaron 60 s?"}
  LAT -- sí --> PL["latido: MQTT telemetria latido = 1<br/>+ POST /api/latido (uptime, rssi)"]
  LAT -- no --> LED
  PL --> LED
  LED["LED verde: fijo en línea, parpadeo lento sin red<br/>LED rojo: parpadeo rápido si falla el sensor,<br/>fijo si hay alerta propia"] --> P["lógica propia del nodo<br/>(diagramas 2 y 3)"]
  P --> L
```

Latido: lo mandan `pir`, `puerta` y `acel`. `dht` (cada 30 s) y `luz` (cada 60 s) ya mandan datos seguido y no lo necesitan.

## 2. Nodo dht

```mermaid
flowchart TD
  L{{"loop()"}} --> AT["nodo::atender(sin latido)"]
  AT --> T{"¿pasaron 30 s?"}
  T -- no --> BOT
  T -- sí --> LEE["leer DHT22 (T y HR)"]
  LEE --> V{"resultado"}
  V -- válida --> PUB["MQTT telemetria + POST /api/mediciones<br/>temperatura y humedad"]
  V -- tercera inválida seguida --> ERR["evento sensor_error<br/>(MQTT + POST /api/eventos)"]
  V -- inválida --> BOT
  PUB --> BOT
  ERR --> BOT
  BOT{"botón D6"} -- "pulsación corta" --> OL["encender OLED 30 s"]
  BOT -- "pulsación larga (≥ 1.5 s)" --> SIL["silenciar 30 min<br/>publicar cmd/silenciar"]
  BOT -- nada --> REG
  OL --> REG
  SIL --> REG
  REG["reglas de alarma:<br/>alerta local = 3 lecturas fuera de 22–28 °C o 40–60 %<br/>se cierra con 3 dentro del margen (0.5 °C / 2 %)"] --> BZ{"(alerta local u orden on<br/>vigente 150 s) y no silenciado"}
  BZ -- sí --> ON["buzzer D5 encendido"]
  BZ -- no --> OFF["buzzer apagado"]
  ON --> PIN["LED rojo y OLED con el estado"]
  OFF --> PIN
  PIN --> L
  MQ[/"mensaje en cmd/alarma"/] -.-> ORD["on: renueva la orden 150 s<br/>off: la cancela"]
  ORD -.-> REG
```

## 3. Nodos de evento y de luz

```mermaid
flowchart LR
  subgraph PIR["pir (D5)"]
    direction TB
    P1{"¿flanco de subida?"} -- "sí y pasaron 10 s" --> P2["evento movimiento"]
    P1 -.-> P3["LED rojo 5 s<br/>tras cada detección"]
  end
  subgraph PUERTA["puerta (D5, pull-up)"]
    direction TB
    Q1{"¿cambió el estado<br/>(antirrebote 50 ms)?"} -- sí --> Q2["evento puerta_abierta<br/>o puerta_cerrada"]
    Q1 -.-> Q3["LED rojo fijo<br/>mientras está abierta"]
  end
  subgraph ACEL["acel (ADS1115 por I²C)"]
    direction TB
    A1["leer X, Y, Z<br/>|a| en g"] --> A2{"¿| |a| − 1 g | > 0.5 g?<br/>[umbral POR CONFIRMAR]"}
    A2 -- "sí y pasaron 2 s" --> A3["evento golpe con magnitud"]
    A2 -.-> A4["LED rojo 5 s tras el golpe"]
  end
  subgraph LUZ["luz (A0)"]
    direction TB
    L1["muestra cada 5 s"] --> L2{"¿12 muestras?"}
    L2 -- sí --> L3["promedio ADC cada 60 s<br/>(MQTT + POST /api/mediciones)"]
    L3 --> L4["LED rojo si el promedio < 300<br/>(lámparas apagadas) [POR CONFIRMAR]"]
  end
```

Lo que decide si algo es alerta en el servidor (temperatura y humedad con las mismas reglas del firmware, puerta abierta, golpe, nodo sin reporte) lo evalúa el **motor de alertas de la API** (`servidor/api/alertas.js`), no el nodo. n8n solo manda los avisos por WhatsApp y Telegram con horario.
