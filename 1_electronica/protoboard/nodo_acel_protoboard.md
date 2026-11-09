# Nodo `acel (GY-61 + ADS1115)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [nodo_acel_protoboard.svg](nodo_acel_protoboard.svg) / [png](nodo_acel_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

ADS1115 y GY-61 **clavados en la protoboard** (tiras de pines, de pie) para que vibren con ella; una costilla de la tapa sujeta su borde superior. ADS1115 en I²C (D1 SCL, D2 SDA, 0x48 con ADDR a GND). GY-61 X/Y/Z → A0/A1/A2. Componentes del ADS1115 hacia la fila a y del GY-61 hacia la fila j. LED en las columnas 19 y 30.

## Convenciones

- Protoboard de 400 puntos: columnas 1–30, filas a–e y f–j (cada columna de 5 está unida), canal central.
- Rieles del lado A (junto a la fila a): **5V/VIN interior**, **GND exterior**. Rieles del lado J: **3V3 interior**, **GND exterior**. Rotularlos con cinta.
- NodeMCU Amica con el micro-USB hacia la columna 1; pines en las filas **b** (lado A0/VIN) e **i** (lado D0–D8). Cada pin deja **un solo orificio libre** (fila a o j).
- Puentes cortos con cable UTP sólido; módulos fuera de la placa con Dupont macho-hembra del kit.

## Componentes

| Ref. | Valor | Orificios | Polaridad / nota |
|---|---|---|---|
| C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 3), -: riel A GND (junto a col. 3) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| R5 | 330 Ω | 1: g19, 2: d19 | Cruza el canal (filas g→d). LED verde |
| R6 | 330 Ω | 1: g30, 2: d30 | Cruza el canal (filas g→d). LED rojo |
| ADS1115 | ADS1115 (breakout 10 pines) | VDD: c20, GND: c21, SCL: c22, SDA: c23, ADDR: c24, ALRT: c25, A0: c26, A1: c27, A2: c28, A3: c29 | Tira de 10 pines en la fila c, columnas 20–29, componentes hacia la fila a [orden de pines POR CONFIRMAR] |
| GY61 | GY-61 (ADXL335) | VCC: h25, X: h26, Y: h27, Z: h28, GND: h29 | Tira de 5 pines en la fila h, columnas 25–29, componentes hacia la fila j [orden POR CONFIRMAR] |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado J |
| 5 | j6 | h19 | cafe | 50 mm | D7 → columna 19 (LED verde), por fuera de la fila j |
| 6 | j5 | h30 | morado | 80 mm | D8 → columna 30 (LED rojo), por fuera de la fila j |
| 7 | j14 | h22 | azul | 40 mm | D1/SCL → columna 22, por fuera de la fila j |
| 8 | j13 | h23 | verde | 45 mm | D2/SDA → columna 23, por fuera de la fila j |
| 9 | f22 | e22 | azul | 20 mm | SCL cruza el canal hacia el ADS1115 |
| 10 | f23 | e23 | verde | 20 mm | SDA cruza el canal hacia el ADS1115 |
| 11 | e20 | f20 | naranja | 20 mm | VDD del ADS1115 cruza el canal |
| 12 | j20 | riel J 3V3 (junto a col. 20) | naranja | 15 mm | VDD del ADS1115 → riel 3V3 |
| 13 | a21 | riel A GND (junto a col. 21) | negro | 20 mm | GND del ADS1115 → riel GND |
| 14 | a24 | riel A GND (junto a col. 24) | negro | 20 mm | ADDR → GND (dirección 0x48) |
| 15 | j25 | riel J 3V3 (junto a col. 25) | naranja | 15 mm | VCC del GY-61 → riel 3V3 |
| 16 | j29 | riel J GND (junto a col. 29) | negro | 20 mm | GND del GY-61 → riel GND |
| 17 | f26 | e26 | blanco | 20 mm | X del GY-61 → A0 del ADS1115 |
| 18 | f27 | e27 | gris | 20 mm | Y del GY-61 → A1 del ADS1115 |
| 19 | f28 | e28 | cafe | 20 mm | Z del GY-61 → A2 del ADS1115 |
| 20 | a19 | LED_V · A | verde | Dupont 10–20 cm | Ánodo del LED verde, en la tapa |
| 21 | riel A GND (junto a col. 18) | LED_V · K | negro | Dupont 10–20 cm | Cátodo |
| 22 | a30 | LED_R · A | rojo | Dupont 10–20 cm | Ánodo del LED rojo, en la tapa |
| 23 | riel A GND (junto a col. 30) | LED_R · K | negro | Dupont 10–20 cm | Cátodo |

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
| j5 | puente → h30 |
| j6 | puente → h19 |
| j13 | puente → h23 |
| j14 | puente → h22 |
| riel A GND (junto a col. 18) | LED_V.K |
| a19 | LED_V.A |
| d19 | R5.2 |
| g19 | R5.1 |
| h19 | puente ← j6 |
| riel J 3V3 (junto a col. 20) | puente ← j20 |
| c20 | ADS1115.VDD |
| e20 | puente → f20 |
| f20 | puente ← e20 |
| j20 | puente → J_3V3:20 |
| riel A GND (junto a col. 21) | puente ← a21 |
| a21 | puente → A_GND:21 |
| c21 | ADS1115.GND |
| c22 | ADS1115.SCL |
| e22 | puente ← f22 |
| f22 | puente → e22 |
| h22 | puente ← j14 |
| c23 | ADS1115.SDA |
| e23 | puente ← f23 |
| f23 | puente → e23 |
| h23 | puente ← j13 |
| riel A GND (junto a col. 24) | puente ← a24 |
| a24 | puente → A_GND:24 |
| c24 | ADS1115.ADDR |
| riel J 3V3 (junto a col. 25) | puente ← j25 |
| c25 | ADS1115.ALRT |
| h25 | GY61.VCC |
| j25 | puente → J_3V3:25 |
| c26 | ADS1115.A0 |
| e26 | puente ← f26 |
| f26 | puente → e26 |
| h26 | GY61.X |
| c27 | ADS1115.A1 |
| e27 | puente ← f27 |
| f27 | puente → e27 |
| h27 | GY61.Y |
| c28 | ADS1115.A2 |
| e28 | puente ← f28 |
| f28 | puente → e28 |
| h28 | GY61.Z |
| riel J GND (junto a col. 29) | puente ← j29 |
| c29 | ADS1115.A3 |
| h29 | GY61.GND |
| j29 | puente → J_GND:29 |
| riel A GND (junto a col. 30) | LED_R.K |
| a30 | LED_R.A |
| d30 | R6.2 |
| g30 | R6.1 |
| h30 | puente ← j5 |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| X | ADS1115.A0, GY61.X |
| Y | ADS1115.A1, GY61.Y |
| Z | ADS1115.A2, GY61.Z |
| GND | ADS1115.ADDR, ADS1115.GND, C1.-, GY61.GND, LED_R.K, LED_V.K, NodeMCU.GND |
| SCL | ADS1115.SCL, NodeMCU.D1 |
| SDA | ADS1115.SDA, NodeMCU.D2 |
| 3V3 | ADS1115.VDD, GY61.VCC, NodeMCU.3V3 |
| 5V | C1.+, NodeMCU.VIN |
| LED_R | LED_R.A, R6.2 |
| LED_V | LED_V.A, R5.2 |
| D7 | NodeMCU.D7, R5.1 |
| D8 | NodeMCU.D8, R6.1 |

## Chequeo automático

✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las redes coinciden con la red esperada.

## Verificación eléctrica (por escrito, sin simulador)

| Punto | Cálculo | Resultado |
|---|---|---|
| GY-61 a 3V3 | Salidas ratiométricas: 0 g ≈ 1.65 V, ≈ 0.33 V/g; rango ±3 g → 0.66–2.64 V | ✔ Nunca superan 3.3 V |
| ADS1115 a 3V3 | Entradas válidas de −0.3 a VDD + 0.3 V; ganancia ±4.096 V (GAIN_ONE) | ✔ Resolución 0.125 mV ≈ 0.4 mg |
| I²C | Pull-ups del breakout (≈ 10 kΩ) a 3V3 | ✔ Sin resistencias extra |
| Consumo | ADXL335 ≈ 0.35 mA + ADS1115 ≈ 0.2 mA | ✔ Despreciable |
| D1/D2 | GPIO5/GPIO4 sin función de arranque | ✔ |
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
