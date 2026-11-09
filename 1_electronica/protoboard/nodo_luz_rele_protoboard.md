# Nodo `luz con relés (submódulo opcional del fotoperiodo)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [nodo_luz_rele_protoboard.svg](nodo_luz_rele_protoboard.svg) / [png](nodo_luz_rele_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

Divisor: 3V3 → LDR → **A0** → R2 = 10 kΩ → GND. Más luz = más voltaje en A0. Submódulo opcional: **D1 / D2 / D5** mandan IN1 / IN2 / IN3 del módulo de 4 relés de la caja de potencia (activo en bajo: LOW = luz encendida). Un cable de 6 hilos sale de las columnas 27–30.

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
| R2 | 10 kΩ | 1: a25, 2: riel A GND (junto a col. 25) | Del divisor a GND. De pie entre a25 y el riel GND. Valor final según docs/prueba_ldr.md (4.7–47 kΩ; no cambia pines) |

## Conexiones punto a punto

| # | De | A | Color | Largo aprox. | Para qué |
|---|---|---|---|---|---|
| 1 | a1 | riel A 5V (junto a col. 1) | rojo | 15 mm | VIN (5 V del USB) → riel 5V |
| 2 | a2 | riel A GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado A |
| 3 | j1 | riel J 3V3 (junto a col. 1) | naranja | 15 mm | 3V3 → riel 3V3 |
| 4 | j2 | riel J GND (junto a col. 2) | negro | 20 mm | GND → riel GND lado J |
| 5 | j6 | h20 | cafe | 55 mm | D7 → columna 20 (LED verde), por fuera de la fila j |
| 6 | j5 | h22 | morado | 60 mm | D8 → columna 22 (LED rojo), por fuera de la fila j |
| 7 | a15 | b25 | amarillo | 40 mm | A0 → columna 25 (divisor), por fuera de la fila a |
| 8 | j14 | h28 | azul | 55 mm | D1 → columna 28 (IN1, plancha 2), por fuera de la fila j |
| 9 | j13 | h29 | verde | 60 mm | D2 → columna 29 (IN2, plancha 3), por fuera de la fila j |
| 10 | j8 | h30 | blanco | 80 mm | D5 → columna 30 (IN3, plancha 4), por fuera de la fila j |
| 11 | a20 | LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 12 | riel A GND (junto a col. 19) | LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 13 | a22 | LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 14 | riel A GND (junto a col. 23) | LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 15 | c25 | LDR · 1 | amarillo | cable de la LDR | LDR en su capuchón remoto (junto a la lámpara); cable de 2 hilos con terminal Dupont macho crimpado |
| 16 | riel J 3V3 (junto a col. 25) | LDR · 2 | naranja | cable de la LDR | Sin polaridad |
| 17 | f28 | Rele · IN1 | azul | cable de señal | Módulo de 4 relés (caja de potencia): IN1 → plancha 2 |
| 18 | f29 | Rele · IN2 | verde | cable de señal | IN2 → plancha 3 |
| 19 | f30 | Rele · IN3 | blanco | cable de señal | IN3 → plancha 4 (IN4 queda libre) |
| 20 | riel J 3V3 (junto a col. 27) | Rele · VCC | naranja | cable de señal | VCC del lado de control (optoacopladores) a **3V3**: con 3.3 V en VCC, un GPIO en alto apaga bien el opto [verificar con el módulo, P-R1] |
| 21 | riel J GND (junto a col. 27) | Rele · GND | negro | cable de señal |  |
| 22 | riel A 5V (junto a col. 29) | Rele · JD-VCC | rojo | cable de señal | Bobinas a 5 V. **Quitar el puente JD-VCC–VCC del módulo** |

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
| j8 | puente → h30 |
| j13 | puente → h29 |
| j14 | puente → h28 |
| a15 | puente → b25 |
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
| riel A GND (junto a col. 25) | R2.2 |
| riel J 3V3 (junto a col. 25) | LDR.2 |
| a25 | R2.1 |
| b25 | puente ← a15 |
| c25 | LDR.1 |
| riel J 3V3 (junto a col. 27) | Rele.VCC |
| riel J GND (junto a col. 27) | Rele.GND |
| f28 | Rele.IN1 |
| h28 | puente ← j14 |
| riel A 5V (junto a col. 29) | Rele.JD-VCC |
| f29 | Rele.IN2 |
| h29 | puente ← j13 |
| f30 | Rele.IN3 |
| h30 | puente ← j8 |

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| 5V | C1.+, NodeMCU.VIN, Rele.JD-VCC |
| GND | C1.-, LED_R.K, LED_V.K, NodeMCU.GND, R2.2, Rele.GND |
| A0 | LDR.1, NodeMCU.A0, R2.1 |
| 3V3 | LDR.2, NodeMCU.3V3, Rele.VCC |
| LED_R | LED_R.A, R6.2 |
| LED_V | LED_V.A, R5.2 |
| D1 | NodeMCU.D1, Rele.IN1 |
| D2 | NodeMCU.D2, Rele.IN2 |
| D5 | NodeMCU.D5, Rele.IN3 |
| D7 | NodeMCU.D7, R5.1 |
| D8 | NodeMCU.D8, R6.1 |

## Chequeo automático

✔ Sin errores: todos los orificios existen, ninguno se repite ni queda bajo el NodeMCU, y las redes coinciden con la red esperada.

## Verificación eléctrica (por escrito, sin simulador)

| Punto | Cálculo | Resultado |
|---|---|---|
| A0 del NodeMCU | La placa trae un divisor 220 k / 100 k: acepta 0–3.3 V | ✔ El divisor LDR/10 k nunca supera 3.3 V |
| Corriente del divisor | 3.3 V / (R_LDR + 10 kΩ), con luz (R_LDR ≈ 1–5 kΩ) | ≈ 0.2–0.3 mA ✔ |
| Sensibilidad | R2 = 10 kΩ queda a la mitad del rango típico de una GL55xx con luz de interiores | R2 ≈ √(R_on × R_off) medidos en el capuchón (`docs/prueba_ldr.md`) [modelo de LDR POR CONFIRMAR] |
| Entradas IN1–IN3 (D1, D2, D5) | Opto del módulo entre VCC (3V3) e IN, con ≈ 1 kΩ: LOW → (3.3 − 1.2) / 1 kΩ | ≈ 2 mA por pin ✔ (< 12 mA). En alto (3.3 V = VCC) no circula corriente: relé apagado |
| Arranque | GPIO5, GPIO4 y GPIO14 no tienen función de arranque y quedan en alta impedancia: el opto no enciende | ✔ Relés apagados al arrancar o si el nodo se cuelga. El firmware escribe HIGH antes de `pinMode(OUTPUT)` |
| Bobinas (JD-VCC a 5 V) | 3 × ≈ 72 mA (SRD-05VDC, 0.36 W) [ficha del módulo POR CONFIRMAR] | ≈ 0.22 A del riel 5V ✔ (eliminador de 3 A) |
| Contactos | 10 A / 250 VAC por relé; carga por plancha ≤ 4 × 19 W ≈ 0.6 A a 127 V | ✔ Margen amplio. Fusible lento de 5 A en la caja de potencia |
| Nunca 5 V en un GPIO | IN1–IN3 solo ven el lado de 3V3 del opto; los 5 V quedan en el lado de las bobinas (JD-VCC) | ✔ Por eso se quita el puente JD-VCC |
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
