"""Chequeos del capuchon de la LDR (fase 1): ajuste de LDR, cable y difusor, giro en la horquilla,
voladizos de impresion y vista de corte.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/pruebas_ldr.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from build123d import GeomType, Plane

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nodos  # noqa: E402


def main():
    acc = nodos.capuchon_ldr()
    cap, dif, sop = (acc["piezas"][k] for k in ("capuchon_ldr", "difusor_ldr", "soporte_ldr"))
    fallas = []
    for nom, s in (("capuchon", cap), ("difusor", dif), ("soporte", sop)):
        if not s.is_valid or len(s.solids()) != 1:
            fallas.append(f"{nom}: solido invalido o en {len(s.solids())} partes")
    # gemelo: LDR contra la ventana, cable por la cola, difusor en su asiento
    gem = nodos.ldr_en_capuchon(largo_cable=10)
    ldr, cable = gem["ldr"], gem["cable"]
    dif_m = nodos.difusor_en_asiento(dif)
    for nom, s in (("ldr", ldr), ("cable", cable), ("difusor", dif_m)):
        v = (s & cap).volume
        d = s.distance_to(cap)
        print(f"{nom}: interferencia {v:.3f} mm3, separacion {d:.2f} mm")
        if v > 1e-3:
            fallas.append(f"{nom} choca con el capuchon")
    # giro en la horquilla alrededor del tornillo M3
    rango = [ang for ang in range(-90, 91, 5) if (nodos.sobre_horquilla(ang) * cap & sop).volume < 1e-3]
    libre = [a for a in rango]
    print(f"angulos libres (paso 5 grados): {min(libre)} a {max(libre)}" if libre else "sin angulos libres")
    if not (libre and min(libre) <= -30 and max(libre) >= 30):
        fallas.append("el giro libre no cubre +-30 grados")
    # voladizos: caras que miran hacia abajo por encima de la cama (impresion con la espalda en la cama)
    for nom, s in (("capuchon", cap), ("soporte", sop)):
        z0 = s.bounding_box().min.Z
        malas = 0
        for f in s.faces():
            try:
                nz = f.normal_at().Z
            except Exception:
                continue
            if f.geom_type != GeomType.PLANE:      # agujeros horizontales de 3.4 mm: se imprimen sin soporte
                continue
            if nz < -0.71 and f.center().Z > z0 + 0.05 and f.area > 4.0:
                bb = f.bounding_box()
                ancho = min(bb.size.X, bb.size.Y)
                puente = ancho <= 3.0 or (f.inner_wires() and f.area / f.outer_wire().length < 0.6)
                malas += 0 if puente else 1
                print(f"   {nom}: cara hacia abajo en z={f.center().Z:.1f}, area {f.area:.1f} mm2"
                      f" -> {'puente corto (ok)' if puente else 'VOLADIZO'}")
        print(f"{nom}: voladizos que piden soporte: {malas}")
        if malas:
            fallas.append(f"{nom}: voladizos")
    print("notas:", {k: round(v, 1) for k, v in acc["notas"].items()})
    # corte por el eje
    fig, ax = plt.subplots(figsize=(5, 6))
    sec = cap.intersect(Plane.YZ)
    for f in (sec.faces() if sec else []):
        pts = [tuple(f.outer_wire() @ (i / 200)) for i in range(201)]
        ax.fill([p[1] for p in pts], [p[2] for p in pts], color="0.2")
        for w in f.inner_wires():
            q = [tuple(w @ (i / 100)) for i in range(101)]
            ax.fill([p[1] for p in q], [p[2] for p in q], color="white")
    for s, col in ((ldr, "gold"), (dif_m, "lightblue"), (cable, "tab:red")):
        b = s.bounding_box()
        ax.add_patch(plt.Rectangle((b.min.Y, b.min.Z), b.size.Y, b.size.Z, color=col, alpha=0.8))
    ax.set_aspect("equal")
    ax.set_title("Capuchon LDR: corte por el eje (mm)\ncable rojo, LDR amarilla, difusor azul")
    ax.set_xlabel("y")
    ax.set_ylabel("z (espalda = 0)")
    destino = Path(__file__).resolve().parent / "renders" / "capuchon_ldr_corte.png"
    fig.savefig(destino, dpi=130, bbox_inches="tight")
    print("corte:", destino.name)
    print("FALLAS:" if fallas else "OK", fallas or "")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
