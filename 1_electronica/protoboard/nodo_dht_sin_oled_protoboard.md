# Nodo `dht (sin OLED, respaldo)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [nodo_dht_sin_oled_protoboard.svg](nodo_dht_sin_oled_protoboard.svg) / [png](nodo_dht_sin_oled_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

Respaldo si los encargados no autorizan la pantalla: DATA del DHT22 vuelve a **D2 (GPIO4)**, como en el diseño original. D1 y D4 quedan libres.

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
| R1 | 10 kΩ | 1: j24, 2: riel J 3V3 (junto a col. 24) | Pull-up de DATA. De pie (vertical) entre j24 y el riel 3V3 |
| R3 | 1 kΩ | 1: g27, 2: d27 | Cruza el canal: de D5 a la base |
| R4 | 10 kΩ | 1: a27, 2: riel A GND (junto a col. 27) | Base a GND. De pie entre a27 y el riel GND |
| Q1 | 2N2222 (TO-92) | E: b26, B: b27, C: b28 | **Cara plana hacia la fila a; E-B-C de col. 26 a 28** [verificar pinout del lote] |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado J |
| 5 | j6 | h20 | cafe | 55 mm | D7 → columna 20 (LED verde), por fuera de la fila j |
| 6 | j5 | h22 | morado | 60 mm | D8 → columna 22 (LED rojo), por fuera de la fila j |
| 7 | j8 | h27 | blanco | 70 mm | D5 → columna 27 (R3 hacia la base de Q1), por fuera de la fila j |
| 8 | a26 | riel A GND (junto a col. 26) | negro | 20 mm | Emisor de Q1 → GND |
| 9 | j7 | h21 | gris | 60 mm | D6 → columna 21 (botón), por fuera de la fila j |
| 10 | j13 | h24 | amarillo | 50 mm | D2 → columna 24 (DATA del DHT22), por fuera de la fila j |
| 11 | a20 | LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 12 | riel A GND (junto a col. 19) | LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 13 | a22 | LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 14 | riel A GND (junto a col. 23) | LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 15 | j21 | Boton · 1 | gris | Dupont 10–20 cm | Botón de silencio/pantalla (en la tapa) |
| 16 | riel J GND (junto a col. 7) | Boton · 2 | negro | Dupont 10–20 cm |  |
| 17 | riel J 3V3 (junto a col. 25) | DHT22 · VCC | naranja | Dupont 20 cm | Cámara inferior: cable más largo |
| 18 | f24 | DHT22 · DATA | amarillo | Dupont 20 cm |  |
| 19 | riel J GND (junto a col. 25) | DHT22 · GND | negro | Dupont 20 cm |  |
| 20 | riel A 5V (junto a col. 30) | Buzzer · + | rojo | Dupont 10–20 cm | KY-012: confirmar qué pin es + [POR CONFIRMAR] |
| 21 | a28 | Buzzer · - | blanco | Dupont 10–20 cm | Al colector de Q1 (conmutación del lado bajo) |

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
| riel J GND (junto a col. 7) | Boton.2 |
| j7 | puente → h21 |
| j8 | puente → h27 |
| j13 | puente → h24 |
| riel A GND (junto a col. 19) | LED_V.K |
| a20 | LED_V.A |
| d20 | R5.2 |
| g20 | R5.1 |
| h20 | puente ← j6 |
| h21 | puente ← j7 |
| j21 | Boton.1 |
| a22 | LED_R.A |
| d22 | R6.2 |
| g22 | R6.1 |
| h22 | puente ← j5 |
| riel A GND (junto a col. 23) | LED_R.K |
| riel J 3V3 (junto a col. 24) | R1.2 |
| f24 | DHT22.DATA |
| h24 | puente ← j13 |
| j24 | R1.1 |
| riel J 3V3 (junto a col. 25) | DHT22.VCC |
| riel J GND (junto a col. 25) | DHT22.GND |
| riel A GND (junto a col. 26) | puente ← a26 |
| a26 | puente → A_GND:26 |
| b26 | Q1.E |
| riel A GND (junto a col. 27) | R4.2 |
| a27 | R4.1 |
| b27 | Q1.B |
| d27 | R3.2 |
| g27 | R3.1 |
| h27 | puente ← j8 |
| a28 | Buzzer.- |
| b28 | Q1.C |
| riel A 5V (junto a col. 30) | Buzzer.+ |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| D6 | Boton.1, NodeMCU.D6 |
| GND | Boton.2, C1.-, DHT22.GND, LED_R.K, LED_V.K, NodeMCU.GND, Q1.E, R4.2 |
| 5V | Buzzer.+, C1.+, NodeMCU.VIN |
| COLECTOR | Buzzer.-, Q1.C |
| DATA | DHT22.DATA, NodeMCU.D2, R1.1 |
| 3V3 | DHT22.VCC, NodeMCU.3V3, R1.2 |
| LED_R | LED_R.A, R6.2 |
| LED_V | LED_V.A, R5.2 |
| D5 | NodeMCU.D5, R3.1 |
| D7 | NodeMCU.D7, R5.1 |
| D8 | NodeMCU.D8, R6.1 |
| BASE | Q1.B, R3.2, R4.1 |

## Chequeo automático

✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las redes coinciden con la red esperada.

## Verificación eléctrica (por escrito, sin simulador)

Supuestos: USB entrega 5.0 V; el Amica pasa a VIN ≈ 4.7 V tras su diodo [medir]; GPIO del ESP8266 a 3.3 V,
corriente máx. recomendada ≈ 12 mA por pin.

| Punto | Cálculo | Resultado |
|---|---|---|
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| Base de Q1 (D5, R3 = 1 kΩ) | (3.3 − 0.7) / 1 kΩ − 0.7 / 10 kΩ | ≈ 2.5 mA ✔ |
| Saturación de Q1 | I_C ≈ 30 mA; h_FE mín. 2N2222 ≈ 75 → I_B necesaria ≈ 0.4 mA | 2.5 mA da β forzada ≈ 12 → saturado ✔ (V_CE ≈ 0.1–0.3 V) |
| Buzzer | Entre VIN (≈ 4.7 V) y colector; KY-012 trabaja con 3.5–5.5 V | ✔ El GPIO nunca ve 5 V: solo maneja la base |
| R4 = 10 kΩ base–GND | Mantiene Q1 apagado mientras D5 flota en el arranque | ✔ Sin pitido al encender |
| DHT22 | Alimentado a 3V3 (rango 3.3–6 V); DATA con R1 = 10 kΩ a 3V3 | ✔ Señal de 3.3 V. Si el módulo ya trae pull-up, quedan ≈ 5 kΩ en paralelo: aceptable |
| D8 / GPIO15 en el arranque | Debe estar en bajo: el NodeMCU trae pull-down en GPIO15; el LED con 330 Ω no lo sube | ✔ |
| Botón D6 | INPUT_PULLUP interno, botón a GND | ✔ Sin resistencia externa |
| Consumo 3V3 | ESP8266 pico ≈ 300–400 mA + OLED ≈ 20 mA + DHT22 ≈ 1.5 mA + LED ≈ 8 mA | ✔ Dentro del regulador del Amica (≈ 500–800 mA según modelo) |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V; amortigua picos del WiFi y del buzzer |
| Ninguna señal > 3.3 V en un GPIO | Sensores y OLED a 3V3; el único elemento a 5 V (buzzer) está del lado del colector | ✔ |

**Pendientes de verificar en físico:** pinout del 2N2222 (TO-92 suele ser E-B-C con la cara plana al
frente, pero hay variantes C-B-E); pinout del KY-012 (en muchos módulos "S" es el + del buzzer y el pin
central no se usa); orden de pines de la OLED (VCC-GND o GND-VCC según proveedor) y del módulo DHT22.
