# Decisión: 3 cajas / 5 NodeMCU y carcasas impresas (21-oct-2026)

## Decisión

El profesor confirmó que los **5 NodeMCU son obligatorios**. Se mantiene el diseño vigente:

- **3 cajas / 5 NodeMCU**: `dht` solo; estación de entrada (`pir` + `puerta`); estación del anaquel (`acel` + `luz`).
- **Carcasas impresas en PETG** como montaje final.
- No cambian el firmware, el CAD, `hardware/breadboard/layouts.py` ni la BD.

Se descartan:

| Opción con 5 MCU | Motivo |
|---|---|
| 5 cajas / 5 MCU (escenario A original) | ≈ $1,843, fuera del tope de $1,500 |
| 2 cajas / 5 MCU (`dht` dentro de una estación) | Ahorra 1 fuente (≈ $90), pero el DHT22 queda junto a 2 placas más que generan calor (criterio < 1 °C) y lejos de la altura de los frascos |

Todas las opciones con menos de 5 MCU (Caso A de 2 MCU, 1 MCU, 3 MCU) quedan fuera por el requisito.

## Alternativas a la impresión 3D

La impresión reemplaza **PETG $425 + insertos/tornillos $120 = $545** del presupuesto. Si el PETG ya se compró (CLAUDE.md, 19-oct) es costo hundido y cualquier alternativa **suma** dinero. `[POR CONFIRMAR: PETG comprado o por comprar]`.

| Opción | Ventaja | Desventaja | Precio (21-oct) | Veredicto |
|---|---|---|---|---|
| **PETG impreso (actual)** | Cámara aislada del DHT22, ventana OLED, guías de luz y soportes LDR/MC-38/PIR a medida | Horas de impresión y reimpresiones | $425 + $120 (ya en presupuesto) | **Se mantiene** |
| Gabinete ABS comercial + perforar | Acabado limpio, limpiable con alcohol | El GP-17 ya se descartó (35 mm de fondo); sin cámara aislada del DHT22; perforaciones a mano; los soportes de LDR y MC-38 igual hacen falta | `[POR CONFIRMAR]`: no se encontró precio público en MXN | Solo si no hay impresora |
| Caja de registro de PVC (ferretería) | Barata y robusta, tapa atornillada | Aspecto de obra; mismas carencias; tamaños estándar quizá no alojen la MB-102 (≈ 165 × 55 mm) | `[POR CONFIRMAR]`: Home Depot MX no muestra precio en línea | Plan B de emergencia |
| Acrílico cortado con láser | Rápido si hay láser disponible | Rediseño a 2D; uniones pegadas; cámara del DHT22 difícil. MDF no: absorbe humedad | `[POR CONFIRMAR: acceso a láser]` | No vale la pena en 6 semanas |
| Sin caja (protoboard sobre base) | Sin costo, depuración fácil | No cumple "removible, limpiable, con tapa" | $0 | Solo como prototipo v0 |
| Híbrido: gabinete + piezas impresas pequeñas | Menos horas de impresión | Igual requiere filamento; dos sistemas de montaje | `[POR CONFIRMAR]` | Solo si fallan las impresiones grandes |

Aun sin impresión 3D habría que fabricar el capuchón de la LDR, las guías del MC-38 y la cámara del DHT22. Por eso la impresión sigue siendo la mejor opción mientras haya impresora. `[POR CONFIRMAR: acceso a impresora y horas disponibles]`.

## Versiones de prototipado

| Versión | Contenido | Material | Semanas |
|---|---|---|---|
| v0 | Protoboards sin caja; firmware + MQTT + n8n de punta a punta | Nada extra | 1–2 |
| v1 | Piezas de prueba pequeñas: ventana OLED, cámara DHT22, capuchón LDR, guía MC-38, bahía de protoboard | PETG (poco) | 2–3 |
| v2 | 3 cajas completas; prueba < 1 °C contra termohigrómetro y legibilidad a 2 m | PETG | 3–4 |
| v3 | Instalación en el cuarto, ajustes, reimpresiones | Margen del carrete | 5–6 |

## Presupuesto

El total del escenario adoptado y los recortes están en `docs/presupuesto.md`.

## Pendientes

- ¿PETG comprado o por comprar?
- ¿Acceso a impresora 3D y horas disponibles?
- Campus y ciudad de compra: UNIT solo tiene tiendas en CDMX y Guadalajara; recoger en tienda solo evita el envío si el equipo está en una de esas ciudades. `[POR CONFIRMAR]`
- Selector de compuertas de los profesores: esquema, tabla de verdad y voltaje `[POR CONFIRMAR]`. Con 5 MCU se monta en el nodo que corresponda según su función.

## Fuentes consultadas (21-oct-2026)

- UNIT, sucursales: https://uelectronics.com/unit-sucursales-tienda-de-electronica/
- UNIT, preguntas frecuentes: https://uelectronics.com/preguntas-frecuentes/
- Home Depot México, cajas eléctricas: https://www.homedepot.com.mx/b/electrico/conduit-cajas-y-accesorios/cajas-electricas-y-tapas
