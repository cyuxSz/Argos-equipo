# Prueba del capuchón de la LDR: elegir R2 y el umbral de lámparas apagadas

Borrador del 20-oct-2026. **No hace falta flashear el NodeMCU**: se mide la resistencia de la LDR con el multímetro. El voltaje y las cuentas de A0 se calculan después.

## Qué se imprime (fase 1)

| Pieza | Material | Para qué |
|---|---|---|
| `capuchon_ldr` | PETG **negro** | Cuerpo opaco. Lleva la ventana de Ø4.5 mm (diafragma) y una visera de 4 mm que limita la luz lateral a ≈ ±51°. La cola en U con túnel sirve para el cincho del cable. La oreja M3 pivota en la horquilla |
| `difusor_ldr` | PETG **blanco o natural** | Disco de Ø10 × 0.9 mm. Va a presión en el asiento, por el frente, con una gota de pegamento |
| `soporte_ldr` | PETG negro | Horquilla que se fija junto a la lámpara con 2 tornillos de 3.5 mm o 2 cinchos. Lleva un M3 × 16 con tuerca como pivote |

¿Por qué el cuerpo es negro y el difusor va aparte? El capuchón anterior era una sola pieza blanca con 0.6 mm de piel. El PETG blanco deja pasar luz por las paredes, así que la LDR también veía la luz lateral del cuarto. El cuerpo negro deja entrar luz solo por la ventana. El disco aparte se puede cambiar: más grueso (1.2 mm) si satura, más delgado (0.6 mm) si no alcanza, sin reimprimir el cuerpo.

## Armado

1. Suelda la LDR al cable de 2 hilos y cubre cada soldadura con termocontraíble.
2. Mete la LDR por la cola hasta que su cabeza toque la ventana. Ciñe el cable con un cincho que pase por el túnel de la cola.
3. Pega el difusor por el frente.
4. Monta el capuchón en la horquilla (M3 × 16 + tuerca), apúntalo a la lámpara y aprieta.

**Calor:** el PETG se ablanda a ≈ 80 °C. Toca la lámpara tras 1 h encendida. Si quema al tacto, aleja el capuchón. El tipo de lámpara y su temperatura están `[POR CONFIRMAR]`.

## Mediciones (multímetro en Ω, LDR dentro del capuchón y desconectada de la protoboard)

Haz 3 lecturas por condición, con unos segundos entre ellas. Anota la menor y la mayor.

| # | Lámpara | Luz del cuarto / puerta | Distancia a la lámpara | Ángulo | R_LDR (kΩ) |
|---|---|---|---|---|---|
| 1 | Encendida | Encendida, cerrada | 10 cm | 0° | |
| 2 | Encendida | Apagada | 10 cm | 0° | |
| 3 | Apagada | Encendida, cerrada | 10 cm | 0° | |
| 4 | Apagada | Encendida, **abierta** | 10 cm | 0° | |
| 5 | Apagada | Apagada | 10 cm | 0° | |
| 6–7 | Encendida / apagada | Encendida | 5 cm y 20 cm | 0° | |
| 8–9 | Encendida / apagada | Encendida | 10 cm | 30° y 45° | |
| 10 | Encendida 1 h | Encendida | 10 cm | 0° | (deriva por calor) |

- **R_on** = la mayor R con la lámpara encendida (el peor caso: menos luz).
- **R_off** = la menor R con la lámpara apagada (el peor caso: la luz del cuarto o de la puerta).
- Si R_off no es al menos ≈ 3 veces R_on, el capuchón no separa bien los dos estados. En ese caso apunta mejor el capuchón, súbele la visera o usa el difusor de 1.2 mm, y repite.

## Elegir R2 y el umbral

1. **R2 ≈ √(R_on × R_off)**, redondeada al valor comercial más cercano (4.7 k, 10 k, 22 k, 47 k). Así los dos estados quedan a lados opuestos de la mitad de la escala. El circuito actual usa 10 kΩ. **Cambiar R2 no cambia ningún pin.**
2. Voltaje en A0: V = 3.3 × R2 / (R_LDR + R2). Cuentas aproximadas: ≈ V / 3.3 × 1023. Es nominal: el divisor interno del NodeMCU varía de placa a placa.
3. **Umbral = (cuentas_off_máx + cuentas_on_mín) / 2.** Necesita al menos ≈ 100 cuentas de margen a cada lado.
4. El firmware usa hoy 300 (provisional; `firmware/src/luz/main.cpp`). El cambio se aprueba antes de flashear.
5. Confirma con el nodo armado (cuando el equipo flashee) que el LED rojo de `luz` enciende solo con las lámparas apagadas.

Registra los valores en la tabla de pruebas del proyecto.
