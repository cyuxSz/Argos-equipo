# Ficha de impresión 3D (FDM): Argos

Versión 2, 20-oct-2026. Sale de `cad/nodos.py` (build123d 0.13). **Nada se ha impreso todavía.** Todas las medidas son nominales (`cad/medidas.json`); antes de las piezas finales, imprime las pruebas de ajuste de `cad/exports/pruebas/`.

## Archivos

| Carpeta | Contenido | Uso |
|---|---|---|
| `cad/exports/*.stl` | Cada pieza ya **orientada para imprimir** | Abrir en el slicer |
| `cad/exports/3mf/*.3mf` | Las mismas piezas, en mm y sin ambigüedad de unidades | Abrir en el slicer (preferible). La base del `dht` no tiene 3MF: el mallador lo rechaza; usa su STL |
| `cad/exports/*.step` | Fuente, en coordenadas del nodo | Editar o medir |
| `cad/exports/impresion/*.step` | Fuente orientada para imprimir | Origen del 3MF |

Para regenerar todo:

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/nodos.py
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" python cad/exportar_3mf.py
```

## Ajustes comunes (PETG; partir de aquí y ajustar al filamento comprado)

| Ajuste | Valor |
|---|---|
| Boquilla / cama | 235–245 °C / 75–85 °C |
| Boquilla | 0.4 mm |
| Capa | 0.2 mm (el detalle más fino es de 0.3 mm) |
| Perímetros | 5 (paredes de 2 mm sólidas) |
| Superior / inferior | 5 / 4 capas |
| Relleno | 25 % giroide (salvo donde se indica) |
| Soportes | **Ninguno**. Todas las piezas pasan el chequeo sin soportes |
| Ventilador | 30–50 % (PETG) |
| Cama mínima | **≥ 202 × 80 mm** para las bases de las estaciones. Una cama de 220 mm alcanza, con poco margen |

## Piezas

| Caja | Pieza | Material / color | Orientación en la cama | Relleno | Masa (g) | Observaciones |
|---|---|---|---|---|---|---|
| `dht` | base | PETG blanco/gris | Espalda | 25 % | 91.8 | 4 insertos M3 × 5 en las torretas |
| `dht` | tapa | PETG blanco/gris | Frente | 25 % | 31.6 | Ventana de la OLED, LED, botón, buzzer |
| `dht` | émbolo del botón | PETG | Ceja | 100 % | 0.1 | **Brim** o imprimir junto a otras piezas |
| `dht` | soporte de pared | PETG | Espalda | 25 % | 26.5 | O el soporte de anaquel (+6 g), según el lugar |
| Entrada | base | PETG blanco/gris | Espalda | 25 % | 89.3 | 202 mm con orejas; 4 insertos |
| Entrada | tapa | PETG blanco/gris | Frente | 25 % | 44.5 | Domo PIR; rótulos PIR / PUERTA |
| Entrada | porta-sensor (REED) | PETG | Piso | 40 % | 4.3 | Retención de 0.4 mm: probar primero. Salida del cable en +x |
| Entrada | porta-imán (IMAN) | PETG | Piso | 40 % | 4.4 | Cara lisa hacia el reed; muesca V en la espalda |
| Entrada | calzas de 2 y 4 mm | PETG | Planas | 100 % | 6.3 | Con las mismas ranuras que los portas |
| Entrada | 2 tacos de pared | PETG | Espalda | 40 % | 13.6 | Perno impreso: 40 % o más |
| Anaquel | base | PETG blanco/gris | Espalda | 25 % | 89.5 | Orejas rígidas con ranura M3 |
| Anaquel | tapa | PETG blanco/gris | Frente | 25 % | 47.6 | Costillas del `acel`; rótulos ACEL / LUZ |
| Anaquel | capuchón de la LDR | **PETG negro** (ver nota) | Cola (espalda) | 100 % | 5.2 | Ventana de Ø4.5 mm, visera de 4 mm, túnel para cincho, oreja M3 con agujero en gota |
| Anaquel | difusor de la LDR | **PETG blanco o natural** | Plano | 100 %, líneas concéntricas | 0.1 | Ø10 × 0.9 mm. Imprime 3 (0.6 / 0.9 / 1.2 mm) para la prueba de `docs/prueba_ldr.md` |
| Anaquel | horquilla de la LDR | PETG negro (o el del resto) | Placa | 40 % | 2.9 | M3 × 16 + tuerca; 2 tornillos de 3.5 mm o 2 cinchos |
| **Total** | | | | | **≈ 458 g** | Con 1 kg quedan ≈ 540 g para pruebas y reimpresiones |

**Nota del color negro.** El carrete comprado es de un solo color `[color POR CONFIRMAR]`. El capuchón solo necesita ser **opaco**. Sin comprar otro carrete se puede:
- imprimirlo en el PETG comprado y pintarlo por dentro y por fuera con acrílico negro mate (2 manos);
- o forrarlo con cinta de aislar negra;
- o pedir unos metros de filamento negro prestado.

Verifícalo con la prueba de luz: con la ventana tapada, la LDR no debe cambiar al encender la lámpara.

## Insertos y tornillería

| Pieza | Fijación |
|---|---|
| Bases (3) | 4 insertos térmicos M3 × 5 cada una (agujero de 4.0 mm), a 230–240 °C, perpendiculares |
| Tapas (3) | 4 × M3 × 10 avellanados cada una |
| Capuchón de la LDR | 1 × M3 × 16 + tuerca (pivote) |
| Horquilla de la LDR | 2 tornillos de 3.5 mm avellanados, o 2 cinchos |
| Portas del MC-38 | Cinta VHB debajo, 2 tornillos de cabeza plana de 3.5 mm por las ranuras, o ambos |

## Chequeos que pasaron (en el modelo)

- **Interferencias** con el gemelo nominal: 0 en las 3 cajas. Holgura mínima de los módulos libres: 3.5 mm (`dht`) y 4.07 mm (estaciones).
- **Capuchón de la LDR** (`cad/pruebas_ldr.py`):
  - la LDR, el cable y el difusor entran sin interferencia;
  - el capuchón gira en la horquilla de −90° a +75° sin chocar;
  - 0 voladizos (solo un puente de 1.6 mm en el túnel).
- **Portas del MC-38** (`cad/pruebas_mc38.py`):
  - el cuerpo asienta sin interferencia;
  - los topes retienen (0.84 mm³ de interferencia al pasar);
  - 0 voladizos;
  - las ranuras dan ±3.1 mm de ajuste por pieza.
- **Imprimibilidad** (build123d-mcp / augura) de las piezas nuevas. Los avisos restantes:
  - En el capuchón, el piso del túnel mide 0.8 mm, justo 2 perímetros.
  - En la horquilla queda un aviso de pared de 0.43 mm sin ubicación reportada (`[POR CONFIRMAR]` en el laminado).
  - En los portas, los avisos de menos de 1 mm² vienen del rótulo hundido en la pared vertical: no requieren soporte.

## Antes de imprimir las piezas finales

1. Imprime el peine de holguras y los cupones de `cad/exports/pruebas/`.
2. Imprime un porta del MC-38 y comprueba que el cuerpo real entra con "clic" y no se cae. Si no:
   - si no entra, baja `mc38.porta.retencion` a 0.3;
   - si se cae, súbela a 0.5.
3. Imprime el capuchón y los 3 difusores, y haz la prueba de `docs/prueba_ldr.md`.
