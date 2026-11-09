# Prompts de armado en protoboard (constructa.io, Tinkercad u otras herramientas con IA)

Generado por `hardware/breadboard/prompts.py` desde `layouts.py`: es la misma distribución verificada de los dibujos `hardware/breadboard/nodo_<id>_protoboard.png` y del WireViz. Si cambias `layouts.py`, vuelve a generarlo.

## Cómo usarlos

1. Copia el bloque de **una** caja completa (el `dht` o una estación) y pégalo en la herramienta. Una caja por conversación funciona mejor que todas juntas.
2. Compara el resultado con `hardware/breadboard/nodo_<id>_protoboard.png` y la sección *Redes* del bloque. Si la herramienta movió algo, pídele que lo corrija citando el orificio exacto.
3. **No sustituyas componentes** para que el dibujo "funcione": el armado real usa estas piezas.

> **Limitaciones que no pude verificar.** No encontré documentación pública de constructa.io ni de una función de IA en Tinkercad que genere circuitos desde texto. Hasta donde sé, Tinkercad Circuits **no incluye** el NodeMCU (ESP8266), la OLED I²C, el ADS1115 ni el DHT22. Si la herramienta no tiene una pieza, el dibujo no será fiel: en ese caso usa como referencia los dibujos de protoboard de este proyecto, que ya están orificio por orificio.

## Prompt general (pegar antes de cualquier nodo si la herramienta lo permite)

```text
Vas a dibujar circuitos para armar físicamente en protoboard. Respeta al pie de la letra las coordenadas de orificio (columna 1-30, fila a-j o riel), los valores y los colores de cable. Si te falta una pieza en tu biblioteca, dímelo en lugar de sustituirla. Todos los GPIO son de 3.3 V; nada que entre a un GPIO puede ser de 5 V.
```

### `dht`: dht (con OLED 2.42")

```text
Dibuja en una protoboard de 400 puntos el circuito 'dht' EXACTAMENTE como se describe.
No agregues, quites ni muevas componentes. No cambies pines ni valores.

PROTOBOARD: 400 puntos, 30 columnas (1 a 30) y filas a-e / f-j separadas por el canal central.
Rieles: arriba (junto a la fila a) interior = +5V, exterior = GND.
        abajo (junto a la fila j) interior = +3.3V, exterior = GND.

PLACA NodeMCU: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas 1-15, puerto micro-USB hacia la columna 1.
  Fila b (col. 1 a 15): VIN, GND, RST, EN, 3V3, GND, CLK, SD0, CMD, SD1, SD2, SD3, RSV, RSV, A0.
  Fila i (col. 1 a 15): 3V3, GND, TX, RX, D8, D7, D6, D5, GND, 3V3, D4, D3, D2, D1, D0.

COMPONENTES EN LA PROTOBOARD:
  - C1 (220 µF / 16 V electrolítico): pin + en riel superior interior (+5V), junto a la columna 3; pin - en riel superior exterior (GND), junto a la columna 3. Polaridad: pata larga (+) al riel 5V; franja (−) al riel GND
  - R5 (330 Ω): pin 1 en g20; pin 2 en d20. Cruza el canal (filas g→d). LED verde
  - R6 (330 Ω): pin 1 en g22; pin 2 en d22. Cruza el canal (filas g→d). LED rojo
  - R1 (10 kΩ): pin 1 en j24; pin 2 en riel inferior interior (+3.3V), junto a la columna 24. Pull-up de DATA. De pie (vertical) entre j24 y el riel 3V3
  - R3 (1 kΩ): pin 1 en g27; pin 2 en d27. Cruza el canal: de D5 a la base
  - R4 (10 kΩ): pin 1 en a27; pin 2 en riel superior exterior (GND), junto a la columna 27. Base a GND. De pie entre a27 y el riel GND
  - Q1 (2N2222 (TO-92)): pin E en b26; pin B en b27; pin C en b28. Cara plana hacia la fila a; E-B-C de col. 26 a 28 [verificar pinout del lote]

PUENTES (cable corto rígido, color indicado):
  - de a1 a riel superior interior (+5V), junto a la columna 1, color rojo (VIN (5 V del USB) → riel 5V).
  - de a2 a riel superior exterior (GND), junto a la columna 2, color negro (GND → riel GND lado A).
  - de j1 a riel inferior interior (+3.3V), junto a la columna 1, color naranja (3V3 → riel 3V3).
  - de j2 a riel inferior exterior (GND), junto a la columna 2, color negro (GND → riel GND lado J).
  - de j6 a h20, color cafe (D7 → columna 20 (LED verde), por fuera de la fila j).
  - de j5 a h22, color morado (D8 → columna 22 (LED rojo), por fuera de la fila j).
  - de j8 a h27, color blanco (D5 → columna 27 (R3 hacia la base de Q1), por fuera de la fila j).
  - de a26 a riel superior exterior (GND), junto a la columna 26, color negro (Emisor de Q1 → GND).
  - de j7 a h21, color gris (D6 → columna 21 (botón), por fuera de la fila j).
  - de j11 a h24, color amarillo (D4 → columna 24 (DATA del DHT22), por fuera de la fila j).
  - de j13 a h23, color verde (D2/SDA → columna 23 (OLED), por fuera de la fila j).
  - de j14 a h25, color azul (D1/SCL → columna 25 (OLED), por fuera de la fila j).

MÓDULOS FUERA DE LA PROTOBOARD (cable Dupont macho-hembra desde el orificio indicado):
  - LED verde de 5 mm: A ← a20 (cable verde); K ← riel superior exterior (GND), junto a la columna 19 (cable negro).
  - LED rojo de 5 mm: A ← a22 (cable rojo); K ← riel superior exterior (GND), junto a la columna 23 (cable negro).
  - pulsador táctil de 6x6 mm: 1 ← j21 (cable gris); 2 ← riel inferior exterior (GND), junto a la columna 7 (cable negro).
  - sensor DHT22 de 3 pines (VCC, DATA, GND): VCC ← riel inferior interior (+3.3V), junto a la columna 25 (cable naranja); DATA ← f24 (cable amarillo); GND ← riel inferior exterior (GND), junto a la columna 25 (cable negro).
  - buzzer activo KY-012 de 5 V (+, -): + ← riel superior interior (+5V), junto a la columna 30 (cable rojo); - ← a28 (cable blanco).
  - pantalla OLED 2.42" SSD1309 I2C de 4 pines (VCC, GND, SCL, SDA): VCC ← riel inferior interior (+3.3V), junto a la columna 12 (cable naranja); GND ← riel inferior exterior (GND), junto a la columna 12 (cable negro); SCL ← f25 (cable azul); SDA ← f23 (cable verde).

REDES QUE DEBEN QUEDAR CONECTADAS (para verificar):
  - D7: NodeMCU.D7, R5.1
  - LED_V: LED_V.A, R5.2
  - D8: NodeMCU.D8, R6.1
  - LED_R: LED_R.A, R6.2
  - 5V: Buzzer.+, C1.+, NodeMCU.VIN
  - D5: NodeMCU.D5, R3.1
  - BASE: Q1.B, R3.2, R4.1
  - COLECTOR: Buzzer.-, Q1.C
  - D6: Boton.1, NodeMCU.D6
  - GND: Boton.2, C1.-, DHT22.GND, LED_R.K, LED_V.K, NodeMCU.GND, OLED.GND, Q1.E, R4.2
  - 3V3: DHT22.VCC, NodeMCU.3V3, OLED.VCC, R1.2
  - SCL: NodeMCU.D1, OLED.SCL
  - SDA: NodeMCU.D2, OLED.SDA
  - DATA: DHT22.DATA, NodeMCU.D4, R1.1
```

### `entrada`: Estación de entrada (pir + puerta)

```text
Dibuja en una protoboard de 830 puntos el circuito 'entrada' EXACTAMENTE como se describe.
No agregues, quites ni muevas componentes. No cambies pines ni valores.

PROTOBOARD: 830 puntos, 63 columnas (1 a 63) y filas a-e / f-j separadas por el canal central.
Rieles: arriba (junto a la fila a) interior = +5V, exterior = GND.
        abajo (junto a la fila j) interior = +3.3V, exterior = GND.
Los 4 rieles están PARTIDOS entre las columnas 31 y 32. 5V y GND se unen con puentes; el de 3.3V NO se une (cada placa tiene su propio 3.3V).

PLACA NodeMCU_pir: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas 1-15, puerto micro-USB hacia la columna 1.
  Fila b (col. 1 a 15): VIN, GND, RST, EN, 3V3, GND, CLK, SD0, CMD, SD1, SD2, SD3, RSV, RSV, A0.
  Fila i (col. 1 a 15): 3V3, GND, TX, RX, D8, D7, D6, D5, GND, 3V3, D4, D3, D2, D1, D0.
PLACA NodeMCU_puerta: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas 34-48, puerto micro-USB hacia la columna 34.
  Fila b (col. 34 a 48): VIN, GND, RST, EN, 3V3, GND, CLK, SD0, CMD, SD1, SD2, SD3, RSV, RSV, A0.
  Fila i (col. 34 a 48): 3V3, GND, TX, RX, D8, D7, D6, D5, GND, 3V3, D4, D3, D2, D1, D0.

COMPONENTES EN LA PROTOBOARD:
  - pir_C1 (220 µF / 16 V electrolítico): pin + en riel superior interior (+5V), junto a la columna 3; pin - en riel superior exterior (GND), junto a la columna 3. Polaridad: pata larga (+) al riel 5V; franja (−) al riel GND
  - pir_R5 (330 Ω): pin 1 en g20; pin 2 en d20. Cruza el canal (filas g→d). LED verde
  - pir_R6 (330 Ω): pin 1 en g22; pin 2 en d22. Cruza el canal (filas g→d). LED rojo
  - puerta_C1 (220 µF / 16 V electrolítico): pin + en riel superior interior (+5V), junto a la columna 36; pin - en riel superior exterior (GND), junto a la columna 36. Polaridad: pata larga (+) al riel 5V; franja (−) al riel GND
  - puerta_R5 (330 Ω): pin 1 en g53; pin 2 en d53. Cruza el canal (filas g→d). LED verde
  - puerta_R6 (330 Ω): pin 1 en g55; pin 2 en d55. Cruza el canal (filas g→d). LED rojo

PUENTES (cable corto rígido, color indicado):
  - de a1 a riel superior interior (+5V), junto a la columna 1, color rojo ([pir] VIN (5 V del USB) → riel 5V).
  - de a2 a riel superior exterior (GND), junto a la columna 2, color negro ([pir] GND → riel GND lado A).
  - de j1 a riel inferior interior (+3.3V), junto a la columna 1, color naranja ([pir] 3V3 → riel 3V3).
  - de j2 a riel inferior exterior (GND), junto a la columna 2, color negro ([pir] GND → riel GND lado J).
  - de j6 a h20, color cafe ([pir] D7 → columna 20 (LED verde), por fuera de la fila j).
  - de j5 a h22, color morado ([pir] D8 → columna 22 (LED rojo), por fuera de la fila j).
  - de j8 a h27, color blanco ([pir] D5 → columna 27 (OUT del PIR), por fuera de la fila j).
  - de a34 a riel superior interior (+5V), junto a la columna 34, color rojo ([puerta] VIN (5 V del USB) → riel 5V).
  - de a35 a riel superior exterior (GND), junto a la columna 35, color negro ([puerta] GND → riel GND lado A).
  - de j34 a riel inferior interior (+3.3V), junto a la columna 34, color naranja ([puerta] 3V3 → riel 3V3).
  - de j35 a riel inferior exterior (GND), junto a la columna 35, color negro ([puerta] GND → riel GND lado J).
  - de j39 a h53, color cafe ([puerta] D7 → columna 53 (LED verde), por fuera de la fila j).
  - de j38 a h55, color morado ([puerta] D8 → columna 55 (LED rojo), por fuera de la fila j).
  - de j41 a h60, color blanco ([puerta] D5 → columna 60 (reed), por fuera de la fila j).
  - de riel superior interior (+5V), junto a la columna 31 a riel superior interior (+5V), junto a la columna 33, color rojo (Une el riel 5V partido (las dos mitades comparten la fuente)).
  - de riel superior exterior (GND), junto a la columna 31 a riel superior exterior (GND), junto a la columna 33, color negro (Une el riel GND superior partido).
  - de riel inferior exterior (GND), junto a la columna 31 a riel inferior exterior (GND), junto a la columna 33, color negro (Une el riel GND inferior partido. El riel 3V3 NO se une).

MÓDULOS FUERA DE LA PROTOBOARD (cable Dupont macho-hembra desde el orificio indicado):
  - LED verde de 5 mm: A ← a20 (cable verde); K ← riel superior exterior (GND), junto a la columna 19 (cable negro).
  - LED rojo de 5 mm: A ← a22 (cable rojo); K ← riel superior exterior (GND), junto a la columna 23 (cable negro).
  - sensor de movimiento HC-SR501 (VCC, OUT, GND): VCC ← riel superior interior (+5V), junto a la columna 28 (cable rojo); OUT ← f27 (cable blanco); GND ← riel superior exterior (GND), junto a la columna 28 (cable negro).
  - LED verde de 5 mm: A ← a53 (cable verde); K ← riel superior exterior (GND), junto a la columna 52 (cable negro).
  - LED rojo de 5 mm: A ← a55 (cable rojo); K ← riel superior exterior (GND), junto a la columna 56 (cable negro).
  - sensor magnético de puerta MC-38 (2 cables): 1 ← f60 (cable blanco); 2 ← riel inferior exterior (GND), junto a la columna 60 (cable negro).
  - módulo de entrada USB-C a terminales (+5V, GND): + ← riel superior interior (+5V), junto a la columna 32 (cable rojo); - ← riel superior exterior (GND), junto a la columna 32 (cable negro).

REDES QUE DEBEN QUEDAR CONECTADAS (para verificar):
  - pir_D7: NodeMCU_pir.D7, pir_R5.1
  - pir_LED_V: pir_LED_V.A, pir_R5.2
  - pir_D8: NodeMCU_pir.D8, pir_R6.1
  - pir_LED_R: pir_LED_R.A, pir_R6.2
  - pir_D5: NodeMCU_pir.D5, pir_PIR.OUT
  - puerta_D7: NodeMCU_puerta.D7, puerta_R5.1
  - puerta_LED_V: puerta_LED_V.A, puerta_R5.2
  - puerta_D8: NodeMCU_puerta.D8, puerta_R6.1
  - puerta_LED_R: puerta_LED_R.A, puerta_R6.2
  - puerta_D5: NodeMCU_puerta.D5, puerta_Reed.1
  - 5V: Entrada5V.+, NodeMCU_pir.VIN, NodeMCU_puerta.VIN, pir_C1.+, pir_PIR.VCC, puerta_C1.+
  - GND: Entrada5V.-, NodeMCU_pir.GND, NodeMCU_puerta.GND, pir_C1.-, pir_LED_R.K, pir_LED_V.K, pir_PIR.GND, puerta_C1.-, puerta_LED_R.K, puerta_LED_V.K, puerta_Reed.2
```

### `anaquel`: Estación del anaquel (acel + luz)

```text
Dibuja en una protoboard de 830 puntos el circuito 'anaquel' EXACTAMENTE como se describe.
No agregues, quites ni muevas componentes. No cambies pines ni valores.

PROTOBOARD: 830 puntos, 63 columnas (1 a 63) y filas a-e / f-j separadas por el canal central.
Rieles: arriba (junto a la fila a) interior = +5V, exterior = GND.
        abajo (junto a la fila j) interior = +3.3V, exterior = GND.
Los 4 rieles están PARTIDOS entre las columnas 31 y 32. 5V y GND se unen con puentes; el de 3.3V NO se une (cada placa tiene su propio 3.3V).

PLACA NodeMCU_acel: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas 1-15, puerto micro-USB hacia la columna 1.
  Fila b (col. 1 a 15): VIN, GND, RST, EN, 3V3, GND, CLK, SD0, CMD, SD1, SD2, SD3, RSV, RSV, A0.
  Fila i (col. 1 a 15): 3V3, GND, TX, RX, D8, D7, D6, D5, GND, 3V3, D4, D3, D2, D1, D0.
PLACA NodeMCU_luz: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas 34-48, puerto micro-USB hacia la columna 34.
  Fila b (col. 34 a 48): VIN, GND, RST, EN, 3V3, GND, CLK, SD0, CMD, SD1, SD2, SD3, RSV, RSV, A0.
  Fila i (col. 34 a 48): 3V3, GND, TX, RX, D8, D7, D6, D5, GND, 3V3, D4, D3, D2, D1, D0.

COMPONENTES EN LA PROTOBOARD:
  - acel_C1 (220 µF / 16 V electrolítico): pin + en riel superior interior (+5V), junto a la columna 3; pin - en riel superior exterior (GND), junto a la columna 3. Polaridad: pata larga (+) al riel 5V; franja (−) al riel GND
  - acel_R5 (330 Ω): pin 1 en g19; pin 2 en d19. Cruza el canal (filas g→d). LED verde
  - acel_R6 (330 Ω): pin 1 en g30; pin 2 en d30. Cruza el canal (filas g→d). LED rojo
  - acel_ADS1115 (ADS1115 (breakout 10 pines)): pin VDD en c20; pin GND en c21; pin SCL en c22; pin SDA en c23; pin ADDR en c24; pin ALRT en c25; pin A0 en c26; pin A1 en c27; pin A2 en c28; pin A3 en c29. Tira de 10 pines en la fila c, columnas 20–29, componentes hacia la fila a [orden de pines POR CONFIRMAR]
  - acel_GY61 (GY-61 (ADXL335)): pin VCC en h25; pin X en h26; pin Y en h27; pin Z en h28; pin GND en h29. Tira de 5 pines en la fila h, columnas 25–29, componentes hacia la fila j [orden POR CONFIRMAR]
  - luz_C1 (220 µF / 16 V electrolítico): pin + en riel superior interior (+5V), junto a la columna 36; pin - en riel superior exterior (GND), junto a la columna 36. Polaridad: pata larga (+) al riel 5V; franja (−) al riel GND
  - luz_R5 (330 Ω): pin 1 en g53; pin 2 en d53. Cruza el canal (filas g→d). LED verde
  - luz_R6 (330 Ω): pin 1 en g55; pin 2 en d55. Cruza el canal (filas g→d). LED rojo
  - luz_R2 (10 kΩ): pin 1 en a58; pin 2 en riel superior exterior (GND), junto a la columna 58. Del divisor a GND. De pie entre a58 y el riel GND. Valor final según docs/prueba_ldr.md (4.7–47 kΩ; no cambia pines)

PUENTES (cable corto rígido, color indicado):
  - de a1 a riel superior interior (+5V), junto a la columna 1, color rojo ([acel] VIN (5 V del USB) → riel 5V).
  - de a2 a riel superior exterior (GND), junto a la columna 2, color negro ([acel] GND → riel GND lado A).
  - de j1 a riel inferior interior (+3.3V), junto a la columna 1, color naranja ([acel] 3V3 → riel 3V3).
  - de j2 a riel inferior exterior (GND), junto a la columna 2, color negro ([acel] GND → riel GND lado J).
  - de j6 a h19, color cafe ([acel] D7 → columna 19 (LED verde), por fuera de la fila j).
  - de j5 a h30, color morado ([acel] D8 → columna 30 (LED rojo), por fuera de la fila j).
  - de j14 a h22, color azul ([acel] D1/SCL → columna 22, por fuera de la fila j).
  - de j13 a h23, color verde ([acel] D2/SDA → columna 23, por fuera de la fila j).
  - de f22 a e22, color azul ([acel] SCL cruza el canal hacia el ADS1115).
  - de f23 a e23, color verde ([acel] SDA cruza el canal hacia el ADS1115).
  - de e20 a f20, color naranja ([acel] VDD del ADS1115 cruza el canal).
  - de j20 a riel inferior interior (+3.3V), junto a la columna 20, color naranja ([acel] VDD del ADS1115 → riel 3V3).
  - de a21 a riel superior exterior (GND), junto a la columna 21, color negro ([acel] GND del ADS1115 → riel GND).
  - de a24 a riel superior exterior (GND), junto a la columna 24, color negro ([acel] ADDR → GND (dirección 0x48)).
  - de j25 a riel inferior interior (+3.3V), junto a la columna 25, color naranja ([acel] VCC del GY-61 → riel 3V3).
  - de j29 a riel inferior exterior (GND), junto a la columna 29, color negro ([acel] GND del GY-61 → riel GND).
  - de f26 a e26, color blanco ([acel] X del GY-61 → A0 del ADS1115).
  - de f27 a e27, color gris ([acel] Y del GY-61 → A1 del ADS1115).
  - de f28 a e28, color cafe ([acel] Z del GY-61 → A2 del ADS1115).
  - de a34 a riel superior interior (+5V), junto a la columna 34, color rojo ([luz] VIN (5 V del USB) → riel 5V).
  - de a35 a riel superior exterior (GND), junto a la columna 35, color negro ([luz] GND → riel GND lado A).
  - de j34 a riel inferior interior (+3.3V), junto a la columna 34, color naranja ([luz] 3V3 → riel 3V3).
  - de j35 a riel inferior exterior (GND), junto a la columna 35, color negro ([luz] GND → riel GND lado J).
  - de j39 a h53, color cafe ([luz] D7 → columna 53 (LED verde), por fuera de la fila j).
  - de j38 a h55, color morado ([luz] D8 → columna 55 (LED rojo), por fuera de la fila j).
  - de a48 a b58, color amarillo ([luz] A0 → columna 58 (divisor), por fuera de la fila a).
  - de riel superior interior (+5V), junto a la columna 31 a riel superior interior (+5V), junto a la columna 33, color rojo (Une el riel 5V partido (las dos mitades comparten la fuente)).
  - de riel superior exterior (GND), junto a la columna 31 a riel superior exterior (GND), junto a la columna 33, color negro (Une el riel GND superior partido).
  - de riel inferior exterior (GND), junto a la columna 31 a riel inferior exterior (GND), junto a la columna 33, color negro (Une el riel GND inferior partido. El riel 3V3 NO se une).

MÓDULOS FUERA DE LA PROTOBOARD (cable Dupont macho-hembra desde el orificio indicado):
  - LED verde de 5 mm: A ← a19 (cable verde); K ← riel superior exterior (GND), junto a la columna 18 (cable negro).
  - LED rojo de 5 mm: A ← a30 (cable rojo); K ← riel superior exterior (GND), junto a la columna 30 (cable negro).
  - LED verde de 5 mm: A ← a53 (cable verde); K ← riel superior exterior (GND), junto a la columna 52 (cable negro).
  - LED rojo de 5 mm: A ← a55 (cable rojo); K ← riel superior exterior (GND), junto a la columna 56 (cable negro).
  - fotorresistencia (LDR) de 5 mm: 1 ← c58 (cable amarillo); 2 ← riel inferior interior (+3.3V), junto a la columna 58 (cable naranja).
  - módulo de entrada USB-C a terminales (+5V, GND): + ← riel superior interior (+5V), junto a la columna 32 (cable rojo); - ← riel superior exterior (GND), junto a la columna 32 (cable negro).

REDES QUE DEBEN QUEDAR CONECTADAS (para verificar):
  - acel_D7: NodeMCU_acel.D7, acel_R5.1
  - acel_LED_V: acel_LED_V.A, acel_R5.2
  - acel_D8: NodeMCU_acel.D8, acel_R6.1
  - acel_LED_R: acel_LED_R.A, acel_R6.2
  - acel_3V3: NodeMCU_acel.3V3, acel_ADS1115.VDD, acel_GY61.VCC
  - acel_SCL: NodeMCU_acel.D1, acel_ADS1115.SCL
  - acel_SDA: NodeMCU_acel.D2, acel_ADS1115.SDA
  - acel_X: acel_ADS1115.A0, acel_GY61.X
  - acel_Y: acel_ADS1115.A1, acel_GY61.Y
  - acel_Z: acel_ADS1115.A2, acel_GY61.Z
  - luz_D7: NodeMCU_luz.D7, luz_R5.1
  - luz_LED_V: luz_LED_V.A, luz_R5.2
  - luz_D8: NodeMCU_luz.D8, luz_R6.1
  - luz_LED_R: luz_LED_R.A, luz_R6.2
  - luz_A0: NodeMCU_luz.A0, luz_LDR.1, luz_R2.1
  - luz_3V3: NodeMCU_luz.3V3, luz_LDR.2
  - 5V: Entrada5V.+, NodeMCU_acel.VIN, NodeMCU_luz.VIN, acel_C1.+, luz_C1.+
  - GND: Entrada5V.-, NodeMCU_acel.GND, NodeMCU_luz.GND, acel_ADS1115.ADDR, acel_ADS1115.GND, acel_C1.-, acel_GY61.GND, acel_LED_R.K, acel_LED_V.K, luz_C1.-, luz_LED_R.K, luz_LED_V.K, luz_R2.2
```
