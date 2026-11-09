"""Chequeos del porta-sensor y porta-iman del MC-38 (fase 2): ajuste del cuerpo, retencion, voladizos y
rango de gap con las ranuras.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pruebas_mc38.py
"""
import sys
from pathlib import Path

from build123d import GeomType

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nodos  # noqa: E402
from nodos import caja_c, med, DIS  # noqa: E402


def main():
    P = med("mc38", "porta")
    fallas = []
    for nom, cuerpo, rot, cable in (("sensor", med("mc38", "cuerpo_sensor"), "REED", True),
                                    ("iman", med("mc38", "cuerpo_iman"), "IMAN", False)):
        pieza = nodos.porta_mc38(cuerpo, rot, cable)
        bx, by, bz = cuerpo
        modelo = caja_c(0, 0, P["piso"], bx, by, bz)          # cuerpo asentado en el piso
        v, d = (modelo & pieza).volume, modelo.distance_to(pieza)
        # al entrar, el cuerpo tiene que pasar los topes: interferencia esperada = retencion
        entrando = caja_c(0, 0, P["piso"] + bz * 0.5 + 0.9, bx, by, bz)
        v2 = (entrando & pieza).volume
        bb = pieza.bounding_box()
        print(f"{nom}: valido {pieza.is_valid}; asentado: interferencia {v:.3f} mm3, separacion {d:.2f} mm; "
              f"al pasar los topes: {v2:.2f} mm3 (retencion); caja {[round(x, 1) for x in bb.size]} mm; "
              f"masa {pieza.volume / 1000 * DIS['densidad_petg']:.1f} g")
        if not pieza.is_valid or v > 1e-3:
            fallas.append(f"{nom}: no asienta")
        if v2 < 1e-3:
            fallas.append(f"{nom}: sin retencion")
        z0 = bb.min.Z
        for f in pieza.faces():
            if f.geom_type != GeomType.PLANE:
                continue
            if f.normal_at().Z < -0.71 and f.center().Z > z0 + 0.05 and f.area > 2.0:
                fallas.append(f"{nom}: voladizo en z={f.center().Z:.1f} ({f.area:.1f} mm2)")
    rl, rw = P["ranura_largo"], P["ranura_ancho"]
    print(f"ajuste fino por ranuras: +-{(rl - rw) / 2:.1f} mm por pieza; paredes en el gap: "
          f"{2 * P['pared_frente']:.1f} mm (el gap se mide cuerpo a cuerpo)")
    print("FALLAS:" if fallas else "OK", fallas or "")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
