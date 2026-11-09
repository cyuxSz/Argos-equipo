# Caja de potencia del fotoperiodo (luz) · submódulo opcional

**Submódulo opcional:** la versión base del proyecto son las 3 cajas sin cambios (el nodo `luz` solo mide con la LDR). Esto se arma solo si da tiempo y lo aprueban los encargados; no cambia nada de la versión base.

Estado: diseño del 5-nov-2026, sin armar ni medir. Fuente de verdad de las conexiones: `hardware/breadboard/layouts.py` (`nodo_luz_rele`, `estacion_anaquel_rele` y `CAJA_POTENCIA`).

## Qué hace

El nodo `luz` en su variante `luz_rele` (estación del anaquel con relés) enciende y apaga las luminarias de cada plancha con un módulo de 4 relés. Cada relé corta solo la fase (L) de una salida:

| Relé | Pin del nodo `luz_rele` | Plancha | Salida |
|---|---|---|---|
| CH1 (IN1) | D1 (GPIO5) | 2 | extensión cortada «P2» |
| CH2 (IN2) | D2 (GPIO4) | 3 | extensión cortada «P3» |
| CH3 (IN3) | D5 (GPIO14) | 4 | extensión cortada «P4» |
| CH4 | — | libre | — |

Lógica: **LOW = luz encendida**. Al arrancar, si el nodo se cuelga o si falta el cable de señal, los relés quedan abiertos y la luz se apaga. La alerta grave «luces que no siguen el horario» la detecta la LDR.

## Material (presupuesto aparte del equipo, tope ≈ $500 MXN)

| Pieza | Cant. | Estimado (MXN) |
|---|---|---|
| Módulo de 4 relés de 5 V con optoacoplador y puente JD-VCC (relés SRD-05VDC, 10 A) | 1 | $70–110 |
| Extensión de 3 m, 3 contactos, calibre 16, **con tierra** | 3 | $120–210 |
| Portafusible en línea 5x20 + fusible **lento de 5 A** | 1 | $25–40 |
| Regleta de clemas (8 posiciones: 4 neutro + 4 tierra) | 1 | $15–25 |
| Cable de señal de 6 hilos (Dupont del kit) | — | $0 |
| Caja impresa en PETG (≈ 141 g) | — | $0 |
| **Total** | | **≈ $230–385** |

Las 3 extensiones se cortan. Los 3 extremos con contactos son las salidas P2, P3 y P4, y una de las clavijas sobrantes es la entrada «PARED». Los precios son estimados: revisar en el carrito. Los tornillos M3 se atornillan directo en el PETG (piloto de 2.8 mm), sin insertos.

## Cableado

**Baja tensión** (cable de 6 hilos, de la estación del anaquel a la caja):

| Hilo | Protoboard (estación) | Módulo |
|---|---|---|
| azul | f61 (D1) | IN1 |
| verde | f62 (D2) | IN2 |
| blanco | f63 (D5) | IN3 |
| naranja | riel 3V3, col. 60 | VCC |
| negro | riel GND, col. 60 | GND |
| rojo | riel 5V, col. 62 | JD-VCC |

**Quitar el puente JD-VCC–VCC del módulo.** Así los optoacopladores trabajan a 3.3 V, igual que el ESP8266, y las bobinas a 5 V. Ningún GPIO ve 5 V.

**127 V** (dentro de la caja, del lado de arriba):

1. PARED: fase (L) → portafusible → COM1. Puentes cortos de COM1 a COM2 y de COM2 a COM3.
2. NO1 → L de P2; NO2 → L de P3; NO3 → L de P4. Los NC quedan libres.
3. Neutro de PARED → regleta → neutro de P2, P3 y P4.
4. Tierra de PARED → regleta → tierra de P2, P3 y P4.
5. Cada cable lleva un cincho en su ancla, junto a su agujero del techo, como alivio de tensión.

## Pruebas (antes de enchufar a la pared)

| Id | Prueba | Cómo | Esperado |
|---|---|---|---|
| P-R1 | Opto a 3.3 V | Estación con 5 V y sin enchufar la caja; poner IN1 a GND con un puente | El relé hace clic y su LED enciende. Si no conmuta con VCC a 3V3, avisar: hay que cambiar el módulo o agregar un transistor por canal |
| P-R2 | Arranque | Energizar la estación | Ningún relé hace clic |
| P-R3 | Continuidad | Multímetro en continuidad, caja **desenchufada**: clavija L → contacto L de P2 con IN1 en bajo y en alto | Cerrado solo con IN1 en bajo. Repetir con P3 y P4 |
| P-R4 | Aislamiento | Continuidad entre L y N, entre L y tierra, y entre cualquier pin de 127 V y el GND de 5 V | Abierto en todos los casos |
| P-R5 | Fusible | Quitar el fusible | Ninguna salida tiene fase |
| P-R6 | 127 V | Con la revisión del Ing. Puga, enchufar con una luminaria | Enciende y apaga con IN1. Después, una plancha completa |

## Pendientes `[POR CONFIRMAR]`

- Medidas reales del módulo (PCB, agujeros, ubicación de la tira de pines), del cable de las extensiones (redondo o plano) y del portafusible: ajustar `cad/medidas.json` → `caja_potencia` y regenerar.
- Breaker del circuito C7.
- Horario por plancha y firmware del fotoperiodo: por ahora el entorno `luz_rele` (`USAR_RELES=1`) solo deja los relés apagados; el entorno `luz` no los toca.

## Archivos

- Esquemático de 127 V: `hardware/kicad/caja_potencia.kicad_sch`; lado de control: `hardware/kicad/nodo_luz_rele.kicad_sch` (PDF y SVG en `hardware/kicad/salida/`).
- 3D: `cad/caja_potencia.py` → `cad/exports/nodo_potencia_*`; estación con salida extra: `cad/nodos.py anaquel_rele` → `cad/exports/nodo_anaquel_rele_*`.
- Protoboard: `hardware/breadboard/estacion_anaquel_rele_protoboard.png`.
- Firmware: `pio run -d firmware -e luz_rele` (solo compilar).
