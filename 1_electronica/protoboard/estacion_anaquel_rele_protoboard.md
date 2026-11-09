# Nodo `Estación del anaquel con relés (submódulo opcional)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [estacion_anaquel_rele_protoboard.svg](estacion_anaquel_rele_protoboard.svg) / [png](estacion_anaquel_rele_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

Igual que la estación del anaquel, pero el nodo luz usa la variante **luz_rele**: D1/D2/D5 salen por un cable de 6 hilos a la caja de potencia del fotoperiodo (docs/caja_potencia_luz.md).

## Convenciones

- Protoboard de 830 puntos: columnas 1–63, filas a–e y f–j (cada columna de 5 está unida), canal central.
- Rieles del lado A (junto a la fila a): **5V/VIN interior**, **GND exterior**. Rieles del lado J: **3V3 interior**, **GND exterior**. Rotularlos con cinta.
- NodeMCU Amica con el micro-USB hacia la columna 1; pines en las filas **b** (lado A0/VIN) e **i** (lado D0–D8). Cada pin deja **un solo orificio libre** (fila a o j).
- Puentes cortos con cable UTP sólido; módulos fuera de la placa con Dupont macho-hembra del kit.

## Componentes

| Ref. | Valor | Orificios | Polaridad / nota |
|---|---|---|---|
| acel_C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 3), -: riel A GND (junto a col. 3) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| acel_R5 | 330 Ω | 1: g19, 2: d19 | Cruza el canal (filas g→d). LED verde |
| acel_R6 | 330 Ω | 1: g30, 2: d30 | Cruza el canal (filas g→d). LED rojo |
| acel_ADS1115 | ADS1115 (breakout 10 pines) | VDD: c20, GND: c21, SCL: c22, SDA: c23, ADDR: c24, ALRT: c25, A0: c26, A1: c27, A2: c28, A3: c29 | Tira de 10 pines en la fila c, columnas 20–29, componentes hacia la fila a [orden de pines POR CONFIRMAR] |
| acel_GY61 | GY-61 (ADXL335) | VCC: h25, X: h26, Y: h27, Z: h28, GND: h29 | Tira de 5 pines en la fila h, columnas 25–29, componentes hacia la fila j [orden POR CONFIRMAR] |
| luz_rele_C1 | 220 µF / 16 V electrolítico | +: riel A 5V (junto a col. 36), -: riel A GND (junto a col. 36) | **Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND |
| luz_rele_R5 | 330 Ω | 1: g53, 2: d53 | Cruza el canal (filas g→d). LED verde |
| luz_rele_R6 | 330 Ω | 1: g55, 2: d55 | Cruza el canal (filas g→d). LED rojo |
| luz_rele_R2 | 10 kΩ | 1: a58, 2: riel A GND (junto a col. 58) | Del divisor a GND. De pie entre a58 y el riel GND. Valor final según docs/prueba_ldr.md (4.7–47 kΩ; no cambia pines) |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | [acel] VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | [acel] GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | [acel] 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | [acel] GND → riel GND lado J |
| 5 | j6 | h19 | cafe | 50 mm | [acel] D7 → columna 19 (LED verde), por fuera de la fila j |
| 6 | j5 | h30 | morado | 80 mm | [acel] D8 → columna 30 (LED rojo), por fuera de la fila j |
| 7 | j14 | h22 | azul | 40 mm | [acel] D1/SCL → columna 22, por fuera de la fila j |
| 8 | j13 | h23 | verde | 45 mm | [acel] D2/SDA → columna 23, por fuera de la fila j |
| 9 | f22 | e22 | azul | 20 mm | [acel] SCL cruza el canal hacia el ADS1115 |
| 10 | f23 | e23 | verde | 20 mm | [acel] SDA cruza el canal hacia el ADS1115 |
| 11 | e20 | f20 | naranja | 20 mm | [acel] VDD del ADS1115 cruza el canal |
| 12 | j20 | riel J 3V3 (junto a col. 20) | naranja | 15 mm | [acel] VDD del ADS1115 → riel 3V3 |
| 13 | a21 | riel A GND (junto a col. 21) | negro | 20 mm | [acel] GND del ADS1115 → riel GND |
| 14 | a24 | riel A GND (junto a col. 24) | negro | 20 mm | [acel] ADDR → GND (dirección 0x48) |
| 15 | j25 | riel J 3V3 (junto a col. 25) | naranja | 15 mm | [acel] VCC del GY-61 → riel 3V3 |
| 16 | j29 | riel J GND (junto a col. 29) | negro | 20 mm | [acel] GND del GY-61 → riel GND |
| 17 | f26 | e26 | blanco | 20 mm | [acel] X del GY-61 → A0 del ADS1115 |
| 18 | f27 | e27 | gris | 20 mm | [acel] Y del GY-61 → A1 del ADS1115 |
| 19 | f28 | e28 | cafe | 20 mm | [acel] Z del GY-61 → A2 del ADS1115 |
| 20 | a34 | riel A 5V (junto a col. 34) | rojo | 15 mm | [luz_rele] VIN (5 V del USB) → riel 5V |
| 21 | a35 | riel A GND (junto a col. 35) | negro | 20 mm | [luz_rele] GND → riel GND lado A |
| 22 | j34 | riel J 3V3 (junto a col. 34) | naranja | 15 mm | [luz_rele] 3V3 → riel 3V3 |
| 23 | j35 | riel J GND (junto a col. 35) | negro | 20 mm | [luz_rele] GND → riel GND lado J |
| 24 | j39 | h53 | cafe | 55 mm | [luz_rele] D7 → columna 53 (LED verde), por fuera de la fila j |
| 25 | j38 | h55 | morado | 60 mm | [luz_rele] D8 → columna 55 (LED rojo), por fuera de la fila j |
| 26 | a48 | b58 | amarillo | 40 mm | [luz_rele] A0 → columna 58 (divisor), por fuera de la fila a |
| 27 | j47 | h61 | azul | 55 mm | [luz_rele] D1 → columna 61 (IN1, plancha 2), por fuera de la fila j |
| 28 | j46 | h62 | verde | 60 mm | [luz_rele] D2 → columna 62 (IN2, plancha 3), por fuera de la fila j |
| 29 | j41 | h63 | blanco | 80 mm | [luz_rele] D5 → columna 63 (IN3, plancha 4), por fuera de la fila j |
| 30 | riel A 5V (junto a col. 31) | riel A 5V (junto a col. 33) | rojo | 15 mm | Une el riel 5V partido (las dos mitades comparten la fuente) |
| 31 | riel A GND (junto a col. 31) | riel A GND (junto a col. 33) | negro | 15 mm | Une el riel GND superior partido |
| 32 | riel J GND (junto a col. 31) | riel J GND (junto a col. 33) | negro | 15 mm | Une el riel GND inferior partido. El riel 3V3 NO se une |
| 33 | a19 | acel_LED_V · A | verde | Dupont 10–20 cm | Ánodo del LED verde, en la tapa |
| 34 | riel A GND (junto a col. 18) | acel_LED_V · K | negro | Dupont 10–20 cm | Cátodo |
| 35 | a30 | acel_LED_R · A | rojo | Dupont 10–20 cm | Ánodo del LED rojo, en la tapa |
| 36 | riel A GND (junto a col. 30) | acel_LED_R · K | negro | Dupont 10–20 cm | Cátodo |
| 37 | a53 | luz_rele_LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 38 | riel A GND (junto a col. 52) | luz_rele_LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 39 | a55 | luz_rele_LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 40 | riel A GND (junto a col. 56) | luz_rele_LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 41 | c58 | luz_rele_LDR · 1 | amarillo | cable de la LDR | LDR en su capuchón remoto (junto a la lámpara); cable de 2 hilos con terminal Dupont macho crimpado |
| 42 | riel J 3V3 (junto a col. 58) | luz_rele_LDR · 2 | naranja | cable de la LDR | Sin polaridad |
| 43 | f61 | luz_rele_Rele · IN1 | azul | cable de señal | Módulo de 4 relés (caja de potencia): IN1 → plancha 2 |
| 44 | f62 | luz_rele_Rele · IN2 | verde | cable de señal | IN2 → plancha 3 |
| 45 | f63 | luz_rele_Rele · IN3 | blanco | cable de señal | IN3 → plancha 4 (IN4 queda libre) |
| 46 | riel J 3V3 (junto a col. 60) | luz_rele_Rele · VCC | naranja | cable de señal | VCC del lado de control (optoacopladores) a **3V3**: con 3.3 V en VCC, un GPIO en alto apaga bien el opto [verificar con el módulo, P-R1] |
| 47 | riel J GND (junto a col. 60) | luz_rele_Rele · GND | negro | cable de señal |  |
| 48 | riel A 5V (junto a col. 62) | luz_rele_Rele · JD-VCC | rojo | cable de señal | Bobinas a 5 V. **Quitar el puente JD-VCC–VCC del módulo** |
| 49 | riel A 5V (junto a col. 32) | Entrada5V · + | rojo | cable corto | Módulo de entrada USB-C a terminales (5 V de la fuente de la caja) |
| 50 | riel A GND (junto a col. 32) | Entrada5V · - | negro | cable corto |  |

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
| riel A 5V (junto a col. 3) | acel_C1.+ |
| riel A GND (junto a col. 3) | acel_C1.- |
| j5 | puente → h30 |
| j6 | puente → h19 |
| j13 | puente → h23 |
| j14 | puente → h22 |
| riel A GND (junto a col. 18) | acel_LED_V.K |
| a19 | acel_LED_V.A |
| d19 | acel_R5.2 |
| g19 | acel_R5.1 |
| h19 | puente ← j6 |
| riel J 3V3 (junto a col. 20) | puente ← j20 |
| c20 | acel_ADS1115.VDD |
| e20 | puente → f20 |
| f20 | puente ← e20 |
| j20 | puente → J_3V3:20 |
| riel A GND (junto a col. 21) | puente ← a21 |
| a21 | puente → A_GND:21 |
| c21 | acel_ADS1115.GND |
| c22 | acel_ADS1115.SCL |
| e22 | puente ← f22 |
| f22 | puente → e22 |
| h22 | puente ← j14 |
| c23 | acel_ADS1115.SDA |
| e23 | puente ← f23 |
| f23 | puente → e23 |
| h23 | puente ← j13 |
| riel A GND (junto a col. 24) | puente ← a24 |
| a24 | puente → A_GND:24 |
| c24 | acel_ADS1115.ADDR |
| riel J 3V3 (junto a col. 25) | puente ← j25 |
| c25 | acel_ADS1115.ALRT |
| h25 | acel_GY61.VCC |
| j25 | puente → J_3V3:25 |
| c26 | acel_ADS1115.A0 |
| e26 | puente ← f26 |
| f26 | puente → e26 |
| h26 | acel_GY61.X |
| c27 | acel_ADS1115.A1 |
| e27 | puente ← f27 |
| f27 | puente → e27 |
| h27 | acel_GY61.Y |
| c28 | acel_ADS1115.A2 |
| e28 | puente ← f28 |
| f28 | puente → e28 |
| h28 | acel_GY61.Z |
| riel J GND (junto a col. 29) | puente ← j29 |
| c29 | acel_ADS1115.A3 |
| h29 | acel_GY61.GND |
| j29 | puente → J_GND:29 |
| riel A GND (junto a col. 30) | acel_LED_R.K |
| a30 | acel_LED_R.A |
| d30 | acel_R6.2 |
| g30 | acel_R6.1 |
| h30 | puente ← j5 |
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
| riel A 5V (junto a col. 36) | luz_rele_C1.+ |
| riel A GND (junto a col. 36) | luz_rele_C1.- |
| j38 | puente → h55 |
| j39 | puente → h53 |
| j41 | puente → h63 |
| j46 | puente → h62 |
| j47 | puente → h61 |
| a48 | puente → b58 |
| riel A GND (junto a col. 52) | luz_rele_LED_V.K |
| a53 | luz_rele_LED_V.A |
| d53 | luz_rele_R5.2 |
| g53 | luz_rele_R5.1 |
| h53 | puente ← j39 |
| a55 | luz_rele_LED_R.A |
| d55 | luz_rele_R6.2 |
| g55 | luz_rele_R6.1 |
| h55 | puente ← j38 |
| riel A GND (junto a col. 56) | luz_rele_LED_R.K |
| riel A GND (junto a col. 58) | luz_rele_R2.2 |
| riel J 3V3 (junto a col. 58) | luz_rele_LDR.2 |
| a58 | luz_rele_R2.1 |
| b58 | puente ← a48 |
| c58 | luz_rele_LDR.1 |
| riel J 3V3 (junto a col. 60) | luz_rele_Rele.VCC |
| riel J GND (junto a col. 60) | luz_rele_Rele.GND |
| f61 | luz_rele_Rele.IN1 |
| h61 | puente ← j47 |
| riel A 5V (junto a col. 62) | luz_rele_Rele.JD-VCC |
| f62 | luz_rele_Rele.IN2 |
| h62 | puente ← j46 |
| f63 | luz_rele_Rele.IN3 |
| h63 | puente ← j41 |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| 5V | Entrada5V.+, NodeMCU_acel.VIN, NodeMCU_luz_rele.VIN, acel_C1.+, luz_rele_C1.+, luz_rele_Rele.JD-VCC |
| GND | Entrada5V.-, NodeMCU_acel.GND, NodeMCU_luz_rele.GND, acel_ADS1115.ADDR, acel_ADS1115.GND, acel_C1.-, acel_GY61.GND, acel_LED_R.K, acel_LED_V.K, luz_rele_C1.-, luz_rele_LED_R.K, luz_rele_LED_V.K, luz_rele_R2.2, luz_rele_Rele.GND |
| acel_3V3 | NodeMCU_acel.3V3, acel_ADS1115.VDD, acel_GY61.VCC |
| acel_SCL | NodeMCU_acel.D1, acel_ADS1115.SCL |
| acel_SDA | NodeMCU_acel.D2, acel_ADS1115.SDA |
| acel_D7 | NodeMCU_acel.D7, acel_R5.1 |
| acel_D8 | NodeMCU_acel.D8, acel_R6.1 |
| luz_rele_3V3 | NodeMCU_luz_rele.3V3, luz_rele_LDR.2, luz_rele_Rele.VCC |
| luz_rele_A0 | NodeMCU_luz_rele.A0, luz_rele_LDR.1, luz_rele_R2.1 |
| luz_rele_D1 | NodeMCU_luz_rele.D1, luz_rele_Rele.IN1 |
| luz_rele_D2 | NodeMCU_luz_rele.D2, luz_rele_Rele.IN2 |
| luz_rele_D5 | NodeMCU_luz_rele.D5, luz_rele_Rele.IN3 |
| luz_rele_D7 | NodeMCU_luz_rele.D7, luz_rele_R5.1 |
| luz_rele_D8 | NodeMCU_luz_rele.D8, luz_rele_R6.1 |
| acel_X | acel_ADS1115.A0, acel_GY61.X |
| acel_Y | acel_ADS1115.A1, acel_GY61.Y |
| acel_Z | acel_ADS1115.A2, acel_GY61.Z |
| acel_LED_R | acel_LED_R.A, acel_R6.2 |
| acel_LED_V | acel_LED_V.A, acel_R5.2 |
| luz_rele_LED_R | luz_rele_LED_R.A, luz_rele_R6.2 |
| luz_rele_LED_V | luz_rele_LED_V.A, luz_rele_R5.2 |

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
