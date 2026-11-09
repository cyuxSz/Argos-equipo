# Nodo `luz (fotorresistencia)`: circuito en protoboard

Generado por `hardware/breadboard/protoboard.py` desde `layouts.py`. Dibujo: [nodo_luz_protoboard.svg](nodo_luz_protoboard.svg) / [png](nodo_luz_protoboard.png).

> **Borrador.** Pinout del NodeMCU Amica, medidas de la protoboard y pinout de los módulos son nominales: verificar con la serigrafía y el multímetro antes de energizar.

Divisor: 3V3 → LDR → **A0** → R2 = 10 kΩ → GND. Más luz = más voltaje en A0.

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
| 8 | a20 | LED_V · A | verde | Dupont 10–20 cm | Ánodo (pata larga) del LED verde, en la tapa |
| 9 | riel A GND (junto a col. 19) | LED_V · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 10 | a22 | LED_R · A | rojo | Dupont 10–20 cm | Ánodo (pata larga) del LED rojo, en la tapa |
| 11 | riel A GND (junto a col. 23) | LED_R · K | negro | Dupont 10–20 cm | Cátodo (pata corta, lado plano) |
| 12 | c25 | LDR · 1 | amarillo | cable de la LDR | LDR en su capuchón remoto (junto a la lámpara); cable de 2 hilos con terminal Dupont macho crimpado |
| 13 | riel J 3V3 (junto a col. 25) | LDR · 2 | naranja | cable de la LDR | Sin polaridad |

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

## Redes resultantes (calculadas)

| Red | Miembros |
|---|---|
| 5V | C1.+, NodeMCU.VIN |
| GND | C1.-, LED_R.K, LED_V.K, NodeMCU.GND, R2.2 |
| A0 | LDR.1, NodeMCU.A0, R2.1 |
| 3V3 | LDR.2, NodeMCU.3V3 |
| LED_R | LED_R.A, R6.2 |
| LED_V | LED_V.A, R5.2 |
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
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
