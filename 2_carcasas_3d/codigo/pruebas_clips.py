"""Cupon de la variante modular: 3 clips de protoboard y 3 broches de tapa con distinto apriete.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pruebas_clips.py

Salida: cad/exports/modular/pruebas/prueba_clips_base.stl y prueba_clips_tira.stl (+ .step).
Usa las mismas funciones que las cajas (nodos.clip_piso, lengua_pared, pestana_tapa): la variante que
ajuste bien se copia a DIS["clip"]["gancho"] y DIS["broche"]["aprieto"] en cad/nodos.py.

Como probar: la protoboard de 400 puntos real se apoya contra el riel izquierdo y se baja sobre los tres clips
(1 = gancho de 0.8 mm, 2 = 1.0, 3 = 1.2). La tira se presiona sobre la pared (1 = apriete 0.35 mm, 2 = 0.5, 3 = 0.65).
"""
import os

os.environ["ARGOS_MODULAR"] = "1"

from build123d import Plane, Pos, Rot, export_step, export_stl  # noqa: E402

import nodos  # noqa: E402
from nodos import DIS, caja, clip_piso, lengua_pared, med, pestana_tapa, texto  # noqa: E402

PRUEBAS = nodos.RAIZ / "exports" / "modular" / "pruebas"
GANCHOS = (0.8, 1.0, 1.2)
APRIETOS = (0.35, 0.5, 0.65)
CENTROS = (15.0, 43.0, 71.0)


def cupon():
    p, W = DIS["pared"], DIS["ancho"]
    largo, ancho_pb, alto_pb = med("protoboard_nodo_propuesta", "dimensiones")
    Db = 16.0                                   # pared recortada: la lengua mide lo mismo que en la caja
    xb = ancho_pb / 2
    y1 = largo + 3.5
    base = caja(-xb - 4.0, 0, 0, W / 2 + xb + 4.0, y1, p)
    base += caja(-xb - DIS["clip"]["juego"] - 1.6, 0, p, 1.6, y1, 6.0)          # riel izquierdo (tope fijo)
    base += caja(W / 2 - p, 0, 0, p, y1, Db)                                    # pared con las lenguas
    xo = W / 2 - p - DIS["holgura"]
    tira = caja(xo - 6.0, 0, Db, W / 2 - xo + 6.0, y1, DIS["tapa"])
    for k, yc in enumerate(CENTROS):
        suma, resta = clip_piso(1, xb, yc, p + alto_pb, W / 2 - p, p, gancho=GANCHOS[k])
        base = base - resta + suma
        suma, resta = lengua_pared(1, W, p, Db, yc, aprieto=APRIETOS[k])
        base = base - resta + suma
        # respaldo detras de la pestana (en la caja lo da la tapa completa, que no puede moverse hacia adentro)
        base += caja(xo - 3.0 - DIS["holgura"] - 1.6, yc - 11.0, p, 1.6, 17.0, Db - 1.0 - p)
        tira += pestana_tapa(1, W, p, Db, yc)
        for pieza, z, x in ((base, p, -10.0), (tira, Db + DIS["tapa"], xo - 2.5)):
            try:
                marca = texto(str(k + 1), 5.0, Plane(origin=(x, yc, z), z_dir=(0, 0, 1)), 0.5)
                if pieza is base:
                    base -= marca
                else:
                    tira -= marca
            except Exception as err:
                print("aviso: numero omitido:", err)
    return base, tira


def a_cama(s, voltear=False):
    if voltear:
        s = Rot(180, 0, 0) * s
    bb = s.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * s


def main():
    PRUEBAS.mkdir(parents=True, exist_ok=True)
    base, tira = cupon()
    choque = (base & tira).volume
    for nombre, s, voltear in (("prueba_clips_base", base, False), ("prueba_clips_tira", tira, True)):
        export_step(s, str(PRUEBAS / f"{nombre}.step"))
        export_stl(a_cama(s, voltear), str(PRUEBAS / f"{nombre}.stl"), tolerance=0.02, angular_tolerance=0.2)
        bb = s.bounding_box().size
        print(f"{nombre}: {bb.X:.0f} x {bb.Y:.0f} x {bb.Z:.1f} mm, {s.volume / 1000 * DIS['densidad_petg']:.1f} g de PETG, "
              f"{len(s.solids())} solido(s)")
    print(f"choque base-tira: {choque:.3f} mm3 (debe ser 0)")


if __name__ == "__main__":
    main()
