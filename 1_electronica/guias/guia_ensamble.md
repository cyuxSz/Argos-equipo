# Guía de ensamble y pruebas: nodos Argos

Borrador del 19-oct-2026. Se apoya en:
- los circuitos de `hardware/breadboard/nodo_<id>_protoboard.md` (tabla de orificios) y sus dibujos;
- los cableados de `hardware/wiring/nodo_<id>.png`;
- las piezas de `cad/exports/`.

> **Antes de empezar:** todo pinout y toda medida son nominales. Compara cada módulo con su serigrafía. Si algo no coincide (orden de pines del KY-012, de la OLED, del GY-61, del ADS1115 o del 2N2222), **detente y corrige `layouts.py`**: el dibujo, el WireViz y el gemelo CAD se regeneran desde ahí.

## 1. Herramientas y material

- Multímetro con prueba de continuidad y de diodo. Cautín con punta cónica para los insertos. Destornillador para M3 avellanado (hexagonal o Phillips, según el tornillo comprado). Pinzas y pelacables.
- Cable UTP sólido (reciclado) para los puentes; Dupont macho-hembra del kit para los módulos fuera de la placa.
- Fijaciones: ver `cad/informe_verificacion.md` §6.

## 2. Impresión (PETG)

| Ajuste | Valor de partida |
|---|---|
| Boquilla / cama | 235–245 °C / 75–85 °C (ajustar al filamento comprado) |
| Capa | 0.2 mm |
| Perímetros | 5 (paredes de 2 mm sólidas) |
| Relleno | 25 % giroide |
| Soportes | **Ninguno**: cada STL ya viene orientado |
| Brim | Solo el émbolo del botón (o imprimirlo junto a otras piezas) |

1. **Primero la pieza de prueba de ajuste** (Fase 7). Si los LED, el émbolo o la tapa no entran, cambia `holgura` en `cad/medidas.json` y regenera.
2. Tapa del `luz`: el difusor son las 3 primeras capas (0.6 mm). Imprímela en PETG **blanco o natural**: un color oscuro no deja pasar la luz.

## 3. Insertos térmicos

1. Con el cautín a 230–240 °C, apoya el inserto M3 × 5 sobre el agujero de 4.0 mm de cada torreta de la base.
2. Bájalo **perpendicular** y sin forzar, hasta que quede 0.2–0.3 mm abajo del borde.
3. Deja enfriar 1 min antes de atornillar.

## 4. Armado común (los cinco nodos)

1. **Rotular la protoboard de 400 puntos.**
   - Lado A (junto a la fila a): riel interior **5V**, riel exterior **GND**.
   - Lado J (junto a la fila j): riel interior **3V3**, riel exterior **GND**.
2. **NodeMCU:** clávalo en las filas **b** e **i**, columnas 1–15, con el micro-USB hacia la columna 1. Comprueba con la serigrafía que **VIN** quede en b1 y **3V3** en i1.
3. **Puentes de alimentación (UTP):** a1 → riel 5V · a2 → GND A · j1 → riel 3V3 · j2 → GND J.
4. **C1 220 µF:** en los rieles del lado A, junto a la columna 3. **Pata larga (+) al 5V**; franja (−) a GND.
5. **LED:** resistencias de 330 Ω y puentes de D7/D8 según la tabla del nodo. Los LED van en la tapa: **pata larga = ánodo**, al cable que viene de la resistencia.
6. **Circuito propio del nodo** (§5), siguiendo la tabla de orificios. En los orificios libres a/j junto al NodeMCU **solo puentes UTP**: un Dupont no cabe por el borde de la placa.
7. **Pruebas sin energía** (§6). Luego **pruebas con energía** (§7).
8. **Montaje en la base:**
   - Pega la protoboard con su adhesivo, dentro de sus cuatro guías.
   - Ordena los cables hacia los costados.
   - Pon el sobre de sílica en su compartimento, junto a la pared derecha. Nunca en la cámara del DHT22.
9. **Tapa:**
   - Empuja los LED desde adentro hasta que la ceja toque el collar.
   - Monta los módulos de la tapa (§5).
   - Conecta los Dupont y cierra con **4 tornillos M3 × 10 avellanados**. Aprieta sin forzar: el inserto ya da el tope.
10. **Cable USB** por el hueco del techo, con un cincho en las ranuras de la oreja superior como alivio de tensión.
11. **Montaje:** atornilla o pega el soporte impreso. Presenta el nodo con las cabezas de los pernos en la parte redonda de los ojos de cerradura y **bájalo 6 mm**. Para retirarlo: súbelo y sácalo.

## 4 bis. Estaciones (dos NodeMCU en una MB-102 de 830 puntos, cajas horizontales)

> **Instalación horizontal (174 × 80 mm).** Estación de entrada: imprime los **2 tacos** de `soporte_pared`, cuelga la caja de ellos con las ranuras hacia abajo, marca los agujeros con la propia caja, retírala y atornilla (o pega con tira removible). Estación del anaquel: atornilla o sujeta con cinchos las orejas a la estructura. En ambas, el cable de 5 V, el del MC-38 y el de la LDR salen por abajo. Cada par de LED tiene su nombre (PIR / PUERTA, ACEL / LUZ) a la derecha.

1. **Antes de clavar nada, revisa los rieles con el multímetro.** Mide continuidad entre la columna 30 y la 34 de cada riel:
   - Si los rieles vienen partidos a la mitad (lo común en las MB-102), la distribución ya lo considera.
   - Si el **riel de 3V3** viene continuo, **córtalo** entre las columnas 31 y 33. Las dos placas nunca deben compartir su 3V3.
2. **Arma cada mitad con la distribución de su nodo:**
   - Arriba (columnas 1–30) el `pir` o el `acel`.
   - Abajo (columnas 34–63) el `puerta` o la `luz`, corridos 33 columnas.
   - El detalle orificio por orificio está en `hardware/breadboard/estacion_<entrada|anaquel>_protoboard.md`.
3. **Puentes de riel:** une 5V y las dos GND entre las columnas 31 y 33. El 3V3 no se une.
4. **Energía de la estación:**
   - El módulo USB-C va contra la pared izquierda: + al riel 5V y − a GND, en la columna 32.
   - Cada NodeMCU recibe 5 V por su pin VIN.
   - El micro-USB de cada placa solo se usa para flashear.
5. **Cables que salen de la caja:**
   - Estación de entrada: el cable del MC-38 sale por la pared izquierda, con un cincho.
   - Estación del anaquel: el cable de la LDR va hasta su capuchón impreso (cuerpo negro, difusor blanco aparte). El capuchón pivota en la horquilla `soporte_ldr`, que se fija junto a la lámpara con 2 tornillos o 2 cinchos. Armado, prueba y elección de R2: `docs/prueba_ldr.md`.

## 5. Particularidades por nodo

| Nodo | Pasos extra |
|---|---|
| `dht` | Q1 (2N2222) en b26–b28, **cara plana hacia la fila a, E-B-C** (verificar con la hoja de datos del lote). R3 1 kΩ cruza el canal (col. 27); R4 10 kΩ y R1 10 kΩ van de pie. DHT22 en la cuna de la cámara inferior, con la rejilla al frente; su cable pasa por la muesca de la doble pared (sellar con un poco de espuma). OLED en su marco, con el conector abajo (por eso el firmware gira la imagen). Botón 6 × 6 en su cuna, con el émbolo impreso delante. Buzzer KY-012 a presión en su anillo: **confirmar qué pin es +** |
| `luz` | R2 10 kΩ de pie, entre a25 y GND (valor final según `docs/prueba_ldr.md`). La LDR va en el capuchón remoto: entra por la cola hasta tocar la ventana |
| `pir` | Ajusta los potenciómetros del HC-SR501 antes de cerrar: sensibilidad media, tiempo mínimo, jumper en **H** (redisparo). PCB en su marco con 2 tornillos M2 × 6; el domo sale por el agujero frontal |
| `puerta` | Cable del MC-38 por la entrada lateral izquierda, con cincho; crimpa terminales Dupont macho en sus puntas. **Portas (fase 2):** empuja cada cuerpo en su porta hasta que pase los 4 topes ("clic"). La cara lisa (pared delgada) mira al otro cuerpo; la muesca V de la espalda marca el centro. El reed (rótulo REED) va en el marco y el imán (IMAN) en la hoja, con las muescas V alineadas entre sí. La polaridad N/S del imán no importa para un reed. Fija cada porta con cinta VHB debajo, con 2 tornillos de cabeza plana de 3.5 mm por las ranuras, o con ambos. Las ranuras dan ±3 mm por pieza para ajustar el gap. Si la hoja queda hundida respecto al marco, pon calzas de 2 o 4 mm (llevan las mismas ranuras). El gap se mide cuerpo a cuerpo e incluye las 2 paredes de 1.2 mm |
| `acel` | ADS1115 (fila c, col. 20–29) con componentes hacia la fila a; GY-61 (fila h, col. 25–29) con componentes hacia la fila j. Al cerrar, las costillas de la tapa deben morder el borde superior de ambas PCB. **Anota cómo quedaron X e Y** respecto a las marcas del frente. Fija la caja **rígida** al anaquel (M3 o cinchos apretados, nunca cinta de espuma) |

**Prueba del MC-38** (multímetro en continuidad entre los 2 cables, sin conectar a la protoboard):

1. Antes de fijar nada, acerca el imán al reed sobre la mesa. Anota la distancia a la que el contacto **cierra** al acercar y a la que **abre** al alejar. Ese es el gap máximo real `[POR CONFIRMAR]`. Si cierra a menos de 15 mm, trabaja a ≈ 70 % de esa distancia, no a 15–25 mm.
2. Fija los portas con la puerta cerrada y mide el gap. Debe quedar abajo de la distancia de cierre, con margen.
3. Abre y cierra la puerta 20 veces. El contacto debe cerrar las 20 veces con la puerta cerrada y abrir las 20 con la puerta abierta ≥ 5 cm. Repite empujando la puerta contra su juego.
4. Anota en `cad/medidas.json` (`mc38.cuerpo_iman`, `mc38.separacion_trabajo`) las medidas reales y regenera.

## 6. Pruebas sin energía (continuidad y resistencia)

Sin cable USB. El multímetro va en continuidad (Ω) o en diodo, según la fila.

| Nodo | Entre | Esperado |
|---|---|---|
| Todos | Riel 5V ↔ GND · riel 3V3 ↔ GND | **Sin continuidad.** Un pitido breve al inicio es C1 cargándose |
| Todos | GND lado A ↔ GND lado J | Continuidad (se unen por el NodeMCU) |
| Todos | D7 ↔ ánodo del LED verde · D8 ↔ ánodo del LED rojo | ≈ 330 Ω |
| Todos | LED en prueba de diodo (rojo + en el ánodo) | El LED enciende tenue |
| `dht` | DATA (D4) ↔ 3V3 | ≈ 10 kΩ (≈ 5 kΩ si el módulo trae su propio pull-up) |
| `dht` | D5 ↔ GND | ≈ 11 kΩ (R3 + R4) |
| `dht` | Base ↔ emisor de Q1 (diodo) | 0.6–0.7 V |
| `dht` | + del buzzer ↔ riel 5V | Continuidad |
| `luz` | A0 ↔ GND | ≈ 9.7 kΩ (10 kΩ en paralelo con el divisor interno del NodeMCU) |
| `pir` | D5 ↔ OUT del PIR | Continuidad |
| `puerta` | D5 ↔ GND | 0 Ω con el imán cerca; abierto sin imán |
| `acel` | ADDR ↔ GND · X ↔ A0 · Y ↔ A1 · Z ↔ A2 | Continuidad |

## 7. Pruebas con energía (P-02)

Alimenta por micro-USB con la fuente de 5 V ≥ 1 A. **No hace falta flashear** para estas medidas. Si la placa trae un programa anterior, los LED pueden comportarse distinto: no importa.

| Punto | Esperado |
|---|---|
| Riel 3V3 | **3.14–3.47 V** (3.3 V ± 5 %) |
| Riel 5V (VIN) | **≈ 4.6–5.1 V**: el diodo del NodeMCU baja unos 0.3 V |
| Cualquier pin que entre a un GPIO | **Nunca > 3.3 V** |
| `dht`: DATA, SDA, SCL en reposo | ≈ 3.3 V |
| `dht`: colector de Q1 en reposo | ≈ VIN (buzzer callado). Si suena al encender, revisa R4 y el pinout de Q1 |
| `luz`: A0 | Sube con más luz, entre 0 y 3.3 V |
| `pir`: OUT | 0 V. Unos 3.3 V con movimiento (tras 30–60 s de calentamiento) |
| `puerta`: D5 | 3.3 V con la puerta abierta; 0 V con el imán cerca |
| `acel`: X, Y, Z del GY-61 | ≈ 1.65 V; el eje que mira hacia abajo marca ≈ 1.32 o 1.98 V |
| Consumo (P-05, multímetro en serie con VIN) | `dht` ≈ 55–60 mA con la OLED; otros ≈ 40 mA |

Registra los valores en la tabla de pruebas del proyecto (P-01 a P-09). **El flasheo del firmware de `firmware/` lo hace el equipo, con aprobación.** Este repositorio solo lo compila.

## 8. Al terminar cada nodo

- [ ] El nodo se abre y se cierra sin forzar, y se retira del soporte sin herramientas.
- [ ] Los LED se ven a 3 m; en el `dht`, la pantalla se lee a 2 m.
- [ ] Hay sílica en el compartimento y ningún cable toca la cámara del DHT22.
- [ ] Están anotados los cambios respecto a este documento: pinouts reales, medidas, holgura usada.
