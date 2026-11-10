# Ideas de forma e identidad para las cajas de Argos

Documento de trabajo del Frente 2 (10-nov-2026). Son **ideas generales, sin modelar**. El equipo investiga cada una, compara y decide cuáles se aplican. Ninguna está aprobada.

## Cómo usar este documento

1. Cada idea trae qué es, para qué serviría, qué investigar y las dudas abiertas.
2. Buscar referencias (fotos de productos, modelos impresos, artículos) y guardar 2 o 3 por idea.
3. Hacer bocetos a mano: no hace falta CAD.
4. Calificar cada idea con la tabla del final y elegir.
5. La idea elegida se aplica primero al `dht`; si funciona, pasa a las estaciones.

## Reglas que cualquier idea debe respetar

- Se imprime **sin soportes** en PETG y cabe en una cama de 220 × 220 mm (las estaciones ya miden 202 mm con orejas).
- Superficie del frente lisa, que se pueda limpiar con alcohol: nada de texturas profundas donde se junte polvo.
- El DHT22 sigue en su cámara separada, abajo, lejos de la placa y la pantalla, con aire que entra y sale.
- Pantalla legible a 2 m y LED visibles a 3 m.
- No se cambian pines ni cableado.
- No copiar la forma ni el logo de un producto comercial.
- Quedan unas 2 semanas: una idea que no se pueda modelar e imprimir en ese tiempo se deja como trabajo futuro.

## Orden sugerido

Primero la 1 y la 2. Las demás son complementos que se pueden combinar con ellas.

---

## 1. Persianas en la cámara del DHT22

**Qué es.** Cambiar las ranuras rectas de la cámara del sensor por aletas inclinadas, como las casetas de las estaciones meteorológicas.

**Para qué serviría.**
- Deja pasar el aire pero tapa la línea de vista: la luz y el calor radiante de las lámparas no pegan directo en el sensor.
- Es el rasgo más reconocible: a primera vista dice "esto mide el ambiente".
- Tiene justificación técnica para el reporte y el jurado, no es solo adorno.

**Qué investigar.**
- Caseta de Stevenson y escudos de radiación para sensores de temperatura: por qué existen y cómo son.
- Ángulo y separación de las aletas: qué tanto frenan el aire frente a unas ranuras simples.
- Si un DHT22 dentro de una caja con persianas responde más lento a los cambios.
- Cómo imprimir aletas sin soportes: inclinación máxima, aletas como parte de la pared o como pieza aparte que se encaja.

**Dudas abiertas.**
- ¿Aletas solo al frente, o también a los lados y abajo?
- ¿Pieza fija o rejilla desmontable para limpiar?
- ¿Cuánto cambia la lectura? Se puede comparar con el termohigrómetro de referencia cuando llegue el hardware (criterio actual: menos de 1 °C de diferencia).

## 2. El ojo de Argos

**Qué es.** Argos Panoptes es el gigante de los cien ojos de la mitología griega, el vigilante que nunca duerme. La idea es usar un ojo como motivo de la marca.

**Dónde podría ir.**
- Alrededor del domo del sensor de movimiento, que ya parece un ojo: un aro o un párpado en relieve.
- Alrededor de la pantalla del `dht`.
- Como iris de ranuras radiales que al mismo tiempo sirvan de ventilación o de salida del sonido del buzzer.
- Como logo pequeño hundido junto a la palabra "Argos".

**Qué investigar.**
- El mito de Argos Panoptes y cómo contarlo en una frase para el video.
- Logos y productos que usan un ojo o un iris sin verse intimidantes (el cuarto es un espacio de trabajo, no debe parecer cámara de vigilancia).
- Cómo se ve un relieve bajo (0.4 a 0.8 mm) impreso en PETG blanco, y si conviene resaltarlo con otro color.

**Dudas abiertas.**
- ¿Ojo realista, geométrico o solo un círculo con un punto?
- ¿Un mismo ojo en las tres cajas o uno distinto por sensor?
- ¿Se usa también en el dashboard y en el video, para que todo el proyecto se vea igual?

---

## 3. Silueta de cápsula

**Qué es.** Extremos semicirculares en lugar de caja rectangular.

**Para qué serviría.** Se distingue de un gabinete comprado y no tiene esquinas que se enganchen. Va bien con las estaciones, que son largas y horizontales.

**Qué investigar.** Cuánto espacio interior se pierde en los extremos; si la protoboard de 830 puntos sigue cabiendo en la cama de impresión; cómo quedan las orejas de montaje en un extremo curvo.

## 4. Frente inclinado en el `dht`

**Qué es.** La cara de la pantalla inclinada unos 10 a 15°.

**Para qué serviría.** Leer la pantalla sin agacharse ni estirarse, según la altura a la que quede la caja.

**Qué investigar.** A qué altura va a quedar el `dht` en el cuarto (dato pendiente de los encargados); ángulo de visión de una pantalla OLED; cómo se imprime una tapa inclinada sin soportes.

## 5. Aro de luz

**Qué es.** Una franja translúcida entre la tapa y la base que se ilumina con los LED verde y rojo.

**Para qué serviría.** Ver el estado de la caja desde un lado y desde más lejos, no solo de frente.

**Qué investigar.** Guías de luz y difusores impresos; qué filamento difunde mejor (PETG natural o transparente); cuánta luz da un LED de 5 mm con resistencia de 330 Ω repartida en una franja larga; si el verde y el rojo se mezclan y confunden.

## 6. Ventilas con patrón

**Qué es.** Sustituir las ranuras rectas de la zona de la placa por un patrón: panal hexagonal, nervaduras de hoja o puntos.

**Para qué serviría.** Da carácter y puede aludir a las plantas del cultivo in vitro.

**Qué investigar.** Qué formas se imprimen sin soportes en una pared vertical (el hexágono y el rombo sí; el círculo grande no); área abierta que se necesita para ventilar; qué tan fácil es limpiar el patrón.

## 7. Dos tonos

**Qué es.** Base de un color y tapa de otro, o cambio de filamento en las primeras capas para que el texto y los iconos queden en otro color.

**Para qué serviría.** Contraste: hoy el texto hundido en PETG blanco casi no se ve.

**Qué investigar.** Cambio de filamento por capa en el laminador; qué colores hay disponibles y si entran en el presupuesto; combinaciones que se vean limpias en un laboratorio.

## 8. Iconos por sensor

**Qué es.** Un icono junto a cada par de LED: termómetro, puerta, persona, sol, onda de vibración.

**Para qué serviría.** Que cualquiera entienda qué avisa cada luz sin leer.

**Qué investigar.** Iconos simples que se lean a 3 mm de trazo; iconos de uso libre o dibujados por el equipo.

## 9. Riel común de montaje

**Qué es.** Una sola pieza de pared en forma de cuña en la que cuelga cualquiera de las tres cajas.

**Para qué serviría.** Poner y quitar una caja con una mano y poder cambiarla de lugar.

**Qué investigar.** Unión tipo cuña francesa y cola de milano impresas; qué permiten los encargados fijar en la pared y en los anaqueles.

## 10. Otras ideas para explorar

- **Familia de tamaños.** Que las tres cajas compartan proporciones, radios y posición de la marca, para que se reconozcan como un conjunto.
- **Etiqueta intercambiable.** Una plaquita que entra a presión con el nombre del nodo o del experimento, en lugar del texto fijo.
- **Código de color por sensor.** Un detalle de color distinto en cada caja, repetido en el dashboard.
- **Tapa con ventana.** Una zona translúcida para ver la electrónica: útil en la Expo, discutible en el cuarto.
- **Pie de mesa.** Un soporte para exhibir las cajas de pie en el stand, sin pared.

---

## Tabla para decidir

Calificar cada idea de 1 (malo) a 5 (bueno) y sumar.

| Idea | Ayuda a la función | Da identidad | Fácil de imprimir | Fácil de limpiar | Cabe en el tiempo | Total |
|---|---|---|---|---|---|---|
| 1. Persianas del DHT22 | | | | | | |
| 2. Ojo de Argos | | | | | | |
| 3. Cápsula | | | | | | |
| 4. Frente inclinado | | | | | | |
| 5. Aro de luz | | | | | | |
| 6. Ventilas con patrón | | | | | | |
| 7. Dos tonos | | | | | | |
| 8. Iconos | | | | | | |
| 9. Riel común | | | | | | |

## Entregable

- Referencias guardadas por idea y la tabla llena.
- 2 o 3 bocetos a mano que combinen las ideas elegidas.
- Una decisión del equipo: qué se aplica ahora, qué queda como trabajo futuro y por qué.

Fechas en el plan del Frente 2: propuesta el jueves 12 de nov, decisión el viernes 13.
