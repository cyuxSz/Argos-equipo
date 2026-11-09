"""Vistas ortograficas acotadas (frente, costado, espalda) de un nodo, con matplotlib.

Lo llama nodos.py despues de exportar. Proyecta las aristas visibles con build123d y agrega cotas.
"""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from build123d import Compound  # noqa: E402

RENDERS = Path(__file__).resolve().parent / "renders"

# (origen de la camara, arriba, mapeo de coordenadas 3D -> 2D del dibujo)
VISTAS = {
    "Frente": ((0, 0, 1000), (0, 1, 0), lambda p: (p.X, p.Y)),
    "Costado derecho": ((1000, 0, 0), (0, 1, 0), lambda p: (-p.Z, p.Y)),
    "Espalda": ((0, 0, -1000), (0, 1, 0), lambda p: (-p.X, p.Y)),
}


def _aristas(shape, origen, arriba):
    vis, ocultas = shape.project_to_viewport(origen, arriba, (0, 0, 0))
    return vis, ocultas


def _polilinea(e, n=24):
    try:
        if e.geom_type.name == "LINE":
            return [e.position_at(0), e.position_at(1)]
    except Exception:
        pass
    return [e.position_at(i / n) for i in range(n + 1)]


def cota(ax, a, b, desplaz, texto, vertical=False):
    """Cota entre los puntos a y b (2D), desplazada perpendicularmente."""
    (x1, y1), (x2, y2) = a, b
    if vertical:
        xs = x1 + desplaz
        ax.plot([x1, xs + math.copysign(1.5, desplaz)], [y1, y1], color="#555", lw=0.4)
        ax.plot([x2, xs + math.copysign(1.5, desplaz)], [y2, y2], color="#555", lw=0.4)
        ax.annotate("", xy=(xs, y1), xytext=(xs, y2), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#b03030"))
        ax.text(xs + math.copysign(1.5, desplaz), (y1 + y2) / 2, texto, rotation=90, va="center",
                ha="left" if desplaz > 0 else "right", fontsize=6.5, color="#b03030")
    else:
        ys = y1 + desplaz
        ax.plot([x1, x1], [y1, ys + math.copysign(1.5, desplaz)], color="#555", lw=0.4)
        ax.plot([x2, x2], [y2, ys + math.copysign(1.5, desplaz)], color="#555", lw=0.4)
        ax.annotate("", xy=(x1, ys), xytext=(x2, ys), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#b03030"))
        ax.text((x1 + x2) / 2, ys + math.copysign(1.2, desplaz), texto, ha="center",
                va="bottom" if desplaz > 0 else "top", fontsize=6.5, color="#b03030")


def dibujar(n):
    """n: diccionario que devuelve nodo_<id>() en nodos.py."""
    RENDERS.mkdir(exist_ok=True)
    nodo, W, H, D = n["nodo"], n["W"], n["H"], n["D"]
    cerrado = Compound(children=[n["piezas"]["base"], n["piezas"]["tapa"]])
    bb = cerrado.bounding_box()
    alto_fig = max(3.4, 11 * (bb.size.Y + 50) / (2 * W + D + 110))
    fig, ejes = plt.subplots(1, 3, figsize=(11, min(8.5, alto_fig)), sharey=True,
                             gridspec_kw={"width_ratios": [W + 50, D + 30, W + 30]})
    for ax, (titulo, (origen, arriba, _)) in zip(ejes, VISTAS.items()):
        vis, ocultas = _aristas(cerrado, origen, arriba)
        for e in ocultas:
            pts = _polilinea(e)
            ax.plot([p.X for p in pts], [p.Y for p in pts], color="#bbbbbb", lw=0.3, ls=(0, (2, 2)))
        for e in vis:
            pts = _polilinea(e)
            ax.plot([p.X for p in pts], [p.Y for p in pts], color="#222222", lw=0.6)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        ax.set_title(titulo, fontsize=9)
    # cotas: las proyecciones quedan centradas en el origen de la vista; se usan los limites reales
    for ax in ejes:
        ax.relim()
        ax.autoscale_view()
    fx = ejes[0]
    x0, x1 = fx.get_xlim()
    y0, y1 = fx.get_ylim()
    xa, xb = -W / 2, W / 2
    yb0, yb1 = (y0 + y1) / 2 - bb.size.Y / 2, (y0 + y1) / 2 + bb.size.Y / 2
    cx = bb.size.X
    cota(fx, (xa, yb0), (xb, yb0), -8, f"{W:.0f} cuerpo")
    if cx > W + 0.1:
        cota(fx, (-cx / 2, yb0), (cx / 2, yb0), -17, f"{cx:.0f} con orejas")
    if bb.size.Y > H + 0.1:
        cota(fx, (xa, yb0), (xa, yb1), -8, f"{bb.size.Y:.1f} con orejas", vertical=True)
        cota(fx, (xb, yb0 + (bb.size.Y - H) / 2), (xb, yb1 - (bb.size.Y - H) / 2), 8, f"{H:.1f} cuerpo",
              vertical=True)
    else:
        cota(fx, (xb, yb0), (xb, yb1), 24, f"{H:.1f} cuerpo", vertical=True)
    fx.set_xlim(x0 - 25, x1 + 25)
    fx.set_ylim(y0 - 26, y1 + 6)
    sx = ejes[1]
    x0, x1 = sx.get_xlim()
    y0, y1 = sx.get_ylim()
    cota(sx, (x0, y0), (x1, y0), -8, f"{D:.1f}")
    sx.set_xlim(x0 - 12, x1 + 12)
    sx.set_ylim(y0 - 18, y1 + 6)
    ex = ejes[2]
    ex.set_xlim(ex.get_xlim()[0] - 12, ex.get_xlim()[1] + 12)
    nota = (f"Paso entre pernos del soporte: {n['paso_pernos']:.1f} mm" if n["paso_pernos"]
            else "Orejas laterales con ranura para M3 o cincho (fijacion rigida)")
    ex.text(0.5, -0.02, nota, transform=ex.transAxes, ha="center", va="top", fontsize=7)
    fig.suptitle(f"Nodo {nodo}: vistas acotadas en mm, misma escala (borrador; componentes nominales)",
                 fontsize=10, y=1.02)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(RENDERS / f"nodo_{nodo}_vistas.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)
