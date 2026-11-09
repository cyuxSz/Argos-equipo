# Fase 7: prueba de ajuste antes de imprimir la familia

Objetivo: comprobar con **≈ 73 g de PETG** que las piezas críticas del nodo `dht` ajustan, antes de gastar ≈ 556 g en los cinco nodos. Los cupones son **recortes de las piezas finales**: si ajustan, la pieza completa ajusta.

Archivos en `cad/exports/pruebas/`: el `.stl` ya viene orientado; `*_cama.step` es la misma pieza y `.step` está en coordenadas del nodo. Se regeneran con `cad/pruebas.py`.

## 1. Qué imprimir

| Cupón | Prueba | Cara en la cama | Tamaño (mm) | PETG |
|---|---|---|---|---|
| `prueba_peine_holguras` | Holgura de LED, émbolo, cuna del botón e inserto M3, en 3 variantes | Placa | 70 × 52 × 9.5 | 12.8 g |
| `prueba_tapa_oled_led_boton` | Ventana y marco de la OLED, collares de LED, botón y buzzer | Frente | 58 × 76 × 8.5 | 13.6 g |
| `prueba_bahia_protoboard` | Guías de esquina de la protoboard de 400 puntos | Espalda | 58 × 91 × 6 | 14.2 g |
| `prueba_camara_dht22` | Cuna del DHT22, doble pared, paso del cable y ventilas | Espalda | 80 × 52 × 22 | 32.0 g |

Los 4 dan 0 soportes en el chequeo automático. Los únicos avisos son las paredes finas del texto hundido.

**Orden:** primero el **peine** (es el más barato y fija la holgura) y después los otros tres. Usa el mismo filamento, la misma impresora y los mismos ajustes que usarás para las piezas finales (ver `docs/guia_ensamble.md` §2).

## 2. Qué revisar

### Peine de holguras

Cada fila tiene tres variantes: **1** = holgura actual − 0.1 mm, **2** = actual (0.3 mm), **3** = actual + 0.1 mm.

| Fila | Pieza real que se prueba | Ajuste correcto |
|---|---|---|
| Agujeros grandes (Ø 5.2 / 5.3 / 5.4) | LED de 5 mm del kit | Entra con la mano, sin juego lateral, y la ceja no pasa |
| Agujeros chicos (Ø 4.3 / 4.4 / 4.5) | Émbolo impreso (vástago de 4 mm), o una broca de 4 mm como calibre | Se desliza sin trabarse |
| Cunas cuadradas | Botón 6 × 6 del kit | Entra a presión suave y no se cae al voltear la pieza |
| Torretas (Ø 3.9 / 4.0 / 4.1) | Inserto M3 × 5 con cautín | Queda recto y a ras; sin grietas en la torreta |

**Cómo ajustar:**

| Variante que funciona | Qué cambiar |
|---|---|
| 2 | No cambies nada |
| 1 | Baja `impresion.holgura` en `cad/medidas.json` a 0.2 |
| 3 | Sube `impresion.holgura` a 0.4 |
| Solo falla el inserto | Cambia `fijacion.inserto_termico.agujero` |

Después de cambiar algo, corre `cad/nodos.py` y `cad/pruebas.py`.

### Tapa: OLED, LED y botón

- [ ] El módulo OLED real entra en su marco por detrás, sin forzar, y su **área activa queda centrada** en la ventana. Si no queda centrada, mide cuánto se corre y ajusta `oled.centro_activo_desde_conector` en `cad/medidas.json` (hoy son 20 mm, valor supuesto).
- [ ] El conector de la OLED (abajo) y sus Dupont hembra salen por el hueco del marco.
- [ ] Los LED entran desde adentro y la ceja hace tope en el collar. La cúpula sobresale ≈ 1.5 mm.
- [ ] El émbolo y el botón 6 × 6 se accionan con un clic claro, sin quedarse hundidos.
- [ ] El buzzer entra a presión en su anillo.

### Bahía de la protoboard

- [ ] La protoboard de 400 puntos real entra entre las cuatro guías con un juego de 0.2–0.5 mm.
- [ ] Mide la protoboard con calibrador. Si no es 82.5 × 54.6 × 8.5 mm, corrige `protoboard_nodo_propuesta.dimensiones`.

### Cámara del DHT22

- [ ] El DHT22 real entra en su cuna (rieles laterales a 0.3 mm) con la rejilla hacia el frente.
- [ ] El cable del DHT22 pasa por la muesca de la doble pared hacia la bahía.
- [ ] Las ventilas de los costados, del piso y del aire entre paredes salieron abiertas, sin hilos de PETG.

## 3. Qué medir con el calibrador (y dónde anotarlo)

Anota cada medida en `cad/medidas.json` y cambia su `fuente` a `"medido"`. Luego corre `cad/nodos.py`: los cinco nodos se vuelven a verificar solos.

| Componente | Medidas (mm) | Clave en `medidas.json` |
|---|---|---|
| NodeMCU Amica | Largo y ancho de la PCB; alto total sobre la protoboard (de la base del header a la parte más alta); distancia del borde de la PCB al centro del micro-USB y su altura | `nodemcu.pcb`, `alto_sobre_protoboard`, `usb` |
| Cable micro-USB | Ancho, alto y largo del capuchón de plástico | `nodemcu.cable_usb_capuchon` |
| Protoboard 400 puntos | Largo, ancho, alto | `protoboard_nodo_propuesta.dimensiones` |
| OLED 2.42" | PCB (largo, ancho, alto con el vidrio); área activa; distancia del borde del conector al centro del área activa; número y orden de pines (4 = I²C) | `oled.modulo_2p42`, `area_activa_2p42`, `centro_activo_desde_conector` |
| DHT22 (AR0600) | Cuerpo; si trae PCB o pull-up; largo del cable | `dht22.cuerpo`, `formato`, `modulo_pcb` |
| HC-SR501 | PCB; Ø y alto del domo; separación de los agujeros; alto por detrás | `hc_sr501.*` |
| GY-61 y ADS1115 | Largo (a lo largo de la tira de pines) y alto de cada PCB; de qué lado van los componentes; orden de pines | `gy61.pcb`, `ads1115.pcb` |
| MC-38 | Sensor e imán (largo, ancho, alto); separación a la que cierra | `mc38.*` |
| KY-012 | PCB; Ø y alto del buzzer; **qué pin es +** (con multímetro) | `buzzer_ky012.*` |
| Botón del kit | 6 × 6 o 12 × 12; alto del cuerpo y del vástago | `boton_kit.*` |
| LED y LDR | Ø del LED y su ceja; Ø de la cabeza de la LDR | `led.diametro`, `led.agujero`, `ldr.cabeza_diametro` |
| Anaquel | Espesor de la repisa; material (madera, metal, alambre) | `DIS["anaquel_espesor"]` en `nodos.py` |

## 4. Registro de resultados

| Fecha | Cupón | Variante / resultado | Cambio aplicado | Quién |
|---|---|---|---|---|
| | | | | |
