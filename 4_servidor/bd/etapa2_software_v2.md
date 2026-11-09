# Etapa 2 de software (BD), versión 2

21-oct-2026. Actualiza el PDF entregado el 20-oct (`Etapa2SoftwareBD`) a como manejamos hoy el proyecto. Solo cambian las secciones de abajo; los artículos (1b, 1c), las referencias y el roadmap no cambian. El esquema ejecutable está en [`esquema.sql`](esquema.sql). **No se ha probado en un servidor MySQL.**

## Qué cambió y por qué

| # | Antes (PDF) | Ahora | Motivo |
|---|---|---|---|
| 1 | "Cada nodo con su propia fuente de 5 V" | 3 cajas, una **fuente de 5 V** por caja: `dht` sola; estación de entrada (`pir` + `puerta`); estación del anaquel (`acel` + `luz`) | Reacomodo del 19-oct (escenario B del presupuesto). Siguen siendo 5 microcontroladores, uno por integrante |
| 2 | "El único actuador autorizado es el buzzer" | 6 actuadores: el buzzer del `dht` y el **LED rojo de cada nodo**, que reacciona a su sensor | El reto pide 1 sensor y 1 actuador por integrante (Etapa 2). El LED verde es indicador de estado, no actuador: ya queda en EstadoNodo |
| 3 | Nodo guarda `area` y `punto_montaje` | Nueva entidad **Caja**; Nodo apunta a su caja | Dos nodos de la misma estación comparten ubicación: dejarla en Nodo crea la dependencia transitiva id_nodo → caja → ubicación (rompe 3FN) |
| 4 | AccionControl solo con alerta opcional | Agrega `origen` (alerta, local, manual) y `duracion_s` | El LED rojo lo decide el propio nodo (local) y a veces dura 5 s; el buzzer lo ordena n8n por una alerta |
| 5 | Evento sin `sensor_error` | `sensor_error` en Evento y `sensor_falla` como tipo de Alerta | Ya está en el contrato MQTT y el firmware lo publica |
| 6 | "Acelerómetro del kit (modelo por confirmar)" | GY-61 (ADXL335) leído por un ADS1115 | Definido el 19-oct |
| 7 | — | El latido (`parametro: "latido"`) no se guarda como Medición: solo actualiza `EstadoNodo.ultimo_reporte` | Evita llenar Medición de filas sin significado |
| 8 | Responsable como texto en Nodo; Umbral ligado solo a Parámetro | Nueva clase **Responsable**; **Umbral** ligado directamente a **Sensor** (además de Parámetro) | El nombre del responsable se repetía en cada nodo; el umbral debe saber a qué sensor se aplica |

## 1 a) Descripción del prototipo (párrafos que cambian)

El prototipo usa cinco NodeMCU (ESP8266), uno por integrante, repartidos en tres cajas impresas en PETG. El nodo `dht` va solo en su caja, para que el calor de la electrónica no altere la lectura. Los nodos `pir` y `puerta` comparten la estación de entrada, y `acel` y `luz` la del anaquel. Cada caja tiene una fuente de 5 V; dentro de una estación las dos placas comparten 5 V y tierra, pero cada una conserva su propio regulador de 3.3 V.

Cada nodo tiene un sensor y un actuador: un LED rojo que reacciona a su sensor (`pir`: 5 s tras un movimiento; `puerta`: mientras está abierta; `acel`: 5 s tras un golpe; `luz`: cuando lee las lámparas apagadas; `dht`: mientras hay alerta de temperatura o humedad). El `dht` tiene además el buzzer con transistor, el único actuador que suena, y lo encienden tanto la regla local como la orden de n8n. El LED verde indica si el nodo está conectado.

## 2 a) Requerimientos que cambian

| Clave | Requerimiento funcional |
|---|---|
| RF01 (Luis, `pir`) | El sistema deberá registrar cada evento de movimiento con su fecha y hora, indicar si ocurrió fuera del horario autorizado de acceso y encender el LED rojo del nodo durante 5 s tras cada detección. |
| RF03 (Arianna, `luz`) | El sistema deberá registrar el nivel de luz de la fotorresistencia, encender el LED rojo cuando lea las lámparas apagadas y abrir una alerta cuando el nivel no coincida con el fotoperiodo esperado. |
| RF04 (Iván, `puerta`) | El sistema deberá registrar la apertura y el cierre de la puerta, mantener encendido el LED rojo mientras esté abierta y abrir una alerta si permanece abierta más del tiempo configurado. |
| RF05 (Mía, `acel`) | El sistema deberá registrar cada golpe o vibración con su magnitud, encender el LED rojo durante 5 s y abrir una alerta cuando supere el umbral calibrado. |
| RF08 (equipo) | El sistema deberá registrar cada acción de control de los seis actuadores (buzzer y LED rojos), indicando si la originó una alerta, la regla local del nodo o una prueba manual. |
| RF11 (equipo) | El sistema deberá registrar a qué caja pertenece cada nodo y la ubicación de la caja. |

RF02, RF06, RF07, RF09, RF10 y RNF01–RNF06 no cambian. Se agrega **RNF07**: *los nodos de una misma caja comparten la fuente de 5 V pero nunca su salida de 3.3 V.*

## 2 b) Descripción textual (párrafos que cambian)

En el cuarto de incubación in vitro se instalan cinco nodos NodeMCU repartidos en tres cajas. Cada caja tiene un nombre corto único (`dht`, `entrada` o `anaquel`), una descripción y una ubicación compuesta por área y punto de montaje, y aloja uno o dos nodos. Cada nodo pertenece a una sola caja y tiene un nombre corto único que coincide con su tópico MQTT, y un responsable del equipo (clase propia).

Cada nodo tiene al menos un actuador, su LED rojo, y el nodo `dht` tiene además un buzzer. Un actuador pertenece a un solo nodo y ejecuta acciones de control (encender o apagar) con fecha y hora y, si aplica, una duración. Cada acción tiene un origen: una alerta (el buzzer que ordena n8n), la regla local del nodo (el LED que reacciona a su sensor) o una prueba manual. Solo las acciones originadas por una alerta quedan ligadas a ella.

Los sensores producen también un evento `sensor_error` cuando dejan de dar lecturas válidas, y ese evento abre una alerta de tipo `sensor_falla`.

## Reglas de negocio (versión 2)

- **RN1–RN6, RN8:** sin cambios.
- **RN7 (cambia).** Cada nodo tiene uno o dos actuadores: todos tienen su LED rojo y solo el `dht` tiene además el buzzer. Un actuador pertenece a un solo nodo y ejecuta muchas acciones. Una acción pertenece a un actuador y puede originarse en una alerta (participación opcional); si su origen es `alerta`, la alerta es obligatoria, y en otro caso debe quedar vacía.
- **RN9 (nueva).** Una caja aloja uno o dos nodos y cada nodo está en exactamente una caja (1:1..2, participación total en ambos lados).
- **RN10 (nueva).** Un nodo no puede tener dos actuadores del mismo tipo.
- **RN11 (nueva).** Cada nodo tiene un responsable; un responsable atiende uno o más nodos (1:1..*, total en ambos lados).
- **RN12 (nueva).** Cada umbral se aplica a un sensor y a un parámetro; un sensor tiene 0..* umbrales, uno por parámetro.

## 3. Modelo conceptual: clases y relaciones que cambian

Pasa de 12 a **14 clases** (agrega Caja y Responsable).

| Relación | Cardinalidad | Participación |
|---|---|---|
| Caja aloja Nodo (nueva) | 1 caja : 1..2 nodos | Total en ambos lados (RN9) |
| Nodo posee Actuador (cambia) | 1 nodo : 1..2 actuadores | Total en ambos lados (RN7) |
| Responsable responde de Nodo (nueva) | 1 responsable : 1..* nodos | Total en ambos lados (RN11) |
| Sensor se compara con Umbral (nueva) | 1 sensor : 0..* umbrales | Total del umbral, parcial del sensor (RN12) |
| Alerta dispara AcciónControl | 0..1 alerta : 0..* acciones | Parcial (origen local o manual) |

Atributo compuesto: la **ubicación** ahora es de Caja (área + punto de montaje).

## 4. Modelo relacional: relaciones que cambian

| Relación | Atributos | PK | FK |
|---|---|---|---|
| **Caja** (nueva) | id_caja, descripcion, area, punto_montaje | id_caja | — |
| **Responsable** (nueva) | id_responsable, nombre | id_responsable | — |
| **Nodo** | id_nodo, id_caja, id_responsable, descripcion | id_nodo | id_caja → Caja; id_responsable → Responsable |
| **Umbral** | id_umbral, id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer | id_umbral | id_sensor → Sensor; id_parametro → Parametro; UNIQUE (id_sensor, id_parametro) |
| **Actuador** | id_actuador, id_nodo, tipo | id_actuador | id_nodo → Nodo; UNIQUE (id_nodo, tipo) |
| **AccionControl** | id_accion, id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora | id_accion | id_actuador → Actuador; id_alerta → Alerta (opcional) |

## 5. 3FN: dependencias que cambian

| Relación | Dependencias funcionales | Justificación |
|---|---|---|
| Caja | id_caja → descripcion, area, punto_montaje | La ubicación depende de la caja y no se repite en sus dos nodos |
| Responsable | id_responsable → nombre; nombre → id_responsable | El nombre no se repite en Nodo |
| Nodo | id_nodo → id_caja, id_responsable, descripcion | Se quitó la dependencia transitiva id_nodo → id_caja → area, punto_montaje |
| Umbral | id_umbral → id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer | (id_sensor, id_parametro) es llave candidata |
| Actuador | id_actuador → id_nodo, tipo; (id_nodo, tipo) → id_actuador | (id_nodo, tipo) es llave candidata; ninguna dependencia transitiva |
| AccionControl | id_accion → id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora | `origen` no se deduce de id_alerta (local y manual dejan id_alerta vacío), así que no es redundante |

## 6. Diccionario de datos: cambios

**Caja (nueva)**

| Atributo | Descripción | Tipo | Long. | Restricciones |
|---|---|---|---|---|
| id_caja | Nombre corto de la caja | VARCHAR | 10 | PK, NOT NULL |
| descripcion | Qué nodos aloja | VARCHAR | 60 | NOT NULL |
| area | Área de instalación | VARCHAR | 40 | NOT NULL, DEFAULT 'Cuarto de incubación' |
| punto_montaje | Pared, anaquel, etc. | VARCHAR | 40 | NULL |

**Responsable (nueva):** `id_responsable INT PK AUTO_INCREMENT`, `nombre VARCHAR(60) UNIQUE NOT NULL`.

**Nodo:** se quitan `area`, `punto_montaje` y `responsable`; se agregan `id_caja VARCHAR(10) FK → Caja, NOT NULL` e `id_responsable INT FK → Responsable, NOT NULL`.

**Umbral:** se agrega `id_sensor INT FK → Sensor, NOT NULL` y `UNIQUE (id_sensor, id_parametro)`.

**Actuador:** `tipo` pasa a `ENUM('buzzer','led_rojo') NOT NULL`, con `UNIQUE (id_nodo, tipo)`.

**AccionControl:** se agregan `origen ENUM('alerta','local','manual') NOT NULL` y `duracion_s SMALLINT UNSIGNED NULL` (NULL significa "hasta un off"), con `CHECK ((origen = 'alerta') = (id_alerta IS NOT NULL))`.

**Evento:** `tipo` agrega `sensor_error`. **Alerta:** `tipo` agrega `sensor_falla`.

## Cómo se llenan las tablas desde MQTT (para el flujo de n8n)

| Mensaje | Tabla |
|---|---|
| `telemetria/{nodo}` con temperatura, humedad o luz | Medicion (una fila por lectura). Si la luz cruza `umbral_luz_adc`, o la T/HR abre o cierra su alerta, también AccionControl del LED rojo (`origen = 'local'`), solo cuando cambia de estado |
| `telemetria/{nodo}` con `latido` | Solo `EstadoNodo.ultimo_reporte` |
| `evento/{nodo}` | Evento; y AccionControl del LED rojo con `origen = 'local'`, inferida de la regla del firmware (movimiento o golpe: `on` 5 s; puerta abierta: `on`; puerta cerrada: `off`) |
| `estado/{nodo}` (incluye el LWT) | EstadoNodo |
| n8n publica `cmd/alarma = on` | AccionControl del buzzer con `origen = 'alerta'` |

> El firmware **no publica** el estado de sus LED: el contrato MQTT no lo incluye y no lo cambiamos. n8n deduce la acción a partir del evento y de la regla documentada. Está en la lista de preguntas al profesor si esto basta como registro del actuador.
