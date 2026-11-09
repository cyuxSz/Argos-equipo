"""Piezas de prueba de ajuste (Fase 7): recortes de las piezas reales del nodo dht + peine de holguras.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pruebas.py

Salida: cad/exports/pruebas/<cupon>.stl (orientado para imprimir) y .step, y un resumen en consola.
Los recortes salen de la misma geometria que las piezas finales: si una prueba falla, se corrige
cad/medidas.json o la holgura y se regeneran nodos y pruebas.
"""
import json

from build123d import Pos, Rot, export_step, export_stl

import nodos
from nodos import DIS, SALIDA, caja, caja_c, cil, med, texto
from build123d import Plane

PRUEBAS = SALIDA / "pruebas"


def a_cama(s, voltear=False):
    if voltear:
        s = Rot(180, 0, 0) * s
    bb = s.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * s


def peine_holguras():
    """Placa con 3 variantes (holgura -0.1 / actual / +0.1) de cada ajuste critico."""
    hg = DIS["holgura"]
    deltas = (-0.1, 0.0, 0.1)
    placa = caja_c(0, 0, 0, 70, 52, 2.5)
    for i, d in enumerate(deltas):
        x = -22 + 22 * i
        # LED de 5 mm: agujero de la tapa (5.3 = 5.0 + 0.3)
        placa -= cil(x, 16, -0.1, med("led", "diametro") + hg + d, 3.0)
        # embolo del boton: agujero de 4.4 para un vastago de 4.0
        placa -= cil(x, 4, -0.1, 4.0 + hg + 0.1 + d, 3.0)
        # cuna del boton (6x6 nominal): hueco cuadrado de lado + holgura
        b = med("boton_kit", "cuerpo")[0]
        placa += caja_c(x, -10, 2.5, b + 2 * hg + 2.4 + 2 * d, b + 2 * hg + 2.4 + 2 * d, 4.0) - \
            caja_c(x, -10, 2.4, b + 2 * hg + 2 * d, b + 2 * hg + 2 * d, 4.2)
        # torreta con agujero para inserto M3 x 5 (4.0 nominal)
        placa += cil(x, -21, 2.5, 8.0, 7.0) - cil(x, -21, 4.0, DIS["inserto_d"] + d, 5.6)
        # numero de variante hundido (1 = mas justo, 3 = mas holgado)
        try:
            placa -= texto(str(i + 1), 5.0, Plane(origin=(x, 23, 2.5), z_dir=(0, 0, 1)), 0.6)
        except Exception as err:
            print("aviso: numero omitido:", err)
    return placa


def main():
    PRUEBAS.mkdir(parents=True, exist_ok=True)
    n = nodos.nodo_dht()
    base, tapa = n["piezas"]["base"], n["piezas"]["tapa"]
    W, H, Db, D = n["W"], n["H"], n["Db"], n["D"]
    pb_y0 = n["y_pb_inf"]  # borde inferior de la protoboard en el dht

    cupones = {
        # tapa: ventana y marco de la OLED + collares de LED + boton (cara frontal en la cama)
        "prueba_tapa_oled_led_boton": (tapa & caja(-32.5, 56, Db - 6, 65, 128 - 56, 20), True),
        # base: camara del DHT22 con doble pared, cuna y ventilas, recortada a 22 mm de alto
        "prueba_camara_dht22": (base & caja(-W / 2 - 1, 0, -1, W + 2, pb_y0 + 1, 23), False),
        # base: fondo de la bahia con las 4 guias de la protoboard (6 mm de alto)
        "prueba_bahia_protoboard": (base & caja(-29, pb_y0 - 6, -1, 58, H - 2 - (pb_y0 - 6), 7), False),
        # peine de holguras: LED, embolo, cuna del boton e inserto M3
        "prueba_peine_holguras": (peine_holguras(), False),
    }
    resumen = {}
    for nombre, (s, voltear) in cupones.items():
        export_step(s, str(PRUEBAS / f"{nombre}.step"))
        s_cama = a_cama(s, voltear)
        export_step(s_cama, str(PRUEBAS / f"{nombre}_cama.step"))
        export_stl(s_cama, str(PRUEBAS / f"{nombre}.stl"), tolerance=0.02, angular_tolerance=0.2)
        bb = s_cama.bounding_box().size
        resumen[nombre] = {"caja_mm": [round(v, 1) for v in bb],
                           "masa_g_petg": round(s.volume / 1000 * DIS["densidad_petg"], 1)}
        print(nombre, resumen[nombre])
    (PRUEBAS / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
