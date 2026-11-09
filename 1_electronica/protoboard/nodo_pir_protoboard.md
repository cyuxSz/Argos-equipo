# Nodo `pir (HC-SR501)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [nodo_pir_protoboard.svg](nodo_pir_protoboard.svg) / [png](nodo_pir_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

HC-SR501 a 5 V (VIN); su salida OUT es de 3.3 V y entra directo a **D5**.

## Convenciones

- Protoboard de 400 puntos: columnas 1–30, filas a–e y f–j (cada columna de 5 está unida), canal central.
- Rieles del lado A (junto a la fila a): **5V/VIN interior**, **GND exterior**. Rieles del lado J: **3V3 interior**, **GND exterior**. Rotularlos con cinta.
- NodeMCU Amica con el micro-USB hacia la columna 1; pines en las filas **b** (lado A0/VIN) e **i** (lado D0–D8). Cada pin deja **un solo orificio libre** (fila a o j).
- Puentes cortos con cable UTP sólido; módulos fuera de la placa con Dupont macho-hembra del kit.

## Componentes

| Ref. | Valor | Orificios | Polaridad / nota |
|---|---|---|---|
| C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 3), -: riel A GND (junto a col. 3) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| R5 | 330 Ω | 1: g20, 2: d20 | Cruza el canal (filas g→d). LED verde |
| R6 | 330 Ω | 1: g22, 2: d22 | Cruza el canal (filas g→d). LED rojo |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado J |
| 5 | j6 | h20 | cafe | 55 mm | D7 → columna 20 (LED verde), por fuera de la fila j |
| 6 | j5 | h22 | morado | 60 mm | D8 → columna 22 (LED rojo), por fuera de la fila j |
| 7 | j8 | h27 | blanco | 70 mm | D5 → columna 27 (OUT del PIR), por fuera de la fila j |
| 8 | a20 | LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 9 | riel A GND (junto a col. 19) | LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 10 | a22 | LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 11 | riel A GND (junto a col. 23) | LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 12 | riel A 5V (junto a col. 28) | PIR · VCC | rojo | Dupont 10–20 cm | HC-SR501 en la tapa; pinout VCC-OUT-GND [verificar serigrafía] |
| 13 | f27 | PIR · OUT | blanco | Dupont 10–20 cm |  |
| 14 | riel A GND (junto a col. 28) | PIR · GND | negro | Dupont 10–20 cm |  |

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
| riel A 5V (junto a col. 3) | C1.+ |
| riel A GND (junto a col. 3) | C1.- |
| j5 | puente → h22 |
| j6 | puente → h20 |
| j8 | puente → h27 |
| riel A GND (junto a col. 19) | LED_V.K |
| a20 | LED_V.A |
| d20 | R5.2 |
| g20 | R5.1 |
| h20 | puente ← j6 |
| a22 | LED_R.A |
| d22 | R6.2 |
| g22 | R6.1 |
| h22 | puente ← j5 |
| riel A GND (junto a col. 23) | LED_R.K |
| f27 | PIR.OUT |
| h27 | puente ← j8 |
| riel A 5V (junto a col. 28) | PIR.VCC |
| riel A GND (junto a col. 28) | PIR.GND |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| 5V | C1.+, NodeMCU.VIN, PIR.VCC |
| GND | C1.-, LED_R.K, LED_V.K, NodeMCU.GND, PIR.GND |
| LED_R | LED_R.A, R6.2 |
| LED_V | LED_V.A, R5.2 |
| D5 | NodeMCU.D5, PIR.OUT |
| D7 | NodeMCU.D7, R5.1 |
| D8 | NodeMCU.D8, R6.1 |

## Chequeo automático

✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las redes coinciden con la red esperada.

## Verificación eléctrica (por escrito, sin simulador)

| Punto | Cálculo | Resultado |
|---|---|---|
| Alimentación del PIR | VIN ≈ 4.7 V; el HC-SR501 acepta 4.5–20 V | ✔ Justo arriba del mínimo: medir VIN con el nodo armado (P-02) |
| OUT → D5 | Salida de 3.3 V del regulador interno del módulo | ✔ Sin divisor. Medir que no pase de 3.3 V (P-02) |
| Consumo | HC-SR501 ≈ 65 µA en reposo | ✔ Despreciable |
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
