# Plano de ubicación de las cajas en el cuarto

6-nov-2026. Generado con `cad/cuarto.py` a partir de las medidas de los encargados (5-nov) y de supuestos marcados `[POR CONFIRMAR]`. Para cambiar un supuesto, edita `SUP` en el script y vuelve a correrlo:

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib --with pyvista python cad/cuarto.py
```

Salidas:

- Plano 2D (planta y anaquel A visto desde el pasillo): `cad/renders/cuarto_plano.png` / `.svg`.
- Renders 3D: `cad/renders/cuarto_iso.png`, `cuarto_desde_puerta.png` y `cuarto_zoom_<caja>.png`.
- Modelo 3D: `cad/exports/cuarto/cuarto.step` y `cuarto.glb` (el GLB se abre con el Visor 3D de Windows).
- Largos de cable: `cad/exports/cuarto/cables.json`.

## Datos usados

| Dato | Valor | Fuente |
|---|---|---|
| Anaquel (largo × fondo × alto) | 184 × 48.3 × 183 cm, 2 anaqueles | Encargados |
| Pasillo entre anaqueles | 129.5 cm | Encargados |
| Luminaria a plataforma | ~34 cm | Encargados |
| Contactos C7 | Pared del fondo, a ~150 cm de altura, centrados en el pasillo | Encargados |
| Punta de los anaqueles a la pared de la puerta | ~250 cm | `[POR CONFIRMAR]` |
| Zona entre anaqueles y puerta | Libre en el modelo; hay mesas y sillas que ubica el equipo | Usuario |
| Contacto junto a la puerta | Pared de la puerta, del lado del anaquel B, a 30 cm del marco y a 30 cm del piso | `[POR CONFIRMAR]` |
| Minisplit | Pared del fondo, 40–70 cm por encima de los anaqueles (se usó 55 cm, ~238 cm del piso) | Usuario (aproximado) |
| Altura de las planchas | P1 180, P2 140, P3 100, P4 60 cm | `[POR CONFIRMAR]` |
| Puerta | 90 × 210 cm, centrada en el pasillo, abre hacia adentro con la bisagra del lado del anaquel A | `[POR CONFIRMAR]` |
| Luminarias | 61 cm (GLP24 = 24 in), 2 por plancha | `[POR CONFIRMAR]` |
| Anaqueles | Pegados a la pared del fondo y a las paredes laterales | `[POR CONFIRMAR]` |

## Ubicación de cada caja

| Caja | Dónde | Por qué |
|---|---|---|
| `dht` | Anaquel B, cara del pasillo, a media longitud, a ~110 cm (altura de los frascos de la plancha 3) | Mide a la altura de los frascos. Queda a ~24 cm bajo la luminaria y a ~1.5 m del minisplit. La pantalla se ve desde el pasillo. |
| Estación del anaquel (`acel` + `luz`) | Anaquel A, cara del pasillo, bajo el borde de la plancha 2, a ~26 cm de la pared del fondo | El `acel` queda fijo al anaquel y la LDR a ~10 cm de la luminaria de la plancha 3. Es la caja más cercana al contacto. |
| Estación de entrada (`pir` + `puerta`) | Pared de la puerta, del lado de la chapa, a 150 cm | El PIR ve el pasillo completo y el MC-38 alcanza el marco con su cable de 30 cm. |
| Caja de potencia (opcional) | Junto a la estación del anaquel, en el anaquel A | Cable de señal corto (6 hilos). |

## Cables (ruta por paredes y postes + 20 %)

| Cable | Ruta | Comprar | Tipo |
|---|---|---|---|
| Fuente → estación del anaquel | 110 cm | **1.5 m** | USB-C |
| Fuente → `dht` | 197 cm | **3 m** | micro-USB |
| Fuente (contacto junto a la puerta) → estación de entrada | 134 cm | **1.6 m** | USB-C |
| LDR → estación del anaquel | 8 cm | El del capuchón alcanza | 2 hilos |
| MC-38 → estación de entrada | 14 cm | Su cable de 30 cm alcanza | 2 hilos |
| Opcional: señal → caja de potencia | 32 cm | 40 cm | 6 hilos Dupont |
| Opcional: PARED → caja de potencia | 142 cm | 1.7 m | Clavija de 127 V |
| Opcional: P2/P3/P4 → anaquel A | 39–79 cm | Las extensiones de 3 m sobran | 127 V |
| Opcional: P2/P3/P4 → anaquel B (cruzando por arriba) | 237–317 cm | **2.8–3.8 m: las extensiones de 3 m no alcanzan para P3 y P4** | 127 V |

## Lo que salió del plano

1. **Estación de entrada:** se conecta al contacto que está junto a la puerta (~1.6 m de USB-C). Sin ese contacto serían ~5 m desde la pared del fondo. Con ~2.5 m entre los anaqueles y la puerta, el PIR junto a la puerta ve la zona de mesas y el pasillo; hay que ajustar su sensibilidad para que no dispare con alguien sentado.
2. **`dht`:** necesita un cable micro-USB de 3 m. El de la fuente Steren ELI-712 seguramente es más corto `[POR CONFIRMAR]`.
3. **Fotoperiodo (opcional):** si un relé controla la misma plancha en los dos anaqueles, las salidas hacia el anaquel B necesitan extensiones de 4–5 m en vez de 3 m, o una regleta en cada anaquel. Hay que decidir si cada relé es "plancha N de los dos anaqueles" o "plancha N de un solo anaquel".
4. **Soporte del `dht`:** a media longitud del anaquel no hay poste. Va colgado del borde de la plancha con su pinza, o con cinchos si no autorizan atornillar (pregunta C5).

## Por confirmar en la próxima visita (cinta métrica y foto)

- Altura real de cada plancha desde el piso y su espesor (pregunta C7).
- Ancho de la puerta, lado de la bisagra y hacia dónde abre.
- Altura y pared del minisplit, y hacia dónde sopla.
- Si los anaqueles están pegados a las paredes.
- Distancia de los anaqueles a la pared de la puerta; pared, altura y distancia de los contactos junto a la puerta.
- Largo del cable de las fuentes que se van a usar.
