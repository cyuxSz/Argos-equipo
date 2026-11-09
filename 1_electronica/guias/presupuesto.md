# Presupuesto de hardware extra (21-oct-2026)

Tope del equipo: **$1,500 MXN**. Precios de octubre de 2026: los marcados *visto* se leyeron en línea el 21-oct (ver links); los marcados *(est.)* son estimaciones **sin verificar**. Revisar todo en el carrito.

## Decisiones vigentes

- **3 cajas / 5 NodeMCU** (5 NodeMCU obligatorios; ver `docs/decision_cajas_5mcu.md`).
- **Protoboard de 400 puntos** para el nodo que va solo (la MB-102 de 830 puntos mide ≈ 165 × 55 mm).
- **OLED 2.42" SSD1309 I²C de 4 pines** en el nodo `dht`: dígitos de ≈ 21 mm, legibles a 2 m.
- **LED con 330 Ω:** el kit trae 50 (10 por kit × 5).
- **Carcasas y soportes impresos en PETG** (se compra 1 kg); no se compran gabinetes.
- Sin paquete Dupont: los kits traen 50 M-M y 50 M-H. Para los puentes cortos, cable UTP sólido reciclado.
- **Fuentes de 5 V: se compran.** Un cargador prestado tendría que quedarse instalado para siempre.
- **Termohigrómetro: prestado.** Solo se usa en pruebas y calibración. Preguntar primero a los encargados si el cuarto ya tiene uno.
- **Sílica: se compra.** Sin repuestos de buzzer ni de transistor.

## Escenario B: 3 cajas / 5 NodeMCU (21-oct-2026, **el que se usa**)

Son **5 microcontroladores independientes** (uno por integrante, cada uno con su sensor, sus LED y su usuario MQTT). Se reparten en 3 cajas: `dht` solo, estación de entrada (`pir` + `puerta`) y estación del anaquel (`acel` + `luz`). Cada estación comparte caja, fuente y una MB-102 de 830 puntos del kit.

| Concepto | Cant. | Unit. | Subtotal | Proveedor (link) | Estado |
|---|---|---|---|---|---|
| DHT22 con cables (AR0600) | 1 | 120 | 120 | [UNIT](https://uelectronics.com/producto/sensor-de-temperatura-y-humedad-dht22-con-cables/) · [Geek Factory $119–133](https://www.geekfactory.mx/producto/dht22-o-am2302-sensor-de-temperatura-y-humedad-relativa/) | UNIT sin verificar; Geek Factory visto |
| Reed switch MC-38 con imán (AR1246) | 1 | 25 | 25 | [UNIT $25](https://uelectronics.com/producto/sensor-magnetico-mc-38/) · [MV Electrónica $24](https://mvelectronica.com/producto/interruptor-magnetico-mc-38-sensor-de-puerta-o-ventana) | visto |
| Buzzer activo KY-012 (AR0031) | 1 | 16 | 16 | [UNIT $16](https://uelectronics.com/producto/buzzer-activo-ky-012/) · [Ideaelectronica $18](https://www.ideaelectronica.mx/modulos/11683-xs-191-modulo-buzzer-zumbador-activo-ky-012-35-a-55v.html) | visto |
| ADS1115 (AR0318) | 1 | 47 | 47 | [UNIT $47](https://uelectronics.com/producto/ads1115-adc-amplificador-de-ganancia-programable/) · [Lionchip $56.84](https://www.lionchipmexico.com/product-page/modulo-adc-16-bits-i2c-ads1115-para-arduino-raspberry-pic-avr-5v) | visto |
| Transistor 2N2222 TO-92 | 1 | 1 | 1 | [UNIT TO-92](https://uelectronics.com/producto/2n2222-transistor-bjt-npn-40v-to-92/) (precio sin ver) | *(est.)* |
| Resistencia 1 kΩ | 3 | 0.50 | 1.50 | kit / UNIT | *(est.)* |
| Resistencia 10 kΩ | 4 | 0.50 | 2 | kit / UNIT | *(est.)* |
| Capacitor 220 µF (16 V no hallado; **25 V** sirve) | 5 | 3 | 15 | [Steren E220-25R](https://www.steren.com.mx/capacitor-electrolitico-radial-de-220-uf-micro-faradios-a-25-volts.html) ($3 lista) | visto |
| OLED 2.42" SSD1309 **I²C** 4 pines | 1 | 232 | 232 | [Amazon MX $231.99](https://www.amazon.com.mx/pulgadas-pantalla-controlador-microcontroladores-compatibles/dp/B0H925W6PG) | visto; confirmar I²C en la ficha (muchas vienen en SPI) |
| Protoboard 400 puntos (solo `dht`) | 1 | 55.68 | 55.68 | [Steren 509-005](https://www.steren.com.mx/mini-protoboard-de-1-bloque-y-2-tiras.html) | visto; confirmar nº de puntos |
| Fuente 5 V con cable micro-USB (`dht`) | 1 | 139 | 139 | [Steren ELI-712 vía Cyberpuerta](https://www.cyberpuerta.mx/Energia/Cargadores-Baterias-Pilas/Cargadores-de-Dispositivos-Moviles/Steren-Cargador-de-Pared-ELI-712-5V-1x-USB-Blanco.html) | visto; corriente sin confirmar |
| Fuente 5 V / 2 A (una por estación) | 2 | 139 | 278 | igual que la anterior | ídem |
| Módulo de entrada USB-C a terminales | 2 | 15 | 30 | sin proveedor en MX hallado (probar Mercado Libre: "breakout USB-C") | *(est.)* |
| Filamento PETG 1 kg | 1 | 348 | 348 | [Creality MX Hyper PETG](https://store.creality.com/mx/products/hyper-petg-filamento-1-75mm-1kg) ([CR PETG $289](https://store.creality.com/mx/products/cr-petg-filamento-de-7-75-mm-1kg) agotado) | visto, en stock |
| Insertos térmicos M3 + tornillos M3 | 1 | 120 | 120 | sin precio MX hallado (Mercado Libre / Amazon MX: "insertos M3 latón") | *(est.)* |
| Sílica gel | 1 | 60 | 60 | sin hallar (el deshumidificador de Steren cuesta $243 y está agotado; no es equivalente) | *(est.)* |
| Termohigrómetro de referencia | — | prestado | 0 | | |
| Envío (UNIT/DHL; costo real sin confirmar) | 1 | 150 | 150 | | *(est.)* |
| **Total** | | | **≈ $1,640.18 (≈ $140 arriba del tope)** | | |

*Visto* = precio leído en la página o en un resultado de búsqueda el 21-oct-2026; **no** es un carrito. UNIT bloquea la consulta automática (403), así que sus precios salen de resultados de búsqueda; Mercado Libre también bloqueó. Confirmar todo en el carrito.

### Recortes para entrar en el tope

Sin tocar el DHT22, la OLED 2.42", el PETG ni la sílica:
- **Comprar en sucursal en vez de envío (−150):** AG Electrónica anuncia sucursal y ventas en Monterrey ([agelectronica.com](https://agelectronica.com/inicio), chat "Ventas MTY"). Steren también tiene tiendas físicas `[POR CONFIRMAR dirección]`. UNIT solo mostró recoger en sucursal en Guadalajara/CDMX.
- Tuercas M3 cautivas en vez de insertos térmicos (el CAD admite ambas): −120 `[POR CONFIRMAR]`.
- Fuentes: usar cargadores USB sobrantes de 5 V / 1 A o más para pruebas y comprar solo los definitivos; o una sola fuente de 2 A por estación (ya contado).

Con envío y insertos fuera: ≈ **$1,370**, dentro del tope.

Los extras de instalación (prensaestopas, borneras, cable, conectores; ≈ $250 est.) no están en el BOM: pedirlos prestados al laboratorio.

## Proveedores consultados (21-oct-2026)

| Proveedor | Resultado |
|---|---|
| [UNIT Electronics](https://uelectronics.com/) | Tiene casi todo (DHT22, MC-38, KY-012, ADS1115, 2N2222). Bloquea consulta automática; revisar carrito y envío a Monterrey. |
| [AG Electrónica](https://agelectronica.com/inicio) | Sucursal/ventas Monterrey; buscador por parámetro, no pude buscar las claves AR sin la interfaz. |
| [Steren](https://www.steren.com.mx/) | Solo tiene DHT11 (no DHT22), 2N2222A metálico TO-18 (pinout distinto a TO-92), capacitores, protoboard. |
| [Geek Factory](https://www.geekfactory.mx/) | DHT22 $119–133. |
| [Amazon MX](https://www.amazon.com.mx/) | OLED I²C $231.99; el resto más caro. |
| [Creality MX](https://store.creality.com/mx/collections/creality-filamento-especial) | PETG 1 kg $348. |
| Mercado Libre, Mouser, DigiKey, Tayda, AliExpress | No consultables desde aquí (403/404/sin MX); no los usé. DigiKey/Mouser/AliExpress tardan y causan impuestos de importación. |

## Lista para buscar proveedores (piezas por comprar)

Cantidades exactas del escenario B, sin repuestos. Los NodeMCU, LDR, HC-SR501, GY-61, LED, botón, protoboards MB-102 y jumpers vienen en los kits del curso: **no se compran**.

| # | Pieza | Piezas | Qué buscar | Nota |
|---|---|---|---|---|
| 1 | DHT22 (AM2302) | 1 | DHT22, **no** DHT11 | Con cables o con módulo y pull-up de 10 kΩ |
| 2 | Reed switch MC-38 con imán | 1 | MC-38 normalmente abierto, con cable | Va en el marco de la puerta |
| 3 | Buzzer activo 5 V | 1 | KY-012 o equivalente de 5 V | `[pinout del módulo POR CONFIRMAR]` |
| 4 | ADS1115 | 1 | Módulo I²C de 16 bits, dirección 0x48 | Para el GY-61 de `acel` |
| 5 | Transistor 2N2222 | 1 | 2N2222 / 2N2222A, TO-92 | Conmuta el buzzer |
| 6 | Resistencia 1 kΩ | 3 | 1/4 W, 5 % | Base del transistor (el kit trae más; verificar) |
| 7 | Resistencia 10 kΩ | 4 | 1/4 W, 5 % | Pull-ups y base–GND (el kit trae más; verificar) |
| 8 | Capacitor electrolítico 220 µF / 16 V | 5 | ≥ 16 V, 5 mm de paso | C1, uno por nodo |
| 9 | OLED 2.42" SSD1309 | 1 | I²C de 4 pines (GND, VCC, SCL, SDA) | Verificar que sea I²C y no SPI |
| 10 | Protoboard 400 puntos | 1 | Mini/half de 400 puntos | Solo la caja `dht` |
| 11 | Fuente 5 V / 1 A, micro-USB | 1 | Cargador con cable micro-USB | Caja `dht` |
| 12 | Fuente 5 V / 2 A | 2 | Cargador 5 V / 2 A | Una por estación; ver cable o módulo de entrada |
| 13 | Módulo de entrada USB-C a terminales | 2 | USB-C macho/hembra a borneras, 5 V | Uno por estación |
| 14 | Filamento PETG | 1 kg | 1 carrete de 1 kg | Diámetro según la impresora `[POR CONFIRMAR]` |
| 15 | Insertos térmicos M3 | mín. 12 | Latón, M3 | 4 por tapa × 3 cajas; sumar los de bahías `[POR CONFIRMAR]` |
| 16 | Tornillos M3 | mín. 12 | Cabeza cilíndrica o botón, largo `[POR CONFIRMAR]` | Uno por inserto |
| 17 | Sílica gel | 1 lote | Bolsitas o granulada, indicadora si hay | Para las 3 cajas |

Pedir en un solo proveedor ahorra envíos. Si venden en lotes mínimos (resistencias, capacitores, insertos y tornillos), conviene el lote más chico.
