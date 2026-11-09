# Nodo `Estación de entrada (pir + puerta)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [estacion_entrada_protoboard.svg](estacion_entrada_protoboard.svg) / [png](estacion_entrada_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

Dos nodos independientes en una MB-102 de 830 puntos: **pir** en las columnas 1–30 y **puerta** en las 34–63. Comparten la fuente (módulo USB-C) y la GND; cada placa conserva su propio 3V3.

## Convenciones

- Protoboard de 830 puntos: columnas 1–63, filas a–e y f–j (cada columna de 5 está unida), canal central.
- Rieles del lado A (junto a la fila a): **5V/VIN interior**, **GND exterior**. Rieles del lado J: **3V3 interior**, **GND exterior**. Rotularlos con cinta.
- NodeMCU Amica con el micro-USB hacia la columna 1; pines en las filas **b** (lado A0/VIN) e **i** (lado D0–D8). Cada pin deja **un solo orificio libre** (fila a o j).
- Puentes cortos con cable UTP sólido; módulos fuera de la placa con Dupont macho-hembra del kit.

## Componentes

| Ref. | Valor | Orificios | Polaridad / nota |
|---|---|---|---|
| pir_C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 3), -: riel A GND (junto a col. 3) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| pir_R5 | 330 Ω | 1: g20, 2: d20 | Cruza el canal (filas g→d). LED verde |
| pir_R6 | 330 Ω | 1: g22, 2: d22 | Cruza el canal (filas g→d). LED rojo |
| puerta_C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 36), -: riel A GND (junto a col. 36) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| puerta_R5 | 330 Ω | 1: g53, 2: d53 | Cruza el canal (filas g→d). LED verde |
| puerta_R6 | 330 Ω | 1: g55, 2: d55 | Cruza el canal (filas g→d). LED rojo |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | [pir] VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | [pir] GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | [pir] 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | [pir] GND → riel GND lado J |
| 5 | j6 | h20 | cafe | 55 mm | [pir] D7 → columna 20 (LED verde), por fuera de la fila j |
| 6 | j5 | h22 | morado | 60 mm | [pir] D8 → columna 22 (LED rojo), por fuera de la fila j |
| 7 | j8 | h27 | blanco | 70 mm | [pir] D5 → columna 27 (OUT del PIR), por fuera de la fila j |
| 8 | a34 | riel A 5V (junto a col. 34) | rojo | 15 mm | [puerta] VIN (5 V del USB) → riel 5V |
| 9 | a35 | riel A GND (junto a col. 35) | negro | 20 mm | [puerta] GND → riel GND lado A |
| 10 | j34 | riel J 3V3 (junto a col. 34) | naranja | 15 mm | [puerta] 3V3 → riel 3V3 |
| 11 | j35 | riel J GND (junto a col. 35) | negro | 20 mm | [puerta] GND → riel GND lado J |
| 12 | j39 | h53 | cafe | 55 mm | [puerta] D7 → columna 53 (LED verde), por fuera de la fila j |
| 13 | j38 | h55 | morado | 60 mm | [puerta] D8 → columna 55 (LED rojo), por fuera de la fila j |
| 14 | j41 | h60 | blanco | 70 mm | [puerta] D5 → columna 60 (reed), por fuera de la fila j |
| 15 | riel A 5V (junto a col. 31) | riel A 5V (junto a col. 33) | rojo | 15 mm | Une el riel 5V partido (las dos mitades comparten la fuente) |
| 16 | riel A GND (junto a col. 31) | riel A GND (junto a col. 33) | negro | 15 mm | Une el riel GND superior partido |
| 17 | riel J GND (junto a col. 31) | riel J GND (junto a col. 33) | negro | 15 mm | Une el riel GND inferior partido. El riel 3V3 NO se une |
| 18 | a20 | pir_LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 19 | riel A GND (junto a col. 19) | pir_LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 20 | a22 | pir_LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 21 | riel A GND (junto a col. 23) | pir_LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 22 | riel A 5V (junto a col. 28) | pir_PIR · VCC | rojo | Dupont 10–20 cm | HC-SR501 en la tapa; pinout VCC-OUT-GND [verificar serigrafía] |
| 23 | f27 | pir_PIR · OUT | blanco | Dupont 10–20 cm |  |
| 24 | riel A GND (junto a col. 28) | pir_PIR · GND | negro | Dupont 10–20 cm |  |
| 25 | a53 | puerta_LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 26 | riel A GND (junto a col. 52) | puerta_LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 27 | a55 | puerta_LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 28 | riel A GND (junto a col. 56) | puerta_LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 29 | f60 | puerta_Reed · 1 | blanco | cable del MC-38 | Cable del MC-38 (≈ 30 cm) con terminal Dupont macho crimpado |
| 30 | riel J GND (junto a col. 60) | puerta_Reed · 2 | negro | cable del MC-38 | Sin polaridad |
| 31 | riel A 5V (junto a col. 32) | Entrada5V · + | rojo | cable corto | Módulo de entrada USB-C a terminales (5 V de la fuente de la caja) |
| 32 | riel A GND (junto a col. 32) | Entrada5V · - | negro | cable corto |  |

## Mapa de orificios

| Orificio | Qué entra |
|---|---|
| riel A 5V (junto a col. 1) | puente ← a1 |
| riel J 3V3 (junto a col. 1) | puente ← j1 |
| a1 | puente → A_5V:1 |
| j1 | puente → J_3V3:1 |
| riel A GND (junto a col. 2) | puente ← a2 |
| riel J GND (junto a col. 2) | puente ← j2 |
| a2 | puente → A_GND:2 |
| j2 | puente → J_GND:2 |
| riel A 5V (junto a col. 3) | pir_C1.+ |
| riel A GND (junto a col. 3) | pir_C1.- |
| j5 | puente → h22 |
| j6 | puente → h20 |
| j8 | puente → h27 |
| riel A GND (junto a col. 19) | pir_LED_V.K |
| a20 | pir_LED_V.A |
| d20 | pir_R5.2 |
| g20 | pir_R5.1 |
| h20 | puente ← j6 |
| a22 | pir_LED_R.A |
| d22 | pir_R6.2 |
| g22 | pir_R6.1 |
| h22 | puente ← j5 |
| riel A GND (junto a col. 23) | pir_LED_R.K |
| f27 | pir_PIR.OUT |
| h27 | puente ← j8 |
| riel A 5V (junto a col. 28) | pir_PIR.VCC |
| riel A GND (junto a col. 28) | pir_PIR.GND |
| riel A 5V (junto a col. 31) | puente → A_5V:33 |
| riel A GND (junto a col. 31) | puente → A_GND:33 |
| riel J GND (junto a col. 31) | puente → J_GND:33 |
| riel A 5V (junto a col. 32) | Entrada5V.+ |
| riel A GND (junto a col. 32) | Entrada5V.- |
| riel A 5V (junto a col. 33) | puente ← A_5V:31 |
| riel A GND (junto a col. 33) | puente ← A_GND:31 |
| riel J GND (junto a col. 33) | puente ← J_GND:31 |
| riel A 5V (junto a col. 34) | puente ← a34 |
| riel J 3V3 (junto a col. 34) | puente ← j34 |
| a34 | puente → A_5V:34 |
| j34 | puente → J_3V3:34 |
| riel A GND (junto a col. 35) | puente ← a35 |
| riel J GND (junto a col. 35) | puente ← j35 |
| a35 | puente → A_GND:35 |
| j35 | puente → J_GND:35 |
| riel A 5V (junto a col. 36) | puerta_C1.+ |
| riel A GND (junto a col. 36) | puerta_C1.- |
| j38 | puente → h55 |
| j39 | puente → h53 |
| j41 | puente → h60 |
| riel A GND (junto a col. 52) | puerta_LED_V.K |
| a53 | puerta_LED_V.A |
| d53 | puerta_R5.2 |
| g53 | puerta_R5.1 |
| h53 | puente ← j39 |
| a55 | puerta_LED_R.A |
| d55 | puerta_R6.2 |
| g55 | puerta_R6.1 |
| h55 | puente ← j38 |
| riel A GND (junto a col. 56) | puerta_LED_R.K |
| riel J GND (junto a col. 60) | puerta_Reed.2 |
| f60 | puerta_Reed.1 |
| h60 | puente ← j41 |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| 5V | Entrada5V.+, NodeMCU_pir.VIN, NodeMCU_puerta.VIN, pir_C1.+, pir_PIR.VCC, puerta_C1.+ |
| GND | Entrada5V.-, NodeMCU_pir.GND, NodeMCU_puerta.GND, pir_C1.-, pir_LED_R.K, pir_LED_V.K, pir_PIR.GND, puerta_C1.-, puerta_LED_R.K, puerta_LED_V.K, puerta_Reed.2 |
| pir_D5 | NodeMCU_pir.D5, pir_PIR.OUT |
| pir_D7 | NodeMCU_pir.D7, pir_R5.1 |
| pir_D8 | NodeMCU_pir.D8, pir_R6.1 |
| puerta_D5 | NodeMCU_puerta.D5, puerta_Reed.1 |
| puerta_D7 | NodeMCU_puerta.D7, puerta_R5.1 |
| puerta_D8 | NodeMCU_puerta.D8, puerta_R6.1 |
| pir_LED_R | pir_LED_R.A, pir_R6.2 |
| pir_LED_V | pir_LED_V.A, pir_R5.2 |
| puerta_LED_R | puerta_LED_R.A, puerta_R6.2 |
| puerta_LED_V | puerta_LED_V.A, puerta_R5.2 |

## Chequeo automático

✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las redes coinciden con la red esperada.

## Verificación eléctrica (por escrito, sin simulador)

| Punto | Cálculo | Resultado |
|---|---|---|
| Alimentación compartida | Una fuente de 5 V ≥ 2 A (una por caja) entra por el módulo USB-C al riel 5V; cada NodeMCU recibe 5 V por su pin VIN | ✔ Consumo de la estación ≈ 0.1–0.2 A promedio, picos de WiFi ≈ 0.6 A |
| VIN directo | Alimentar por VIN salta el diodo del USB de la placa: los módulos de 5 V reciben ≈ 5.0 V en lugar de ≈ 4.7 V | ✔ Mejor margen para el HC-SR501 (mínimo 4.5 V) |
| 3V3 separado | Cada NodeMCU tiene su propio regulador; unir sus salidas los pondría a pelear | ✔ El riel 3V3 queda partido entre las columnas 31 y 32. **Verificar con el multímetro; si la protoboard trae el riel continuo, cortarlo** |
| Flasheo | Conectar la PC al micro-USB de una placa con la estación energizada es seguro: el diodo de la placa evita el retorno hacia la PC | ✔ La placa de arriba tiene su USB hacia el techo de la caja |
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
