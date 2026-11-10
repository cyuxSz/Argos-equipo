# Carcasas modulares (variante del 10-nov-2026)

Modelo base de las tres cajas con encajes a presión. **Todo es nominal**: nada se ha impreso y las medidas de los componentes siguen sin calibrador. Antes de imprimir se ajusta con las medidas reales y con el cupón de clips.

La versión anterior (tapa con 4 tornillos M3 e insertos) sigue intacta como respaldo: `cad/nodos.py` sin `--modular`.

## Qué cambia

| Antes | Variante modular |
|---|---|
| Protoboard entre 4 guías de esquina, sin nada que la retenga | **Clips de protoboard**: 2 en el `dht` y 4 en cada estación. La protoboard entra a presión y sale jalándola |
| Tapa con 4 tornillos M3 e insertos térmicos (cautín) | **Tapa a presión**: 4 broches en el `dht` y 6 en cada estación. Sin tornillos ni insertos |
| OLED metida en su marco, sin retención | **Grapa de la OLED**: pieza suelta que cruza la espalda del módulo y muerde dos muescas del marco |
| Esquinas con chaflán de 2.5 mm | Esquinas redondeadas de 6 mm, frente sin tornillos y línea de sombra entre tapa y base |

No cambia: tamaño exterior, cámara del DHT22, ventilas, orejas y soportes de pared, posición de LED, pantalla, botón, buzzer y PIR. **Tampoco cambia el cableado**: `1_electronica/fuente/layouts.py` no se tocó, así que los esquemáticos, los dibujos de protoboard, WireViz y Fritzing siguen vigentes.

## Cómo funcionan los encajes

- **Clip de protoboard** (`clip_piso`). Brazo vertical de 22 × 1.6 mm paralelo al borde largo de la protoboard. Una ranura pasante en el piso lo deja suelto, así se imprime desde la cama con las fibras a lo largo del brazo (la orientación fuerte). El gancho en V sobresale 1.0 mm sobre el borde de la protoboard; las dos caras van a 45°, por eso se imprime sin soportes. La raíz se une a la pared con un refuerzo.
- **Broche de la tapa** (`lengua_pared` + `pestana_tapa`). Dos ranuras verticales en la pared lateral forman una lengua de 10 × 12 mm adelgazada a 1.4 mm, con un diente en V hacia adentro. La tapa lleva una pestaña con la muesca. Apriete nominal de 0.5 mm. Para abrir se jala la tapa; no hay herramienta.
- **Grapa de la OLED**. Barra de 1.6 mm con dos patas y dientes; se imprime de canto. Abre porque la barra se arquea.

Los brazos cumplen la regla de partida para PETG: largo de 6 a 8 veces el espesor (brazo del clip 18 / 1.6 ≈ 11; lengua 12 / 1.4 ≈ 8.6).

## Verificación hecha

| Chequeo | Resultado |
|---|---|
| Interferencias entre carcasa y componentes (`dht`, entrada, anaquel, anaquel con relés) | 0 en las cuatro |
| Holguras de módulos libres ≥ 2 mm | Sin faltas |
| Grapa de la OLED contra tapa y electrónica | 0 mm³; queda a 0.2 mm de la OLED |
| Imprimibilidad de base y tapa del `dht` (augura) | Sin soportes. Solo quedan los avisos de pared fina del texto hundido, que ya existían |
| Cupón: choque entre base y tira | 0 mm³ |

**No verificado:** fuerza real de cierre y de retención (depende del filamento y la impresora), ajuste con piezas reales, fatiga de los broches al abrir muchas veces. La estación del anaquel y la de entrada no pasaron por el análisis de imprimibilidad por separado; usan las mismas funciones que el `dht`.

## Cupón de clips (se imprime primero)

`2_carcasas_3d/imprimir/pruebas_ajuste/prueba_clips_base.stl` (71 × 86 × 16 mm, ≈ 23 g) y `prueba_clips_tira.stl` (≈ 3 g).

| Número | Gancho del clip | Apriete del broche |
|---|---|---|
| 1 | 0.8 mm | 0.35 mm |
| 2 (el de las cajas) | 1.0 mm | 0.50 mm |
| 3 | 1.2 mm | 0.65 mm |

- Clips: apoyar la protoboard de 400 puntos contra el riel y bajarla sobre los tres clips. Bien = entra con un clic, no se cae al voltear y sale jalando sin lastimar el brazo.
- Broches: presionar la tira sobre la pared. Bien = cierra a mano con un clic y no se suelta sola.
- La variante que funcione se copia a `DIS["clip"]["gancho"]` y `DIS["broche"]["aprieto"]` en `2_carcasas_3d/codigo/nodos.py`.

## Comandos

Se corren en el repositorio principal (Luis); el código está copiado en `2_carcasas_3d/codigo/`.

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/nodos.py --modular dht entrada anaquel anaquel_rele
```

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib --with pyvista python cad/modular_vista.py
```

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pruebas_clips.py
```

Salidas: en este repositorio las piezas están en `2_carcasas_3d/imprimir/modular_stl/` y los renders en `2_carcasas_3d/renders/modular/`.

## Pendiente

- El PIR sigue solo en su marco, sin retención (los componentes de su espalda no dejan pasar una grapa). Opción: dos postes para sus agujeros M2 `[distancia entre centros POR CONFIRMAR, nominal 28 mm]`.
- El montaje a pared sigue con ojos de cerradura y tacos impresos: ya se quita y pone sin herramienta, así que no se cambió.
- No hay bandeja extraíble aparte: la protoboard hace de cartucho. Si se quiere sacar todo junto con los módulos de la tapa, haría falta mover OLED, botón y buzzer a la base.
- `regenerar.py`, el visor web, los 3MF y la vista explosionada todavía usan la versión con tornillos.
- Si se adopta la variante: actualizar `cad/CLAUDE.md` (hoy pide "tapa con 4 × M3") y quitar los insertos de `docs/presupuesto.md`.

## Ideas de forma e identidad (sin construir)

Resumen; la versión para investigar y decidir está en [ideas_forma.md](ideas_forma.md). Ideas generales para que las cajas se reconozcan como "Argos". Todas deben seguir siendo imprimibles sin soportes, limpiables con alcohol y caber en la cama.

1. **El ojo de Argos.** Argos Panoptes es el gigante de los cien ojos. Motivo de ojo alrededor del domo del PIR y de la ventana de la pantalla: un aro en relieve o un iris de ranuras radiales que además sirve de ventilación.
2. **Silueta de cápsula.** Extremos semicirculares en lugar de rectángulo. Encaja bien con las estaciones horizontales y se distingue de un gabinete comercial.
3. **Frente inclinado en el `dht`.** Pantalla inclinada unos 10–15° hacia arriba o abajo según la altura de montaje, para leerla mejor a 2 m.
4. **Persianas de estación meteorológica.** La cámara del DHT22 con aletas inclinadas en lugar de ranuras. Es funcional (protege de la luz de las lámparas y deja pasar el aire) y da el rasgo más reconocible.
5. **Aro de luz.** Una tira de PETG natural entre tapa y base que difunde los LED; el estado se vería también de lado. Requiere acercar los LED al borde.
6. **Ventilas con patrón.** Panal hexagonal o nervaduras de hoja (el proyecto es de cultivo in vitro) en lugar de ranuras rectas. En paredes verticales los hexágonos se imprimen sin soportes.
7. **Dos tonos.** Base gris y tapa blanca, o un cambio de filamento en las primeras capas de la tapa para que el texto y los iconos hundidos queden en otro color.
8. **Iconos por sensor.** Un icono hundido (termómetro, puerta, onda, sol, persona) junto a cada par de LED, además del texto.
9. **Riel común.** Una sola pieza de pared tipo cuña (cola de milano) para las tres cajas, de modo que cualquiera cuelgue en cualquier riel.

Para decidir: bocetos a mano de 2 o 3 combinaciones, elegir una y aplicarla primero al `dht`.

## Referencias

- SnapBoards, sistema de portadores a presión para placas: https://www.hackster.io/news/dhamdhawach-horsuwan-delivers-tool-free-rapid-prototyping-with-3d-printable-snapboards-b868a72f21de
- CheeseBoard, placa de montaje con clips: https://makerworld.com/en/models/1475104-cheeseboard
- openGrid: https://www.printables.com/model/1214361-opengrid-walldesk-mounting-framework-and-ecosystem
- Uniones a presión impresas (Hubs): https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-Druck/
- Clips impresos (Sovol): https://www.sovol3d.com/blogs/news/3d-printed-snap-fit-joints-how-to-design-clips-that-work
