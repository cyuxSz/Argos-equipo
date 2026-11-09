# Informe de verificación de carcasas: tres cajas para cinco nodos

Fecha: 19-oct-2026; actualizado el 20-oct-2026 (v2: capuchón de la LDR y portas del MC-38). Modelo: `cad/nodos.py` (build123d 0.13). Datos crudos: `cad/exports/verificacion_<caja>.json`.

> **Todo es nominal.** Las medidas de componentes vienen de hojas de datos o de valores típicos (`cad/medidas.json`) y **no se han medido con calibrador**. Ninguna pieza se ha impreso.

**Reacomodo del 19-oct.** Los cinco microcontroladores siguen siendo independientes, uno por integrante, pero ahora van en tres cajas:
- `dht`, solo, por su cámara aislada;
- **estación de entrada**: `pir` + `puerta`;
- **estación del anaquel**: `acel` + `luz`.

Cada estación lleva dos NodeMCU en una MB-102 de 830 puntos del kit y una fuente de 5 V con módulo de entrada USB-C. El 3V3 de cada placa queda separado. Las cajas sueltas de `luz`, `pir`, `puerta` y `acel` se descartaron; se pueden regenerar con `cad/nodos.py luz`, etc.

## 1. Resultado por caja

| Caja | Cuerpo (mm) | Con orejas (mm) | Piezas del gemelo | Interferencias | Holgura mín., módulos libres | Imprimibilidad |
|---|---|---|---|---|---|---|
| `dht` (vertical) | 80 × 138.3 × 40.5 | 80 × 166.3 × 40.5 | 37 | **0** | 3.5 mm ✔ | ✔ sin soportes |
| Estación de entrada (**horizontal**) | 173.9 × 80 × 40.5 (domo +12) | 201.9 × 80 × 40.5 | 37 | **0** | 4.07 mm ✔ | ✔ sin soportes |
| Estación del anaquel (**horizontal**) | 173.9 × 80 × 40.5 | 201.9 × 80 × 40.5 | 35 | **0** | 4.07 mm ✔ | ✔ sin soportes (capuchón v2: solo un puente de 1.6 mm) |

**Estaciones horizontales (20-oct).** Se modelan en vertical y se giran 90°, así que ocupan solo **8 cm de alto** en el invernadero (antes 17 cm). Cabe en una cama de 220 × 220 mm con las orejas (202 mm), con poco margen. Tres cambios por el giro:
- **Orejas en los extremos.** En la estación de entrada llevan ojos de cerradura con la ranura hacia abajo (por gravedad la caja queda trabada) y se cuelgan de **dos tacos de pared impresos** (`soporte_pared`). Para instalar: se cuelga la caja de los tacos, se marcan los agujeros con ella y se atornillan; no hace falta medir la distancia (≈ 186 mm entre pernos). En la del anaquel llevan ranuras M3 de 10 mm para fijarla rígida.
- **Cables hacia abajo.** El cable del MC-38 (entrada) y el de la LDR (anaquel) salen por la pared inferior; el USB-C de 5 V también.
- **Cada par de LED lleva rotulado su sensor** (PIR / PUERTA, ACEL / LUZ), hundido 0.4 mm a la derecha del par. Con PETG blanco el contraste es bajo: se puede resaltar con un marcador.

## Filamento (PETG sólido)

| Caja | Total |
|---|---|
| `dht` (con soporte de pared) | ≈ 150 g |
| Estación de entrada (con 2 tacos de pared, portas y calzas del MC-38) | ≈ 162 g |
| Estación del anaquel (con capuchón, difusor y horquilla de la LDR) | ≈ 145 g |
| **Total** | **≈ 458 g** (con cinco cajas: ≈ 556 g) |

Detalle por pieza, orientación y relleno: `docs/impresion_3d.md`.

## 2. Qué tiene cada nodo (la estación hereda los rasgos de sus dos nodos)

**Común a los cinco** (función `comun()`):
- Protoboard de 400 puntos con guías de esquina; NodeMCU con el micro-USB hacia el techo; salida del cable por el techo.
- Dos LED en la tapa con collar de tope; 4 torretas con inserto M3 y tornillos avellanados por el frente (la tapa se abre sin descolgar el nodo).
- Labio de la tapa; costilla perforada para sílica junto a la pared derecha.
- Ventilas bajas en los costados y altas en el techo (con la placa adentro, el calor sale por arriba).
- ID del nodo hundido en el costado derecho y marca "Argos" en el frente.

| Nodo | Rasgos propios |
|---|---|
| `dht` | Cámara inferior de 40 mm con doble pared y 3 mm de aire ventilado. Cuna del DHT22 (a 21 mm de la protoboard). OLED 2.42" tras una ventana con chaflán. Botón con émbolo impreso. Buzzer con anillo y agujeros de sonido |
| `luz` | **Capuchón remoto v2 (20-oct):** cuerpo negro opaco, ventana de Ø4.5 mm con asiento cónico de tope para la LDR, disco difusor aparte (Ø10 × 0.9 mm, PETG blanco) y visera de 4 mm (≈ ±51°). La cola en U lleva un túnel para cincho. La oreja M3 con agujero en gota pivota en la horquilla `soporte_ldr` (−90° a +75°). Prueba y elección de R2: `docs/prueba_ldr.md`. La caja suelta `luz` conserva el difusor de 0.6 mm en la tapa, pero ya no se usa |
| `pir` | Agujero de Ø24 mm para el domo del HC-SR501 y marco para su PCB. Los potenciómetros quedan accesibles al abrir la tapa |
| `puerta` | Caja en la pared junto al marco (el cable USB no va en la hoja). Entrada del cable del MC-38 en gota (sin soportes) con ranuras para cincho. **Portas v2 (20-oct):**
  - bolsillo con chaflán de entrada y 4 topes de retención de 0.4 mm;
  - pared de 1.2 mm hacia el otro cuerpo;
  - muesca V de centrado en la espalda;
  - rótulo REED / IMAN;
  - orejas con ranuras de ±3.1 mm para tornillo o VHB;
  - calzas de 2 y 4 mm con las mismas ranuras.

  Medidas del imán y gap real `[POR CONFIRMAR]`. Prueba en `docs/guia_ensamble.md` |
| `acel` | ADS1115 y GY-61 de pie en la protoboard; dos costillas de la tapa muerden 2 mm del borde superior de cada PCB para que no vibren por separado. Ejes X/Y hundidos en el frente. **Orejas laterales** con ranura para M3 o cincho: fijación rígida, sin espuma ni ojos de cerradura |

**Cambios de distribución que salieron del gemelo:**
- En el `dht`, ningún Dupont va en los orificios junto al NodeMCU.
- En el `acel`, los módulos pasaron a las columnas 20–29 (con 19–28 el ADS1115 quedaba bajo la antena del NodeMCU) y los LED a las columnas 19 y 30.

`layouts.py`, los dibujos de protoboard y WireViz ya están actualizados.

## 3. Imprimibilidad (build123d-mcp / augura)

| Pieza | Resultado |
|---|---|
| Bases (dht, acel, puerta) | Solo puentes de 1.6–2 mm. Avisos menores (< 1.5 mm²) y pared de 0.2 mm, todos en el ID hundido del costado. Las bases de `luz` y `pir` salen del mismo generador: no se analizaron por separado |
| Tapas (dht, luz, pir, acel) | Solo puentes. Pared mínima de 0.10 mm, causada por el texto "Argos" hundido sobre la cama: una placa de prueba con solo ese texto da el mismo aviso |
| Soportes de pared y anaquel | 0 hallazgos |
| Capuchón LDR v2 | Puente de 1.6 mm (túnel). Piso del túnel de 0.8 mm (2 perímetros). Agujero M3 en gota |
| Horquilla LDR | Agujero M3 en gota. Aviso de pared de 0.43 mm sin ubicación `[revisar en el slicer]` |
| Portas MC-38 v2 | Solo avisos < 1 mm² del rótulo hundido en la pared vertical |
| Émbolo del botón (`dht`) | Imprimir con brim (pieza de 6 mm) |

Correcciones aplicadas por el chequeo:
- Avellanado a 90° en las torretas.
- Cuna del botón sin escalón.
- Labio de la tapa con cortes rectos.
- Bolsillo de la LDR del mismo diámetro que su tubo.
- Agujero en gota para el cable del MC-38.
- (v2) Capuchón: la oreja ya no queda como sólido aparte (tocaba en una línea). Rampa a 45° sobre la cola y asiento cónico en vez de techos planos.
- (v2) Porta: la muesca V atravesaba la pared de 1.2 mm; pasó a la espalda.

## 4. Filamento (PETG sólido, 1.27 g/cm³)

| Nodo | Base | Tapa | Extras | Soporte de pared | Total |
|---|---|---|---|---|---|
| `dht` | 91.9 | 35.0 | 0.1 (émbolo) | 26.5 | **153.5 g** |
| `luz` | 58.1 | 24.2 | — | 19.3 | **101.6 g** |
| `pir` | 58.1 | 23.1 | — | 19.3 | **100.5 g** |
| `puerta` | 58.0 | 24.0 | 13.5 (portas + calzas) | 19.3 | **114.8 g** |
| `acel` | 59.3 | 26.2 | — | — | **85.5 g** |
| **Familia** | | | | | **≈ 556 g** |

El soporte de anaquel pesa unos 6 g más que el de pared. Con 1 kg de PETG quedan ≈ 400 g para la prueba de ajuste y reimpresiones.

## 5. Archivos (`cad/exports/`)

- `nodo_<id>_<pieza>.step`: edición, en coordenadas del nodo.
- `nodo_<id>_<pieza>.stl`: ya orientado para imprimir.
- `impresion/`: STEP orientados para imprimir.
- `vista/`: STEP girados para visores con z hacia arriba.
- `nodo_<id>_ensamble.step` y `nodo_<id>_gemelo.step`.
- `3mf/`: 3MF por pieza (`cad/exportar_3mf.py`); la base del `dht` solo en STL.
- `archivo/2026-10-20_v1/`: exports anteriores a la v2; `archivo/obsoletos/`: piezas que ya no se usan.

Vistas acotadas en `cad/renders/nodo_<id>_vistas.png|svg` y renders en `cad/renders/nodo_<id>_iso.png`. Fase 6: `nodo_dht_explosionada.png` y `nodo_dht_escena_anaquel.png`, generados con `cad/escenas.py`; la escena es esquemática y sus medidas de anaquel y frascos son supuestas.

## 6. Lista de fijaciones

| Cant. (familia) | Pieza | Uso |
|---|---|---|
| 20 (+5 repuesto) | Inserto térmico M3 × 5, Ø ext. 4.6 mm | 4 por nodo, en las torretas de la base |
| 20 (+5) | Tornillo M3 × 10 cabeza plana avellanada (ISO 10642 / DIN 965) | Tapa → base, por el frente |
| 8 | Tornillo 3.5 × 25 avellanado + taquete 5 mm, **o** tiras adhesivas removibles | Soportes de pared de dht, luz, pir y puerta (2 por soporte) |
| 2 | Tornillo M3 × 12 + tuerca y arandela, **o** 2 cinchos | Orejas del `acel` contra el anaquel |
| 2 | Tornillo M2 × 6 autorroscante | PCB del HC-SR501 [separación de agujeros POR CONFIRMAR] |
| 5 + 2 | Cincho de 2.5 mm | Alivio del cable USB (5) y del cable del MC-38 (2) |
| 5 | Sobre de sílica de 1 g | Uno por nodo, en su compartimento |
| 2 | Cinta doble cara (VHB o removible) | Porta-sensor y porta-imán del MC-38 |
| 4 | Tornillo 3.5 × 16 cabeza plana (opcional) | Portas del MC-38, por las ranuras |
| 1 + 2 | M3 × 16 + tuerca; 2 tornillos 3.5 mm o 2 cinchos | Pivote del capuchón LDR; horquilla junto a la lámpara |

## 7. Qué se probó y qué no

**Probado en el modelo:**
- Interferencias y holguras con el gemelo nominal.
- Chequeo automático de imprimibilidad.
- Coherencia del gemelo con `layouts.py`.
- Que los 6 firmwares (dht, dht sin OLED, luz, pir, puerta, acel) compilan.
- (v2) `cad/pruebas_ldr.py`: ajuste de LDR, cable y difusor; giro en la horquilla; voladizos. `cad/pruebas_mc38.py`: asiento, retención y voladizos de los portas.

**No probado:**
- Ninguna medida real. Lo crítico: NodeMCU y su micro-USB; OLED (área activa); HC-SR501 (domo, agujeros, alto); GY-61 y ADS1115 (largo y alto de la PCB, orden de pines, lado de los componentes); MC-38; KY-012; botón 6 × 6; LED y LDR.
- Impresión, ajuste de 0.3 mm, prueba térmica del DHT22, lectura de la pantalla a 2 m y resistencia de los pernos impresos.

**Pendientes de diseño:**
1. Retenedor de la OLED.
2. Retención del DHT22 en su cuna.
3. Pinza de anaquel en C (brazos arriba y abajo de la repisa): ajustar `anaquel_espesor` (18 mm supuesto) al medir; si la repisa es de alambre, rediseñar.
4. ~~Piel de 0.6 mm de la LDR~~: resuelto con el capuchón v2. Falta la prueba con la lámpara real (`docs/prueba_ldr.md`) para elegir el difusor (0.6 / 0.9 / 1.2 mm), R2 y el umbral.
6. Medir el MC-38 real (cuerpos y distancia de cierre) y ajustar `mc38.porta.retencion` con un porta impreso.
5. Confirmar que las costillas del `acel` muerden la PCB sin tocar componentes.
